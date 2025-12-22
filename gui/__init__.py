"""
===============================================================================
STL2TechnicalDrawing - Módulo GUI
===============================================================================
Pasta: gui/
Arquivo: gui/__init__.py
Descrição: Interface gráfica PyQt6 - Widgets 3D, 2D e janelas
===============================================================================
"""

from .gl_widget import GLWidget
from .main_window import MainWindow
from .technical_drawing_widget import TechnicalDrawingWidget
from .drawing_preview_window import DrawingPreviewWindow

__all__ = [
    'GLWidget', 'MainWindow', 
    'TechnicalDrawingWidget', 'DrawingPreviewWindow'
]
