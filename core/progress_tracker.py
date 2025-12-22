"""
===============================================================================
STL2TechnicalDrawing - Sistema de Progresso e Cancelamento
===============================================================================
Pasta: core/
Arquivo: core/progress_tracker.py
Descrição: Sistema centralizado para rastreamento de progresso real
===============================================================================
"""

from typing import Callable, Optional
from dataclasses import dataclass
import time


@dataclass
class ProgressInfo:
    """Informações de progresso"""
    current: int
    total: int
    message: str
    elapsed_time: float = 0.0
    
    @property
    def percentage(self) -> float:
        """Retorna porcentagem (0-100)"""
        if self.total == 0:
            return 0.0
        return (self.current / self.total) * 100
    
    @property
    def is_complete(self) -> bool:
        """Verifica se está completo"""
        return self.current >= self.total


class ProgressTracker:
    """
    Rastreador de progresso com callbacks e cancelamento.
    Thread-safe para uso em workers.
    """
    
    def __init__(self):
        self.callback: Optional[Callable[[ProgressInfo], None]] = None
        self.cancelled: bool = False
        self.start_time: float = 0.0
    
    def set_callback(self, callback: Callable[[ProgressInfo], None]):
        """Define callback para atualização de progresso"""
        self.callback = callback
    
    def start(self):
        """Inicia tracking"""
        self.cancelled = False
        self.start_time = time.time()
    
    def report(self, current: int, total: int, message: str):
        """
        Reporta progresso atual.
        
        Args:
            current: Valor atual (0 a total)
            total: Valor total
            message: Mensagem descritiva
        """
        if self.callback:
            elapsed = time.time() - self.start_time
            info = ProgressInfo(current, total, message, elapsed)
            self.callback(info)
    
    def cancel(self):
        """Marca como cancelado"""
        self.cancelled = True
    
    def is_cancelled(self) -> bool:
        """Verifica se foi cancelado"""
        return self.cancelled
    
    def check_cancelled(self):
        """
        Verifica cancelamento e lança exceção se cancelado.
        Use em loops longos.
        """
        if self.cancelled:
            raise CancelledException("Operação cancelada pelo usuário")


class CancelledException(Exception):
    """Exceção para operação cancelada"""
    pass