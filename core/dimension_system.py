"""
===============================================================================
STL2TechnicalDrawing - Sistema de Dimensionamento Avançado
===============================================================================
Pasta: core/
Arquivo: core/dimension_system.py
Descrição: Sistema inteligente de criação e posicionamento de cotas
===============================================================================
"""

import numpy as np
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum
import math

from core.projection_engine import ProjectedView, ViewType, Edge2D


class DimensionType(Enum):
    """Tipos de dimensões"""
    LINEAR_HORIZONTAL = "linear_h"
    LINEAR_VERTICAL = "linear_v"
    LINEAR_ALIGNED = "linear_aligned"
    DIAMETER = "diameter"
    RADIUS = "radius"
    ANGLE = "angle"
    ARC_LENGTH = "arc_length"


class DimensionPlacement(Enum):
    """Posicionamento da dimensão"""
    OUTSIDE = "outside"      # Fora da peça
    INSIDE = "inside"        # Dentro da peça
    LEADER = "leader"        # Com linha de chamada


@dataclass
class DimensionStyle:
    """Estilo visual da dimensão"""
    line_width: float = 0.5
    arrow_size: float = 3.0
    text_height: float = 3.5
    text_gap: float = 1.5
    extension_gap: float = 1.5
    extension_overshoot: float = 2.0
    decimal_places: int = 2
    unit: str = "mm"
    show_unit: bool = False


@dataclass
class Dimension:
    """Representa uma dimensão completa com posicionamento"""
    dim_type: DimensionType
    value: float
    
    # Pontos de definição (coordenadas do modelo)
    point1: Tuple[float, float]
    point2: Tuple[float, float]
    
    # Posicionamento calculado
    dim_line_start: Tuple[float, float] = (0, 0)
    dim_line_end: Tuple[float, float] = (0, 0)
    text_position: Tuple[float, float] = (0, 0)
    text_rotation: float = 0.0
    
    # Linhas de extensão
    ext_line1_start: Tuple[float, float] = (0, 0)
    ext_line1_end: Tuple[float, float] = (0, 0)
    ext_line2_start: Tuple[float, float] = (0, 0)
    ext_line2_end: Tuple[float, float] = (0, 0)
    
    # Metadados
    placement: DimensionPlacement = DimensionPlacement.OUTSIDE
    layer: int = 0  # Para evitar sobreposição
    style: DimensionStyle = field(default_factory=DimensionStyle)
    
    def formatted_value(self) -> str:
        """Retorna o valor formatado"""
        decimals = self.style.decimal_places
        
        if self.dim_type == DimensionType.DIAMETER:
            text = f"⌀{self.value:.{decimals}f}"
        elif self.dim_type == DimensionType.RADIUS:
            text = f"R{self.value:.{decimals}f}"
        elif self.dim_type == DimensionType.ANGLE:
            text = f"{self.value:.{decimals}f}°"
        else:
            text = f"{self.value:.{decimals}f}"
        
        if self.style.show_unit and self.dim_type not in [DimensionType.ANGLE]:
            text += f" {self.style.unit}"
        
        return text


