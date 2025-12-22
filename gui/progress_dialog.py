"""
===============================================================================
STL2TechnicalDrawing - Diálogo de Progresso Baseado em Eventos
===============================================================================
Pasta: gui/
Arquivo: gui/progress_dialog.py
Descrição: Diálogo com barra de progresso sincronizada com o processamento
===============================================================================
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont


class ProgressDialog(QDialog):
    """Diálogo de progresso baseado em eventos reais de processamento"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.current_progress = 0
        
        self.setWindowTitle("Gerando Desenho Técnico")
        self.setModal(True)
        self.setFixedSize(400, 150)
        
        # Remove botões de fechar
        self.setWindowFlags(
            Qt.WindowType.Dialog | 
            Qt.WindowType.CustomizeWindowHint | 
            Qt.WindowType.WindowTitleHint
        )
        
        self._setup_ui()
        
        # Timer para animação da barra (apenas visual, não muda a mensagem)
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self._animate_progress)
        self.animation_timer.start(50)  # 50ms para suavidade
    
    def _setup_ui(self):
        """Configura a interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Label de mensagem
        self.lbl_message = QLabel("Iniciando processamento...")
        self.lbl_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont("Segoe UI", 11)
        self.lbl_message.setFont(font)
        self.lbl_message.setWordWrap(True)
        layout.addWidget(self.lbl_message)
        
        # Barra de progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setFixedHeight(20)
        layout.addWidget(self.progress_bar)
        
        # Label de etapa
        self.lbl_step = QLabel("")
        self.lbl_step.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_step.setStyleSheet("color: #888; font-size: 9px;")
        layout.addWidget(self.lbl_step)
        
        # Estilo
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
            }
            QLabel {
                color: #ffffff;
            }
            QProgressBar {
                border: 1px solid #555;
                border-radius: 5px;
                background-color: #3c3c3c;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #0d6efd,
                    stop: 1 #0b5ed7
                );
                border-radius: 4px;
            }
        """)
    
    def _animate_progress(self):
        """Anima a barra de progresso suavemente"""
        # Incrementa progressivamente até o valor alvo
        current = self.progress_bar.value()
        if current < self.current_progress:
            # Incrementa de forma suave
            increment = max(1, (self.current_progress - current) // 10)
            self.progress_bar.setValue(min(current + increment, self.current_progress))
    
    def set_progress(self, value: int, message: str = None, step: str = None):
        """
        Define o progresso atual
        
        Args:
            value: Valor de 0 a 100
            message: Mensagem principal (opcional)
            step: Descrição da etapa atual (opcional)
        """
        self.current_progress = max(0, min(100, value))
        
        if message:
            self.lbl_message.setText(message)
        
        if step:
            self.lbl_step.setText(step)
    
    def set_message(self, message: str):
        """Define uma mensagem específica"""
        self.lbl_message.setText(message)
    
    def set_step(self, step: str):
        """Define a descrição da etapa atual"""
        self.lbl_step.setText(step)
    
    def complete(self):
        """Marca como completo e fecha"""
        self.current_progress = 100
        self.progress_bar.setValue(100)
        self.lbl_message.setText("Concluído!")
        self.lbl_step.setText("")
        
        # Aguarda um momento antes de fechar
        QTimer.singleShot(500, self.accept)
    
    def closeEvent(self, event):
        """Intercepta o fechamento para parar o timer"""
        self.animation_timer.stop()
        event.accept()


class SimpleProgressDialog(QDialog):
    """Versão simplificada com apenas mensagens rotativas (para compatibilidade)"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.messages = [
            "Analisando geometria...",
            "Calculando projeções...",
            "Detectando contornos...",
            "Processando arestas visíveis...",
            "Identificando linhas ocultas...",
            "Calculando dimensões...",
            "Posicionando cotas...",
            "Finalizando desenho técnico..."
        ]
        
        self.current_message_index = 0
        
        self.setWindowTitle("Gerando Desenho Técnico")
        self.setModal(True)
        self.setFixedSize(400, 150)
        
        # Remove botões de fechar
        self.setWindowFlags(
            Qt.WindowType.Dialog | 
            Qt.WindowType.CustomizeWindowHint | 
            Qt.WindowType.WindowTitleHint
        )
        
        self._setup_ui()
        
        # Timer para rotação de mensagens
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_message)
        self.timer.start(2000)  # A cada 2 segundos
    
    def _setup_ui(self):
        """Configura a interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Label de mensagem
        self.lbl_message = QLabel(self.messages[0])
        self.lbl_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont("Segoe UI", 11)
        self.lbl_message.setFont(font)
        self.lbl_message.setWordWrap(True)
        layout.addWidget(self.lbl_message)
        
        # Barra de progresso indeterminada
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)  # Modo indeterminado
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(20)
        layout.addWidget(self.progress_bar)
        
        # Estilo
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
            }
            QLabel {
                color: #ffffff;
            }
            QProgressBar {
                border: 1px solid #555;
                border-radius: 5px;
                background-color: #3c3c3c;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #0d6efd;
                border-radius: 4px;
            }
        """)
    
    def _update_message(self):
        """Atualiza a mensagem exibida"""
        self.current_message_index = (self.current_message_index + 1) % len(self.messages)
        self.lbl_message.setText(self.messages[self.current_message_index])
    
    def set_message(self, message: str):
        """Define uma mensagem específica"""
        self.lbl_message.setText(message)
    
    def closeEvent(self, event):
        """Intercepta o fechamento para parar o timer"""
        self.timer.stop()
        event.accept()