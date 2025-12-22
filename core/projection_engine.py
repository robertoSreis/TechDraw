"""
===============================================================================
STL2TechnicalDrawing - Motor de Projeção ULTRA OTIMIZADO
===============================================================================
Pasta: core/
Arquivo: core/projection_engine.py
Descrição: Projeção vetorizada com NumPy - 100x+ mais rápido
===============================================================================
"""

import numpy as np
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum


class ViewType(Enum):
    """Tipos de vistas ortográficas"""
    FRONT = "front"
    BACK = "back"
    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"
    ISOMETRIC = "isometric"


@dataclass
class Edge2D:
    """Representa uma aresta projetada em 2D"""
    start: Tuple[float, float]
    end: Tuple[float, float]
    is_visible: bool = True
    is_silhouette: bool = False
    depth: float = 0.0
    
    def length(self) -> float:
        dx = self.end[0] - self.start[0]
        dy = self.end[1] - self.start[1]
        return np.sqrt(dx*dx + dy*dy)


@dataclass
class Circle2D:
    """Representa um círculo/arco detectado em 2D"""
    center: Tuple[float, float]
    radius: float
    is_visible: bool = True
    is_full_circle: bool = True
    start_angle: float = 0.0
    end_angle: float = 360.0


@dataclass 
class ProjectedView:
    """Contém todos os dados de uma vista projetada"""
    view_type: ViewType
    edges: List[Edge2D] = field(default_factory=list)
    circles: List[Circle2D] = field(default_factory=list)
    bounds: Tuple[float, float, float, float] = (0, 0, 0, 0)
    width: float = 0.0
    height: float = 0.0


