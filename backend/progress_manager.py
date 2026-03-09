"""
DaVinci Decoder - Progress Manager
Gerencia progresso em tempo real das tentativas de decifração
"""
import queue
import threading
from typing import Dict, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ProgressUpdate:
    """Atualização de progresso"""
    current: int
    total: int
    algorithm: str
    status: str  # 'testing', 'success', 'failed'
    timestamp: str
    percentage: float


class ProgressManager:
    """Gerencia progresso de múltiplas sessões de decifração"""
    
    def __init__(self):
        self.sessions: Dict[str, queue.Queue] = {}
        self.lock = threading.Lock()
    
    def create_session(self, session_id: str):
        """Cria nova sessão de progresso"""
        with self.lock:
            self.sessions[session_id] = queue.Queue()
    
    def update_progress(self, session_id: str, current: int, total: int,
                       algorithm: str, status: str = "testing"):
        """Atualiza progresso de uma sessão"""
        with self.lock:
            if session_id not in self.sessions:
                return
            
            percentage = (current / total * 100) if total > 0 else 0
            
            update = ProgressUpdate(
                current=current,
                total=total,
                algorithm=algorithm,
                status=status,
                timestamp=datetime.now().isoformat(),
                percentage=round(percentage, 1)
            )
            
            self.sessions[session_id].put(update)
    
    def get_updates(self, session_id: str, timeout: float = 30.0):
        """Generator que retorna atualizações de progresso (SSE)"""
        if session_id not in self.sessions:
            return
        
        session_queue = self.sessions[session_id]
        
        try:
            while True:
                try:
                    update = session_queue.get(timeout=timeout)
                    
                    # Formatar como Server-Sent Event
                    yield {
                        'current': update.current,
                        'total': update.total,
                        'algorithm': update.algorithm,
                        'status': update.status,
                        'percentage': update.percentage,
                        'timestamp': update.timestamp
                    }
                    
                    # Se chegou ao final, parar
                    if update.current >= update.total:
                        break
                        
                except queue.Empty:
                    # Timeout - cliente ainda está conectado
                    yield {'heartbeat': True}
                    
        finally:
            self.cleanup_session(session_id)
    
    def cleanup_session(self, session_id: str):
        """Remove sessão após conclusão"""
        with self.lock:
            if session_id in self.sessions:
                del self.sessions[session_id]


# Instância global
progress_manager = ProgressManager()
