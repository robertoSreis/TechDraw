"""
===============================================================================
STL2TechnicalDrawing - Módulo CORE
===============================================================================
Pasta: core/
Arquivo: core/__init__.py
Descrição: Módulo principal com carregamento, análise e projeção de geometria
===============================================================================
"""

from .stl_loader import STLLoader, MeshData
from .projection_engine import (
    ProjectionEngine, ProjectedView, Edge2D, Circle2D, ViewType
)
from .feature_detector import (
    FeatureDetector, DetectedFeatures
)
from .dimension_system import (
    DimensionSystem, Dimension, DimensionType, DimensionStyle
)
from .geometry_analyzer import (
    GeometryAnalyzer, GeometricFeature, FeatureType, EdgeInfo, FaceInfo
)

__all__ = [
    # Loader
    'STLLoader', 'MeshData',
    # Projection
    'ProjectionEngine', 'ProjectedView', 'Edge2D', 'Circle2D', 'ViewType',
    # Features
    'FeatureDetector', 'DetectedFeatures',
    # Dimensions
    'DimensionSystem', 'Dimension', 'DimensionType', 'DimensionStyle',
    # Geometry
    'GeometryAnalyzer', 'GeometricFeature', 'FeatureType', 'EdgeInfo', 'FaceInfo'
]
