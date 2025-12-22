"""
===============================================================================
STL2TechnicalDrawing - Detector de Features Geométricas
===============================================================================
Pasta: core/
Arquivo: core/feature_detector.py
Descrição: Detecta círculos, arcos, dimensões e outras features geométricas
===============================================================================
"""

import numpy as np
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum
from scipy import optimize

from core.projection_engine import ProjectedView, Edge2D, Circle2D, ViewType


class DimensionType(Enum):
    """Tipos de dimensões"""
    LINEAR_HORIZONTAL = "linear_h"
    LINEAR_VERTICAL = "linear_v"
    LINEAR_ALIGNED = "linear_aligned"
    DIAMETER = "diameter"
    RADIUS = "radius"
    ANGLE = "angle"


@dataclass
class Dimension:
    """Representa uma dimensão/cota no desenho técnico"""
    dim_type: DimensionType
    value: float
    unit: str = "mm"
    start_point: Tuple[float, float] = (0, 0)
    end_point: Tuple[float, float] = (0, 0)
    text_position: Tuple[float, float] = (0, 0)
    extension_offset: float = 0.1  # Offset das linhas de extensão
    
    def formatted_value(self, decimals: int = 2) -> str:
        """Retorna valor formatado com unidade"""
        if self.dim_type == DimensionType.DIAMETER:
            return f"⌀{self.value:.{decimals}f}"
        elif self.dim_type == DimensionType.RADIUS:
            return f"R{self.value:.{decimals}f}"
        elif self.dim_type == DimensionType.ANGLE:
            return f"{self.value:.{decimals}f}°"
        else:
            return f"{self.value:.{decimals}f}"


@dataclass
class DetectedFeatures:
    """Contém todas as features detectadas em uma vista"""
    circles: List[Circle2D] = field(default_factory=list)
    dimensions: List[Dimension] = field(default_factory=list)
    bounding_box: Tuple[float, float, float, float] = (0, 0, 0, 0)


