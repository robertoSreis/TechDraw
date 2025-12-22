"""
===============================================================================
STL2TechnicalDrawing - Janela Principal COM INTERFACE ACCORDION
===============================================================================
Pasta: gui/
Arquivo: gui/main_window.py
Descrição: Interface organizada com menu em árvore e barra de status inteligente
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
    QToolBox, QScrollArea
)
from PyQt6.QtCore import Qt, QSize, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QAction, QKeySequence

from gui.gl_widget import GLWidget
from core.stl_loader import STLLoader, MeshData
from utils.constants import WINDOW_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT, VIEWS


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
    """Janela principal da aplicação com interface accordion"""
    
    def __init__(self):
        super().__init__()
        
        self.stl_loader = STLLoader()
        self.mesh_data: Optional[MeshData] = None
        self.loader_worker: Optional[STLLoaderWorker] = None
        self.progress_dialog: Optional[QProgressDialog] = None
        
        # Timer para limpar mensagens temporárias da statusbar
        self.statusbar_timer = QTimer()
        self.statusbar_timer.timeout.connect(self._clear_temp_status)
        
        self.setWindowTitle(WINDOW_TITLE)
        self.setMinimumSize(1000, 700)
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setAcceptDrops(True)
        
        self._setup_ui()
        self._setup_menu()
        self._setup_toolbar()
        self._setup_statusbar()
        self._connect_signals()
        
        self.showMaximized()
    
    def _setup_ui(self):
        """Configura a interface com accordion"""
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
        self.gl_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        gl_layout.addWidget(self.gl_widget)
        
        splitter.addWidget(gl_container)
        
        # ========== Painel lateral com ACCORDION ==========
        side_panel = QWidget()
        side_panel.setMaximumWidth(300)
        side_panel.setMinimumWidth(250)
        side_layout = QVBoxLayout(side_panel)
        side_layout.setContentsMargins(2, 2, 2, 2)
        side_layout.setSpacing(5)
        
        # ==========================================
        # SEÇÃO FIXA 1: Vistas Predefinidas
        # ==========================================
        views_group = QGroupBox("⚙️ Vistas Predefinidas")
        views_layout = QVBoxLayout(views_group)
        views_layout.setSpacing(4)
        views_layout.setContentsMargins(5, 8, 5, 5)

        # Primeira linha
        views_grid1 = QHBoxLayout()
        views_grid1.setSpacing(3)
        for name, view_id, key in [("Frontal", "front", "1"), ("Traseira", "back", "2"), ("Superior", "top", "3")]:
            btn = QPushButton(f"{name} ({key})")
            btn.setFixedHeight(40)
            btn.setMinimumWidth(75)
            btn.clicked.connect(lambda checked, v=view_id: self.gl_widget.set_view(v))
            views_grid1.addWidget(btn)
        views_layout.addLayout(views_grid1)

        # Segunda linha
        views_grid2 = QHBoxLayout()
        views_grid2.setSpacing(3)
        for name, view_id, key in [("Inferior", "bottom", "4"), ("Esquerda", "left", "5"), ("Direita", "right", "6")]:
            btn = QPushButton(f"{name} ({key})")
            btn.setFixedHeight(40)
            btn.setMinimumWidth(75)
            btn.clicked.connect(lambda checked, v=view_id: self.gl_widget.set_view(v))
            views_grid2.addWidget(btn)
        views_layout.addLayout(views_grid2)

        # Isométrica e Reset
        btn_iso = QPushButton("🔲 Vista Isométrica (7)")
        btn_iso.setFixedHeight(32)
        btn_iso.clicked.connect(lambda: self.gl_widget.set_view('isometric'))
        views_layout.addWidget(btn_iso)
        
        btn_reset = QPushButton("🔄 Resetar Vista (R)")
        btn_reset.setFixedHeight(32)
        btn_reset.clicked.connect(self.gl_widget.reset_view)
        views_layout.addWidget(btn_reset)
        
        side_layout.addWidget(views_group)
        
        # ==========================================
        # SEÇÃO FIXA 2: Ações Principais
        # ==========================================
        actions_group = QGroupBox("🎯 Ações")
        actions_layout = QVBoxLayout(actions_group)
        actions_layout.setSpacing(10)
        actions_layout.setContentsMargins(5, 8, 5, 5)
        
        self.btn_generate = QPushButton("📐 Gerar Desenho")
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
        
        self.btn_export = QPushButton("💾 Exportar IMG")
        self.btn_export.setEnabled(False)
        self.btn_export.setFixedHeight(32)
        self.btn_export.clicked.connect(self._export_image)
        
        actions_layout.addWidget(self.btn_generate)
        actions_layout.addWidget(self.btn_export)
        
        side_layout.addWidget(actions_group)
        
        # ==========================================
        # ACCORDION / TOOLBOX para seções colapsáveis
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
        
        self.lbl_filename = QLabel("<b>Arquivo:</b><br>Nenhum")
        self.lbl_vertices = QLabel("<b>Vértices:</b> -")
        self.lbl_faces = QLabel("<b>Faces:</b> -")
        self.lbl_edges = QLabel("<b>Arestas:</b> -")
        self.lbl_dimensions = QLabel("<b>Dimensões:</b><br>-")
        self.lbl_volume = QLabel("<b>Volume:</b> -")
        self.lbl_simplification = QLabel("")
        
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
        self.toolbox.addItem(info_page, "📊 Info do Modelo")
        
        # --- PÁGINA 2: Opções de Exibição ---
        display_page = QWidget()
        display_layout = QVBoxLayout(display_page)
        display_layout.setContentsMargins(5, 5, 5, 5)
        display_layout.setSpacing(10)
        
        self.chk_faces = QCheckBox("Faces (F)")
        self.chk_faces.setChecked(True)
        self.chk_faces.toggled.connect(self.gl_widget.toggle_faces)
        
        self.chk_edges = QCheckBox("Arestas (E)")
        self.chk_edges.setChecked(True)
        self.chk_edges.toggled.connect(self.gl_widget.toggle_edges)
        
        self.chk_wireframe = QCheckBox("Wireframe (W)")
        self.chk_wireframe.toggled.connect(self.gl_widget.toggle_wireframe)
        
        self.chk_grid = QCheckBox("Grid (G)")
        self.chk_grid.setChecked(True)
        self.chk_grid.toggled.connect(self.gl_widget.toggle_grid)
        
        for chk in [self.chk_faces, self.chk_edges, self.chk_wireframe, self.chk_grid]:
            chk.setStyleSheet("padding: 3px; font-size: 9px;")
            display_layout.addWidget(chk)
        
        # Info sobre simplificação
        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setFrameShadow(QFrame.Shadow.Sunken)
        display_layout.addWidget(line2)
        
        info_simplify = QLabel(
            "<i style='color: #4CAF50; font-size: 8px;'>"
            "💡 Malhas simplificadas<br>"
            "automaticamente"
            "</i>"
        )
        info_simplify.setWordWrap(True)
        display_layout.addWidget(info_simplify)
        
        display_layout.addStretch()
        self.toolbox.addItem(display_page, "🎨 Exibição")
        
        side_layout.addWidget(self.toolbox)
        
        # ==========================================
        # SEÇÃO FIXA 3: Navegação (no final)
        # ==========================================
        help_group = QGroupBox("🖱️ Navegação")
        help_layout = QVBoxLayout(help_group)
        help_layout.setContentsMargins(5, 8, 5, 5)
        
        help_label = QLabel(
            "<b>Mouse:</b><br>"
            "• Esq: Rotacionar<br>"
            "• Meio: Pan<br>"
            "• Scroll: Zoom"
        )
        help_label.setStyleSheet("color: #aaa; font-size: 8px;")
        help_label.setWordWrap(True)
        help_layout.addWidget(help_label)
        
        side_layout.addWidget(help_group)
        
        splitter.addWidget(side_panel)
        splitter.setSizes([1000, 300])
        
        main_layout.addWidget(splitter)
    
    def _setup_menu(self):
        """Configura o menu principal"""
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("&Arquivo")
        
        open_action = QAction("&Abrir STL...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._open_file)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        export_action = QAction("&Exportar Imagem...", self)
        export_action.setShortcut(QKeySequence("Ctrl+E"))
        export_action.triggered.connect(self._export_image)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("&Sair", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        view_menu = menubar.addMenu("&Visualizar")
        
        for view_name, view_data in VIEWS.items():
            action = QAction(view_data['name'], self)
            action.triggered.connect(lambda checked, v=view_name: self.gl_widget.set_view(v))
            view_menu.addAction(action)
        
        view_menu.addSeparator()
        
        reset_action = QAction("&Resetar Vista", self)
        reset_action.setShortcut(QKeySequence("R"))
        reset_action.triggered.connect(self.gl_widget.reset_view)
        view_menu.addAction(reset_action)
        
        help_menu = menubar.addMenu("A&juda")
        
        about_action = QAction("&Sobre", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _setup_toolbar(self):
        """Configura a barra de ferramentas"""
        toolbar = QToolBar("Ferramentas")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        open_action = QAction("📁 Abrir", self)
        open_action.setStatusTip("Abrir arquivo STL")
        open_action.triggered.connect(self._open_file)
        toolbar.addAction(open_action)
        
        toolbar.addSeparator()

        clear_action = QAction("🗑️ Limpar", self)
        clear_action.setStatusTip("Limpar modelo carregado")
        clear_action.triggered.connect(self._clear_model)
        toolbar.addAction(clear_action)
    
    def _setup_statusbar(self):
        """Configura a barra de status inteligente"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        # Label permanente para info geral
        self.status_label_permanent = QLabel("Pronto")
        self.status_label_permanent.setStyleSheet("color: #aaa; padding: 2px 5px;")
        self.statusbar.addPermanentWidget(self.status_label_permanent)
        
        self._set_status("Pronto. Abra um arquivo STL para começar.", permanent=True)
    
    def _set_status(self, message: str, permanent: bool = False, timeout: int = 5000):
        """
        Define mensagem na statusbar
        
        Args:
            message: Mensagem a exibir
            permanent: Se True, fica permanente. Se False, temporária
            timeout: Tempo em ms para limpar (apenas se não permanent)
        """
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
    
    def _connect_signals(self):
        """Conecta sinais e slots"""
        self.gl_widget.viewChanged.connect(self._on_view_changed)
    
    def _on_view_changed(self, view_name: str):
        """Callback quando a vista muda"""
        if view_name in VIEWS:
            self._set_status(f"Vista alterada: {VIEWS[view_name]['name']}", timeout=3000)
    
    def _open_file(self):
        """Abre diálogo para selecionar arquivo STL"""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Abrir Arquivo STL",
            "",
            "Arquivos STL (*.stl);;Todos os arquivos (*)"
        )
        
        if filepath:
            self._load_stl(filepath)
    
    def _clear_model(self):
        """Limpa o modelo carregado"""
        if self.mesh_data is None:
            QMessageBox.information(self, "Informação", "Nenhum modelo carregado.")
            return
        
        self.mesh_data = None
        self.gl_widget.clear_mesh()
        
        self.lbl_filename.setText("<b>Arquivo:</b><br>Nenhum")
        self.lbl_vertices.setText("<b>Vértices:</b> -")
        self.lbl_faces.setText("<b>Faces:</b> -")
        self.lbl_edges.setText("<b>Arestas:</b> -")
        self.lbl_dimensions.setText("<b>Dimensões:</b><br>-")
        self.lbl_volume.setText("<b>Volume:</b> -")
        self.lbl_simplification.setText("")
        
        self.btn_generate.setEnabled(False)
        self.btn_export.setEnabled(False)
        
        self.gl_widget.reset_view()
        
        self._set_status("Modelo removido", permanent=True)
    
    def _load_stl(self, filepath: str):
        """Carrega um arquivo STL usando threading"""
        try:
            self.progress_dialog = QProgressDialog(
                "Carregando arquivo STL...",
                "Cancelar",
                0, 100,
                self
            )
            self.progress_dialog.setWindowTitle("Carregando")
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
            QMessageBox.critical(self, "Erro", f"Erro ao iniciar carregamento:\n{str(e)}")
            self._set_status("Erro ao carregar arquivo", permanent=True)
    
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
            
            filepath = self.loader_worker.filepath if self.loader_worker else "desconhecido"
            filename = os.path.basename(filepath)
            
            self.lbl_filename.setText(f"<b>Arquivo:</b><br>{filename}")
            self.lbl_vertices.setText(f"<b>Vértices:</b> {len(mesh_data.vertices):,}")
            self.lbl_faces.setText(f"<b>Faces:</b> {len(mesh_data.faces):,}")
            self.lbl_edges.setText(f"<b>Arestas:</b> {len(mesh_data.edges):,}")
            
            bounds = mesh_data.bounds
            width = bounds[1][0] - bounds[0][0]
            height = bounds[1][1] - bounds[0][1]
            depth = bounds[1][2] - bounds[0][2]
            
            self.lbl_dimensions.setText(
                f"<b>Dimensões:</b><br>"
                f"L: {width:.1f} mm<br>"
                f"A: {height:.1f} mm<br>"
                f"P: {depth:.1f} mm"
            )
            
            if hasattr(self.loader_worker.loader, 'mesh') and self.loader_worker.loader.mesh:
                mesh = self.loader_worker.loader.mesh
                if mesh.is_watertight:
                    self.lbl_volume.setText(f"<b>Vol:</b> {mesh.volume:.1f} mm³")
                else:
                    self.lbl_volume.setText("<b>Vol:</b> N/A (aberto)")
            else:
                self.lbl_volume.setText("<b>Volume:</b> -")
            
            if mesh_data.simplified_edge_count < mesh_data.original_edge_count:
                reduction = 100 - (mesh_data.simplified_edge_count / mesh_data.original_edge_count * 100)
                self.lbl_simplification.setText(
                    f"<b style='color: #4CAF50;'>✓ Simplificado</b><br>"
                    f"<span style='font-size: 8px;'>"
                    f"F: {mesh_data.original_face_count:,} → {mesh_data.simplified_face_count:,}<br>"
                    f"A: {mesh_data.original_edge_count:,} → {mesh_data.simplified_edge_count:,}<br>"
                    f"<b>-{reduction:.1f}%</b>"
                    f"</span>"
                )
            else:
                self.lbl_simplification.setText(
                    "<i style='color: #888; font-size: 8px;'>Não simplificado</i>"
                )
            
            self.btn_generate.setEnabled(True)
            self.btn_export.setEnabled(True)
            
            if self.progress_dialog:
                self.progress_dialog.close()
            
            self._set_status(f"✓ Carregado: {filename} | {len(mesh_data.vertices):,} vértices | {len(mesh_data.edges):,} arestas", permanent=True)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Erro", f"Erro ao processar modelo:\n{str(e)}")
            if self.progress_dialog:
                self.progress_dialog.close()
    
    def _on_load_error(self, error_msg: str):
        """Callback quando ocorre erro"""
        if self.progress_dialog:
            self.progress_dialog.close()
        
        QMessageBox.critical(self, "Erro ao Carregar", f"Não foi possível carregar:\n\n{error_msg}")
        self._set_status("Erro ao carregar arquivo", permanent=True)
    
    def _on_load_canceled(self):
        """Callback quando o carregamento é cancelado"""
        if self.loader_worker and self.loader_worker.isRunning():
            self.loader_worker.terminate()
            self.loader_worker.wait()
        
        self._set_status("Carregamento cancelado", timeout=3000)
    
    def _generate_technical_drawing(self):
        """Gera o desenho técnico"""
        if self.mesh_data is None:
            QMessageBox.warning(self, "Aviso", "Nenhum modelo carregado.")
            return
        
        try:
            from gui.drawing_preview_window import DrawingPreviewWindow
            
            self._set_status("Gerando desenho técnico...", timeout=0)
            
            self.preview_window = DrawingPreviewWindow(self.mesh_data, self)
            self.preview_window.show()
            
            self._set_status("✓ Desenho técnico gerado", timeout=5000)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Erro", f"Erro ao gerar desenho técnico:\n{str(e)}")
            self._set_status("Erro na geração", permanent=True)
    
    def _export_image(self):
        """Exporta a vista atual"""
        if self.mesh_data is None:
            QMessageBox.warning(self, "Aviso", "Nenhum modelo carregado.")
            return
        
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar Imagem",
            "modelo_3d.png",
            "PNG (*.png);;JPEG (*.jpg)"
        )
        
        if filepath:
            try:
                image = self.gl_widget.grabFramebuffer()
                image.save(filepath)
                self._set_status(f"✓ Imagem exportada: {os.path.basename(filepath)}", timeout=5000)
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao exportar:\n{str(e)}")
    
    def _show_about(self):
        """Mostra diálogo sobre"""
        QMessageBox.about(
            self,
            "Sobre Technical Drawing",
            "<h3>STL to Technical Drawing</h3>"
            "<p>Gerador automático de desenhos técnicos.</p>"
            "<p><b>Versão:</b> 1.2.35</p>"
            "<p><b>Por:</b> Roberto Reis - SE3D | 2018</p>"
        )
    
    def dragEnterEvent(self, event):
        """Aceita arrastar arquivos STL"""
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith('.stl'):
                    event.acceptProposedAction()
                    return
    
    def dropEvent(self, event):
        """Carrega arquivo STL arrastado"""
        for url in event.mimeData().urls():
            filepath = url.toLocalFile()
            if filepath.lower().endswith('.stl'):
                self._load_stl(filepath)
                break
    
    def closeEvent(self, event):
        """Limpa threads ao fechar"""
        if self.loader_worker and self.loader_worker.isRunning():
            self.loader_worker.terminate()
            self.loader_worker.wait()
        event.accept()