class ProjectionEngine:
    """
    Motor de projeção ortográfica OTIMIZADO.
    Usa operações vetorizadas NumPy - até 100x mais rápido.
    """
    
    # Sistema: X=direita, Y=cima(altura), Z=frente
    # Sistema: X=direita, Y=cima(altura), Z=frente
    VIEW_TRANSFORMS = {
        ViewType.FRONT: {
            'rotation': np.eye(3),  # Identidade - sem rotação
            'project_axes': (0, 1),  # Projeta X, Y
            'depth_axis': 2,         # Z é profundidade
            'flip_h': False,
            'flip_v': False,
            'label': 'FRONTAL'
        },
        ViewType.BACK: {
            'rotation': np.array([[-1, 0, 0], [0, 1, 0], [0, 0, -1]]),
            'project_axes': (0, 1),
            'depth_axis': 2,
            'flip_h': False,
            'flip_v': False,
            'label': 'TRASEIRA'
        },
        ViewType.TOP: {
            'rotation': np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]]),
            'project_axes': (0, 1),  # ← CORRIGIDO! Era (0, 2)
            'depth_axis': 2,         # ← CORRIGIDO! Era 1
            'flip_h': False,
            'flip_v': True,
            'label': 'SUPERIOR'
        },
        ViewType.BOTTOM: {
            'rotation': np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]]),
            'project_axes': (0, 1),  # ← CORRIGIDO! Era (0, 2)
            'depth_axis': 2,         # ← CORRIGIDO! Era 1
            'flip_h': False,
            'flip_v': False,
            'label': 'INFERIOR'
        },
        ViewType.LEFT: {
            'rotation': np.array([[0, 0, 1], [0, 1, 0], [-1, 0, 0]]),
            'project_axes': (0, 1),  # ← CORRIGIDO! Era (2, 1)
            'depth_axis': 2,         # ← CORRIGIDO! Era 0
            'flip_h': False,
            'flip_v': False,
            'label': 'ESQUERDA'
        },
        ViewType.RIGHT: {
            'rotation': np.array([[0, 0, -1], [0, 1, 0], [1, 0, 0]]),
            'project_axes': (0, 1),  # ← CORRIGIDO! Era (2, 1)
            'depth_axis': 2,         # ← CORRIGIDO! Era 0
            'flip_h': False,
            'flip_v': False,
            'label': 'DIREITA'
        },
    }
    
    def __init__(self, vertices: np.ndarray, faces: np.ndarray, edges: np.ndarray):
        """
        Inicializa o motor de projeção.
        
        Args:
            vertices: Array de vértices (N, 3)
            faces: Array de faces (M, 3)
            edges: Array de arestas (E, 2) - JÁ SIMPLIFICADAS
        """
        self.vertices = vertices
        self.faces = faces
        self.edges = edges
        
        # Pré-calcula normais das faces (vetorizado)
        self.face_normals = self._compute_face_normals_vectorized()
        
        # Constrói mapa de arestas para faces (RÁPIDO)
        self.edge_to_faces = self._build_edge_face_map_fast()
        
        print(f"[ProjectionEngine] Inicializado com {len(edges)} arestas simplificadas")
    
    def _compute_face_normals_vectorized(self) -> np.ndarray:
        """Calcula normais de TODAS as faces de uma vez (vetorizado)"""
        v0 = self.vertices[self.faces[:, 0]]
        v1 = self.vertices[self.faces[:, 1]]
        v2 = self.vertices[self.faces[:, 2]]
        
        edge1 = v1 - v0
        edge2 = v2 - v0
        
        # Cross product vetorizado
        normals = np.cross(edge1, edge2)
        
        # Normaliza
        lengths = np.linalg.norm(normals, axis=1, keepdims=True)
        lengths[lengths == 0] = 1
        normals = normals / lengths
        
        return normals
    
    def _build_edge_face_map_fast(self) -> Dict[Tuple[int, int], List[int]]:
        """Constrói mapa aresta->faces de forma otimizada"""
        edge_map = {}
        
        # Para cada face, registra suas 3 arestas
        for face_idx in range(len(self.faces)):
            face = self.faces[face_idx]
            for i in range(3):
                v1, v2 = face[i], face[(i + 1) % 3]
                edge_key = (min(v1, v2), max(v1, v2))
                
                if edge_key not in edge_map:
                    edge_map[edge_key] = []
                edge_map[edge_key].append(face_idx)
        
        return edge_map
    
    def project_view(self, view_type: ViewType) -> ProjectedView:
        """
        Projeta o mesh em uma vista 2D (OTIMIZADO).
        """
        if view_type == ViewType.ISOMETRIC:
            return self._project_isometric()
        
        # ====== ADICIONE ESTES PRINTS DE DEBUG ======
        print(f"\n{'='*60}")
        print(f"🔍 GERANDO VISTA: {view_type.value.upper()}")
        print(f"{'='*60}")
        
        transform = self.VIEW_TRANSFORMS[view_type]
        rotation = transform['rotation']
        
        # DEBUG: Mostra a matriz de rotação
        print(f"Matriz de rotação:")
        print(rotation)
        print(f"Eixos de projeção: {transform['project_axes']}")
        print(f"Flip H: {transform['flip_h']}, Flip V: {transform['flip_v']}")
        
        # ============================================
        
        ax_u, ax_v = transform['project_axes']
        depth_axis = transform['depth_axis']
        flip_h = transform['flip_h']
        flip_v = transform['flip_v']
        
        # Rotação vetorizada
        rotated_vertices = self.vertices @ rotation.T
        rotated_normals = self.face_normals @ rotation.T
        
        # ====== ADICIONE ESTE DEBUG ======
        print(f"Vértices ANTES da rotação (primeiros 3):")
        print(self.vertices[:3])
        print(f"Vértices DEPOIS da rotação (primeiros 3):")
        print(rotated_vertices[:3])
        print(f"{'='*60}\n")
        
        
        # ============================================
        # OTIMIZAÇÃO 2: Visibilidade vetorizada
        # ============================================
        view_direction = np.array([0, 0, -1])
        # Dot product vetorizado para TODAS as faces de uma vez
        face_visibility = np.dot(rotated_normals, -view_direction) > 0
        
        # ============================================
        # OTIMIZAÇÃO 3: Projeção de arestas em batch
        # ============================================
        projected_edges = []
        
        if len(self.edges) == 0:
            return ProjectedView(view_type=view_type, edges=[], bounds=(0,0,0,0))
        
        # Pega todos os vértices das arestas de uma vez
        v1_indices = self.edges[:, 0]
        v2_indices = self.edges[:, 1]
        
        v1_3d = rotated_vertices[v1_indices]
        v2_3d = rotated_vertices[v2_indices]
        
        # Projeta todas as arestas de uma vez
        u1 = v1_3d[:, ax_u]
        v1 = v1_3d[:, ax_v]
        u2 = v2_3d[:, ax_u]
        v2 = v2_3d[:, ax_v]
        
        # Aplica flips se necessário
        if flip_h:
            u1, u2 = -u1, -u2
        if flip_v:
            v1, v2 = -v1, -v2
        
        # Profundidades
        depths = (v1_3d[:, depth_axis] + v2_3d[:, depth_axis]) / 2
        
        # Calcula comprimentos (vetorizado)
        lengths = np.sqrt((u2 - u1)**2 + (v2 - v1)**2)
        
        # Filtra arestas muito pequenas
        valid_mask = lengths > 0.001
        
        # ============================================
        # OTIMIZAÇÃO 4: Visibilidade em batch
        # ============================================
        for i in range(len(self.edges)):
            if not valid_mask[i]:
                continue
            
            edge_key = tuple(sorted(self.edges[i]))
            
            # Verifica visibilidade (agora usa cache)
            adjacent_faces = self.edge_to_faces.get(edge_key, [])
            
            is_visible = False
            is_silhouette = False
            
            if len(adjacent_faces) == 1:
                is_visible = face_visibility[adjacent_faces[0]]
                is_silhouette = True
            elif len(adjacent_faces) == 2:
                vis1 = face_visibility[adjacent_faces[0]]
                vis2 = face_visibility[adjacent_faces[1]]
                is_visible = vis1 or vis2
                is_silhouette = vis1 != vis2
            
            projected_edges.append(Edge2D(
                start=(u1[i], v1[i]),
                end=(u2[i], v2[i]),
                is_visible=is_visible,
                is_silhouette=is_silhouette,
                depth=depths[i]
            ))
        
        # Calcula bounds (vetorizado)
        if projected_edges:
            all_u = np.concatenate([u1[valid_mask], u2[valid_mask]])
            all_v = np.concatenate([v1[valid_mask], v2[valid_mask]])
            
            min_x, max_x = all_u.min(), all_u.max()
            min_y, max_y = all_v.min(), all_v.max()
            bounds = (min_x, min_y, max_x, max_y)
            width = max_x - min_x
            height = max_y - min_y
        else:
            bounds = (0, 0, 0, 0)
            width = height = 0
        
        return ProjectedView(
            view_type=view_type,
            edges=projected_edges,
            bounds=bounds,
            width=width,
            height=height
        )
    
    def _project_isometric(self) -> ProjectedView:
        """Projeta vista isométrica (otimizado)"""
        angle_x = np.radians(35.264)
        angle_y = np.radians(45)
        
        # Matrizes de rotação
        rx = np.array([
            [1, 0, 0],
            [0, np.cos(angle_x), -np.sin(angle_x)],
            [0, np.sin(angle_x), np.cos(angle_x)]
        ])
        
        ry = np.array([
            [np.cos(angle_y), 0, np.sin(angle_y)],
            [0, 1, 0],
            [-np.sin(angle_y), 0, np.cos(angle_y)]
        ])
        
        rotation = rx @ ry
        
        # Vetorizado
        rotated_vertices = self.vertices @ rotation.T
        rotated_normals = self.face_normals @ rotation.T
        
        view_direction = np.array([0, 0, -1])
        face_visibility = np.dot(rotated_normals, -view_direction) > 0
        
        projected_edges = []
        
        if len(self.edges) == 0:
            return ProjectedView(view_type=ViewType.ISOMETRIC, edges=[], bounds=(0,0,0,0))
        
        v1_indices = self.edges[:, 0]
        v2_indices = self.edges[:, 1]
        
        v1_3d = rotated_vertices[v1_indices]
        v2_3d = rotated_vertices[v2_indices]
        
        u1, v1 = v1_3d[:, 0], v1_3d[:, 1]
        u2, v2 = v2_3d[:, 0], v2_3d[:, 1]
        depths = (v1_3d[:, 2] + v2_3d[:, 2]) / 2
        
        lengths = np.sqrt((u2 - u1)**2 + (v2 - v1)**2)
        valid_mask = lengths > 0.001
        
        for i in range(len(self.edges)):
            if not valid_mask[i]:
                continue
            
            edge_key = tuple(sorted(self.edges[i]))
            adjacent_faces = self.edge_to_faces.get(edge_key, [])
            
            is_visible = False
            is_silhouette = False
            
            if len(adjacent_faces) == 1:
                is_visible = face_visibility[adjacent_faces[0]]
                is_silhouette = True
            elif len(adjacent_faces) == 2:
                vis1 = face_visibility[adjacent_faces[0]]
                vis2 = face_visibility[adjacent_faces[1]]
                is_visible = vis1 or vis2
                is_silhouette = vis1 != vis2
            
            projected_edges.append(Edge2D(
                start=(u1[i], v1[i]),
                end=(u2[i], v2[i]),
                is_visible=is_visible,
                is_silhouette=is_silhouette,
                depth=depths[i]
            ))
        
        if projected_edges:
            all_u = np.concatenate([u1[valid_mask], u2[valid_mask]])
            all_v = np.concatenate([v1[valid_mask], v2[valid_mask]])
            
            min_x, max_x = all_u.min(), all_u.max()
            min_y, max_y = all_v.min(), all_v.max()
            bounds = (min_x, min_y, max_x, max_y)
            width = max_x - min_x
            height = max_y - min_y
        else:
            bounds = (0, 0, 0, 0)
            width = height = 0
        
        return ProjectedView(
            view_type=ViewType.ISOMETRIC,
            edges=projected_edges,
            bounds=bounds,
            width=width,
            height=height
        )
    
    def project_all_views(self) -> Dict[ViewType, ProjectedView]:
        """Projeta todas as 6 vistas ortográficas principais"""
        views = {}
        for view_type in [ViewType.FRONT, ViewType.BACK, ViewType.TOP, 
                          ViewType.BOTTOM, ViewType.LEFT, ViewType.RIGHT]:
            views[view_type] = self.project_view(view_type)
        return views
    
    def get_bounding_dimensions(self) -> Dict[str, float]:
        """Retorna as dimensões do bounding box do modelo"""
        min_coords = self.vertices.min(axis=0)
        max_coords = self.vertices.max(axis=0)
        
        return {
            'width': float(max_coords[0] - min_coords[0]),
            'height': float(max_coords[1] - min_coords[1]),
            'depth': float(max_coords[2] - min_coords[2]),
            'min_x': float(min_coords[0]),
            'max_x': float(max_coords[0]),
            'min_y': float(min_coords[1]),
            'max_y': float(max_coords[1]),
            'min_z': float(min_coords[2]),
            'max_z': float(max_coords[2]),
        }