class FeatureDetector:
    """
    Detecta features geométricas em vistas projetadas.
    Identifica círculos, calcula dimensões principais.
    """
    
    def __init__(self, scale_factor: float = 1.0):
        """
        Inicializa o detector.
        
        Args:
            scale_factor: Fator de escala para converter para unidades reais
        """
        self.scale_factor = scale_factor
        self.tolerance = 0.01  # Tolerância para detecção de padrões
    
    def detect_features(self, view: ProjectedView, 
                        real_dimensions: Dict[str, float]) -> DetectedFeatures:
        """
        Detecta todas as features em uma vista projetada.
        
        Args:
            view: Vista projetada
            real_dimensions: Dimensões reais do modelo {'width', 'height', 'depth'}
            
        Returns:
            DetectedFeatures com círculos e dimensões encontradas
        """
        features = DetectedFeatures()
        
        # Detecta círculos
        features.circles = self._detect_circles(view.edges)
        
        # Calcula dimensões principais baseadas na vista
        features.dimensions = self._calculate_dimensions(view, real_dimensions)
        
        # Bounding box
        features.bounding_box = view.bounds
        
        return features
    
    def _detect_circles(self, edges: List[Edge2D]) -> List[Circle2D]:
        """
        Detecta círculos nas arestas projetadas.
        Procura por sequências de arestas que formam arcos.
        """
        circles = []
        
        # Agrupa arestas conectadas
        edge_chains = self._find_edge_chains(edges)
        
        for chain in edge_chains:
            if len(chain) >= 8:  # Mínimo de segmentos para um círculo
                circle = self._fit_circle_to_chain(chain)
                if circle is not None:
                    circles.append(circle)
        
        return circles
    
    def _find_edge_chains(self, edges: List[Edge2D]) -> List[List[Edge2D]]:
        """Encontra cadeias de arestas conectadas"""
        if not edges:
            return []
        
        chains = []
        used = set()
        
        for i, start_edge in enumerate(edges):
            if i in used:
                continue
            
            chain = [start_edge]
            used.add(i)
            current_end = start_edge.end
            
            # Tenta encontrar arestas conectadas
            found = True
            while found:
                found = False
                for j, edge in enumerate(edges):
                    if j in used:
                        continue
                    
                    # Verifica se conecta
                    dist_start = np.sqrt((edge.start[0] - current_end[0])**2 + 
                                         (edge.start[1] - current_end[1])**2)
                    dist_end = np.sqrt((edge.end[0] - current_end[0])**2 + 
                                       (edge.end[1] - current_end[1])**2)
                    
                    if dist_start < self.tolerance:
                        chain.append(edge)
                        current_end = edge.end
                        used.add(j)
                        found = True
                        break
                    elif dist_end < self.tolerance:
                        # Inverte a aresta
                        chain.append(Edge2D(edge.end, edge.start, edge.is_visible))
                        current_end = edge.start
                        used.add(j)
                        found = True
                        break
            
            if len(chain) >= 3:
                chains.append(chain)
        
        return chains
    
    def _fit_circle_to_chain(self, chain: List[Edge2D]) -> Optional[Circle2D]:
        """
        Tenta ajustar um círculo a uma cadeia de arestas.
        Usa least squares para encontrar o melhor círculo.
        """
        # Coleta todos os pontos
        points = []
        for edge in chain:
            points.append(edge.start)
        points.append(chain[-1].end)
        points = np.array(points)
        
        if len(points) < 8:
            return None
        
        # Estimativa inicial: centróide e raio médio
        center_estimate = points.mean(axis=0)
        radius_estimate = np.mean(np.sqrt(np.sum((points - center_estimate)**2, axis=1)))
        
        def residuals(params):
            cx, cy, r = params
            distances = np.sqrt((points[:, 0] - cx)**2 + (points[:, 1] - cy)**2)
            return distances - r
        
        try:
            result = optimize.least_squares(
                residuals, 
                [center_estimate[0], center_estimate[1], radius_estimate],
                bounds=([-np.inf, -np.inf, 0.001], [np.inf, np.inf, np.inf])
            )
            
            cx, cy, r = result.x
            
            # Verifica qualidade do ajuste
            residual_std = np.std(residuals(result.x))
            
            if residual_std < self.tolerance * radius_estimate:
                # Verifica se é círculo completo
                angles = np.arctan2(points[:, 1] - cy, points[:, 0] - cx)
                angle_range = np.ptp(angles)
                is_full = angle_range > 5.5  # ~315 graus
                
                return Circle2D(
                    center=(cx, cy),
                    radius=r,
                    is_visible=chain[0].is_visible,
                    is_full_circle=is_full
                )
        except:
            pass
        
        return None
    
    def _calculate_dimensions(self, view: ProjectedView, 
                              real_dims: Dict[str, float]) -> List[Dimension]:
        """
        Calcula as dimensões principais para uma vista.
        
        As dimensões dependem do tipo de vista:
        - FRONT: largura (X) e altura (Y)
        - TOP: largura (X) e profundidade (Z)
        - LEFT/RIGHT: profundidade (Z) e altura (Y)
        """
        dimensions = []
        
        if not view.edges:
            return dimensions
        
        min_x, min_y, max_x, max_y = view.bounds
        view_width = max_x - min_x
        view_height = max_y - min_y
        
        # Mapeia dimensões reais baseado no tipo de vista
        if view.view_type == ViewType.FRONT:
            h_dim = real_dims.get('width', view_width / self.scale_factor)
            v_dim = real_dims.get('height', view_height / self.scale_factor)
            h_label = "Largura"
            v_label = "Altura"
        elif view.view_type == ViewType.BACK:
            h_dim = real_dims.get('width', view_width / self.scale_factor)
            v_dim = real_dims.get('height', view_height / self.scale_factor)
            h_label = "Largura"
            v_label = "Altura"
        elif view.view_type == ViewType.TOP:
            h_dim = real_dims.get('width', view_width / self.scale_factor)
            v_dim = real_dims.get('depth', view_height / self.scale_factor)
            h_label = "Largura"
            v_label = "Profundidade"
        elif view.view_type == ViewType.BOTTOM:
            h_dim = real_dims.get('width', view_width / self.scale_factor)
            v_dim = real_dims.get('depth', view_height / self.scale_factor)
            h_label = "Largura"
            v_label = "Profundidade"
        elif view.view_type in [ViewType.LEFT, ViewType.RIGHT]:
            h_dim = real_dims.get('depth', view_width / self.scale_factor)
            v_dim = real_dims.get('height', view_height / self.scale_factor)
            h_label = "Profundidade"
            v_label = "Altura"
        else:
            # Isométrica ou outra
            return dimensions
        
        # Cria dimensão horizontal (abaixo da vista)
        offset = view_height * 0.15
        dim_h = Dimension(
            dim_type=DimensionType.LINEAR_HORIZONTAL,
            value=h_dim,
            start_point=(min_x, min_y - offset),
            end_point=(max_x, min_y - offset),
            text_position=((min_x + max_x) / 2, min_y - offset * 1.5),
            extension_offset=offset * 0.3
        )
        dimensions.append(dim_h)
        
        # Cria dimensão vertical (à direita da vista)
        offset = view_width * 0.15
        dim_v = Dimension(
            dim_type=DimensionType.LINEAR_VERTICAL,
            value=v_dim,
            start_point=(max_x + offset, min_y),
            end_point=(max_x + offset, max_y),
            text_position=(max_x + offset * 1.5, (min_y + max_y) / 2),
            extension_offset=offset * 0.3
        )
        dimensions.append(dim_v)
        
        return dimensions
    
    def add_diameter_dimension(self, circle: Circle2D, 
                               scale_factor: float = 1.0) -> Dimension:
        """Cria uma dimensão de diâmetro para um círculo"""
        diameter = circle.radius * 2 / scale_factor
        
        return Dimension(
            dim_type=DimensionType.DIAMETER,
            value=diameter,
            start_point=(circle.center[0] - circle.radius, circle.center[1]),
            end_point=(circle.center[0] + circle.radius, circle.center[1]),
            text_position=(circle.center[0], circle.center[1] + circle.radius * 1.3)
        )
    
    def add_radius_dimension(self, circle: Circle2D,
                             scale_factor: float = 1.0) -> Dimension:
        """Cria uma dimensão de raio para um arco"""
        radius = circle.radius / scale_factor
        
        return Dimension(
            dim_type=DimensionType.RADIUS,
            value=radius,
            start_point=circle.center,
            end_point=(circle.center[0] + circle.radius, circle.center[1]),
            text_position=(circle.center[0] + circle.radius * 0.7, 
                          circle.center[1] + circle.radius * 0.3)
        )