class DimensionSystem:
    """
    Sistema inteligente de dimensionamento.
    Calcula posições ideais para evitar sobreposição e manter clareza.
    """
    
    def __init__(self, style: Optional[DimensionStyle] = None):
        self.style = style or DimensionStyle()
        self.dimensions: List[Dimension] = []
        self.occupied_regions: List[Tuple[float, float, float, float]] = []
    
    def clear(self):
        """Limpa todas as dimensões"""
        self.dimensions = []
        self.occupied_regions = []
    
    def create_horizontal_dimension(self, 
                                     x1: float, y1: float,
                                     x2: float, y2: float,
                                     value: float,
                                     offset: float = 10.0) -> Dimension:
        """
        Cria uma dimensão horizontal.
        
        Args:
            x1, y1: Primeiro ponto
            x2, y2: Segundo ponto
            value: Valor da dimensão
            offset: Distância da linha de cota aos pontos
        """
        # Garante que x1 < x2
        if x1 > x2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
        
        # Posição Y da linha de cota
        min_y = min(y1, y2)
        dim_y = min_y - offset
        
        # Verifica colisão e ajusta se necessário
        layer = self._find_free_layer(x1, dim_y - 5, x2, dim_y + 5, 'horizontal')
        dim_y = min_y - offset - (layer * 8)
        
        dim = Dimension(
            dim_type=DimensionType.LINEAR_HORIZONTAL,
            value=value,
            point1=(x1, y1),
            point2=(x2, y2),
            dim_line_start=(x1, dim_y),
            dim_line_end=(x2, dim_y),
            text_position=((x1 + x2) / 2, dim_y - self.style.text_gap),
            text_rotation=0,
            ext_line1_start=(x1, y1 - self.style.extension_gap),
            ext_line1_end=(x1, dim_y - self.style.extension_overshoot),
            ext_line2_start=(x2, y2 - self.style.extension_gap),
            ext_line2_end=(x2, dim_y - self.style.extension_overshoot),
            layer=layer,
            style=self.style
        )
        
        self.dimensions.append(dim)
        self._mark_region_occupied(x1, dim_y - 5, x2, dim_y + 5)
        
        return dim
    
    def create_vertical_dimension(self,
                                   x1: float, y1: float,
                                   x2: float, y2: float,
                                   value: float,
                                   offset: float = 10.0) -> Dimension:
        """
        Cria uma dimensão vertical.
        """
        # Garante que y1 < y2
        if y1 > y2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
        
        # Posição X da linha de cota
        max_x = max(x1, x2)
        dim_x = max_x + offset
        
        # Verifica colisão
        layer = self._find_free_layer(dim_x - 5, y1, dim_x + 5, y2, 'vertical')
        dim_x = max_x + offset + (layer * 8)
        
        dim = Dimension(
            dim_type=DimensionType.LINEAR_VERTICAL,
            value=value,
            point1=(x1, y1),
            point2=(x2, y2),
            dim_line_start=(dim_x, y1),
            dim_line_end=(dim_x, y2),
            text_position=(dim_x + self.style.text_gap, (y1 + y2) / 2),
            text_rotation=-90,
            ext_line1_start=(x1 + self.style.extension_gap, y1),
            ext_line1_end=(dim_x + self.style.extension_overshoot, y1),
            ext_line2_start=(x2 + self.style.extension_gap, y2),
            ext_line2_end=(dim_x + self.style.extension_overshoot, y2),
            layer=layer,
            style=self.style
        )
        
        self.dimensions.append(dim)
        self._mark_region_occupied(dim_x - 5, y1, dim_x + 5, y2)
        
        return dim
    
    def create_diameter_dimension(self,
                                   center_x: float, center_y: float,
                                   radius: float,
                                   angle: float = 45.0) -> Dimension:
        """
        Cria uma dimensão de diâmetro.
        
        Args:
            center_x, center_y: Centro do círculo
            radius: Raio do círculo
            angle: Ângulo da linha de cota (graus)
        """
        rad = math.radians(angle)
        
        # Pontos nas extremidades do diâmetro
        x1 = center_x - radius * math.cos(rad)
        y1 = center_y - radius * math.sin(rad)
        x2 = center_x + radius * math.cos(rad)
        y2 = center_y + radius * math.sin(rad)
        
        dim = Dimension(
            dim_type=DimensionType.DIAMETER,
            value=radius * 2,
            point1=(x1, y1),
            point2=(x2, y2),
            dim_line_start=(x1, y1),
            dim_line_end=(x2, y2),
            text_position=(center_x, center_y + radius + self.style.text_gap * 2),
            text_rotation=0,
            style=self.style
        )
        
        self.dimensions.append(dim)
        return dim
    
    def create_radius_dimension(self,
                                 center_x: float, center_y: float,
                                 radius: float,
                                 angle: float = 45.0) -> Dimension:
        """
        Cria uma dimensão de raio.
        """
        rad = math.radians(angle)
        
        x2 = center_x + radius * math.cos(rad)
        y2 = center_y + radius * math.sin(rad)
        
        dim = Dimension(
            dim_type=DimensionType.RADIUS,
            value=radius,
            point1=(center_x, center_y),
            point2=(x2, y2),
            dim_line_start=(center_x, center_y),
            dim_line_end=(x2, y2),
            text_position=(
                center_x + (radius * 0.7) * math.cos(rad),
                center_y + (radius * 0.7) * math.sin(rad) + self.style.text_gap
            ),
            text_rotation=0,
            style=self.style
        )
        
        self.dimensions.append(dim)
        return dim
    
    def create_angle_dimension(self,
                                vertex_x: float, vertex_y: float,
                                angle1: float, angle2: float,
                                radius: float = 15.0) -> Dimension:
        """
        Cria uma dimensão angular.
        
        Args:
            vertex_x, vertex_y: Vértice do ângulo
            angle1, angle2: Ângulos das linhas (graus)
            radius: Raio do arco de dimensão
        """
        # Calcula ângulo entre as linhas
        angle_diff = abs(angle2 - angle1)
        if angle_diff > 180:
            angle_diff = 360 - angle_diff
        
        mid_angle = (angle1 + angle2) / 2
        rad = math.radians(mid_angle)
        
        dim = Dimension(
            dim_type=DimensionType.ANGLE,
            value=angle_diff,
            point1=(vertex_x, vertex_y),
            point2=(vertex_x + radius * math.cos(rad), 
                   vertex_y + radius * math.sin(rad)),
            dim_line_start=(vertex_x, vertex_y),
            dim_line_end=(vertex_x + radius * math.cos(rad),
                         vertex_y + radius * math.sin(rad)),
            text_position=(
                vertex_x + (radius + self.style.text_gap) * math.cos(rad),
                vertex_y + (radius + self.style.text_gap) * math.sin(rad)
            ),
            text_rotation=0,
            style=self.style
        )
        
        self.dimensions.append(dim)
        return dim
    
    def _find_free_layer(self, x1: float, y1: float, 
                          x2: float, y2: float,
                          direction: str) -> int:
        """Encontra uma camada livre para evitar sobreposição"""
        layer = 0
        max_layers = 5
        
        while layer < max_layers:
            collision = False
            
            for region in self.occupied_regions:
                rx1, ry1, rx2, ry2 = region
                
                # Verifica interseção de retângulos
                if not (x2 < rx1 or x1 > rx2 or y2 < ry1 or y1 > ry2):
                    collision = True
                    break
            
            if not collision:
                return layer
            
            layer += 1
        
        return layer
    
    def _mark_region_occupied(self, x1: float, y1: float, 
                               x2: float, y2: float):
        """Marca uma região como ocupada"""
        self.occupied_regions.append((
            min(x1, x2), min(y1, y2),
            max(x1, x2), max(y1, y2)
        ))
    
    def auto_dimension_view(self, view: ProjectedView, 
                            real_dims: Dict[str, float]) -> List[Dimension]:
        """
        Cria dimensões automaticamente para uma vista.
        
        Args:
            view: Vista projetada
            real_dims: Dimensões reais do modelo
        """
        self.clear()
        
        if not view.edges:
            return []
        
        min_x, min_y, max_x, max_y = view.bounds
        view_width = max_x - min_x
        view_height = max_y - min_y
        
        if view_width <= 0 or view_height <= 0:
            return []
        
        # Determina dimensões baseado no tipo de vista
        if view.view_type == ViewType.FRONT:
            h_value = real_dims.get('width', view_width)
            v_value = real_dims.get('height', view_height)
        elif view.view_type == ViewType.BACK:
            h_value = real_dims.get('width', view_width)
            v_value = real_dims.get('height', view_height)
        elif view.view_type == ViewType.TOP:
            h_value = real_dims.get('width', view_width)
            v_value = real_dims.get('depth', view_height)
        elif view.view_type == ViewType.BOTTOM:
            h_value = real_dims.get('width', view_width)
            v_value = real_dims.get('depth', view_height)
        elif view.view_type in [ViewType.LEFT, ViewType.RIGHT]:
            h_value = real_dims.get('depth', view_width)
            v_value = real_dims.get('height', view_height)
        else:
            return []  # Isométrica não recebe dimensões automáticas
        
        # Offset proporcional ao tamanho da vista
        offset = max(view_width, view_height) * 0.08
        
        # Dimensão horizontal (abaixo)
        self.create_horizontal_dimension(
            min_x, min_y,
            max_x, min_y,
            h_value,
            offset
        )
        
        # Dimensão vertical (à direita)
        self.create_vertical_dimension(
            max_x, min_y,
            max_x, max_y,
            v_value,
            offset
        )
        
        return self.dimensions
    
    def get_all_dimensions(self) -> List[Dimension]:
        """Retorna todas as dimensões criadas"""
        return self.dimensions
