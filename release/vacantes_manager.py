"""
Módulo para administración de vacantes y áreas.
Maneja operaciones CRUD con persistencia en vacantes.json
"""

import json
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import threading


class VacantesManager:
    """Gestor de vacantes con operaciones CRUD y sincronización automática."""
    
    def __init__(self, filepath: str = 'vacantes.json'):
        """
        Inicializa el gestor de vacantes.
        
        Args:
            filepath: Ruta del archivo JSON con vacantes
        """
        self.filepath = filepath
        self.lock = threading.Lock()  # Para evitar condiciones de carrera
        self._load_data()
    
    def _load_data(self) -> None:
        """Carga datos de vacantes.json."""
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self._init_empty_structure()
        except json.JSONDecodeError:
            print(f"Error: {self.filepath} tiene formato JSON inválido")
            self._init_empty_structure()
    
    def _init_empty_structure(self) -> None:
        """Inicializa estructura vacía de datos."""
        self.data = {
            'vacantes': [],
            'areas': [],
            'configuracion_admin': {
                'habilitada': True,
                'ruta': '/admin',
                'requiere_autenticacion': False,
                'campos_obligatorios_puesto': [
                    'area',
                    'puesto',
                    'descripcion',
                    'requisitos',
                    'conocimientos_clave'
                ]
            }
        }
    
    def _save_data(self) -> Tuple[bool, str]:
        """
        Guarda datos en vacantes.json.
        
        Returns:
            Tuple (éxito, mensaje)
        """
        try:
            with self.lock:
                with open(self.filepath, 'w', encoding='utf-8') as f:
                    json.dump(self.data, f, ensure_ascii=False, indent=2)
            return True, "Datos guardados exitosamente"
        except Exception as e:
            return False, f"Error al guardar: {str(e)}"
    
    # ==================== OPERACIONES CON ÁREAS ====================
    
    def get_areas(self) -> List[Dict]:
        """Obtiene lista de todas las áreas."""
        return self.data.get('areas', [])
    
    def get_area_by_name(self, nombre: str) -> Optional[Dict]:
        """Obtiene un área por nombre."""
        for area in self.data.get('areas', []):
            if area.get('nombre') == nombre:
                return area
        return None
    
    def add_area(self, nombre: str, descripcion: str = '', icon: str = '📁',
                 preguntas_entrevista: Dict = None) -> Tuple[bool, str, Optional[Dict]]:
        """
        Agrega una nueva área.
        
        Args:
            nombre: Nombre del área
            descripcion: Descripción de la área
            icon: Emoji o icono para la área
            preguntas_entrevista: Dict con preguntas por puesto
        
        Returns:
            Tuple (éxito, mensaje, área_creada)
        """
        # Validar que no exista el área
        if self.get_area_by_name(nombre):
            return False, f"El área '{nombre}' ya existe", None
        
        # Validar campos requeridos
        if not nombre or not nombre.strip():
            return False, "El nombre del área es requerido", None
        
        nueva_area = {
            'nombre': nombre.strip(),
            'descripcion': descripcion.strip(),
            'icon': icon,
            'preguntas_entrevista': preguntas_entrevista or {},
            'fecha_creacion': datetime.now().isoformat()
        }
        
        self.data['areas'].append(nueva_area)
        success, msg = self._save_data()
        
        if success:
            return True, f"Área '{nombre}' creada exitosamente", nueva_area
        else:
            self.data['areas'].pop()  # Revertir cambio
            return False, msg, None
    
    def update_area(self, nombre_actual: str, **kwargs) -> Tuple[bool, str]:
        """
        Actualiza los datos de un área existente.
        
        Args:
            nombre_actual: Nombre actual del área
            **kwargs: Campos a actualizar (nombre, descripcion, icon, preguntas_entrevista)
        
        Returns:
            Tuple (éxito, mensaje)
        """
        area = self.get_area_by_name(nombre_actual)
        if not area:
            return False, f"Área '{nombre_actual}' no encontrada"
        
        # Actualizar campos permitidos
        campos_permitidos = ['nombre', 'descripcion', 'icon', 'preguntas_entrevista']
        for campo in campos_permitidos:
            if campo in kwargs and kwargs[campo] is not None:
                area[campo] = kwargs[campo]
        
        area['fecha_modificacion'] = datetime.now().isoformat()
        success, msg = self._save_data()
        
        return success, msg if success else f"Error al actualizar: {msg}"
    
    def delete_area(self, nombre: str) -> Tuple[bool, str]:
        """
        Elimina un área y sus vacantes asociadas.
        
        Args:
            nombre: Nombre del área a eliminar
        
        Returns:
            Tuple (éxito, mensaje)
        """
        area = self.get_area_by_name(nombre)
        if not area:
            return False, f"Área '{nombre}' no encontrada"
        
        # Verificar si hay vacantes en esta área
        vacantes_area = [v for v in self.data.get('vacantes', []) if v.get('area') == nombre]
        if vacantes_area:
            return False, f"No se puede eliminar el área '{nombre}' porque tiene {len(vacantes_area)} vacante(s) asociada(s)"
        
        self.data['areas'].remove(area)
        success, msg = self._save_data()
        
        return success, f"Área '{nombre}' eliminada exitosamente" if success else msg
    
    # ==================== OPERACIONES CON VACANTES ====================
    
    def get_vacantes(self) -> List[Dict]:
        """Obtiene lista de todas las vacantes."""
        return self.data.get('vacantes', [])
    
    def get_vacantes_by_area(self, nombre_area: str) -> List[Dict]:
        """Obtiene vacantes de un área específica."""
        return [v for v in self.data.get('vacantes', []) if v.get('area') == nombre_area]
    
    def get_vacante_by_id(self, vacante_id: str) -> Optional[Dict]:
        """Obtiene una vacante por ID."""
        for vacante in self.data.get('vacantes', []):
            if vacante.get('id') == vacante_id:
                return vacante
        return None
    
    def _generate_vacante_id(self, area: str, puesto: str) -> str:
        """Genera un ID único para la vacante."""
        # Formato: 3 letras de área + 3 letras de puesto + número secuencial
        area_codes = area.replace('/', '').replace(' ', '')[:3].lower()
        puesto_codes = puesto.replace(' ', '')[:3].lower()
        
        # Contar vacantes con el mismo patrón
        pattern = f"{area_codes}-{puesto_codes}-"
        count = sum(1 for v in self.get_vacantes() if v.get('id', '').startswith(pattern))
        
        return f"{area_codes}-{puesto_codes}-{str(count + 1).zfill(3)}"
    
    def add_vacante(self, area: str, puesto: str, descripcion: str,
                   requisitos: List[str], conocimientos_clave: List[str],
                   **kwargs) -> Tuple[bool, str, Optional[Dict]]:
        """
        Agrega una nueva vacante.
        
        Args:
            area: Nombre del área
            puesto: Nombre del puesto
            descripcion: Descripción de la vacante
            requisitos: Lista de requisitos
            conocimientos_clave: Lista de conocimientos clave
            **kwargs: Campos opcionales (requisitos_deseados, responsabilidades, etc)
        
        Returns:
            Tuple (éxito, mensaje, vacante_creada)
        """
        # Validar que el área existe
        if not self.get_area_by_name(area):
            return False, f"El área '{area}' no existe", None
        
        # Validar campos requeridos
        if not puesto or not puesto.strip():
            return False, "El nombre del puesto es requerido", None
        if not descripcion or not descripcion.strip():
            return False, "La descripción es requerida", None
        if not requisitos or (isinstance(requisitos, list) and len(requisitos) == 0) or (isinstance(requisitos, str) and not requisitos.strip()):
            return False, "Se requiere al menos un requisito", None
        
        # Generar ID único
        vacante_id = self._generate_vacante_id(area, puesto)
        
        clean_requisitos = requisitos.strip() if isinstance(requisitos, str) else [r.strip() for r in requisitos if r.strip()]
        clean_conocimientos = conocimientos_clave.strip() if isinstance(conocimientos_clave, str) else [k.strip() for k in conocimientos_clave if k.strip()]
        
        nueva_vacante = {
            'id': vacante_id,
            'area': area,
            'puesto': puesto.strip(),
            'descripcion': descripcion.strip(),
            'requisitos': clean_requisitos,
            'conocimientos_clave': clean_conocimientos,
            'requisitos_deseados': kwargs.get('requisitos_deseados', []),
            'responsabilidades': kwargs.get('responsabilidades', []),
            'tipo': kwargs.get('tipo', 'operativo'),
            'salario_aproximado': kwargs.get('salario_aproximado', 'Por definir'),
            'requerimiento_cv': kwargs.get('requerimiento_cv', True),
            'criterios_evaluacion': kwargs.get('criterios_evaluacion', {}),
            'fecha_creacion': datetime.now().isoformat(),
            'estado': 'activa'
        }
        
        self.data['vacantes'].append(nueva_vacante)
        success, msg = self._save_data()
        
        if success:
            return True, f"Vacante '{puesto}' creada exitosamente", nueva_vacante
        else:
            self.data['vacantes'].pop()  # Revertir cambio
            return False, msg, None
    
    def update_vacante(self, vacante_id: str, **kwargs) -> Tuple[bool, str]:
        """
        Actualiza los datos de una vacante existente.
        
        Args:
            vacante_id: ID de la vacante
            **kwargs: Campos a actualizar
        
        Returns:
            Tuple (éxito, mensaje)
        """
        vacante = self.get_vacante_by_id(vacante_id)
        if not vacante:
            return False, f"Vacante con ID '{vacante_id}' no encontrada"
        
        # Campos permitidos para actualizar
        campos_permitidos = [
            'puesto', 'descripcion', 'requisitos', 'requisitos_deseados',
            'conocimientos_clave', 'responsabilidades', 'tipo',
            'salario_aproximado', 'requerimiento_cv', 'criterios_evaluacion',
            'estado'
        ]
        
        for campo in campos_permitidos:
            if campo in kwargs and kwargs[campo] is not None:
                vacante[campo] = kwargs[campo]
        
        vacante['fecha_modificacion'] = datetime.now().isoformat()
        success, msg = self._save_data()
        
        return success, msg if success else f"Error al actualizar: {msg}"
    
    def delete_vacante(self, vacante_id: str) -> Tuple[bool, str]:
        """
        Elimina una vacante.
        
        Args:
            vacante_id: ID de la vacante a eliminar
        
        Returns:
            Tuple (éxito, mensaje)
        """
        vacante = self.get_vacante_by_id(vacante_id)
        if not vacante:
            return False, f"Vacante con ID '{vacante_id}' no encontrada"
        
        self.data['vacantes'].remove(vacante)
        success, msg = self._save_data()
        
        return success, f"Vacante eliminada exitosamente" if success else msg
    
    def toggle_vacante_state(self, vacante_id: str) -> Tuple[bool, str]:
        """
        Cambia el estado de una vacante entre 'activa' e 'inactiva'.
        
        Args:
            vacante_id: ID de la vacante
        
        Returns:
            Tuple (éxito, mensaje)
        """
        vacante = self.get_vacante_by_id(vacante_id)
        if not vacante:
            return False, f"Vacante con ID '{vacante_id}' no encontrada"
        
        estado_actual = vacante.get('estado', 'activa')
        nuevo_estado = 'inactiva' if estado_actual == 'activa' else 'activa'
        vacante['estado'] = nuevo_estado
        vacante['fecha_modificacion'] = datetime.now().isoformat()
        
        success, msg = self._save_data()
        return success, f"Estado cambiado a '{nuevo_estado}'" if success else msg
    
    # ==================== OPERACIONES DE CONFIGURACIÓN ====================
    
    def get_config(self) -> Dict:
        """Obtiene configuración del sistema."""
        return self.data.get('configuracion_admin', {})
    
    def update_config(self, **kwargs) -> Tuple[bool, str]:
        """Actualiza configuración del sistema."""
        config = self.data.get('configuracion_admin', {})
        
        for key, value in kwargs.items():
            if key in config or key in ['habilitada', 'ruta', 'requiere_autenticacion', 'campos_obligatorios_puesto']:
                config[key] = value
        
        self.data['configuracion_admin'] = config
        success, msg = self._save_data()
        
        return success, msg if success else f"Error al actualizar config: {msg}"
    
    # ==================== UTILIDADES ====================
    
    def get_stats(self) -> Dict:
        """Obtiene estadísticas del sistema."""
        vacantes = self.get_vacantes()
        areas = self.get_areas()
        vacantes_activas = [v for v in vacantes if v.get('estado') == 'activa']
        
        return {
            'total_areas': len(areas),
            'total_vacantes': len(vacantes),
            'vacantes_activas': len(vacantes_activas),
            'vacantes_inactivas': len(vacantes) - len(vacantes_activas),
            'areas': {area.get('nombre'): len(self.get_vacantes_by_area(area.get('nombre'))) for area in areas}
        }
    
    def export_data(self) -> Dict:
        """Exporta todos los datos."""
        return self.data.copy()
    
    def import_data(self, data: Dict) -> Tuple[bool, str]:
        """
        Importa datos (reemplaza toda la estructura).
        
        Args:
            data: Diccionario con la estructura de datos
        
        Returns:
            Tuple (éxito, mensaje)
        """
        try:
            self.data = data
            success, msg = self._save_data()
            return success, msg if success else f"Error al importar: {msg}"
        except Exception as e:
            return False, f"Error al importar datos: {str(e)}"


# Instancia global del gestor
_manager_instance = None


def get_manager(filepath: str = 'vacantes.json') -> VacantesManager:
    """Obtiene o crea la instancia global del gestor de vacantes."""
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = VacantesManager(filepath)
    return _manager_instance
