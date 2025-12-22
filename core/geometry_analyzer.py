"""
===============================================================================
STL2TechnicalDrawing - Analisador de Geometria Avançado
===============================================================================
Pasta: core/
Arquivo: core/geometry_analyzer.py
Descrição: Analisa geometria 3D para detectar features como furos, chanfros, etc.
===============================================================================
"""

import numpy as np
from typing import List, Tuple, Dict, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import math


class FeatureType(Enum):
    """Tipos de features geométricas"""
    HOLE = "hole"              # Furo passante
    POCKET = "pocket"          # Cavidade/rebaixo
    BOSS = "boss"              # Ressalto
    CHAMFER = "chamfer"        # Chanfro
    FILLET = "fillet"          # Arredondamento
    SLOT = "slot"              # Rasgo
    FLAT_FACE = "flat_face"    # Face plana
    CURVED_FACE = "curved"     # Face curva


@dataclass
class GeometricFeature:
    """Representa uma feature geométrica detectada"""
    feature_type: FeatureType
    position: Tuple[float, float, float]
    dimensions: Dict[str, float]  # Depende do tipo
    normal: Optional[Tuple[float, float, float]] = None
    confidence: float = 1.0


@dataclass
class EdgeInfo:
    """Informações detalhadas sobre uma aresta"""
    start_idx: int
    end_idx: int
    start_pos: np.ndarray
    end_pos: np.ndarray
    length: float
    direction: np.ndarray  # Vetor unitário
    adjacent_faces: List[int]
    is_boundary: bool = False
    angle_between_faces: float = 0.0  # Ângulo entre faces adjacentes


@dataclass  
class FaceInfo:
    """Informações detalhadas sobre uma face"""
    index: int
    vertices: np.ndarray
    normal: np.ndarray
    area: float
    centroid: np.ndarray
    is_planar: bool = True
    adjacent_faces: List[int] = field(default_factory=list)


