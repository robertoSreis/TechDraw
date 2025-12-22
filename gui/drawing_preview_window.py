"""
===============================================================================
STL2TechnicalDrawing - Janela de Preview com Progresso Real
===============================================================================
Pasta: gui/
Arquivo: gui/drawing_preview_window.py
Descrição: Janela de preview com progresso sincronizado
===============================================================================
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, Optional
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QToolBar, QStatusBar, QFileDialog, QMessageBox,
    QGroupBox, QCheckBox, QPushButton, QLabel,
    QScrollArea, QFrame, QSizePolicy, QComboBox,
    QSpinBox
)
from PyQt6.QtCore import Qt, QSize, QThread, pyqtSignal
from PyQt6.QtGui import QAction

from gui.technical_drawing_widget import TechnicalDrawingWidget
from core.projection_engine import ProjectionEngine, ViewType, ProjectedView
from core.stl_loader import MeshData


class ProjectionWorker(QThread):
    """Worker thread para gerar projeções com progresso real"""
    
    # Sinais
    progress = pyqtSignal(int, str, str)  # (porcentagem, mensagem, etapa)
    finished = pyqtSignal(dict, dict)      # (views, real_dims)
    error = pyqtSignal(str)
    
    def __init__(self, mesh_data: MeshData):
        super().__init__()
        self.mesh_data = mesh_data
    
    def run(self):
        """Executa o processamento em background com progresso real"""
        try:
            self.progress.emit(5, "Preparando geometria...", "Inicializando motor de projeção")
            self.msleep(100)
            
            vertices = self.mesh_data.vertices.copy()
            
            self.progress.emit(10, "Criando motor de projeção...", "Carregando dados do modelo")
            projection_engine = ProjectionEngine(
                vertices=vertices,
                faces=self.mesh_data.faces,
                edges=self.mesh_data.edges
            )
            
            views = {}
            view_types = [
                ViewType.FRONT, ViewType.BACK, ViewType.TOP,
                ViewType.BOTTOM, ViewType.LEFT, ViewType.RIGHT,
                ViewType.ISOMETRIC
            ]
            
            total_views = len(view_types)
            
            for i, view_type in enumerate(view_types):
                # ADICIONE ESTE PRINT
                print(f"📊 Gerando vista {i+1}/{total_views}: {view_type.value}")
                
                view = projection_engine.project_view(view_type)
                views[view_type] = view
                progress_value = 15 + int((i / total_views) * 70)
                view_name = view_type.value.upper()
                
                self.progress.emit(
                    progress_value,
                    f"Gerando vista {i+1}/{total_views}...",
                    f"Processando vista {view_name}"
                )
                
                view = projection_engine.project_view(view_type)
                views[view_type] = view
                
                self.msleep(50)  # Pequena pausa para visualização
            
            self.progress.emit(85, "Calculando dimensões...", "Analisando bounding box")
            real_dims = projection_engine.get_bounding_dimensions()
            
            self.progress.emit(95, "Finalizando...", "Preparando visualização")
            self.msleep(100)
            
            self.progress.emit(100, "Concluído!", "")
            self.finished.emit(views, real_dims)
            
        except Exception as e:
            import traceback
            error_msg = f"{str(e)}\n\nDetalhes:\n{traceback.format_exc()}"
            self.error.emit(error_msg)


class DrawingPreviewWindow(QMainWindow):
    """Janela de preview e exportação do desenho técnico"""
    
    def __init__(self, mesh_data: MeshData, parent=None):
        super().__init__(parent)
        
        self.mesh_data = mesh_data
        self.views: Dict[ViewType, ProjectedView] = {}
        self.worker: Optional[ProjectionWorker] = None
        self.progress_dialog = None  # QProgressDialog criado quando necessário
        
        self.setWindowTitle("Desenho Técnico - Preview")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        
        self._setup_ui()
        self._setup_toolbar()
        self._setup_statusbar()
        
        self._generate_projections_with_progress()
    
    def _setup_ui(self):
        """Configura a interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(10)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("background-color: #e0e0e0;")
        
        self.drawing_widget = TechnicalDrawingWidget()
        self.drawing_widget.setMinimumSize(800, 600)
        scroll_area.setWidget(self.drawing_widget)
        
        main_layout.addWidget(scroll_area, stretch=3)
        
        control_panel = QWidget()
        control_panel.setMaximumWidth(280)
        control_panel.setMinimumWidth(220)
        control_layout = QVBoxLayout(control_panel)
        control_layout.setContentsMargins(5, 5, 5, 5)
        control_layout.setSpacing(10)
        
        info_group = QGroupBox("Informações do Modelo")
        info_layout = QVBoxLayout(info_group)
        
        self.lbl_dimensions = QLabel("Dimensões: -")
        self.lbl_dimensions.setWordWrap(True)
        info_layout.addWidget(self.lbl_dimensions)
        
        self.lbl_views = QLabel("Vistas: 6 ortográficas")
        info_layout.addWidget(self.lbl_views)
        
        control_layout.addWidget(info_group)
        
        display_group = QGroupBox("Opções de Exibição")
        display_layout = QVBoxLayout(display_group)
        
        self.chk_hidden_lines = QCheckBox("Mostrar Linhas Ocultas")
        self.chk_hidden_lines.setChecked(True)
        self.chk_hidden_lines.toggled.connect(self.drawing_widget.toggle_hidden_lines)
        display_layout.addWidget(self.chk_hidden_lines)
        
        self.chk_dimensions = QCheckBox("Mostrar Dimensões")
        self.chk_dimensions.setChecked(True)
        self.chk_dimensions.toggled.connect(self.drawing_widget.toggle_dimensions)
        display_layout.addWidget(self.chk_dimensions)
        
        self.chk_border = QCheckBox("Mostrar Borda")
        self.chk_border.setChecked(True)
        self.chk_border.toggled.connect(self.drawing_widget.toggle_border)
        display_layout.addWidget(self.chk_border)
        
        control_layout.addWidget(display_group)
        
        views_group = QGroupBox("Vistas a Exportar")
        views_layout = QVBoxLayout(views_group)
        
        self.chk_front = QCheckBox("Frontal")
        self.chk_front.setChecked(True)
        self.chk_top = QCheckBox("Superior")
        self.chk_top.setChecked(True)
        self.chk_right = QCheckBox("Direita")
        self.chk_right.setChecked(True)
        self.chk_left = QCheckBox("Esquerda")
        self.chk_left.setChecked(True)
        self.chk_bottom = QCheckBox("Inferior")
        self.chk_bottom.setChecked(False)
        self.chk_back = QCheckBox("Traseira")
        self.chk_back.setChecked(False)
        self.chk_iso = QCheckBox("Isométrica")
        self.chk_iso.setChecked(True)
        
        self.view_checkboxes = {
            ViewType.FRONT: self.chk_front,
            ViewType.TOP: self.chk_top,
            ViewType.RIGHT: self.chk_right,
            ViewType.LEFT: self.chk_left,
            ViewType.BOTTOM: self.chk_bottom,
            ViewType.BACK: self.chk_back,
            ViewType.ISOMETRIC: self.chk_iso
        }
        
        for chk in self.view_checkboxes.values():
            views_layout.addWidget(chk)
            chk.toggled.connect(self._on_view_toggle)
        
        info_label = QLabel("<i>Selecione quais vistas<br>incluir no desenho</i>")
        info_label.setStyleSheet("color: #888; font-size: 9px;")
        views_layout.addWidget(info_label)
        
        control_layout.addWidget(views_group)
        
        export_group = QGroupBox("Exportação")
        export_layout = QVBoxLayout(export_group)
        
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Formato:"))
        self.combo_format = QComboBox()
        self.combo_format.addItems(["PNG", "JPG"])
        format_layout.addWidget(self.combo_format)
        export_layout.addLayout(format_layout)
        
        res_layout = QHBoxLayout()
        res_layout.addWidget(QLabel("DPI:"))
        self.spin_dpi = QSpinBox()
        self.spin_dpi.setRange(72, 600)
        self.spin_dpi.setValue(300)
        self.spin_dpi.setSingleStep(50)
        res_layout.addWidget(self.spin_dpi)
        export_layout.addLayout(res_layout)
        
        self.btn_export = QPushButton("Exportar Desenho")
        self.btn_export.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.btn_export.clicked.connect(self._export_drawing)
        export_layout.addWidget(self.btn_export)
        
        control_layout.addWidget(export_group)
        control_layout.addStretch()
        
        btn_close = QPushButton("Fechar")
        btn_close.clicked.connect(self.close)
        control_layout.addWidget(btn_close)
        
        main_layout.addWidget(control_panel)
    
    def _setup_toolbar(self):
        """Configura a barra de ferramentas"""
        toolbar = QToolBar("Ferramentas")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        zoom_in = QAction("Zoom +", self)
        zoom_in.triggered.connect(self._zoom_in)
        toolbar.addAction(zoom_in)
        
        zoom_out = QAction("Zoom -", self)
        zoom_out.triggered.connect(self._zoom_out)
        toolbar.addAction(zoom_out)
        
        toolbar.addSeparator()
        
        refresh = QAction("Atualizar", self)
        refresh.triggered.connect(self._generate_projections_with_progress)
        toolbar.addAction(refresh)
        
        toolbar.addSeparator()
        
        export = QAction("Exportar", self)
        export.triggered.connect(self._export_drawing)
        toolbar.addAction(export)
    
    def _setup_statusbar(self):
        """Configura a barra de status"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Aguarde...")
    
    def _generate_projections_with_progress(self):
        """Gera as projeções com diálogo de progresso cancelável"""
        from PyQt6.QtWidgets import QProgressDialog
        from PyQt6.QtCore import Qt
        
        # Usa QProgressDialog padrão com botão cancelar
        self.progress_dialog = QProgressDialog(
            "Gerando projeções...",
            "Cancelar",
            0, 100,
            self
        )
        self.progress_dialog.setWindowTitle("Gerando Desenho Técnico")
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.setMinimumDuration(0)
        self.progress_dialog.setValue(0)
        self.progress_dialog.setAutoClose(False)
        self.progress_dialog.setAutoReset(False)
        
        # Conecta cancelamento
        self.progress_dialog.canceled.connect(self._on_projection_canceled)
        
        self.worker = ProjectionWorker(self.mesh_data)
        self.worker.progress.connect(self._on_projection_progress)
        self.worker.finished.connect(self._on_projections_finished)
        self.worker.error.connect(self._on_projection_error)
        
        self.worker.start()
        self.progress_dialog.exec()
    
    def _on_projection_progress(self, value: int, message: str, step: str):
        """Callback de progresso"""
        if self.progress_dialog:
            self.progress_dialog.setValue(value)
            if step:
                self.progress_dialog.setLabelText(f"{message}\n{step}")
            else:
                self.progress_dialog.setLabelText(message)
    
    def _on_projection_canceled(self):
        """Callback quando o usuário cancela a geração"""
        if self.worker and self.worker.isRunning():
            self.statusbar.showMessage("Cancelando geração...")
            
            # Termina a thread
            self.worker.terminate()
            self.worker.wait(2000)  # Aguarda até 2 segundos
            
            # Se ainda estiver rodando, força
            if self.worker.isRunning():
                self.worker.quit()
                self.worker.wait()
            
            self.statusbar.showMessage("Geração cancelada pelo usuário")
            
            # Fecha a janela de preview se não houver vistas
            if not self.views:
                QMessageBox.information(
                    self,
                    "Cancelado",
                    "Geração de desenho técnico cancelada.\n\n"
                    "A janela será fechada."
                )
                self.close()
        
        if self.progress_dialog:
            self.progress_dialog.close()
    
    def _on_projections_finished(self, views: Dict[ViewType, ProjectedView], real_dims: Dict[str, float]):
        """Callback quando as projeções terminam"""
        self.views = views
        
        self.lbl_dimensions.setText(
            f"Dimensões:\n"
            f"  Largura: {real_dims['width']:.2f} mm\n"
            f"  Altura: {real_dims['height']:.2f} mm\n"
            f"  Prof.: {real_dims['depth']:.2f} mm"
        )
        
        filtered_views = self._get_filtered_views()
        self.drawing_widget.set_views(filtered_views, real_dims)
        
        self.statusbar.showMessage(f"✓ Projeções geradas: {len(filtered_views)} vistas")
        
        if self.progress_dialog:
            self.progress_dialog.setValue(100)
            self.progress_dialog.close()
    
    def _on_projection_error(self, error_msg: str):
        """Callback quando ocorre erro"""
        if self.progress_dialog:
            self.progress_dialog.close()
        
        QMessageBox.critical(self, "Erro", f"Erro ao gerar projeções:\n{error_msg}")
        self.statusbar.showMessage("❌ Erro na geração")
        
        # Fecha a janela se não houver vistas
        if not self.views:
            self.close()
    
    def _get_filtered_views(self) -> Dict[ViewType, ProjectedView]:
        """Retorna apenas as vistas selecionadas"""
        filtered = {}
        for view_type, checkbox in self.view_checkboxes.items():
            if checkbox.isChecked() and view_type in self.views:
                filtered[view_type] = self.views[view_type]
        return filtered
    
    def _on_view_toggle(self):
        """Callback quando uma vista é habilitada/desabilitada"""
        if not self.views:
            return
        
        filtered_views = self._get_filtered_views()
        
        if hasattr(self.drawing_widget, 'real_dimensions'):
            self.drawing_widget.set_views(filtered_views, self.drawing_widget.real_dimensions)
    
    def _zoom_in(self):
        """Aumenta o zoom do desenho"""
        current_size = self.drawing_widget.size()
        new_size = current_size * 1.2
        self.drawing_widget.setMinimumSize(int(new_size.width()), int(new_size.height()))
        self.drawing_widget.resize(int(new_size.width()), int(new_size.height()))
    
    def _zoom_out(self):
        """Diminui o zoom do desenho"""
        current_size = self.drawing_widget.size()
        new_size = current_size * 0.8
        min_size = 400
        new_w = max(int(new_size.width()), min_size)
        new_h = max(int(new_size.height()), min_size)
        self.drawing_widget.setMinimumSize(new_w, new_h)
        self.drawing_widget.resize(new_w, new_h)
    
    def _export_drawing(self):
        """Exporta o desenho técnico para arquivo"""
        format_type = self.combo_format.currentText().lower()
        dpi = self.spin_dpi.value()
        
        width = int(297 * dpi / 25.4)
        height = int(210 * dpi / 25.4)
        
        filter_map = {
            'png': "PNG (*.png)",
            'jpg': "JPEG (*.jpg)"
        }
        
        default_name = f"desenho_tecnico.{format_type}"
        
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar Desenho Técnico",
            default_name,
            filter_map.get(format_type, "Todos (*.*)")
        )
        
        if not filepath:
            return
        
        try:
            self.statusbar.showMessage(f"Exportando para {filepath}...")
            
            self.drawing_widget.export_to_image(filepath, width, height)
            
            self.statusbar.showMessage(f"Exportado: {filepath}")
            
            QMessageBox.information(
                self,
                "Exportação Concluída",
                f"Desenho técnico exportado com sucesso!\n\n"
                f"Arquivo: {filepath}\n"
                f"Resolução: {width}x{height} pixels ({dpi} DPI)"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erro na Exportação",
                f"Erro ao exportar desenho:\n{str(e)}"
            )
    
    def closeEvent(self, event):
        """Intercepta fechamento para limpar threads"""
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        event.accept()