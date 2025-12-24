"""
===============================================================================
STL2TechnicalDrawing - Janela Principal CORRIGIDA V2
===============================================================================
Pasta: gui/
Arquivo: gui/main_window.py
Descrição: Interface com menu reorganizado, tooltips dinâmicos e cor funcional
===============================================================================
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Optional
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QToolBar, QStatusBar, QFileDialog, QMessageBox,
    QGroupBox, QCheckBox, QPushButton, QLabel,
    QSplitter, QFrame, QSizePolicy, QProgressDialog,
    QToolBox, QScrollArea, QComboBox, QColorDialog,QMenu 
)
from PyQt6.QtCore import Qt, QSize, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QAction, QKeySequence, QColor

from gui.gl_widget import GLWidget
from core.stl_loader import STLLoader, MeshData
from utils.constants import WINDOW_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT, VIEWS
from utils.config_manager import ConfigManager
from utils.language_manager import LanguageManager


class STLLoaderWorker(QThread):
    """Worker thread para carregar STL sem bloquear a UI"""
    
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    
    def __init__(self, filepath: str, simplify: bool = True):
        super().__init__()
        self.filepath = filepath
        self.simplify = simplify
        self.loader = STLLoader(simplify_for_drawing=simplify)
    
    def run(self):
        """Executa o carregamento em background"""
        try:
            self.progress.emit(10, "Carregando arquivo STL...")
            self.msleep(100)
            
            self.progress.emit(30, "Processando geometria...")
            mesh_data = self.loader.load(self.filepath)
            
            if self.simplify:
                self.progress.emit(60, "Simplificando malha...")
                self.msleep(200)
            
            self.progress.emit(90, "Preparando visualização...")
            self.msleep(100)
            
            self.progress.emit(100, "Concluído!")
            self.finished.emit(mesh_data)
            
        except Exception as e:
            import traceback
            error_msg = f"{str(e)}\n\nDetalhes:\n{traceback.format_exc()}"
            self.error.emit(error_msg)


class MainWindow(QMainWindow):
    """Janela principal com sistema de configuração e i18n"""
    
    def __init__(self):
        super().__init__()
        
        # Gerenciadores
        self.config = ConfigManager()
        self.lang = LanguageManager()
        
        # Carrega idioma salvo
        saved_lang = self.config.get_language()
        if not self.lang.load_language(saved_lang):
            self.lang.load_language("EN-US")  # Fallback
        
        # Estado
        self.stl_loader = STLLoader()
        self.mesh_data: Optional[MeshData] = None
        self.loader_worker: Optional[STLLoaderWorker] = None
        self.progress_dialog: Optional[QProgressDialog] = None
        
        # Timer para limpar mensagens temporárias da statusbar
        self.statusbar_timer = QTimer()
        self.statusbar_timer.timeout.connect(self._clear_temp_status)
        
        # Configuração da janela
        self.setWindowTitle(WINDOW_TITLE)
        self.setMinimumSize(1000, 700)
        
        # ✅ DragAndDrop
        self.setAcceptDrops(True)
        self.installEventFilter(self)
        
        

        self._setup_ui()
        self._setup_menu()
        self._setup_toolbar()
        self._setup_statusbar()
        self._connect_signals()
        self._apply_language()
        self._load_view_settings()

        # ✅ VERIFICA SE GLWIDGET TEM ATRIBUTO model_color
        if not hasattr(self.gl_widget, 'model_color'):
            from utils.constants import MODEL_COLOR
            self.gl_widget.model_color = MODEL_COLOR

        #teste de aplicação de cor para futura implementação de STL com erros
        #QTimer.singleShot(5000, lambda: self._apply_model_color((1.0, 0.0, 0.0, 1.0)))
        
    def _setup_ui(self):
        """Configura a interface com painel lateral simplificado"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # ========== Widget OpenGL (área principal) ==========
        gl_container = QFrame()
        gl_container.setFrameStyle(QFrame.Shape.StyledPanel)
        gl_layout = QVBoxLayout(gl_container)
        gl_layout.setContentsMargins(0, 0, 0, 0)
        
        self.gl_widget = GLWidget()
        self.gl_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)


        # ✅ HABILITA MENU DE CONTEXTO
        self.gl_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.gl_widget.customContextMenuRequested.connect(self._show_gl_context_menu)
        
        gl_layout.addWidget(self.gl_widget)

        self.gl_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        gl_layout.addWidget(self.gl_widget)
        
        splitter.addWidget(gl_container)

        from utils.constants import MODEL_COLOR
        self.gl_widget.model_color = MODEL_COLOR 
        # ========== Painel lateral SIMPLIFICADO ==========
        side_panel = QWidget()
        side_panel.setMaximumWidth(300)
        side_panel.setMinimumWidth(250)
        side_layout = QVBoxLayout(side_panel)
        side_layout.setContentsMargins(2, 2, 2, 2)
        side_layout.setSpacing(5)
        
        # ==========================================
        # SEÇÃO 1: Vistas Predefinidas
        # ==========================================
        views_group = QGroupBox()
        views_layout = QVBoxLayout(views_group)
        views_layout.setSpacing(4)
        views_layout.setContentsMargins(5, 8, 5, 5)

        # Primeira linha
        views_grid1 = QHBoxLayout()
        views_grid1.setSpacing(3)
        
        self.btn_front = QPushButton()
        self.btn_front.setFixedHeight(40)
        self.btn_front.setMinimumWidth(75)
        self.btn_front.clicked.connect(lambda: self.gl_widget.set_view('front'))
        
        self.btn_back = QPushButton()
        self.btn_back.setFixedHeight(40)
        self.btn_back.setMinimumWidth(75)
        self.btn_back.clicked.connect(lambda: self.gl_widget.set_view('back'))
        
        self.btn_top = QPushButton()
        self.btn_top.setFixedHeight(40)
        self.btn_top.setMinimumWidth(75)
        self.btn_top.clicked.connect(lambda: self.gl_widget.set_view('top'))
        
        views_grid1.addWidget(self.btn_front)
        views_grid1.addWidget(self.btn_back)
        views_grid1.addWidget(self.btn_top)
        views_layout.addLayout(views_grid1)

        # Segunda linha
        views_grid2 = QHBoxLayout()
        views_grid2.setSpacing(3)
        
        self.btn_bottom = QPushButton()
        self.btn_bottom.setFixedHeight(40)
        self.btn_bottom.setMinimumWidth(75)
        self.btn_bottom.clicked.connect(lambda: self.gl_widget.set_view('bottom'))
        
        self.btn_left = QPushButton()
        self.btn_left.setFixedHeight(40)
        self.btn_left.setMinimumWidth(75)
        self.btn_left.clicked.connect(lambda: self.gl_widget.set_view('left'))
        
        self.btn_right = QPushButton()
        self.btn_right.setFixedHeight(40)
        self.btn_right.setMinimumWidth(75)
        self.btn_right.clicked.connect(lambda: self.gl_widget.set_view('right'))
        
        views_grid2.addWidget(self.btn_bottom)
        views_grid2.addWidget(self.btn_left)
        views_grid2.addWidget(self.btn_right)
        views_layout.addLayout(views_grid2)

        # Isométrica e Reset
        self.btn_iso = QPushButton()
        self.btn_iso.setFixedHeight(32)
        self.btn_iso.clicked.connect(lambda: self.gl_widget.set_view('isometric'))
        views_layout.addWidget(self.btn_iso)
        
        self.btn_reset = QPushButton()
        self.btn_reset.setFixedHeight(32)
        self.btn_reset.clicked.connect(self.gl_widget.reset_view)
        views_layout.addWidget(self.btn_reset)
        
        side_layout.addWidget(views_group)
        
        # ==========================================
        # SEÇÃO 2: Ações Principais
        # ==========================================
        actions_group = QGroupBox()
        actions_layout = QVBoxLayout(actions_group)
        actions_layout.setSpacing(10)
        actions_layout.setContentsMargins(5, 8, 5, 5)
        
        self.btn_generate = QPushButton()
        self.btn_generate.setEnabled(False)
        self.btn_generate.setFixedHeight(40)
        self.btn_generate.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #555;
                color: #888;
            }
        """)
        self.btn_generate.clicked.connect(self._generate_technical_drawing)
        
        self.btn_export = QPushButton()
        self.btn_export.setEnabled(False)
        self.btn_export.setFixedHeight(32)
        self.btn_export.clicked.connect(self._export_image)
        
        actions_layout.addWidget(self.btn_generate)
        actions_layout.addWidget(self.btn_export)
        
        side_layout.addWidget(actions_group)
        
        # ==========================================
        # ACCORDION / TOOLBOX - APENAS INFO
        # ==========================================
        self.toolbox = QToolBox()
        self.toolbox.setStyleSheet("""
            QToolBox::tab {
                background-color: #3c3c3c;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 5px;
                font-weight: bold;
                color: #ffffff;
            }
            QToolBox::tab:selected {
                background-color: #0d6efd;
                color: white;
            }
            QToolBox::tab:hover {
                background-color: #4a4a4a;
            }
        """)
        
        # --- PÁGINA 1: Informações do Modelo ---
        info_page = QWidget()
        info_layout = QVBoxLayout(info_page)
        info_layout.setContentsMargins(5, 5, 5, 5)
        info_layout.setSpacing(10)
        
        self.lbl_filename = QLabel()
        self.lbl_vertices = QLabel()
        self.lbl_faces = QLabel()
        self.lbl_edges = QLabel()
        self.lbl_dimensions = QLabel()
        self.lbl_volume = QLabel()
        self.lbl_simplification = QLabel()
        
        for lbl in [self.lbl_filename, self.lbl_vertices, self.lbl_faces, 
                    self.lbl_edges, self.lbl_dimensions, self.lbl_volume]:
            lbl.setWordWrap(True)
            lbl.setStyleSheet("font-size: 12px; padding: 2px;")
            info_layout.addWidget(lbl)
        
        # Separador
        line1 = QFrame()
        line1.setFrameShape(QFrame.Shape.HLine)
        line1.setFrameShadow(QFrame.Shadow.Sunken)
        info_layout.addWidget(line1)
        
        self.lbl_simplification.setWordWrap(True)
        self.lbl_simplification.setStyleSheet("font-size: 10px; padding: 3px;")
        info_layout.addWidget(self.lbl_simplification)
        
        info_layout.addStretch()
        self.toolbox.addItem(info_page, "📊")
        
        side_layout.addWidget(self.toolbox)
        
        # ==========================================
        # SEÇÃO 3: Navegação (no final)
        # ==========================================
        help_group = QGroupBox()
        help_layout = QVBoxLayout(help_group)
        help_layout.setContentsMargins(5, 8, 5, 5)
        
        self.help_label = QLabel()
        self.help_label.setStyleSheet("color: #aaa; font-size: 8px;")
        self.help_label.setWordWrap(True)
        help_layout.addWidget(self.help_label)
        
        side_layout.addWidget(help_group)
        
        splitter.addWidget(side_panel)
        splitter.setSizes([1000, 300])
        
        main_layout.addWidget(splitter)

    def _setup_menu(self):
        """✅ MENU REORGANIZADO - Cor e Idioma no topo"""
        menubar = self.menuBar()
        
        # ========== Menu Arquivo ==========
        self.menu_file = menubar.addMenu("")
        
        self.action_open = QAction("", self)
        self.action_open.setShortcut(QKeySequence.StandardKey.Open)
        self.action_open.triggered.connect(self._open_file)
        self.menu_file.addAction(self.action_open)
        
        self.menu_file.addSeparator()
        
        self.action_export = QAction("", self)
        self.action_export.setShortcut(QKeySequence("Ctrl+E"))
        self.action_export.triggered.connect(self._export_image)
        self.menu_file.addAction(self.action_export)
        
        self.menu_file.addSeparator()
        
        self.action_exit = QAction("", self)
        self.action_exit.setShortcut(QKeySequence.StandardKey.Quit)
        self.action_exit.triggered.connect(self.close)
        self.menu_file.addAction(self.action_exit)
        
        # ========== Menu Visualizar ==========
        self.menu_view = menubar.addMenu("")
        
        for view_name in VIEWS.keys():
            action = QAction("", self)
            action.setData(view_name)
            action.triggered.connect(lambda checked, v=view_name: self.gl_widget.set_view(v))
            self.menu_view.addAction(action)
            setattr(self, f"action_view_{view_name}", action)
        
        self.menu_view.addSeparator()
        
        self.action_reset = QAction("", self)
        self.action_reset.setShortcut(QKeySequence("R"))
        self.action_reset.triggered.connect(self.gl_widget.reset_view)
        self.menu_view.addAction(self.action_reset)
        
        # ========== ✅ NOVO: Menu Configurações ==========
        self.menu_settings = menubar.addMenu("")
        
        # Submenu Idioma
        self.menu_language = self.menu_settings.addMenu("")
        self.language_actions = []
        
        for lang in self.lang.get_available_languages():
            action = QAction(lang['name'], self)
            action.setData(lang['code'])
            action.setCheckable(True)
            action.triggered.connect(lambda checked, code=lang['code']: self._change_language(code))
            self.menu_language.addAction(action)
            self.language_actions.append(action)
        
        self.menu_settings.addSeparator()
        
        # Cor do Modelo
        self.action_model_color = QAction("", self)
        self.action_model_color.triggered.connect(self._choose_model_color)
        self.menu_settings.addAction(self.action_model_color)
        
        self.action_reset_color = QAction("", self)
        self.action_reset_color.triggered.connect(self._reset_model_color)
        self.menu_settings.addAction(self.action_reset_color)
        
        # ========== Menu Ajuda ==========
        self.menu_help = menubar.addMenu("")
        
        self.action_about = QAction("", self)
        self.action_about.triggered.connect(self._show_about)
        self.menu_help.addAction(self.action_about)
    
    def _setup_toolbar(self):
        """✅ TOOLBAR COM TOOLTIPS DINÂMICOS"""
        toolbar = QToolBar("Ferramentas")
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # Botão Abrir
        self.tool_open = QAction("📂", self)
        self.tool_open.triggered.connect(self._open_file)
        toolbar.addAction(self.tool_open)
        
        # Botão Limpar
        self.tool_clear = QAction("🗑️", self)
        self.tool_clear.triggered.connect(self._clear_model)
        toolbar.addAction(self.tool_clear)
        
        toolbar.addSeparator()
        
        # Mirror X
        self.tool_mirror_x = QAction("↔️ X", self)
        self.tool_mirror_x.setCheckable(True)
        self.tool_mirror_x.toggled.connect(self._toggle_mirror_x)
        toolbar.addAction(self.tool_mirror_x)
        
        # Mirror Y
        self.tool_mirror_y = QAction("🔄 Y", self)
        self.tool_mirror_y.setCheckable(True)
        self.tool_mirror_y.toggled.connect(self._toggle_mirror_y)
        toolbar.addAction(self.tool_mirror_y)

        #Mirror Z
        self.tool_mirror_z = QAction("↕️ Z", self)
        self.tool_mirror_z.setCheckable(True)
        self.tool_mirror_z.toggled.connect(self._toggle_mirror_z)
        toolbar.addAction(self.tool_mirror_z)
        
        toolbar.addSeparator()
        
        # Arestas
        self.tool_edges = QAction("📏", self)
        self.tool_edges.setCheckable(True)
        self.tool_edges.setChecked(True)
        self.tool_edges.toggled.connect(self._toggle_edges)
        toolbar.addAction(self.tool_edges)
        
        # Faces
        self.tool_faces = QAction("🔲", self)
        self.tool_faces.setCheckable(True)
        self.tool_faces.setChecked(True)
        self.tool_faces.toggled.connect(self._toggle_faces)
        toolbar.addAction(self.tool_faces)
        
        # Grid
        self.tool_grid = QAction("⊞", self)
        self.tool_grid.setCheckable(True)
        self.tool_grid.setChecked(True)
        self.tool_grid.toggled.connect(self._toggle_grid)
        toolbar.addAction(self.tool_grid)
    
    def _setup_statusbar(self):
        """Configura a barra de status inteligente"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        # Label permanente para info geral
        self.status_label_permanent = QLabel()
        self.status_label_permanent.setStyleSheet("color: #aaa; padding: 2px 5px;")
        self.statusbar.addPermanentWidget(self.status_label_permanent)
        
        self._set_status(self.lang.get("statusbar.ready"), permanent=True)
    
    def eventFilter(self, obj, event):
        """Filtra eventos para garantir que drag/drop funcione"""
        from PyQt6.QtCore import QEvent
        
        if event.type() == QEvent.Type.DragEnter:
            print(f"📥 EventFilter: DragEnter em {obj}")
            self.dragEnterEvent(event)
            return True
            
        elif event.type() == QEvent.Type.Drop:
            print(f"📤 EventFilter: Drop em {obj}")
            self.dropEvent(event)
            return True
            
        return super().eventFilter(obj, event)

    def _connect_signals(self):
        """Conecta sinais e slots"""
        self.gl_widget.viewChanged.connect(self._on_view_changed)

    def _show_gl_context_menu(self, pos):
        """Mostra menu de contexto na área 3D"""
        menu = QMenu(self)
        
        # 1. ABRIR ARQUIVO
        action_open = menu.addAction(self.action_open.icon(), self.action_open.text())
        action_open.triggered.connect(self._open_file)
        
        # 2. LIMPAR
        action_clear = menu.addAction("🗑️ " + self.lang.get("toolbar.clear"))
        action_clear.triggered.connect(self._clear_model)
        action_clear.setEnabled(self.mesh_data is not None)
        
        menu.addSeparator()
        
        # 3. SUBMENU: VISTAS (reutiliza as ações do menu View)
        view_menu = menu.addMenu("👁️ " + self.lang.get("menu.view"))
        
        for view_name in VIEWS.keys():
            view_key = f"menu.view_{view_name}"
            translated_name = self.lang.get(view_key, self.lang.get(f"views.{view_name}"))
            
            action = view_menu.addAction(translated_name)
            action.triggered.connect(lambda checked, v=view_name: self.gl_widget.set_view(v))
        
        view_menu.addSeparator()
        action_reset_view = view_menu.addAction(self.action_reset.text())
        action_reset_view.triggered.connect(self.gl_widget.reset_view)
        
        menu.addSeparator()
        
        # 4. ESPELHAMENTO (reutiliza da toolbar)
        mirror_menu = menu.addMenu("🔄 " + self.lang.get("toolbar.mirror", "Espelhar"))
        
        action_mirror_x = mirror_menu.addAction(self.tool_mirror_x.text())
        action_mirror_x.setCheckable(True)
        action_mirror_x.setChecked(self.tool_mirror_x.isChecked())
        action_mirror_x.toggled.connect(self._toggle_mirror_x)
        
        action_mirror_y = mirror_menu.addAction(self.tool_mirror_y.text())
        action_mirror_y.setCheckable(True)
        action_mirror_y.setChecked(self.tool_mirror_y.isChecked())
        action_mirror_y.toggled.connect(self._toggle_mirror_y)
        
        action_mirror_z = mirror_menu.addAction(self.tool_mirror_z.text())
        action_mirror_z.setCheckable(True)
        action_mirror_z.setChecked(self.tool_mirror_z.isChecked())
        action_mirror_z.toggled.connect(self._toggle_mirror_z)
        
        menu.addSeparator()
        
        # 5. EXIBIÇÃO (Faces, Arestas, Grid)
        display_menu = menu.addMenu("⚙️ " + self.lang.get("sidebar.display", "Exibição"))
        
        action_faces = display_menu.addAction(self.tool_faces.text())
        action_faces.setCheckable(True)
        action_faces.setChecked(self.tool_faces.isChecked())
        action_faces.toggled.connect(self._toggle_faces)
        
        action_edges = display_menu.addAction(self.tool_edges.text())
        action_edges.setCheckable(True)
        action_edges.setChecked(self.tool_edges.isChecked())
        action_edges.toggled.connect(self._toggle_edges)
        
        action_grid = display_menu.addAction(self.tool_grid.text())
        action_grid.setCheckable(True)
        action_grid.setChecked(self.tool_grid.isChecked())
        action_grid.toggled.connect(self._toggle_grid)
        
        menu.addSeparator()
        
        # 6. EXPORTAR IMAGEM
        if self.mesh_data is not None:
            action_export = menu.addAction(self.action_export.icon(), self.action_export.text())
            action_export.triggered.connect(self._export_image)
        
        # 7. GERENCIAR COR DO MODELO (se tiver modelo carregado)
        if self.mesh_data is not None:
            color_menu = menu.addMenu("🎨 " + self.lang.get("menu.settings_model_color", "Cor"))
            
            action_change_color = color_menu.addAction(self.action_model_color.text())
            action_change_color.triggered.connect(self._choose_model_color)
            
            action_reset_color = color_menu.addAction(self.action_reset_color.text())
            action_reset_color.triggered.connect(self._reset_model_color)
        
        # Mostra o menu na posição do clique
        menu.exec(self.gl_widget.mapToGlobal(pos))
        
    def _apply_language(self):
        """✅ APLICA TRADUÇÕES COM TOOLTIPS DINÂMICOS"""
        # Título da janela
        self.setWindowTitle(WINDOW_TITLE)
        
        # ========== Menus ==========
        self.menu_file.setTitle(self.lang.get("menu.file"))
        self.action_open.setText(self.lang.get("menu.file_open"))
        self.action_export.setText(self.lang.get("menu.file_export"))
        self.action_exit.setText(self.lang.get("menu.file_exit"))
        
        self.menu_view.setTitle(self.lang.get("menu.view"))
        self.action_reset.setText(self.lang.get("menu.view_reset"))
        
        # Views no menu
        for view_name in VIEWS.keys():
            # ✅ CORREÇÃO: Usa a chave correta para tradução das vistas
            view_key = f"menu.view_{view_name}"
            translated_name = self.lang.get(view_key, self.lang.get(f"views.{view_name}"))
            
            action = getattr(self, f"action_view_{view_name}", None)
            if action:
                action.setText(translated_name)
        
        # ✅ NOVO: Menu Configurações
        self.menu_settings.setTitle(self.lang.get("menu.settings", "Settings"))
        self.menu_language.setTitle(self.lang.get("menu.settings_language", "Language"))
        self.action_model_color.setText(self.lang.get("menu.settings_model_color", "Model Color..."))
        self.action_reset_color.setText(self.lang.get("menu.settings_reset_color", "Reset Default Color"))
        
        # Marca idioma atual
        current_lang = self.lang.get_current_language()
        for action in self.language_actions:
            action.setChecked(action.data() == current_lang)
        
        self.menu_help.setTitle(self.lang.get("menu.help"))
        self.action_about.setText(self.lang.get("menu.help_about"))
        
        # ========== ✅ TOOLBAR TOOLTIPS DINÂMICOS ==========
        self.tool_open.setToolTip(self.lang.get("toolbar.open"))
        self.tool_open.setStatusTip(self.lang.get("toolbar.open"))
        
        self.tool_clear.setToolTip(self.lang.get("toolbar.clear"))
        self.tool_clear.setStatusTip(self.lang.get("toolbar.clear"))
        
        self.tool_mirror_x.setToolTip(self.lang.get("toolbar.mirror_x"))
        self.tool_mirror_x.setStatusTip(self.lang.get("toolbar.mirror_x"))
        
        self.tool_mirror_y.setToolTip(self.lang.get("toolbar.mirror_y"))
        self.tool_mirror_y.setStatusTip(self.lang.get("toolbar.mirror_y"))

        self.tool_mirror_z.setToolTip(self.lang.get("toolbar.mirror_z", "Mirror Z"))
        self.tool_mirror_z.setStatusTip(self.lang.get("toolbar.mirror_z", "Mirror Z"))
        
        self.tool_edges.setToolTip(self.lang.get("toolbar.edges"))
        self.tool_edges.setStatusTip(self.lang.get("toolbar.edges"))
        
        self.tool_faces.setToolTip(self.lang.get("toolbar.faces"))
        self.tool_faces.setStatusTip(self.lang.get("toolbar.faces"))
        
        self.tool_grid.setToolTip(self.lang.get("toolbar.grid"))
        self.tool_grid.setStatusTip(self.lang.get("toolbar.grid"))
        
        # ========== Sidebar - Vistas ==========
        views_title = self.lang.get("sidebar.views_title")
        self.toolbox.setItemText(0, views_title.split("️")[-1].strip())
        
        self.btn_front.setText(f"{self.lang.get('sidebar.front')} (1)")
        self.btn_back.setText(f"{self.lang.get('sidebar.back')} (2)")
        self.btn_top.setText(f"{self.lang.get('sidebar.top')} (3)")
        self.btn_bottom.setText(f"{self.lang.get('sidebar.bottom')} (4)")
        self.btn_left.setText(f"{self.lang.get('sidebar.left')} (5)")
        self.btn_right.setText(f"{self.lang.get('sidebar.right')} (6)")
        self.btn_iso.setText(f"{self.lang.get('sidebar.isometric')} (7)")
        self.btn_reset.setText(self.lang.get("sidebar.reset"))
        
        # ========== Sidebar - Ações ==========
        self.btn_generate.setText(self.lang.get("sidebar.generate_drawing"))
        self.btn_export.setText(self.lang.get("sidebar.export_image"))
        
        # ========== Sidebar - Info ==========
        self._update_model_info_labels()
        
        # ========== Sidebar - Navegação ==========
        help_text = (
            f"<b>{self.lang.get('sidebar.navigation_title').replace('🖱️ ', '')}:</b><br>"
            f"{self.lang.get('sidebar.mouse_left')}<br>"
            f"{self.lang.get('sidebar.mouse_middle')}<br>"
            f"{self.lang.get('sidebar.mouse_scroll')}"
        )
        self.help_label.setText(help_text)
        
        # ========== Statusbar ==========
        self._set_status(self.lang.get("statusbar.ready"), permanent=True)

    def _update_model_info_labels(self):
        """Atualiza labels de informação do modelo"""
        if self.mesh_data is None:
            self.lbl_filename.setText(f"<b>{self.lang.get('sidebar.file')}</b><br>{self.lang.get('dialogs.no_model')}")
            self.lbl_vertices.setText(f"<b>{self.lang.get('sidebar.vertices')}</b> -")
            self.lbl_faces.setText(f"<b>{self.lang.get('sidebar.faces')}</b> -")
            self.lbl_edges.setText(f"<b>{self.lang.get('sidebar.edges')}</b> -")
            self.lbl_dimensions.setText(f"<b>{self.lang.get('sidebar.dimensions')}</b><br>-")
            self.lbl_volume.setText(f"<b>{self.lang.get('sidebar.volume')}</b> -")
            self.lbl_simplification.setText("")
    
    def _change_language(self, lang_code: str):
        """✅ TROCA IDIOMA VIA MENU"""
        if self.lang.load_language(lang_code):
            self.config.set_language(lang_code)
            self._apply_language()
            
            # Atualiza checks no menu
            for action in self.language_actions:
                action.setChecked(action.data() == lang_code)
            
            # Atualiza info do modelo se houver um carregado
            if self.mesh_data:
                self._update_loaded_model_info()
    
    def _choose_model_color(self):
        """✅ ESCOLHE COR DO MODELO E APLICA"""
        current_color = self.config.get_model_color()
        qcolor = QColor.fromRgbF(*current_color)
        
        color = QColorDialog.getColor(qcolor, self, self.lang.get("sidebar.choose_color", "Escolher Cor"))
        
        if color.isValid():
            r, g, b, a = color.getRgbF()
            self.config.set_model_color(r, g, b, a)
            self._apply_model_color((r, g, b, a))
    
    def _reset_model_color(self):
        """✅ RESTAURA COR PADRÃO DO MODELO"""
        from utils.constants import DEFAULT_MODEL_COLOR
        self.config.set_model_color(*DEFAULT_MODEL_COLOR)
        self._apply_model_color(DEFAULT_MODEL_COLOR)
    
    def _apply_model_color(self, color: tuple):
        """✅ APLICA COR AO MODELO OPENGL"""
        print(f"🔧 MainWindow._apply_model_color() - Cor recebida: {color}")
        
        # ✅ VERIFICA SE GLWIDGET TEM O MÉTODO
        if hasattr(self.gl_widget, 'set_model_color'):
            print(f"✅ Chamando gl_widget.set_model_color({color})")
            self.gl_widget.set_model_color(color)
        else:
            print(f"❌ GLWidget não tem método set_model_color!")
            # Fallback: define diretamente
            self.gl_widget.model_color = color
            self.gl_widget.update()
        
        print(f"✅ Cor do modelo aplicada")
    
    def _toggle_mirror_x(self, checked: bool):
        """Toggle espelhamento no eixo X"""
        self.config.set_view_setting("mirror_x", checked)
        self.gl_widget.set_mirror_x(checked)
        print(f"Mirror X: {checked}")
    
    def _toggle_mirror_z(self, checked: bool):
        """Toggle espelhamento no eixo Y"""
        self.config.set_view_setting("mirror_y", checked)
        self.gl_widget.set_mirror_y(checked)
        print(f"Mirror Y: {checked}")
    
    def _toggle_mirror_y(self, checked: bool):
        """Toggle espelhamento no eixo Z"""
        self.config.set_view_setting("mirror_z", checked)
        self.gl_widget.set_mirror_z(checked)
        print(f"Mirror Z: {checked}")
    
    def _toggle_edges(self, checked: bool):
        """Toggle exibição de arestas"""
        self.config.set_view_setting("show_edges", checked)
        self.gl_widget.toggle_edges(checked)
    
    def _toggle_faces(self, checked: bool):
        """Toggle exibição de faces"""
        self.config.set_view_setting("show_faces", checked)
        self.gl_widget.toggle_faces(checked)
    
    def _toggle_grid(self, checked: bool):
        """Toggle exibição do grid"""
        self.config.set_view_setting("show_grid", checked)
        self.gl_widget.toggle_grid(checked)
    
    def _set_status(self, message: str, permanent: bool = False, timeout: int = 5000):
        """Define mensagem na statusbar"""
        if permanent:
            self.status_label_permanent.setText(message)
            self.statusbar.clearMessage()
        else:
            self.statusbar.showMessage(message)
            if timeout > 0:
                self.statusbar_timer.stop()
                self.statusbar_timer.start(timeout)
    
    def _clear_temp_status(self):
        """Limpa mensagem temporária da statusbar"""
        self.statusbar.clearMessage()
        self.statusbar_timer.stop()
    
    def _on_view_changed(self, view_name: str):
        """Callback quando a vista muda"""
        if view_name in VIEWS:
            view_text = self.lang.get(f"views.{view_name}", VIEWS[view_name]['name'])
            message = f"{self.lang.get('statusbar.view_changed')} {view_text}"
            self._set_status(message, timeout=3000)
    
    def _open_file(self):
        """Abre diálogo para selecionar arquivo STL"""
        initial_dir = self.config.get_last_directory()
        
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            self.lang.get("dialogs.open_stl"),
            initial_dir,
            f"{self.lang.get('dialogs.stl_files')};;{self.lang.get('dialogs.all_files')}"
        )
        
        if filepath:
            import os
            self.config.set_last_directory(os.path.dirname(filepath))
            self._load_stl(filepath)
    
    def _clear_model(self):
        """Limpa o modelo carregado"""
        if self.mesh_data is None:
            QMessageBox.information(
                self, 
                self.lang.get("dialogs.info"), 
                self.lang.get("dialogs.no_model")
            )
            return
        
        self.mesh_data = None
        self.gl_widget.clear_mesh()
        
        self._update_model_info_labels()
        
        self.btn_generate.setEnabled(False)
        self.btn_export.setEnabled(False)
        
        self.gl_widget.reset_view()
        
        self._set_status(self.lang.get("statusbar.model_removed"), permanent=True)
    
    def _load_stl(self, filepath: str):
        """Carrega um arquivo STL usando threading"""
        try:
            self.progress_dialog = QProgressDialog(
                self.lang.get("statusbar.loading"),
                self.lang.get("dialogs.cancel"),
                0, 100,
                self
            )
            self.progress_dialog.setWindowTitle(self.lang.get("dialogs.loading_title"))
            self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
            self.progress_dialog.setMinimumDuration(0)
            self.progress_dialog.setValue(0)
            
            self.loader_worker = STLLoaderWorker(filepath, simplify=True)
            
            self.loader_worker.progress.connect(self._on_load_progress)
            self.loader_worker.finished.connect(self._on_load_finished)
            self.loader_worker.error.connect(self._on_load_error)
            self.progress_dialog.canceled.connect(self._on_load_canceled)
            
            self.loader_worker.start()
            self.progress_dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                self.lang.get("dialogs.error"), 
                f"{self.lang.get('statusbar.error')}:\n{str(e)}"
            )
            self._set_status(self.lang.get("statusbar.error"), permanent=True)
    
    def _on_load_progress(self, value: int, message: str):
        """Callback de progresso"""
        if self.progress_dialog:
            self.progress_dialog.setValue(value)
            self.progress_dialog.setLabelText(message)
    
    def _on_load_finished(self, mesh_data: MeshData):
        """Callback quando o carregamento termina"""
        try:
            self.mesh_data = mesh_data
            self.gl_widget.set_mesh(self.mesh_data)
            
            self._update_loaded_model_info()
            
            self.btn_generate.setEnabled(True)
            self.btn_export.setEnabled(True)
            
            if self.progress_dialog:
                self.progress_dialog.close()
            
            filepath = self.loader_worker.filepath if self.loader_worker else "desconhecido"
            filename = os.path.basename(filepath)
            
            message = (
                f"{self.lang.get('statusbar.loaded')} {filename} | "
                f"{len(mesh_data.vertices):,} {self.lang.get('statusbar.vertices')} | "
                f"{len(mesh_data.edges):,} {self.lang.get('statusbar.edges')}"
            )
            self._set_status(message, permanent=True)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self, 
                self.lang.get("dialogs.error"), 
                f"{self.lang.get('statusbar.error')}:\n{str(e)}"
            )
            if self.progress_dialog:
                self.progress_dialog.close()
    
    def _update_loaded_model_info(self):
        """Atualiza informações do modelo carregado"""
        if not self.mesh_data:
            return
        
        filepath = self.loader_worker.filepath if self.loader_worker else "desconhecido"
        filename = os.path.basename(filepath)
        
        self.lbl_filename.setText(f"<b>{self.lang.get('sidebar.file')}</b><br>{filename}")
        self.lbl_vertices.setText(f"<b>{self.lang.get('sidebar.vertices')}</b> {len(self.mesh_data.vertices):,}")
        self.lbl_faces.setText(f"<b>{self.lang.get('sidebar.faces')}</b> {len(self.mesh_data.faces):,}")
        self.lbl_edges.setText(f"<b>{self.lang.get('sidebar.edges')}</b> {len(self.mesh_data.edges):,}")
        
        bounds = self.mesh_data.bounds
        width = bounds[1][0] - bounds[0][0]
        height = bounds[1][1] - bounds[0][1]
        depth = bounds[1][2] - bounds[0][2]
        
        w_label = self.lang.get('sidebar.width')
        h_label = self.lang.get('sidebar.height')
        d_label = self.lang.get('sidebar.depth')
        
        self.lbl_dimensions.setText(
            f"<b>{self.lang.get('sidebar.dimensions')}</b><br>"
            f"{w_label}: {width:.1f} mm<br>"
            f"{h_label}: {height:.1f} mm<br>"
            f"{d_label}: {depth:.1f} mm"
        )
        
        if hasattr(self.loader_worker.loader, 'mesh') and self.loader_worker.loader.mesh:
            mesh = self.loader_worker.loader.mesh
            if mesh.is_watertight:
                self.lbl_volume.setText(f"<b>{self.lang.get('sidebar.volume')}</b> {mesh.volume:.1f} mm³")
            else:
                self.lbl_volume.setText(f"<b>{self.lang.get('sidebar.volume')}</b> N/A")
        else:
            self.lbl_volume.setText(f"<b>{self.lang.get('sidebar.volume')}</b> -")
        
        if self.mesh_data.simplified_edge_count < self.mesh_data.original_edge_count:
            reduction = 100 - (self.mesh_data.simplified_edge_count / self.mesh_data.original_edge_count * 100)
            self.lbl_simplification.setText(
                f"<b style='color: #4CAF50;'>{self.lang.get('sidebar.simplified')}</b><br>"
                f"<span style='font-size: 8px;'>"
                f"F: {self.mesh_data.original_face_count:,} → {self.mesh_data.simplified_face_count:,}<br>"
                f"A: {self.mesh_data.original_edge_count:,} → {self.mesh_data.simplified_edge_count:,}<br>"
                f"<b>-{reduction:.1f}%</b>"
                f"</span>"
            )
        else:
            self.lbl_simplification.setText(
                f"<i style='color: #888; font-size: 8px;'>{self.lang.get('sidebar.not_simplified')}</i>"
            )
    
    def _on_load_error(self, error_msg: str):
        """Callback quando ocorre erro"""
        if self.progress_dialog:
            self.progress_dialog.close()
        
        QMessageBox.critical(
            self, 
            self.lang.get("dialogs.error"), 
            f"{self.lang.get('statusbar.error')}:\n\n{error_msg}"
        )
        self._set_status(self.lang.get("statusbar.error"), permanent=True)
    
    def _on_load_canceled(self):
        """Callback quando o carregamento é cancelado"""
        if self.loader_worker and self.loader_worker.isRunning():
            self.loader_worker.terminate()
            self.loader_worker.wait()
        
        self._set_status(self.lang.get("statusbar.model_removed"), timeout=3000)
    
    def _generate_technical_drawing(self):
        """Gera o desenho técnico"""
        if self.mesh_data is None:
            QMessageBox.warning(
                self, 
                self.lang.get("dialogs.warning"), 
                self.lang.get("dialogs.no_model")
            )
            return
        
        try:
            from gui.drawing_preview_window import DrawingPreviewWindow
            
            self._set_status(self.lang.get("statusbar.generating"), timeout=0)
            
            self.preview_window = DrawingPreviewWindow(self.mesh_data, self, self.lang)
            self.preview_window.show()
            
            self._set_status(self.lang.get("statusbar.drawing_generated"), timeout=5000)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self, 
                self.lang.get("dialogs.error"), 
                f"{self.lang.get('statusbar.error')}:\n{str(e)}"
            )
            self._set_status(self.lang.get("statusbar.error"), permanent=True)
    
    def _export_image(self):
        """Exporta a vista atual"""
        if self.mesh_data is None:
            QMessageBox.warning(
                self, 
                self.lang.get("dialogs.warning"), 
                self.lang.get("dialogs.no_model")
            )
            return
        
        initial_dir = self.config.get_last_directory()
        
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            self.lang.get("dialogs.export_image"),
            os.path.join(initial_dir, "modelo_3d.png"),
            "PNG (*.png);;JPEG (*.jpg)"
        )
        
        if filepath:
            try:
                self.config.set_last_directory(os.path.dirname(filepath))
                
                image = self.gl_widget.grabFramebuffer()
                image.save(filepath)
                
                message = f"{self.lang.get('statusbar.exported')} {os.path.basename(filepath)}"
                self._set_status(message, timeout=5000)
            except Exception as e:
                QMessageBox.critical(
                    self, 
                    self.lang.get("dialogs.error"), 
                    f"{self.lang.get('statusbar.error')}:\n{str(e)}"
                )
    
    def _show_about(self):
        """Mostra diálogo sobre com logo, informações e QRCode"""
        import os
        from pathlib import Path
        from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QDialog, QPushButton, QTextEdit, QApplication
        from PyQt6.QtCore import Qt, QTimer
        from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QClipboard
        
        class AboutDialog(QDialog):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setWindowTitle("Sobre o STL2TechnicalDrawing")
                self.setFixedSize(600, 800)
                self.setStyleSheet("""
                    QDialog {
                        background-color: #f5f5f5;
                    }
                    QLabel {
                        background-color: transparent;
                    }
                    QTextEdit {
                        background-color: transparent;
                        border: none;
                    }
                """)
                self.copy_button = None
                self.setup_ui()
                
            def setup_ui(self):
                layout = QVBoxLayout(self)
                layout.setSpacing(10)
                layout.setContentsMargins(20, 20, 20, 20)
                
                # ========== LOGO SE3D ==========
                logo_label = QLabel()
                logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                
                # BUSCA DIRETA PELA MARCA.PNG
                current_file = Path(__file__)  # main_window.py
                project_root = current_file.parent.parent  # Subindo 2 níveis: gui/ -> ../
                
                # Lista de possíveis locais
                search_paths = [
                    Path("marca.png"),  # Diretório atual
                    project_root / "marca.png",  # Raiz do projeto
                    Path.cwd() / "marca.png",  # Diretório de trabalho
                    Path.home() / "Desktop" / "marca.png",  # Desktop
                ]
                
                print("\n🔍 Buscando marca.png:")
                for path in search_paths:
                    print(f"  → {path} - {'✅ EXISTE' if path.exists() else '❌ NÃO'}")
                
                # Tenta carregar a marca
                marca_path = None
                for path in search_paths:
                    if path.exists():
                        marca_path = path
                        print(f"🎯 Usando marca encontrada em: {marca_path}")
                        break
                
                if marca_path:
                    try:
                        logo_pixmap = QPixmap(str(marca_path))
                        if not logo_pixmap.isNull():
                            print(f"✅ Marca carregada: {logo_pixmap.width()}x{logo_pixmap.height()}")
                            
                            # Redimensiona se for muito grande
                            orig_width = logo_pixmap.width()
                            orig_height = logo_pixmap.height()
                            new_width = orig_width // 3  # 1/3 da largura original
                            new_height = orig_height // 3  # 1/3 da altura original

                            logo_pixmap = logo_pixmap.scaled(
                                new_width, new_height,
                                Qt.AspectRatioMode.KeepAspectRatio,
                                Qt.TransformationMode.SmoothTransformation
                            )
                            print(f"📏 Redimensionada para: {logo_pixmap.width()}x{logo_pixmap.height()}")
                            
                            logo_label.setPixmap(logo_pixmap)
                            logo_label.setMinimumHeight(logo_pixmap.height() + 10)
                        else:
                            self._create_fallback_logo(logo_label)
                    except Exception as e:
                        print(f"❌ Erro ao carregar marca: {e}")
                        self._create_fallback_logo(logo_label)
                else:
                    print("⚠️  marca.png não encontrada em nenhum local!")
                    self._create_fallback_logo(logo_label)
                
                layout.addWidget(logo_label)
                
                # Resto do código permanece igual...
                # ========== INFORMAÇÕES DO PROJETO ==========
                info_text = QTextEdit()
                info_text.setReadOnly(True)
                info_text.setHtml(f"""
                <div style="text-align: center; font-family: Arial; line-height: 1.6; color: #333;">
                    <h2 style="color: #2c3e50; margin-top: 0;">STL2TechnicalDrawing</h2>
                    <p style="font-size: 14px;">
                        <b>Versão:</b> 2.0.0<br>
                        <b>Desenvolvido por:</b> Roberto Reis<br>
                        <b>Empresa:</b> SE3D<br><br>
                        
                        <b>Site:</b> <a href="https://www.se3d.com.br" 
                        style="color: #3498db; text-decoration: none;">
                            https://www.se3d.com.br
                        </a><br>
                        
                        <b>GitHub:</b> <a href="https://github.com/robertoSreis/TechDraw" 
                        style="color: #3498db; text-decoration: none;">
                            https://github.com/robertoSreis/TechDraw
                        </a><br><br>
                        
                        <hr style="border: none; border-top: 1px solid #ddd; margin: 15px 0;">
                        
                        <h3 style="color: #2c3e50;">Requisitos Mínimos do Sistema</h3>
                        <div style="text-align: left; display: inline-block;">
                        <p style="font-size: 13px;">
                            <b>Processador:</b><br>
                            • Mínimo: Dual Core 1.8 GHz<br>
                            • Recomendado: 2.3 GHz ou superior<br><br>
                            
                            <b>Placa de Vídeo:</b><br>
                            • Mínimo: Intel UHD Graphics 630 (128MB RAM)<br>
                            • Recomendado: 2GB VRAM dedicada<br><br>
                            
                            <b>Memória RAM:</b><br>
                            • Mínimo: 2GB<br>
                            • Recomendado: 4GB ou mais<br><br>
                            
                            <b>Armazenamento:</b> 500MB livres<br>
                            <b>Sistema Operacional:</b> Windows 10/11, Linux, macOS
                        </p>
                        </div>
                        
                        <hr style="border: none; border-top: 1px solid #ddd; margin: 15px 0;">
                        
                        <h3 style="color: #2c3e50;">Doações Bitcoin</h3>
                        <p style="font-family: monospace; font-size: 12px; background-color: #f8f9fa; 
                        padding: 10px; border-radius: 5px; border: 1px solid #dee2e6;">
                            bc1qe2guhvt3yhp6v9gngrwegzfvuqq6pnepmvemlz
                        </p>
                    </p>
                </div>
                """)
                
                info_text.setMaximumHeight(400)
                info_text.setStyleSheet("""
                    QTextEdit {
                        background-color: transparent;
                        border: none;
                    }
                """)
                layout.addWidget(info_text)
                
                # ========== QR CODE BITCOIN ==========
                qr_label = QLabel("QR Code Bitcoin")
                qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                qr_label.setMaximumHeight(180)
                
                try:
                    import qrcode
                    from io import BytesIO
                    
                    btc_address = "bc1qe2guhvt3yhp6v9gngrwegzfvuqq6pnepmvemlz"
                    
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=6,
                        border=2,
                    )
                    qr.add_data(f"bitcoin:{btc_address}")
                    qr.make(fit=True)
                    
                    img = qr.make_image(fill_color="black", back_color="white")
                    
                    buffer = BytesIO()
                    img.save(buffer, format="PNG")
                    buffer.seek(0)
                    
                    qr_pixmap = QPixmap()
                    qr_pixmap.loadFromData(buffer.read())
                    
                    qr_pixmap = qr_pixmap.scaled(
                        140, 140, 
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    
                    qr_label.setPixmap(qr_pixmap)
                    qr_label.setText("")
                    
                except ImportError:
                    qr_label.setText("(Instale 'qrcode[pil]' para exibir QR Code)")
                    qr_label.setStyleSheet("color: #888; font-style: italic;")
                
                layout.addWidget(qr_label)
                
                # ========== BOTÃO DE COPIAR ==========
                self.copy_button = QPushButton("📋 Copiar Endereço BTC")
                self.copy_button.setStyleSheet("""
                    QPushButton {
                        background-color: #27ae60;
                        color: white;
                        border: none;
                        padding: 10px 20px;
                        border-radius: 5px;
                        font-weight: bold;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: #219653;
                    }
                    QPushButton:pressed {
                        background-color: #1e874b;
                    }
                """)
                self.copy_button.clicked.connect(self.copy_btc_address)
                layout.addWidget(self.copy_button, alignment=Qt.AlignmentFlag.AlignCenter)
                
                # ========== BOTÃO FECHAR ==========
                close_btn = QPushButton("Fechar")
                close_btn.clicked.connect(self.accept)
                close_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #7f8c8d;
                        color: white;
                        border: none;
                        padding: 8px 25px;
                        border-radius: 4px;
                    }
                    QPushButton:hover {
                        background-color: #95a5a6;
                    }
                    QPushButton:pressed {
                        background-color: #6c7b7d;
                    }
                """)
                layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)
                
                # ========== RODAPÉ ==========
                footer = QLabel("© 2024 SE3D")
                footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
                footer.setStyleSheet("color: #7f8c8d; font-size: 12px; margin-top: 10px;")
                layout.addWidget(footer)
                
            def _create_fallback_logo(self, label):
                """Cria um texto simples SE3D como fallback"""
                pixmap = QPixmap(400, 80)
                pixmap.fill(QColor(240, 240, 240))
                painter = QPainter(pixmap)
                painter.setFont(QFont("Arial", 36, QFont.Weight.Bold))
                painter.setPen(QColor(0, 100, 200))
                painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "SE3D")
                painter.end()
                label.setPixmap(pixmap)
                
            def copy_btc_address(self):
                btc_address = "bc1qe2guhvt3yhp6v9gngrwegzfvuqq6pnepmvemlz"
                clipboard = QApplication.clipboard()
                clipboard.setText(btc_address)
                
                self.copy_button.setText("✅ Copiado!")
                self.copy_button.setStyleSheet("""
                    QPushButton {
                        background-color: #2ecc71;
                        color: white;
                        border: none;
                        padding: 10px 20px;
                        border-radius: 5px;
                        font-weight: bold;
                        font-size: 14px;
                    }
                """)
                
                QTimer.singleShot(2000, self.restore_copy_button)
                
            def restore_copy_button(self):
                if self.copy_button:
                    self.copy_button.setText("📋 Copiar Endereço BTC")
                    self.copy_button.setStyleSheet("""
                        QPushButton {
                            background-color: #27ae60;
                            color: white;
                            border: none;
                            padding: 10px 20px;
                            border-radius: 5px;
                            font-weight: bold;
                            font-size: 14px;
                        }
                        QPushButton:hover {
                            background-color: #219653;
                        }
                        QPushButton:pressed {
                            background-color: #1e874b;
                        }
                    """)
        
        dialog = AboutDialog(self)
        dialog.exec()
    
    def dragEnterEvent(self, event):
        print(f"🔵 dragEnterEvent chamado! URLs: {event.mimeData().hasUrls()}")
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                filepath = url.toLocalFile()
                print(f"   📂 Arquivo: {filepath}")
                if filepath.lower().endswith('.stl'):
                    print(f"   ✅ É STL! Aceitando...")
                    event.acceptProposedAction()
                    return
        print("   ❌ Nenhum arquivo STL encontrado")
        event.ignore()

    def dropEvent(self, event):
        print(f"🟢 dropEvent chamado!")
        for url in event.mimeData().urls():
            filepath = url.toLocalFile()
            print(f"   🎯 Soltando: {filepath}")
            if filepath.lower().endswith('.stl'):
                print(f"   ✅ Carregando STL...")
                self.config.set_last_directory(os.path.dirname(filepath))
                self._load_stl(filepath)
                break
        event.acceptProposedAction()
    def closeEvent(self, event):
        """Limpa threads ao fechar e salva configurações"""
        # Salva estado da janela
        self.config.set("window.maximized", self.isMaximized())
        if not self.isMaximized():
            self.config.set("window.width", self.width())
            self.config.set("window.height", self.height())
        
        # Limpa threads
        if self.loader_worker and self.loader_worker.isRunning():
            self.loader_worker.terminate()
            self.loader_worker.wait()
        
        event.accept()
    
    def _load_view_settings(self):
        """Carrega configurações de visualização"""
        settings = self.config.get_view_settings()
        
        self.tool_faces.setChecked(settings.get("show_faces", True))
        self.tool_edges.setChecked(settings.get("show_edges", True))
        self.tool_grid.setChecked(settings.get("show_grid", True))
        self.tool_mirror_x.setChecked(settings.get("mirror_x", False))
        self.tool_mirror_y.setChecked(settings.get("mirror_y", False))
        self.tool_mirror_z.setChecked(settings.get("mirror_z", False))
        
        # Aplica espelhamento no gl_widget
        self.gl_widget.set_mirror_x(settings.get("mirror_x", False))
        self.gl_widget.set_mirror_y(settings.get("mirror_y", False))
        self.gl_widget.set_mirror_z(settings.get("mirror_z", False))
        
        # ✅ Aplica cor do modelo do config
        color = self.config.get_model_color()
        self._apply_model_color(color)