class GeometryAnalyzer:
    """
    Analisador avançado de geometria 3D.
    Detecta features, calcula ângulos, identifica furos e outras características.
    """
    
    def __init__(self, vertices: np.ndarray, faces: np.ndarray, edges: np.ndarray):
        """
        Inicializa o analisador.
        
        Args:
            vertices: Array de vértices (N, 3)
            faces: Array de faces (M, 3)  
            edges: Array de arestas (E, 2)
        """
        self.vertices = vertices
        self.faces = faces
        self.edges = edges
        
        # Análises pré-computadas
        self.face_normals: Optional[np.ndarray] = None
        self.face_areas: Optional[np.ndarray] = None
        self.face_centroids: Optional[np.ndarray] = None
        self.edge_info: List[EdgeInfo] = []
        self.face_info: List[FaceInfo] = []
        
        # Cache de adjacências
        self._face_adjacency: Dict[int, Set[int]] = {}
        self._edge_to_faces: Dict[Tuple[int, int], List[int]] = {}
        
        # Executa análises
        self._analyze_geometry()
    
    def _analyze_geometry(self):
        """Executa todas as análises geométricas"""
        self._compute_face_properties()
        self._build_adjacency_maps()
        self._analyze_edges()
    
    def _compute_face_properties(self):
        """Calcula propriedades de cada face"""
        n_faces = len(self.faces)
        self.face_normals = np.zeros((n_faces, 3))
        self.face_areas = np.zeros(n_faces)
        self.face_centroids = np.zeros((n_faces, 3))
        
        for i, face in enumerate(self.faces):
            v0 = self.vertices[face[0]]
            v1 = self.vertices[face[1]]
            v2 = self.vertices[face[2]]
            
            # Normal
            edge1 = v1 - v0
            edge2 = v2 - v0
            normal = np.cross(edge1, edge2)
            area = np.linalg.norm(normal) / 2
            
            if area > 0:
                normal = normal / (2 * area)
            
            self.face_normals[i] = normal
            self.face_areas[i] = area
            self.face_centroids[i] = (v0 + v1 + v2) / 3
            
            # Cria FaceInfo
            self.face_info.append(FaceInfo(
                index=i,
                vertices=np.array([v0, v1, v2]),
                normal=normal,
                area=area,
                centroid=self.face_centroids[i]
            ))
    
    def _build_adjacency_maps(self):
        """Constrói mapas de adjacência entre faces e arestas"""
        # Mapeia arestas para faces
        for i, face in enumerate(self.faces):
            for j in range(3):
                v1, v2 = face[j], face[(j + 1) % 3]
                edge_key = (min(v1, v2), max(v1, v2))
                
                if edge_key not in self._edge_to_faces:
                    self._edge_to_faces[edge_key] = []
                self._edge_to_faces[edge_key].append(i)
        
        # Constrói adjacência de faces
        for i, face in enumerate(self.faces):
            self._face_adjacency[i] = set()
            
            for j in range(3):
                v1, v2 = face[j], face[(j + 1) % 3]
                edge_key = (min(v1, v2), max(v1, v2))
                
                for adj_face in self._edge_to_faces.get(edge_key, []):
                    if adj_face != i:
                        self._face_adjacency[i].add(adj_face)
            
            self.face_info[i].adjacent_faces = list(self._face_adjacency[i])
    
    def _analyze_edges(self):
        """Analisa cada aresta em detalhe"""
        for edge in self.edges:
            v1_idx, v2_idx = edge[0], edge[1]
            v1 = self.vertices[v1_idx]
            v2 = self.vertices[v2_idx]
            
            direction = v2 - v1
            length = np.linalg.norm(direction)
            
            if length > 0:
                direction = direction / length
            
            edge_key = (min(v1_idx, v2_idx), max(v1_idx, v2_idx))
            adjacent_faces = self._edge_to_faces.get(edge_key, [])
            
            # Calcula ângulo entre faces adjacentes
            angle = 0.0
            is_boundary = len(adjacent_faces) == 1
            
            if len(adjacent_faces) == 2:
                n1 = self.face_normals[adjacent_faces[0]]
                n2 = self.face_normals[adjacent_faces[1]]
                dot = np.clip(np.dot(n1, n2), -1, 1)
                angle = np.degrees(np.arccos(dot))
            
            self.edge_info.append(EdgeInfo(
                start_idx=v1_idx,
                end_idx=v2_idx,
                start_pos=v1,
                end_pos=v2,
                length=length,
                direction=direction,
                adjacent_faces=adjacent_faces,
                is_boundary=is_boundary,
                angle_between_faces=angle
            ))
    
    def get_overall_dimensions(self) -> Dict[str, float]:
        """Retorna as dimensões gerais do modelo"""
        min_coords = self.vertices.min(axis=0)
        max_coords = self.vertices.max(axis=0)
        dims = max_coords - min_coords
        
        return {
            'width': float(dims[0]),     # X
            'height': float(dims[1]),    # Y  
            'depth': float(dims[2]),     # Z
            'min_x': float(min_coords[0]),
            'max_x': float(max_coords[0]),
            'min_y': float(min_coords[1]),
            'max_y': float(max_coords[1]),
            'min_z': float(min_coords[2]),
            'max_z': float(max_coords[2]),
        }
    
    def find_parallel_faces(self, tolerance: float = 0.01) -> List[Tuple[int, int]]:
        """Encontra pares de faces paralelas"""
        parallel_pairs = []
        n_faces = len(self.faces)
        
        for i in range(n_faces):
            for j in range(i + 1, n_faces):
                n1 = self.face_normals[i]
                n2 = self.face_normals[j]
                
                # Faces paralelas: normais iguais ou opostas
                dot = abs(np.dot(n1, n2))
                if dot > 1 - tolerance:
                    parallel_pairs.append((i, j))
        
        return parallel_pairs
    
    def find_perpendicular_faces(self, tolerance: float = 0.01) -> List[Tuple[int, int]]:
        """Encontra pares de faces perpendiculares"""
        perpendicular_pairs = []
        n_faces = len(self.faces)
        
        for i in range(n_faces):
            for j in range(i + 1, n_faces):
                n1 = self.face_normals[i]
                n2 = self.face_normals[j]
                
                dot = abs(np.dot(n1, n2))
                if dot < tolerance:
                    perpendicular_pairs.append((i, j))
        
        return perpendicular_pairs
    
    def find_sharp_edges(self, min_angle: float = 30.0) -> List[EdgeInfo]:
        """Encontra arestas com ângulo maior que o especificado"""
        sharp_edges = []
        
        for edge in self.edge_info:
            if edge.angle_between_faces >= min_angle:
                sharp_edges.append(edge)
        
        return sharp_edges
    
    def detect_cylindrical_regions(self, 
                                    min_segments: int = 8,
                                    tolerance: float = 0.05) -> List[GeometricFeature]:
        """
        Detecta regiões cilíndricas (furos, bosses).
        Procura por conjuntos de faces cujas normais apontam radialmente.
        """
        cylinders = []
        
        # Agrupa faces por orientação da normal
        face_groups = self._group_faces_by_normal_direction()
        
        for group in face_groups:
            if len(group) >= min_segments:
                # Verifica se as faces formam um cilindro
                cylinder = self._check_cylindrical_group(group, tolerance)
                if cylinder is not None:
                    cylinders.append(cylinder)
        
        return cylinders
    
    def _group_faces_by_normal_direction(self) -> List[List[int]]:
        """Agrupa faces cujas normais apontam em direções similares radialmente"""
        # Simplificado: agrupa faces adjacentes com normais similares
        groups = []
        used = set()
        
        for i in range(len(self.faces)):
            if i in used:
                continue
            
            group = [i]
            used.add(i)
            
            # Expande grupo com faces adjacentes similares
            queue = list(self._face_adjacency.get(i, set()))
            
            while queue:
                j = queue.pop(0)
                if j in used:
                    continue
                
                # Verifica se a face tem normal perpendicular ao eixo Y (horizontal)
                normal = self.face_normals[j]
                if abs(normal[1]) < 0.1:  # Normal quase horizontal
                    group.append(j)
                    used.add(j)
                    queue.extend(self._face_adjacency.get(j, set()))
            
            if len(group) >= 4:
                groups.append(group)
        
        return groups
    
    def _check_cylindrical_group(self, face_indices: List[int], 
                                  tolerance: float) -> Optional[GeometricFeature]:
        """Verifica se um grupo de faces forma um cilindro"""
        if len(face_indices) < 8:
            return None
        
        # Coleta centróides das faces
        centroids = np.array([self.face_centroids[i] for i in face_indices])
        
        # Tenta ajustar um círculo no plano XZ
        center_x = centroids[:, 0].mean()
        center_z = centroids[:, 2].mean()
        
        # Calcula raios
        radii = np.sqrt((centroids[:, 0] - center_x)**2 + 
                       (centroids[:, 2] - center_z)**2)
        
        mean_radius = radii.mean()
        radius_std = radii.std()
        
        # Se os raios são consistentes, é um cilindro
        if radius_std / mean_radius < tolerance:
            height = centroids[:, 1].max() - centroids[:, 1].min()
            
            return GeometricFeature(
                feature_type=FeatureType.HOLE if height > 0 else FeatureType.BOSS,
                position=(center_x, centroids[:, 1].mean(), center_z),
                dimensions={
                    'diameter': mean_radius * 2,
                    'radius': mean_radius,
                    'height': height
                },
                confidence=1 - (radius_std / mean_radius)
            )
        
        return None
    
    def get_edge_lengths(self) -> Dict[str, List[float]]:
        """Retorna estatísticas sobre comprimentos de arestas"""
        lengths = [e.length for e in self.edge_info]
        
        if not lengths:
            return {'lengths': [], 'unique': [], 'min': 0, 'max': 0}
        
        # Agrupa comprimentos similares
        lengths_sorted = sorted(lengths)
        unique_lengths = []
        tolerance = 0.01
        
        for length in lengths_sorted:
            is_unique = True
            for ul in unique_lengths:
                if abs(length - ul) < tolerance:
                    is_unique = False
                    break
            if is_unique:
                unique_lengths.append(length)
        
        return {
            'lengths': lengths,
            'unique': unique_lengths,
            'min': min(lengths),
            'max': max(lengths),
            'count': len(lengths)
        }
    
    def get_angles_between_faces(self) -> List[float]:
        """Retorna todos os ângulos entre faces adjacentes"""
        angles = []
        
        for edge in self.edge_info:
            if not edge.is_boundary and edge.angle_between_faces > 0:
                angles.append(edge.angle_between_faces)
        
        return angles
