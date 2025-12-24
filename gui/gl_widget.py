"""
===============================================================================
STL2TechnicalDrawing - Widget OpenGL 3D COM ESPELHAMENTO
===============================================================================
Pasta: gui/
Arquivo: gui/gl_widget.py
Descrição: Widget OpenGL com navegação e espelhamento X/Y funcional
===============================================================================
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from typing import Optional
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtGui import QMouseEvent, QWheelEvent
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *
from OpenGL.GLU import *

from core.stl_loader import MeshData
from utils.constants import (
    BACKGROUND_COLOR, MODEL_COLOR, EDGE_COLOR, WIREFRAME_COLOR,
    ROTATION_SPEED, ZOOM_SPEED, PAN_SPEED,
    MIN_ZOOM, MAX_ZOOM,
    LIGHT_POSITION, LIGHT_AMBIENT, LIGHT_DIFFUSE, LIGHT_SPECULAR,
    MATERIAL_AMBIENT, MATERIAL_DIFFUSE, MATERIAL_SPECULAR, MATERIAL_SHININESS,
    VIEWS
)


class GLWidget(QOpenGLWidget):
    """Widget OpenGL para renderização 3D com navegação por mouse"""
    
    # Sinais
    viewChanged = pyqtSignal(str)
    meshLoaded = pyqtSignal(dict)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        # Dados do mesh
        self.mesh_data: Optional[MeshData] = None
        
        # Transformações da câmera
        self.rotation_x = 25.0
        self.rotation_y = -45.0
        self.rotation_z = 0.0
        self.zoom = 4.0
        self.pan_x = 0.0
        self.pan_y = -0.3
        
        # Estado do mouse
        self.last_mouse_pos = QPoint()
        self.mouse_button = Qt.MouseButton.NoButton
        
        # Opções de renderização
        self.show_faces = True
        self.show_edges = True
        self.show_grid = True
        self.wireframe_mode = False
        
        # ✅ Espelhamento
        self.mirror_x = False
        self.mirror_y = False
        self.mirror_z = False
        
        # ✅ COR DO MODELO (inicializada com a constante)
        from utils.constants import MODEL_COLOR
        self.model_color = MODEL_COLOR

        # VBOs
        self.vbo_vertices = None
        self.vbo_faces = None
        self.vbo_edges = None
        
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    
    def initializeGL(self):
        """Inicializa o contexto OpenGL"""
        glClearColor(*BACKGROUND_COLOR)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        
        glLightfv(GL_LIGHT0, GL_POSITION, LIGHT_POSITION)
        glLightfv(GL_LIGHT0, GL_AMBIENT, LIGHT_AMBIENT)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, LIGHT_DIFFUSE)
        glLightfv(GL_LIGHT0, GL_SPECULAR, LIGHT_SPECULAR)
        
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, MATERIAL_SPECULAR)
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, MATERIAL_SHININESS)
        
        glEnable(GL_NORMALIZE)
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)
    
    def resizeGL(self, width: int, height: int):
        """Redimensiona o viewport"""
        glViewport(0, 0, width, height)
        self._update_projection()
    
    def _update_projection(self):
        """Atualiza a matriz de projeção"""
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        
        width = self.width()
        height = self.height()
        
        if height == 0:
            height = 1
        
        aspect = width / height
        gluPerspective(45.0, aspect, 0.1, 1000.0)
        glMatrixMode(GL_MODELVIEW)
    
    def clear_mesh(self):
        """Limpa o mesh carregado"""
        self.mesh_data = None
        self.update()

    def paintGL(self):
        """Renderiza a cena"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        glTranslatef(self.pan_x, self.pan_y, -self.zoom)
        
        glRotatef(self.rotation_x, 1.0, 0.0, 0.0)
        glRotatef(self.rotation_y, 0.0, 1.0, 0.0)
        glRotatef(self.rotation_z, 0.0, 0.0, 1.0)
        
        if self.show_grid:
            self._draw_grid()
        
        self._draw_axes()
        
        if self.mesh_data is not None:
            self._draw_mesh()
    
    def _draw_grid(self):
        """Desenha grid de referência no plano XZ"""
        glDisable(GL_LIGHTING)
        glColor4f(0.3, 0.3, 0.3, 0.5)
        glLineWidth(1.0)
        
        grid_size = 2.0
        divisions = 20
        step = grid_size * 2 / divisions
        
        glBegin(GL_LINES)
        for i in range(divisions + 1):
            pos = -grid_size + i * step
            glVertex3f(-grid_size, 0, pos)
            glVertex3f(grid_size, 0, pos)
            glVertex3f(pos, 0, -grid_size)
            glVertex3f(pos, 0, grid_size)
        glEnd()
        
        glEnable(GL_LIGHTING)
    
    def _draw_axes(self):
        """Desenha eixos de coordenadas"""
        glDisable(GL_LIGHTING)
        glLineWidth(2.0)
        
        axis_length = 0.5
        
        glBegin(GL_LINES)
        # X - Vermelho
        glColor3f(1.0, 0.2, 0.2)
        glVertex3f(0, 0, 0)
        glVertex3f(axis_length, 0, 0)
        
        # Y - Verde (altura)
        glColor3f(0.2, 1.0, 0.2)
        glVertex3f(0, 0, 0)
        glVertex3f(0, axis_length, 0)
        
        # Z - Azul
        glColor3f(0.2, 0.2, 1.0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, axis_length)
        glEnd()
        
        glEnable(GL_LIGHTING)
    
    def _draw_mesh(self):
        """Desenha o mesh carregado COM ESPELHAMENTO"""
        if self.mesh_data is None:
            return
        
        glPushMatrix()
        scale = self.mesh_data.scale
        
        # ✅ ESPELHAMENTO SIMPLES (não inverte por padrão)
        scale_x = -scale if self.mirror_x else scale
        scale_y = -scale if self.mirror_y else scale
        scale_z = -scale if self.mirror_z else scale
        
        glScalef(scale_x, scale_y, scale_z)
        
        # Desenha faces
        if self.show_faces and not self.wireframe_mode:
            glEnable(GL_LIGHTING)
            
            # ✅ USA self.model_color EM VEZ DA CONSTANTE
            glColor4f(*self.model_color)
            
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            
            glVertexPointer(3, GL_FLOAT, 24, self.mesh_data.vertex_data)
            glNormalPointer(GL_FLOAT, 24, self.mesh_data.vertex_data[3:])
            
            glDrawElements(
                GL_TRIANGLES,
                len(self.mesh_data.face_indices),
                GL_UNSIGNED_INT,
                self.mesh_data.face_indices
            )
        
        # Desenha arestas
        if self.show_edges or self.wireframe_mode:
            glDisable(GL_LIGHTING)
            
            if self.wireframe_mode or not self.show_faces:
                glColor4f(*WIREFRAME_COLOR)
                glLineWidth(1.5)
            else:
                glColor4f(*EDGE_COLOR)
                glLineWidth(1.0)
            
            glEnable(GL_POLYGON_OFFSET_LINE)
            glPolygonOffset(-1.0, -1.0)
            
            glVertexPointer(3, GL_FLOAT, 24, self.mesh_data.vertex_data)
            
            glDrawElements(
                GL_LINES,
                len(self.mesh_data.edge_indices),
                GL_UNSIGNED_INT,
                self.mesh_data.edge_indices
            )
            
            glDisable(GL_POLYGON_OFFSET_LINE)
            glEnable(GL_LIGHTING)
        
        glPopMatrix()
    
    def set_mesh(self, mesh_data: MeshData):
        """Define o mesh a ser renderizado"""
        self.mesh_data = mesh_data
        self.reset_view()
        self.update()
    
    def reset_view(self):
        """Reseta a vista para posição padrão"""
        self.rotation_x = 25.0
        self.rotation_y = -45.0
        self.rotation_z = 0.0
        self.zoom = 4.0
        self.pan_x = 0.0
        self.pan_y = -0.3
        self.update()
    
    def set_view(self, view_name: str):
        """Define uma vista predefinida"""
        if view_name in VIEWS:
            view = VIEWS[view_name]
            self.rotation_x = view['rotation'][0]
            self.rotation_y = view['rotation'][1]
            self.rotation_z = view['rotation'][2]
            self.pan_x = 0.0
            self.pan_y = 0.0
            self.viewChanged.emit(view_name)
            self.update()
    
    def mousePressEvent(self, event: QMouseEvent):
        """Início de interação com mouse"""
        self.last_mouse_pos = event.pos()
        self.mouse_button = event.button()
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Fim de interação com mouse"""
        self.mouse_button = Qt.MouseButton.NoButton
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """Movimento do mouse - rotação e pan"""
        if self.mouse_button == Qt.MouseButton.NoButton:
            return
        
        dx = event.pos().x() - self.last_mouse_pos.x()
        dy = event.pos().y() - self.last_mouse_pos.y()
        
        if self.mouse_button == Qt.MouseButton.LeftButton:
            self.rotation_y += dx * ROTATION_SPEED
            self.rotation_x += dy * ROTATION_SPEED
            self.rotation_x = max(-90, min(90, self.rotation_x))
            
        elif self.mouse_button == Qt.MouseButton.MiddleButton:
            self.pan_x += dx * PAN_SPEED * self.zoom
            self.pan_y -= dy * PAN_SPEED * self.zoom
            
        elif self.mouse_button == Qt.MouseButton.RightButton:
            self.zoom -= dy * ZOOM_SPEED
            self.zoom = max(MIN_ZOOM, min(MAX_ZOOM, self.zoom))
        
        self.last_mouse_pos = event.pos()
        self.update()
    
    def wheelEvent(self, event: QWheelEvent):
        """Zoom com scroll do mouse"""
        delta = event.angleDelta().y()
        zoom_factor = 1.0 - delta * 0.001
        self.zoom *= zoom_factor
        self.zoom = max(MIN_ZOOM, min(MAX_ZOOM, self.zoom))
        self.update()
    
    def keyPressEvent(self, event):
        """Atalhos de teclado"""
        key = event.key()
        
        if key == Qt.Key.Key_1:
            self.set_view('front')
        elif key == Qt.Key.Key_2:
            self.set_view('back')
        elif key == Qt.Key.Key_3:
            self.set_view('top')
        elif key == Qt.Key.Key_4:
            self.set_view('bottom')
        elif key == Qt.Key.Key_5:
            self.set_view('left')
        elif key == Qt.Key.Key_6:
            self.set_view('right')
        elif key == Qt.Key.Key_7:
            self.set_view('isometric')
        elif key == Qt.Key.Key_R:
            self.reset_view()
        elif key == Qt.Key.Key_W:
            self.wireframe_mode = not self.wireframe_mode
            self.update()
        elif key == Qt.Key.Key_G:
            self.show_grid = not self.show_grid
            self.update()
        elif key == Qt.Key.Key_E:
            self.show_edges = not self.show_edges
            self.update()
        elif key == Qt.Key.Key_F:
            self.show_faces = not self.show_faces
            self.update()
    
    def toggle_wireframe(self, enabled: bool):
        """Alterna modo wireframe"""
        self.wireframe_mode = enabled
        self.update()
    
    def toggle_edges(self, enabled: bool):
        """Alterna exibição de arestas"""
        self.show_edges = enabled
        self.update()
    
    def toggle_faces(self, enabled: bool):
        """Alterna exibição de faces"""
        self.show_faces = enabled
        self.update()
    
    def toggle_grid(self, enabled: bool):
        """Alterna exibição do grid"""
        self.show_grid = enabled
        self.update()
    
    # ✅ MÉTODOS DE ESPELHAMENTO
    def set_mirror_x(self, enabled: bool):
        """Ativa/desativa espelhamento no eixo X"""
        self.mirror_x = enabled
        self.update()
    
    def set_mirror_y(self, enabled: bool):
        """Ativa/desativa espelhamento no eixo Y"""
        self.mirror_y = enabled
        self.update()

    def set_mirror_z(self, enabled: bool):
        """Ativa/desativa espelhamento no eixo Z"""
        self.mirror_z = enabled
        self.update()

    def set_model_color(self, color: tuple):
        """Define a cor do modelo diretamente no widget"""
        print(f"🔄 GLWidget.set_model_color() chamado com cor: {color}")
        self.model_color = color  # Armazena localmente
        self.update()  # Força redesenho imediato