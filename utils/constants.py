"""
===============================================================================
STL2TechnicalDrawing - Constantes e Configurações
===============================================================================
Arquivo: utils/constants.py
Descrição: Contém todas as constantes de configuração do projeto
===============================================================================
"""

# =============================================================================
# CONFIGURAÇÕES DA JANELA
# =============================================================================
WINDOW_TITLE = "STL2Technical - Gerador de Desenhos Técnicos"
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900

# =============================================================================
# CONFIGURAÇÕES DO OPENGL - CORES (RGBA)
# =============================================================================
BACKGROUND_COLOR = (0.15, 0.15, 0.18, 1.0)
GRID_COLOR = (0.3, 0.3, 0.3, 0.5)
MODEL_COLOR = (0.7, 0.75, 0.8, 1.0)
EDGE_COLOR = (0.1, 0.1, 0.1, 1.0)  # Arestas normais (escuro)
WIREFRAME_COLOR = (1.0, 0.5, 0.0, 1.0)  # Laranja para wireframe
HIGHLIGHT_COLOR = (1.0, 0.5, 0.0, 1.0)

# =============================================================================
# CONFIGURAÇÕES DE NAVEGAÇÃO
# =============================================================================
ROTATION_SPEED = 0.5
ZOOM_SPEED = 0.1
PAN_SPEED = 0.005
MIN_ZOOM = 0.1
MAX_ZOOM = 100.0

# =============================================================================
# CONFIGURAÇÕES DE ILUMINAÇÃO
# =============================================================================
LIGHT_POSITION = (5.0, 5.0, 10.0, 1.0)
LIGHT_AMBIENT = (0.3, 0.3, 0.3, 1.0)
LIGHT_DIFFUSE = (0.8, 0.8, 0.8, 1.0)
LIGHT_SPECULAR = (1.0, 1.0, 1.0, 1.0)

# =============================================================================
# CONFIGURAÇÕES DE MATERIAL
# =============================================================================
MATERIAL_AMBIENT = (0.2, 0.2, 0.2, 1.0)
MATERIAL_DIFFUSE = (0.7, 0.75, 0.8, 1.0)
MATERIAL_SPECULAR = (0.9, 0.9, 0.9, 1.0)
MATERIAL_SHININESS = 50.0

# =============================================================================
# VISTAS ORTOGRÁFICAS PREDEFINIDAS
# Sistema de coordenadas: X=largura, Y=altura(vertical), Z=profundidade
# =============================================================================
VIEWS = {
    'front': {'rotation': (0, 0, 0), 'name': 'Frontal'},
    'back': {'rotation': (0, 180, 0), 'name': 'Traseira'},
    'top': {'rotation': (90, 0, 0), 'name': 'Superior'},
    'bottom': {'rotation': (-90, 0, 0), 'name': 'Inferior'},
    'left': {'rotation': (0, 90, 0), 'name': 'Esquerda'},
    'right': {'rotation': (0, -90, 0), 'name': 'Direita'},
    'isometric': {'rotation': (25, -45, 0), 'name': 'Isométrica'},
}

# =============================================================================
# ESTILOS DE DIMENSIONAMENTO
# =============================================================================
DIMENSION_FONT_SIZE = 10
DIMENSION_LINE_COLOR = (0.0, 0.0, 0.0, 1.0)
DIMENSION_TEXT_COLOR = (0.0, 0.0, 0.0, 1.0)
DIMENSION_ARROW_SIZE = 3.0

# =============================================================================
# EXPORTAÇÃO
# =============================================================================
EXPORT_DPI = 300
EXPORT_FORMATS = ['PNG', 'JPG', 'PDF', 'SVG']
