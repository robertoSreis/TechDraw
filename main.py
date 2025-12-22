#!/usr/bin/env python3
"""
===============================================================================
STL2TechnicalDrawing - Gerador Automático de Desenhos Técnicos
===============================================================================
Versão: 1.0.0
Autor: Roberto - SE3D

Descrição:
    Aplicação para visualização 3D de arquivos STL e geração automática
    de desenhos técnicos com projeções ortográficas e dimensionamento.

Funcionalidades:
    - Visualização 3D com navegação interativa (rotação, zoom, pan)
    - 7 vistas predefinidas (6 ortográficas + isométrica)
    - Geração automática de desenhos técnicos
    - Projeções ortográficas em layout terceiro diedro
    - Dimensionamento automático
    - Exportação para PNG/JPG em alta resolução

Uso:
    python main.py [arquivo.stl]

===============================================================================
"""

import sys
import os

# ============================================================================
# CONFIGURAÇÃO DE PATH
# ============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# ============================================================================
# IMPORTS
# ============================================================================
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QSurfaceFormat, QFont

from gui.main_window import MainWindow


def setup_opengl():
    """Configura OpenGL antes de criar a aplicação"""
    fmt = QSurfaceFormat()
    fmt.setDepthBufferSize(24)
    fmt.setStencilBufferSize(8)
    fmt.setSamples(4)  # Anti-aliasing
    fmt.setSwapBehavior(QSurfaceFormat.SwapBehavior.DoubleBuffer)
    fmt.setVersion(2, 1)
    fmt.setProfile(QSurfaceFormat.OpenGLContextProfile.CompatibilityProfile)
    QSurfaceFormat.setDefaultFormat(fmt)


def get_stylesheet() -> str:
    """Retorna o stylesheet da aplicação"""
    return """
        QMainWindow {
            background-color: #2b2b2b;
        }
        QWidget {
            background-color: #3c3c3c;
            color: #ffffff;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        QGroupBox {
            border: 1px solid #555;
            border-radius: 5px;
            margin-top: 12px;
            padding-top: 10px;
            font-weight: bold;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
            color: #aaa;
        }
        QPushButton {
            background-color: #0d6efd;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 12px;
            min-height: 20px;
        }
        QPushButton:hover {
            background-color: #0b5ed7;
        }
        QPushButton:pressed {
            background-color: #0a58ca;
        }
        QPushButton:disabled {
            background-color: #6c757d;
            color: #aaa;
        }
        QCheckBox {
            spacing: 8px;
            padding: 4px;
        }
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border-radius: 3px;
            border: 1px solid #555;
            background-color: #2b2b2b;
        }
        QCheckBox::indicator:checked {
            background-color: #0d6efd;
            border-color: #0d6efd;
        }
        QCheckBox::indicator:hover {
            border-color: #0d6efd;
        }
        QLabel {
            color: #e0e0e0;
        }
        QMenuBar {
            background-color: #2b2b2b;
            color: white;
            padding: 2px;
        }
        QMenuBar::item {
            padding: 5px 10px;
            border-radius: 3px;
        }
        QMenuBar::item:selected {
            background-color: #0d6efd;
        }
        QMenu {
            background-color: #3c3c3c;
            color: white;
            border: 1px solid #555;
            padding: 5px;
        }
        QMenu::item {
            padding: 8px 25px;
            border-radius: 3px;
        }
        QMenu::item:selected {
            background-color: #0d6efd;
        }
        QMenu::separator {
            height: 1px;
            background-color: #555;
            margin: 5px 10px;
        }
        QToolBar {
            background-color: #2b2b2b;
            border: none;
            spacing: 5px;
            padding: 5px;
        }
        QToolBar::separator {
            width: 1px;
            background-color: #555;
            margin: 5px;
        }
        QStatusBar {
            background-color: #2b2b2b;
            color: #aaa;
            border-top: 1px solid #555;
        }
        QSplitter::handle {
            background-color: #555;
            width: 2px;
        }
        QSplitter::handle:hover {
            background-color: #0d6efd;
        }
        QFrame {
            border: 1px solid #555;
            border-radius: 3px;
        }
        QScrollArea {
            border: none;
        }
        QScrollBar:vertical {
            background-color: #2b2b2b;
            width: 12px;
            border-radius: 6px;
        }
        QScrollBar::handle:vertical {
            background-color: #555;
            border-radius: 6px;
            min-height: 20px;
        }
        QScrollBar::handle:vertical:hover {
            background-color: #666;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        QScrollBar:horizontal {
            background-color: #2b2b2b;
            height: 12px;
            border-radius: 6px;
        }
        QScrollBar::handle:horizontal {
            background-color: #555;
            border-radius: 6px;
            min-width: 20px;
        }
        QScrollBar::handle:horizontal:hover {
            background-color: #666;
        }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
        }
        QComboBox {
            background-color: #2b2b2b;
            border: 1px solid #555;
            border-radius: 4px;
            padding: 5px 10px;
            min-width: 80px;
        }
        QComboBox:hover {
            border-color: #0d6efd;
        }
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        QComboBox QAbstractItemView {
            background-color: #3c3c3c;
            border: 1px solid #555;
            selection-background-color: #0d6efd;
        }
        QSpinBox, QDoubleSpinBox {
            background-color: #2b2b2b;
            border: 1px solid #555;
            border-radius: 4px;
            padding: 5px;
        }
        QSpinBox:hover, QDoubleSpinBox:hover {
            border-color: #0d6efd;
        }
        QToolTip {
            background-color: #3c3c3c;
            color: white;
            border: 1px solid #555;
            padding: 5px;
            border-radius: 3px;
        }
    """


def check_dependencies():
    """Verifica se todas as dependências estão instaladas"""
    missing = []
    
    try:
        import PyQt6
    except ImportError:
        missing.append("PyQt6")
    
    try:
        import OpenGL
    except ImportError:
        missing.append("PyOpenGL")
    
    try:
        import numpy
    except ImportError:
        missing.append("numpy")
    
    try:
        import stl
    except ImportError:
        missing.append("numpy-stl")
    
    try:
        import trimesh
    except ImportError:
        missing.append("trimesh")
    
    try:
        import scipy
    except ImportError:
        missing.append("scipy")
    
    if missing:
        print("=" * 60)
        print("ERRO: Dependências faltando!")
        print("=" * 60)
        print(f"\nInstale com: pip install {' '.join(missing)}")
        print("\nOu execute: pip install -r requirements.txt")
        print("=" * 60)
        return False
    
    return True


def main():
    """Função principal"""
    # Verifica dependências
    if not check_dependencies():
        sys.exit(1)
    
    # Configura OpenGL
    setup_opengl()
    
    # Cria aplicação
    app = QApplication(sys.argv)
    app.setApplicationName("SE3D -TechDraw")
    app.setOrganizationName("SE3D")
    app.setApplicationVersion("1.2.35")
    app.setStyle("Fusion")
    app.setStyleSheet(get_stylesheet())
    
    # Fonte padrão
    font = QFont("Segoe UI", 9)
    app.setFont(font)
    
    # Cria janela principal
    window = MainWindow()
    window.show()
    window.isMaximized()
    
    # Carrega arquivo se passado por argumento
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        if os.path.exists(filepath) and filepath.lower().endswith('.stl'):
            window._load_stl(filepath)
        else:
            QMessageBox.warning(
                window,
                "Aviso",
                f"Arquivo não encontrado ou formato inválido:\n{filepath}"
            )
    
    # Executa
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
