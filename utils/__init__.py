"""
===============================================================================
STL2TechnicalDrawing - Módulo Utils
===============================================================================
Pasta: utils/
Arquivo: utils/__init__.py
===============================================================================
"""

from .constants import (
    # Janela
    WINDOW_TITLE,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    
    # Cores OpenGL
    BACKGROUND_COLOR,
    GRID_COLOR,
    MODEL_COLOR,
    EDGE_COLOR,
    WIREFRAME_COLOR,
    HIGHLIGHT_COLOR,
    
    # Navegação
    ROTATION_SPEED,
    ZOOM_SPEED,
    PAN_SPEED,
    MIN_ZOOM,
    MAX_ZOOM,
    
    # Iluminação
    LIGHT_POSITION,
    LIGHT_AMBIENT,
    LIGHT_DIFFUSE,
    LIGHT_SPECULAR,
    
    # Material
    MATERIAL_AMBIENT,
    MATERIAL_DIFFUSE,
    MATERIAL_SPECULAR,
    MATERIAL_SHININESS,
    
    # Vistas
    VIEWS,
    
    # Dimensionamento
    DIMENSION_FONT_SIZE,
    DIMENSION_LINE_COLOR,
    DIMENSION_TEXT_COLOR,
    DIMENSION_ARROW_SIZE,
    
    # Exportação
    EXPORT_DPI,
    EXPORT_FORMATS,
    
    # Cores configuráveis
    DEFAULT_MODEL_COLOR,
    COLORBLIND_FRIENDLY_COLORS
)

from .config_manager import ConfigManager
from .language_manager import LanguageManager

__all__ = [
    # Constantes
    'WINDOW_TITLE',
    'WINDOW_WIDTH',
    'WINDOW_HEIGHT',
    'BACKGROUND_COLOR',
    'GRID_COLOR',
    'MODEL_COLOR',
    'EDGE_COLOR',
    'WIREFRAME_COLOR',
    'HIGHLIGHT_COLOR',
    'ROTATION_SPEED',
    'ZOOM_SPEED',
    'PAN_SPEED',
    'MIN_ZOOM',
    'MAX_ZOOM',
    'LIGHT_POSITION',
    'LIGHT_AMBIENT',
    'LIGHT_DIFFUSE',
    'LIGHT_SPECULAR',
    'MATERIAL_AMBIENT',
    'MATERIAL_DIFFUSE',
    'MATERIAL_SPECULAR',
    'MATERIAL_SHININESS',
    'VIEWS',
    'DIMENSION_FONT_SIZE',
    'DIMENSION_LINE_COLOR',
    'DIMENSION_TEXT_COLOR',
    'DIMENSION_ARROW_SIZE',
    'EXPORT_DPI',
    'EXPORT_FORMATS',
    'DEFAULT_MODEL_COLOR',
    'COLORBLIND_FRIENDLY_COLORS',
    
    # Classes
    'ConfigManager',
    'LanguageManager',
]