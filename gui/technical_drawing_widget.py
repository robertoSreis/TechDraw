"""
===============================================================================
STL2TechnicalDrawing - Widget de Desenho Técnico
===============================================================================
Pasta: gui/
Arquivo: gui/technical_drawing_widget.py
Descrição: Widget para renderizar desenho técnico 2D com vistas e dimensões
===============================================================================
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import math
from typing import Dict, Optional, Tuple, List
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal
from PyQt6.QtGui import (
    QPainter, QPen, QColor, QFont, QFontMetrics, 
    QPainterPath, QBrush, QImage
)

from core.projection_engine import ProjectedView, ViewType, Edge2D
from core.dimension_system import Dimension, DimensionType, DimensionSystem


class TechnicalDrawingWidget(QWidget):
    """
    Widget para renderizar desenho técnico com múltiplas vistas ortográficas.
    Layout padrão de terceiro diedro (projeção americana).
    """
    
    # Sinais
    drawingReady = pyqtSignal()
    
    # Cores do desenho técnico
    COLORS = {
        'background': QColor(255, 255, 255),
        'edge_visible': QColor(0, 0, 0),
        'edge_hidden': QColor(120, 120, 120),
        'edge_silhouette': QColor(0, 0, 0),
        'dimension_line': QColor(0, 70, 170),
        'dimension_text': QColor(0, 0, 0),
        'extension_line': QColor(0, 70, 170),
        'border': QColor(0, 0, 0),
        'title_block': QColor(0, 0, 0),
        'view_label': QColor(80, 80, 80),
    }
    
    # Configurações de estilo
    STYLES = {
        'edge_width': 1.5,
        'silhouette_width': 2.0,
        'hidden_edge_width': 0.8,
        'dimension_line_width': 0.5,
        'extension_line_width': 0.4,
        'border_width': 2.0,
        'arrow_size': 6.0,
        'arrow_angle': 15,
        'font_size': 10,
        'title_font_size': 12,
        'margin': 40,
        'view_spacing': 20,
        'dimension_offset': 12,
        'label_offset': 45,  # ← ESTE VALOR define a distancia entre as medidas e o label
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.views: Dict[ViewType, ProjectedView] = {}
        self.dimension_systems: Dict[ViewType, DimensionSystem] = {}
        self.real_dimensions: Dict[str, float] = {}
        
        self.scale = 1.0
        self.show_hidden_lines = True
        self.show_dimensions = True
        self.show_border = True
        
        self.setMinimumSize(800, 600)
        self.setStyleSheet("background-color: white;")
    
    def set_views(self, views: Dict[ViewType, ProjectedView], 
                  real_dimensions: Dict[str, float]):
        """Define as vistas a serem renderizadas."""
        self.views = views
        self.real_dimensions = real_dimensions
        
        # Cria sistemas de dimensionamento para cada vista
        self.dimension_systems = {}
        for view_type, view in views.items():
            if view_type != ViewType.ISOMETRIC:
                dim_sys = DimensionSystem()
                dim_sys.auto_dimension_view(view, real_dimensions)
                self.dimension_systems[view_type] = dim_sys
        
        self.update()
        self.drawingReady.emit()
    
    def paintEvent(self, event):
        """Renderiza o desenho técnico"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        
        # Fundo branco
        painter.fillRect(self.rect(), self.COLORS['background'])
        
        if not self.views:
            self._draw_empty_message(painter)
            return
        
        # Desenha borda
        if self.show_border:
            self._draw_border(painter)
        
        # Calcula layout das vistas
        layout = self._calculate_layout()
        
        # Desenha cada vista
        for view_type, rect in layout.items():
            if view_type in self.views:
                self._draw_view(painter, self.views[view_type], rect, view_type)
        
        # Desenha bloco de título
        self._draw_title_block(painter)
        
        painter.end()
    
    def _calculate_layout(self) -> Dict[ViewType, QRectF]:
        """Calcula o layout das vistas no estilo terceiro diedro."""
        layout = {}
        
        w = self.width()
        h = self.height()
        margin = self.STYLES['margin']
        spacing = self.STYLES['view_spacing']
        
        # Área útil
        title_block_height = 55
        usable_w = w - 2 * margin
        usable_h = h - 2 * margin - title_block_height
        
        # Determina quantas vistas temos
        num_views = len(self.views)
        
        if num_views == 0:
            return layout
        
        # Layout adaptativo baseado nas vistas presentes
        if num_views <= 3:
            # Layout horizontal simples
            cell_w = (usable_w - (num_views - 1) * spacing) / num_views
            cell_h = usable_h
            view_size = min(cell_w, cell_h) * 0.85
            
            col = 0
            for view_type in self.views.keys():
                x = margin + col * (cell_w + spacing) + (cell_w - view_size) / 2
                y = margin + (cell_h - view_size) / 2
                layout[view_type] = QRectF(x, y, view_size, view_size)
                col += 1
        else:
            # Grid 3x3 para múltiplas vistas
            cell_w = (usable_w - 2 * spacing) / 3
            cell_h = (usable_h - 2 * spacing) / 3
            
            # Tamanho das vistas (maior para aproveitar espaço)
            view_size = min(cell_w, cell_h) * 0.90
            
            # Posições (col, row)
            grid_positions = {
                ViewType.TOP: (1, 0),
                ViewType.LEFT: (0, 1),
                ViewType.FRONT: (1, 1),
                ViewType.RIGHT: (2, 1),
                ViewType.BOTTOM: (1, 2),
                ViewType.BACK: (0, 2),
                ViewType.ISOMETRIC: (2, 0)
            }
            
            for view_type, (col, row) in grid_positions.items():
                if view_type in self.views:
                    x = margin + col * (cell_w + spacing) + (cell_w - view_size) / 2
                    y = margin + row * (cell_h + spacing) + (cell_h - view_size) / 2
                    layout[view_type] = QRectF(x, y, view_size, view_size)
        
        return layout
    
    def _draw_view(self, painter: QPainter, view: ProjectedView, 
                   rect: QRectF, view_type: ViewType):
        """Desenha uma única vista"""
        if not view.edges:
            return
        
        painter.save()
        
        # Calcula transformação
        min_x, min_y, max_x, max_y = view.bounds
        model_w = max_x - min_x
        model_h = max_y - min_y
        
        if model_w <= 0 or model_h <= 0:
            painter.restore()
            return
        
        # Escala MAIOR para aproveitar mais espaço
        margin_factor = 0.85
        available_w = rect.width() * margin_factor
        available_h = rect.height() * margin_factor
        
        scale_x = available_w / model_w if model_w > 0 else 1
        scale_y = available_h / model_h if model_h > 0 else 1
        scale = min(scale_x, scale_y)
        
        # Centros
        center_x = rect.x() + rect.width() / 2
        center_y = rect.y() + rect.height() / 2
        model_center_x = (min_x + max_x) / 2
        model_center_y = (min_y + max_y) / 2
        
        def transform(x, y):
            tx = center_x + (x - model_center_x) * scale
            ty = center_y - (y - model_center_y) * scale
            return tx, ty
        
        # 1. Desenha linhas ocultas (tracejadas)
        if self.show_hidden_lines:
            pen = QPen(self.COLORS['edge_hidden'])
            pen.setWidthF(self.STYLES['hidden_edge_width'])
            pen.setStyle(Qt.PenStyle.DashLine)
            pen.setDashPattern([3, 2])
            painter.setPen(pen)
            
            for edge in view.edges:
                if not edge.is_visible:
                    x1, y1 = transform(*edge.start)
                    x2, y2 = transform(*edge.end)
                    painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
        
        # 2. Desenha arestas visíveis
        for edge in view.edges:
            if edge.is_visible:
                x1, y1 = transform(*edge.start)
                x2, y2 = transform(*edge.end)
                
                if edge.is_silhouette:
                    pen = QPen(self.COLORS['edge_silhouette'])
                    pen.setWidthF(self.STYLES['silhouette_width'])
                else:
                    pen = QPen(self.COLORS['edge_visible'])
                    pen.setWidthF(self.STYLES['edge_width'])
                
                pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
                painter.setPen(pen)
                painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
        
        # 3. Desenha dimensões
        if self.show_dimensions and view_type in self.dimension_systems:
            dim_sys = self.dimension_systems[view_type]
            for dim in dim_sys.get_all_dimensions():
                self._draw_dimension(painter, dim, transform, scale)
        
        # 4. Label da vista (com mais espaço)
        self._draw_view_label(painter, view_type, rect)
        
        painter.restore()
    
    def _draw_dimension(self, painter: QPainter, dim: Dimension,
                        transform, scale: float):
        """Desenha uma dimensão completa com linhas de extensão e setas"""
        
        # Transforma todos os pontos
        p1 = transform(*dim.point1)
        p2 = transform(*dim.point2)
        dl_start = transform(*dim.dim_line_start)
        dl_end = transform(*dim.dim_line_end)
        text_pos = transform(*dim.text_position)
        
        ext1_start = transform(*dim.ext_line1_start)
        ext1_end = transform(*dim.ext_line1_end)
        ext2_start = transform(*dim.ext_line2_start)
        ext2_end = transform(*dim.ext_line2_end)
        
        # Linhas de extensão
        pen = QPen(self.COLORS['extension_line'])
        pen.setWidthF(self.STYLES['extension_line_width'])
        painter.setPen(pen)
        
        if dim.dim_type in [DimensionType.LINEAR_HORIZONTAL, 
                            DimensionType.LINEAR_VERTICAL]:
            painter.drawLine(QPointF(*ext1_start), QPointF(*ext1_end))
            painter.drawLine(QPointF(*ext2_start), QPointF(*ext2_end))
        
        # Linha de cota
        pen = QPen(self.COLORS['dimension_line'])
        pen.setWidthF(self.STYLES['dimension_line_width'])
        painter.setPen(pen)
        painter.drawLine(QPointF(*dl_start), QPointF(*dl_end))
        
        # Setas
        self._draw_arrow(painter, dl_start[0], dl_start[1], dl_end[0], dl_end[1])
        self._draw_arrow(painter, dl_end[0], dl_end[1], dl_start[0], dl_start[1])
        
        # Texto
        text = dim.formatted_value()
        font = QFont("Arial", self.STYLES['font_size'])
        painter.setFont(font)
        painter.setPen(QPen(self.COLORS['dimension_text']))
        
        fm = QFontMetrics(font)
        text_width = fm.horizontalAdvance(text)
        text_height = fm.height()
        
        painter.save()
        painter.translate(text_pos[0], text_pos[1])
        
        if dim.dim_type == DimensionType.LINEAR_VERTICAL:
            painter.rotate(-90)
            painter.drawText(QPointF(-text_width/2, text_height/3), text)
        else:
            painter.drawText(QPointF(-text_width/2, text_height/3), text)
        
        painter.restore()
    
    def _draw_arrow(self, painter: QPainter, x1: float, y1: float,
                    x2: float, y2: float):
        """Desenha seta na extremidade da linha de cota"""
        arrow_size = self.STYLES['arrow_size']
        arrow_angle = math.radians(self.STYLES['arrow_angle'])
        
        angle = math.atan2(y2 - y1, x2 - x1)
        
        # Pontos da seta
        p1x = x1 + arrow_size * math.cos(angle + arrow_angle)
        p1y = y1 + arrow_size * math.sin(angle + arrow_angle)
        p2x = x1 + arrow_size * math.cos(angle - arrow_angle)
        p2y = y1 + arrow_size * math.sin(angle - arrow_angle)
        
        path = QPainterPath()
        path.moveTo(x1, y1)
        path.lineTo(p1x, p1y)
        path.lineTo(p2x, p2y)
        path.closeSubpath()
        
        painter.fillPath(path, QBrush(self.COLORS['dimension_line']))
    
    def _draw_view_label(self, painter: QPainter, view_type: ViewType, rect: QRectF):
        """Desenha o label da vista com mais espaçamento"""
        labels = {
            ViewType.FRONT: "FRONTAL",
            ViewType.BACK: "TRASEIRA",
            ViewType.TOP: "SUPERIOR",
            ViewType.BOTTOM: "INFERIOR",
            ViewType.LEFT: "ESQ.",
            ViewType.RIGHT: "DIR.",
            ViewType.ISOMETRIC: "ISOMÉTRICA"
        }
        
        label = labels.get(view_type, "")
        
        painter.save()
        font = QFont("Arial", 8)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QPen(self.COLORS['view_label']))
        
        fm = QFontMetrics(font)
        text_width = fm.horizontalAdvance(label)
        
        x = rect.x() + (rect.width() - text_width) / 2
        y = rect.y() + rect.height() + self.STYLES['label_offset']  # Aumentado
        
        painter.drawText(QPointF(x, y), label)
        painter.restore()
    
    def _draw_border(self, painter: QPainter):
        """Desenha a borda do desenho"""
        pen = QPen(self.COLORS['border'])
        pen.setWidthF(self.STYLES['border_width'])
        painter.setPen(pen)
        
        margin = 15
        painter.drawRect(margin, margin,
                        self.width() - 2 * margin,
                        self.height() - 2 * margin)
        
        # Borda interna
        pen.setWidthF(0.5)
        painter.setPen(pen)
        painter.drawRect(margin + 5, margin + 5,
                        self.width() - 2 * margin - 10,
                        self.height() - 2 * margin - 10)
    
    def _draw_title_block(self, painter: QPainter):
        """Desenha o bloco de título"""
        margin = 20
        block_height = 45
        block_width = 220
        
        x = self.width() - margin - block_width
        y = self.height() - margin - block_height
        
        painter.save()
        
        # Retângulo
        pen = QPen(self.COLORS['title_block'])
        pen.setWidthF(1.0)
        painter.setPen(pen)
        painter.drawRect(int(x), int(y), int(block_width), int(block_height))
        
        # Divisória vertical
        painter.drawLine(int(x + block_width * 0.6), int(y),
                        int(x + block_width * 0.6), int(y + block_height))
        
        # Divisória horizontal
        painter.drawLine(int(x), int(y + block_height * 0.5),
                        int(x + block_width * 0.6), int(y + block_height * 0.5))
        
        copyright_text = "\u00A9 SE3D | TechDraw"

        # Textos
        font = QFont("Arial", 9)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(QPointF(x + 8, y + 16), f"{copyright_text}")
        
        font.setBold(False)
        font.setPointSize(7)
        painter.setFont(font)
        
        # Dimensões
        if self.real_dimensions:
            w = self.real_dimensions.get('width', 0)
            h = self.real_dimensions.get('height', 0)
            d = self.real_dimensions.get('depth', 0)
            dims_text = f"{w:.1f} x {h:.1f} x {d:.1f}"
            painter.drawText(QPointF(x + 8, y + 35), dims_text)
        
        # Escala
        font.setPointSize(8)
        painter.setFont(font)
        painter.drawText(QPointF(x + block_width * 0.65, y + 20), "ESCALA")
        font.setBold(True)
        font.setPointSize(10)
        painter.setFont(font)
        painter.drawText(QPointF(x + block_width * 0.65, y + 36), "1:A4")
        
        painter.restore()
    
    def _draw_empty_message(self, painter: QPainter):
        """Desenha mensagem quando não há vistas"""
        font = QFont("Arial", 12)
        painter.setFont(font)
        painter.setPen(QPen(QColor(150, 150, 150)))
        
        text = "Carregue um modelo e clique em 'Gerar Desenho Técnico'"
        fm = QFontMetrics(font)
        text_width = fm.horizontalAdvance(text)
        
        painter.drawText(QPointF((self.width() - text_width) / 2,
                                  self.height() / 2), text)
    
    def export_to_image(self, filepath: str, width: int = 2480, height: int = 1754):
        """
        Exporta o desenho para imagem em alta resolução.
        Captura o que está na tela e escala para a resolução desejada.
        """
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import QSize
        
        # Captura o tamanho atual (que está correto na tela)
        current_width = self.width()
        current_height = self.height()
        
        # Cria imagem do tamanho ATUAL (o que está na tela)
        screen_image = QImage(current_width, current_height, QImage.Format.Format_RGB32)
        screen_image.fill(Qt.GlobalColor.white)
        
        # Renderiza o que está na tela
        painter = QPainter(screen_image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        self.render(painter)
        painter.end()
        
        # Agora ESCALA para a resolução desejada mantendo proporção
        scaled_image = screen_image.scaled(
            width, 
            height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        
        # Cria imagem final com fundo branco do tamanho exato
        final_image = QImage(width, height, QImage.Format.Format_RGB32)
        final_image.fill(Qt.GlobalColor.white)
        
        # Centraliza a imagem escalada na imagem final
        painter = QPainter(final_image)
        x = (width - scaled_image.width()) // 2
        y = (height - scaled_image.height()) // 2
        painter.drawImage(x, y, scaled_image)
        painter.end()
        
        # Salva
        final_image.save(filepath, quality=95)
        
        return filepath
    
    def toggle_hidden_lines(self, show: bool):
        self.show_hidden_lines = show
        self.update()
    
    def toggle_dimensions(self, show: bool):
        self.show_dimensions = show
        self.update()
    
    def toggle_border(self, show: bool):
        self.show_border = show
        self.update()