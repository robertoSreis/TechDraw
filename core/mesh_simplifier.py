"""
===============================================================================
STL2TechnicalDrawing - Simplificador de Malha para Desenhos Técnicos
===============================================================================
Pasta: core/
Arquivo: core/mesh_simplifier.py
Descrição: Reduz complexidade de malha mantendo apenas features importantes
===============================================================================
"""

import numpy as np
import trimesh
from typing import Tuple, Set, Dict, List
from dataclasses import dataclass
from PyQt6.QtCore import QObject, pyqtSignal


@dataclass
class SimplifiedMesh:
    """Malha simplificada com apenas arestas significativas"""
    vertices: np.ndarray
    faces: np.ndarray
    edges: np.ndarray
    feature_edges: np.ndarray
    silhouette_edges: np.ndarray
    face_normals: np.ndarray


class MeshSimplifier(QObject):
    """
    Simplifica malha STL para desenho técnico.
    Remove triângulos internos e mantém apenas contornos e features.
    """
    
    # Sinais para progresso
    progress = pyqtSignal(int, int, str)  # current, total, message
    
    def __init__(self, 
                 feature_angle_threshold: float = 20.0,
                 simplify_ratio: float = 0.3,
                 min_edge_length: float = 0.01):
        super().__init__()
        self.feature_angle = feature_angle_threshold
        self.simplify_ratio = simplify_ratio
        self.min_edge_length = min_edge_length
        self.should_cancel = False
    
    def cancel(self):
        """Cancela operação"""
        self.should_cancel = True
    
    def simplify(self, mesh: trimesh.Trimesh) -> SimplifiedMesh:
        """Simplifica malha mantendo apenas features importantes"""
        self.should_cancel = False
        
        self.progress.emit(0, 100, "Iniciando simplificação...")
        
        if self.should_cancel:
            raise Exception("Cancelado")
        
        print(f"[Simplificador] Vértices: {len(mesh.vertices):,}, Faces: {len(mesh.faces):,}")
        
        # 1. Simplifica malha
        self.progress.emit(10, 100, "Reduzindo triângulos...")
        simplified_mesh = self._decimate_mesh(mesh)
        
        if self.should_cancel:
            raise Exception("Cancelado")
        
        # 2. Calcula normais
        self.progress.emit(30, 100, "Calculando normais das faces...")
        face_normals = self._compute_face_normals(
            simplified_mesh.vertices, 
            simplified_mesh.faces
        )
        
        if self.should_cancel:
            raise Exception("Cancelado")
        
        # 3. Features
        self.progress.emit(50, 100, "Detectando features importantes...")
        feature_edges = self._extract_feature_edges(
            simplified_mesh.vertices,
            simplified_mesh.faces,
            face_normals
        )
        
        if self.should_cancel:
            raise Exception("Cancelado")
        
        # 4. Silhuetas
        self.progress.emit(70, 100, "Extraindo contornos...")
        silhouette_edges = self._extract_boundary_edges(simplified_mesh.faces)
        
        if self.should_cancel:
            raise Exception("Cancelado")
        
        # 5. Combina
        self.progress.emit(85, 100, "Combinando arestas...")
        all_edges = self._combine_edges(feature_edges, silhouette_edges)
        
        # 6. Filtra
        self.progress.emit(95, 100, "Filtrando micro-arestas...")
        all_edges = self._filter_small_edges(simplified_mesh.vertices, all_edges)
        
        self.progress.emit(100, 100, "Simplificação concluída!")
        
        print(f"[Simplificador] Arestas reduzidas: {len(mesh.faces) * 3:,} → {len(all_edges):,}")
        
        return SimplifiedMesh(
            vertices=simplified_mesh.vertices,
            faces=simplified_mesh.faces,
            edges=all_edges,
            feature_edges=feature_edges,
            silhouette_edges=silhouette_edges,
            face_normals=face_normals
        )
    
    def _decimate_mesh(self, mesh: trimesh.Trimesh) -> trimesh.Trimesh:
        """Reduz número de triângulos"""
        try:
            target_faces = max(100, int(len(mesh.faces) * self.simplify_ratio))
            simplified = mesh.simplify_quadric_decimation(target_faces)
            return simplified
        except:
            return mesh
    
    def _compute_face_normals(self, vertices: np.ndarray, 
                              faces: np.ndarray) -> np.ndarray:
        """Calcula normais de cada face"""
        normals = np.zeros((len(faces), 3))
        
        for i, face in enumerate(faces):
            v0, v1, v2 = vertices[face[0]], vertices[face[1]], vertices[face[2]]
            edge1, edge2 = v1 - v0, v2 - v0
            normal = np.cross(edge1, edge2)
            
            length = np.linalg.norm(normal)
            if length > 0:
                normal /= length
            
            normals[i] = normal
        
        return normals
    
    def _extract_feature_edges(self, vertices: np.ndarray,
                                faces: np.ndarray,
                                normals: np.ndarray) -> np.ndarray:
        """Extrai arestas onde há mudança significativa de direção"""
        edge_to_faces: Dict[Tuple[int, int], List[int]] = {}
        
        for face_idx, face in enumerate(faces):
            for i in range(3):
                v1, v2 = face[i], face[(i + 1) % 3]
                edge_key = (min(v1, v2), max(v1, v2))
                
                if edge_key not in edge_to_faces:
                    edge_to_faces[edge_key] = []
                edge_to_faces[edge_key].append(face_idx)
        
        feature_edges = []
        threshold_rad = np.radians(self.feature_angle)
        
        for edge_key, face_indices in edge_to_faces.items():
            if len(face_indices) == 2:
                n1 = normals[face_indices[0]]
                n2 = normals[face_indices[1]]
                
                dot = np.clip(np.dot(n1, n2), -1, 1)
                angle = np.arccos(dot)
                
                if angle > threshold_rad:
                    feature_edges.append(edge_key)
            elif len(face_indices) == 1:
                feature_edges.append(edge_key)
        
        return np.array(feature_edges, dtype=np.uint32) if feature_edges else np.array([], dtype=np.uint32).reshape(0, 2)
    
    def _extract_boundary_edges(self, faces: np.ndarray) -> np.ndarray:
        """Extrai arestas de contorno"""
        edge_count: Dict[Tuple[int, int], int] = {}
        
        for face in faces:
            for i in range(3):
                v1, v2 = face[i], face[(i + 1) % 3]
                edge_key = (min(v1, v2), max(v1, v2))
                edge_count[edge_key] = edge_count.get(edge_key, 0) + 1
        
        boundary_edges = [edge for edge, count in edge_count.items() if count == 1]
        
        return np.array(boundary_edges, dtype=np.uint32) if boundary_edges else np.array([], dtype=np.uint32).reshape(0, 2)
    
    def _combine_edges(self, edges1: np.ndarray, edges2: np.ndarray) -> np.ndarray:
        """Combina dois conjuntos de arestas sem duplicatas"""
        if len(edges1) == 0:
            return edges2
        if len(edges2) == 0:
            return edges1
        
        edges_set = set()
        
        for edge in edges1:
            edges_set.add(tuple(edge))
        
        for edge in edges2:
            edges_set.add(tuple(edge))
        
        return np.array(list(edges_set), dtype=np.uint32)
    
    def _filter_small_edges(self, vertices: np.ndarray,
                            edges: np.ndarray) -> np.ndarray:
        """Remove arestas muito pequenas"""
        if len(edges) == 0:
            return edges
        
        filtered_edges = []
        
        for edge in edges:
            v1, v2 = vertices[edge[0]], vertices[edge[1]]
            length = np.linalg.norm(v2 - v1)
            
            if length >= self.min_edge_length:
                filtered_edges.append(edge)
        
        return np.array(filtered_edges, dtype=np.uint32) if filtered_edges else np.array([], dtype=np.uint32).reshape(0, 2)