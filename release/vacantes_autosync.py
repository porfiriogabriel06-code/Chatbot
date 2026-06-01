"""
Módulo de integración automática de cambios en vacantes.
Monitora vacantes.json y sincroniza cambios con el chatbot en tiempo real.
"""

import json
import os
import threading
import time
from datetime import datetime
from typing import Callable, Optional, Dict, List


class VacantesWatcher:
    """
    Monitorea cambios en el archivo vacantes.json y dispara callbacks.
    Permite sincronización automática sin reiniciar la aplicación.
    """
    
    def __init__(self, filepath: str = 'vacantes.json', check_interval: int = 2):
        """
        Inicializa el vigilante de vacantes.
        
        Args:
            filepath: Ruta del archivo a monitorear
            check_interval: Intervalo de verificación en segundos
        """
        self.filepath = filepath
        self.check_interval = check_interval
        self.last_mtime = None
        self.last_content_hash = None
        self.is_running = False
        self.thread = None
        self.callbacks = []
        self.data_cache = None
    
    def register_callback(self, callback: Callable[[Dict], None]) -> None:
        """
        Registra un callback para ejecutar cuando cambian las vacantes.
        
        Args:
            callback: Función que recibe los nuevos datos como parámetro
        """
        self.callbacks.append(callback)
    
    def _get_file_hash(self) -> str:
        """Obtiene hash del contenido del archivo."""
        try:
            with open(self.filepath, 'rb') as f:
                content = f.read()
                return str(hash(content))
        except:
            return None
    
    def _load_data(self) -> Optional[Dict]:
        """Carga datos del archivo."""
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    
    def _notify_callbacks(self, data: Dict) -> None:
        """Ejecuta todos los callbacks registrados."""
        for callback in self.callbacks:
            try:
                callback(data)
            except Exception as e:
                print(f"Error en callback de watcher: {e}")
    
    def check_changes(self) -> bool:
        """
        Verifica si el archivo ha cambiado.
        
        Returns:
            True si hay cambios, False en caso contrario
        """
        try:
            if not os.path.exists(self.filepath):
                return False
            
            current_hash = self._get_file_hash()
            
            if current_hash != self.last_content_hash:
                self.last_content_hash = current_hash
                
                # Cargar datos y notificar
                data = self._load_data()
                if data:
                    self.data_cache = data
                    self._notify_callbacks(data)
                    return True
            
            return False
        except Exception as e:
            print(f"Error verificando cambios en {self.filepath}: {e}")
            return False
    
    def start(self) -> None:
        """Inicia el monitoreo en un thread separado."""
        if self.is_running:
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self._watch_loop, daemon=True)
        self.thread.start()
        print(f"Vigilante de vacantes iniciado (intervalo: {self.check_interval}s)")
    
    def stop(self) -> None:
        """Detiene el monitoreo."""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("Vigilante de vacantes detenido")
    
    def _watch_loop(self) -> None:
        """Loop de monitoreo (ejecuta en thread separado)."""
        while self.is_running:
            try:
                self.check_changes()
                time.sleep(self.check_interval)
            except Exception as e:
                print(f"Error en loop de vigilancia: {e}")
                time.sleep(self.check_interval)
    
    def get_cached_data(self) -> Optional[Dict]:
        """Obtiene datos cacheados."""
        return self.data_cache


class VacantesAutoSync:
    """
    Gestor de sincronización automática de vacantes.
    Integra el watcher con el sistema de chatbot para actualizaciones en tiempo real.
    """
    
    def __init__(self, chatbot_module, filepath: str = 'vacantes.json'):
        """
        Inicializa el sistema de sincronización automática.
        
        Args:
            chatbot_module: Módulo del chatbot a sincronizar
            filepath: Ruta del archivo de vacantes
        """
        self.chatbot_module = chatbot_module
        self.watcher = VacantesWatcher(filepath)
        self.watcher.register_callback(self._on_vacantes_changed)
        self.sync_history = []
        self.last_sync = None
    
    def _on_vacantes_changed(self, data: Dict) -> None:
        """
        Callback ejecutado cuando cambian las vacantes.
        Sincroniza los cambios con el módulo del chatbot.
        
        Args:
            data: Nuevos datos de vacantes.json
        """
        try:
            # Actualizar datos en el módulo chatbot
            if 'vacantes' in data:
                self.chatbot_module.vacantes = data.get('vacantes', [])
            
            if 'areas' in data:
                self.chatbot_module.areas = data.get('areas', [])
            
            # Actualizar preguntas de entrevista si están disponibles
            if 'areas' in data:
                self._update_interview_questions(data.get('areas', []))
            
            # Registrar en historial
            self.last_sync = datetime.now()
            self.sync_history.append({
                'timestamp': self.last_sync.isoformat(),
                'vacantes_count': len(data.get('vacantes', [])),
                'areas_count': len(data.get('areas', []))
            })
            
            # Mantener solo últimos 100 syncs
            if len(self.sync_history) > 100:
                self.sync_history = self.sync_history[-100:]
            
            print(f"✅ Vacantes sincronizadas automáticamente - {len(data.get('vacantes', []))} vacantes, {len(data.get('areas', []))} áreas")
        
        except Exception as e:
            print(f"❌ Error sincronizando vacantes: {e}")
    
    def _update_interview_questions(self, areas: List[Dict]) -> None:
        """
        Actualiza las preguntas de entrevista basadas en las áreas.
        
        Args:
            areas: Lista de áreas con preguntas de entrevista
        """
        try:
            # Construir nuevo diccionario de preguntas
            new_questions = {}
            
            for area in areas:
                area_name = area.get('nombre')
                if area_name and 'preguntas_entrevista' in area:
                    preguntas = area.get('preguntas_entrevista', {})
                    if isinstance(preguntas, dict):
                        for puesto, preguntas_list in preguntas.items():
                            if isinstance(preguntas_list, list):
                                new_questions[puesto] = preguntas_list
            
            # Actualizar en el módulo chatbot
            if hasattr(self.chatbot_module, 'INTERVIEW_QUESTIONS_BY_AREA'):
                self.chatbot_module.INTERVIEW_QUESTIONS_BY_AREA.update(new_questions)
                print(f"  • Preguntas de entrevista actualizadas para {len(new_questions)} puestos")
        
        except Exception as e:
            print(f"  ⚠️ Error actualizando preguntas de entrevista: {e}")
    
    def start(self) -> None:
        """Inicia el monitoreo y sincronización automática."""
        self.watcher.start()
    
    def stop(self) -> None:
        """Detiene el monitoreo y sincronización."""
        self.watcher.stop()
    
    def get_sync_stats(self) -> Dict:
        """Obtiene estadísticas de sincronización."""
        return {
            'is_running': self.watcher.is_running,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
            'sync_count': len(self.sync_history),
            'recent_syncs': self.sync_history[-5:] if self.sync_history else []
        }
    
    def force_sync(self) -> bool:
        """Fuerza una sincronización inmediata."""
        return self.watcher.check_changes()


# Instancia global de sincronización automática
_autosync_instance = None


def get_autosync(chatbot_module, filepath: str = 'vacantes.json') -> VacantesAutoSync:
    """Obtiene o crea la instancia global de sincronización automática."""
    global _autosync_instance
    if _autosync_instance is None:
        _autosync_instance = VacantesAutoSync(chatbot_module, filepath)
    return _autosync_instance


def start_autosync(chatbot_module, filepath: str = 'vacantes.json') -> None:
    """Inicia la sincronización automática."""
    autosync = get_autosync(chatbot_module, filepath)
    autosync.start()
