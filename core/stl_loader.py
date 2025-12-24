"""
===============================================================================
STL2TechnicalDrawing - Carregador com EIXO Y CORRIGIDO (NÃO INVERTE)
===============================================================================
Pasta: core/
Arquivo: core/stl_loader.py
Descrição: Carrega STL convertendo Z→Y SEM INVERTER o eixo
===============================================================================
"""

import numpy as np
from stl import mesh as stl_mesh
import trimesh
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass


@dataclass
class MeshData:
    """Estrutura de dados do mesh carregado"""
    vertices: np.ndarray
    normals: np.ndarray
    faces: np.ndarray
    edges: np.ndarray
    bounds: Tuple[np.ndarray, np.ndarray]
    center: np.ndarray
    scale: float
    
    vertex_data: np.ndarray
    face_indices: np.ndarray
    edge_indices: np.ndarray
    
    original_face_count: int = 0
    simplified_face_count: int = 0
    original_edge_count: int = 0
    simplified_edge_count: int = 0


class STLLoader:
    """Carregador de arquivos STL com simplificação OBRIGATÓRIA"""
    
    def __init__(self, simplify_for_drawing: bool = True):
        """
        Args:
            simplify_for_drawing: Se True (padrão), simplifica malha
        """
        self.mesh: Optional[trimesh.Trimesh] = None
        self.mesh_data: Optional[MeshData] = None
        self.filepath: str = ""
        self.simplify = simplify_for_drawing
    
    def load(self, filepath: str) -> MeshData:
        """
        Carrega um arquivo STL e processa para renderização
        """
        self.filepath = filepath
        
        print(f"\n{'='*70}")
        print(f"CARREGANDO STL: {filepath}")
        print(f"{'='*70}")
        
        # Carrega com trimesh
        self.mesh = trimesh.load(filepath)
        
        # Se for uma cena, pega o primeiro mesh
        if isinstance(self.mesh, trimesh.Scene):
            meshes = list(self.mesh.geometry.values())
            if meshes:
                self.mesh = meshes[0]
            else:
                raise ValueError("Arquivo STL vazio ou inválido")
        
        original_face_count = len(self.mesh.faces)
        original_edge_count = len(self.mesh.faces) * 3
        
        print(f"✓ Vértices: {len(self.mesh.vertices):,}")
        print(f"✓ Faces: {original_face_count:,}")
        print(f"✓ Arestas totais: {original_edge_count:,}")
        
        # ============================================================
        # ✅ CONVERSÃO DE COORDENADAS STL → INTERNO
        # ============================================================
        print(f"\n🔄 CONVERTENDO SISTEMA DE COORDENADAS:")
        print(f"   STL padrão → Sistema interno")
        print(f"   X→X (direita), Y→Z (frente), Z→Y (altura)")
        
        # Mostra dimensões ANTES
        bounds_before = self.mesh.bounds
        dims_before = bounds_before[1] - bounds_before[0]
        print(f"\n   ANTES: X={dims_before[0]:.1f}, Y={dims_before[1]:.1f}, Z={dims_before[2]:.1f}")
        
        # ✅ CONVERSÃO CORRETA: Troca Y e Z
        vertices_converted = self.mesh.vertices.copy()
        # Permutação: [X, Y, Z] → [X, Z, Y]
        vertices_converted[:, [1, 2]] = vertices_converted[:, [2, 1]]
        
        # ============================================================
        # ✅ ROTAÇÃO DE 180º NO EIXO Z (CORREÇÃO PARA "DE CABEÇA P/ BAIXO")
        # ============================================================
        print(f"\n🔄 APLICANDO ROTAÇÃO DE 180° NO EIXO Z")
        print(f"   (corrige orientação 'de cabeça para baixo')")
        
        # Matriz de rotação 180º no eixo Z
        rotation_angle = 180.0  # graus
        angle_rad = np.radians(rotation_angle)
        cos_a = np.cos(angle_rad)  # cos(180) = -1
        sin_a = np.sin(angle_rad)  # sin(180) = 0
        
        rotation_matrix = np.array([
            [cos_a, -sin_a, 0],
            [sin_a, cos_a, 0],
            [0, 0, 1]
        ])
        
        # Aplica rotação
        vertices_converted = vertices_converted @ rotation_matrix.T
        
        # ✅ INVERTE X e Y para corrigir orientação
        vertices_converted[:, 0] = -vertices_converted[:, 0]  # Inverte X
        vertices_converted[:, 1] = -vertices_converted[:, 1]  # Inverte Y
        vertices_converted[:, 2] = -vertices_converted[:, 2]  # Inverte Z
        
        self.mesh.vertices = vertices_converted
        
        # Mostra dimensões DEPOIS
        bounds_after = self.mesh.bounds
        dims_after = bounds_after[1] - bounds_after[0]
        print(f"   DEPOIS: X={dims_after[0]:.1f}, Y={dims_after[1]:.1f}, Z={dims_after[2]:.1f}")
        print(f"   ✅ Rotação de 180° aplicada no eixo Z\n")
        
        # ============================================================
        # ✅ CORREÇÃO: CENTRALIZAÇÃO E COLOCA BASE EM Y=0
        # ============================================================
        centroid = self.mesh.centroid
        bounds = self.mesh.bounds
        
        print(f"🔄 CENTRALIZANDO MESH:")
        print(f"   Centro atual: X={centroid[0]:.1f}, Y={centroid[1]:.1f}, Z={centroid[2]:.1f}")
        print(f"   Bounds: min={bounds[0]}, max={bounds[1]}")
        
        # ✅ CORREÇÃO AQUI: Centraliza X e Z, coloca BASE em Y=0
        # (subtrai o valor mínimo de Y para que a base fique em Y=0)
        min_y = bounds[0][1]  # Valor mínimo de Y (base da peça)
        
        self.mesh.vertices[:, 0] -= centroid[0]  # Centraliza X
        self.mesh.vertices[:, 2] -= centroid[2]  # Centraliza Z
        self.mesh.vertices[:, 1] -= min_y        # ✅ BASE em Y=0 (peça acima da grade)
        
        # Atualiza bounds após centralização
        bounds = self.mesh.bounds
        max_dimension = np.max(bounds[1] - bounds[0])
        scale_factor = 2.0 / max_dimension if max_dimension > 0 else 1.0
        
        print(f"   Bounds após centralização: min={bounds[0]}, max={bounds[1]}")
        print(f"   ✅ Peça centralizada e base em Y=0\n")
        
        # ============================================================
        # SIMPLIFICAÇÃO OBRIGATÓRIA PARA DESENHO TÉCNICO
        # ============================================================
        vertices = np.array(self.mesh.vertices, dtype=np.float32)
        faces = np.array(self.mesh.faces, dtype=np.uint32)
        
        if self.simplify:
            print(f"\n{'='*70}")
            print("⚙️ SIMPLIFICANDO MALHA PARA DESENHO TÉCNICO")
            print(f"{'='*70}")
            
            edges = self._simplify_mesh_for_drawing(vertices, faces)
            
            simplified_face_count = len(faces)
            simplified_edge_count = len(edges)
            
            reduction = 100 - (simplified_edge_count / original_edge_count * 100)
            
            print(f"\n✅ SIMPLIFICAÇÃO CONCLUÍDA:")
            print(f"   Faces mantidas: {simplified_face_count:,}")
            print(f"   Arestas: {original_edge_count:,} → {simplified_edge_count:,}")
            print(f"   Redução: {reduction:.1f}%")
            print(f"{'='*70}\n")
        else:
            print("\n⚠️ Simplificação DESABILITADA")
            edges = self._extract_all_edges(faces)
            simplified_face_count = len(faces)
            simplified_edge_count = len(edges)
        
        # Calcula normais
        normals = self._compute_vertex_normals(vertices, faces)
        
        # Prepara dados para OpenGL
        vertex_data = self._prepare_vertex_data(vertices, normals)
        face_indices = faces.flatten().astype(np.uint32)
        edge_indices = edges.flatten().astype(np.uint32) if len(edges) > 0 else np.array([], dtype=np.uint32)
        
        self.mesh_data = MeshData(
            vertices=vertices,
            normals=normals,
            faces=faces,
            edges=edges,
            bounds=(bounds[0], bounds[1]),
            center=self.mesh.centroid,
            scale=scale_factor,
            vertex_data=vertex_data,
            face_indices=face_indices,
            edge_indices=edge_indices,
            original_face_count=original_face_count,
            simplified_face_count=simplified_face_count,
            original_edge_count=original_edge_count,
            simplified_edge_count=simplified_edge_count
        )
        
        return self.mesh_data
    
    # ✅ MÉTODOS DE ROTAÇÃO DE EIXOS
    def _rotate_vertices_x(self, vertices: np.ndarray, angle_degrees: float) -> np.ndarray:
        """
        Rotaciona vértices no eixo X
        
        Args:
            vertices: array de vértices [N, 3]
            angle_degrees: ângulo em graus
        
        Returns:
            vértices rotacionados
        """
        angle_rad = np.radians(angle_degrees)
        
        # Matriz de rotação no eixo X
        cos_a = np.cos(angle_rad)
        sin_a = np.sin(angle_rad)
        
        # Cria matriz de rotação
        rotation_matrix = np.array([
            [1, 0, 0],
            [0, cos_a, -sin_a],
            [0, sin_a, cos_a]
        ])
        
        # Aplica rotação
        return vertices @ rotation_matrix.T  # Multiplicação matricial

    def _rotate_vertices_y(self, vertices: np.ndarray, angle_degrees: float) -> np.ndarray:
        """
        Rotaciona vértices no eixo Y
        
        Args:
            vertices: array de vértices [N, 3]
            angle_degrees: ângulo em graus
        
        Returns:
            vértices rotacionados
        """
        angle_rad = np.radians(angle_degrees)
        
        # Matriz de rotação no eixo Y
        cos_a = np.cos(angle_rad)
        sin_a = np.sin(angle_rad)
        
        # Cria matriz de rotação
        rotation_matrix = np.array([
            [cos_a, 0, sin_a],
            [0, 1, 0],
            [-sin_a, 0, cos_a]
        ])
        
        # Aplica rotação
        return vertices @ rotation_matrix.T  # Multiplicação matricial

    def _rotate_vertices_z(self, vertices: np.ndarray, angle_degrees: float) -> np.ndarray:
        """
        Rotaciona vértices no eixo Z
        
        Args:
            vertices: array de vértices [N, 3]
            angle_degrees: ângulo em graus
        
        Returns:
            vértices rotacionados
        """
        angle_rad = np.radians(angle_degrees)
        
        # Matriz de rotação no eixo Z
        cos_a = np.cos(angle_rad)
        sin_a = np.sin(angle_rad)
        
        # Cria matriz de rotação
        rotation_matrix = np.array([
            [cos_a, -sin_a, 0],
            [sin_a, cos_a, 0],
            [0, 0, 1]
        ])
        
        # Aplica rotação
        return vertices @ rotation_matrix.T  # Multiplicação matricial
    
    def _simplify_mesh_for_drawing(self, vertices: np.ndarray, faces: np.ndarray) -> np.ndarray:
        """
        Simplifica malha mantendo apenas arestas importantes.
        VETORIZADO para máxima performance.
        """
        print("   [1/3] Calculando normais (vetorizado)...")
        
        # VETORIZADO: Calcula TODAS as normais de uma vez
        v0 = vertices[faces[:, 0]]
        v1 = vertices[faces[:, 1]]
        v2 = vertices[faces[:, 2]]
        
        edge1 = v1 - v0
        edge2 = v2 - v0
        
        face_normals = np.cross(edge1, edge2)
        lengths = np.linalg.norm(face_normals, axis=1, keepdims=True)
        lengths[lengths == 0] = 1
        face_normals = face_normals / lengths
        
        print("   [2/3] Construindo mapa de adjacências...")
        edge_to_faces = self._build_edge_face_map(faces)
        
        print("   [3/3] Filtrando arestas por ângulo (otimizado)...")
        
        feature_angle_threshold = 20.0  # Graus
        threshold_rad = np.radians(feature_angle_threshold)
        
        important_edges = []
        
        for edge_key, face_indices in edge_to_faces.items():
            if len(face_indices) == 1:
                important_edges.append(edge_key)
            elif len(face_indices) == 2:
                n1 = face_normals[face_indices[0]]
                n2 = face_normals[face_indices[1]]
                
                dot = np.clip(np.dot(n1, n2), -1, 1)
                angle = np.arccos(dot)
                
                if angle > threshold_rad:
                    important_edges.append(edge_key)
        
        if not important_edges:
            important_edges = [k for k, v in edge_to_faces.items() if len(v) == 1]
        
        return np.array(important_edges, dtype=np.uint32) if important_edges else np.array([], dtype=np.uint32).reshape(0, 2)
    
    def _compute_face_normals(self, vertices: np.ndarray, faces: np.ndarray) -> np.ndarray:
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
    
    def _build_edge_face_map(self, faces: np.ndarray) -> Dict[Tuple[int, int], list]:
        """Constrói mapa de arestas para faces adjacentes"""
        edge_to_faces = {}
        
        for face_idx, face in enumerate(faces):
            for i in range(3):
                v1, v2 = face[i], face[(i + 1) % 3]
                edge_key = (min(v1, v2), max(v1, v2))
                
                if edge_key not in edge_to_faces:
                    edge_to_faces[edge_key] = []
                edge_to_faces[edge_key].append(face_idx)
        
        return edge_to_faces
    
    def _extract_all_edges(self, faces: np.ndarray) -> np.ndarray:
        """Extrai TODAS as arestas (modo legado)"""
        edges_set = set()
        
        for face in faces:
            for i in range(3):
                v1, v2 = face[i], face[(i + 1) % 3]
                edge = (min(v1, v2), max(v1, v2))
                edges_set.add(edge)
        
        return np.array(list(edges_set), dtype=np.uint32) if edges_set else np.array([], dtype=np.uint32).reshape(0, 2)
    
    def _compute_vertex_normals(self, vertices: np.ndarray, faces: np.ndarray) -> np.ndarray:
        """Calcula normais suavizadas por vértice"""
        normals = np.zeros_like(vertices)
        
        for face in faces:
            v0, v1, v2 = vertices[face[0]], vertices[face[1]], vertices[face[2]]
            
            edge1 = v1 - v0
            edge2 = v2 - v0
            face_normal = np.cross(edge1, edge2)
            
            length = np.linalg.norm(face_normal)
            if length > 0:
                face_normal /= length
            
            normals[face[0]] += face_normal
            normals[face[1]] += face_normal
            normals[face[2]] += face_normal
        
        lengths = np.linalg.norm(normals, axis=1, keepdims=True)
        lengths[lengths == 0] = 1
        normals /= lengths
        
        return normals.astype(np.float32)
    
    def _prepare_vertex_data(self, vertices: np.ndarray, normals: np.ndarray) -> np.ndarray:
        """Prepara dados interleaved para VBO"""
        vertex_data = np.zeros((len(vertices), 6), dtype=np.float32)
        vertex_data[:, 0:3] = vertices
        vertex_data[:, 3:6] = normals
        return vertex_data.flatten()
    
    def get_bounding_box(self) -> Dict[str, float]:
        """Retorna as dimensões do bounding box"""
        if self.mesh is None:
            return {}
        
        bounds = self.mesh.bounds
        dimensions = bounds[1] - bounds[0]
        
        return {
            'width': float(dimensions[0]),
            'height': float(dimensions[1]),
            'depth': float(dimensions[2]),
            'min': bounds[0].tolist(),
            'max': bounds[1].tolist()
        }
    
    def get_mesh_info(self) -> Dict[str, Any]:
        """Retorna informações sobre o mesh"""
        if self.mesh is None or self.mesh_data is None:
            return {}
        
        info = {
            'vertices': len(self.mesh.vertices),
            'faces': len(self.mesh.faces),
            'edges': len(self.mesh_data.edges),
            'is_watertight': self.mesh.is_watertight,
            'volume': float(self.mesh.volume) if self.mesh.is_watertight else None,
            'surface_area': float(self.mesh.area),
            'bounds': self.get_bounding_box()
        }
        
        if self.mesh_data.simplified_edge_count < self.mesh_data.original_edge_count:
            face_reduction = 100 - (self.mesh_data.simplified_face_count / self.mesh_data.original_face_count * 100)
            edge_reduction = 100 - (self.mesh_data.simplified_edge_count / self.mesh_data.original_edge_count * 100)
            
            info['simplification'] = {
                'original_faces': self.mesh_data.original_face_count,
                'simplified_faces': self.mesh_data.simplified_face_count,
                'original_edges': self.mesh_data.original_edge_count,
                'simplified_edges': self.mesh_data.simplified_edge_count,
                'face_reduction': f"{face_reduction:.1f}%",
                'edge_reduction': f"{edge_reduction:.1f}%"
            }
        
        return info
