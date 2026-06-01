"""
Módulo avanzado de análisis de CV para evaluación de candidatos.

Analiza múltiples dimensiones del CV:
- Experiencia laboral
- Habilidades técnicas
- Habilidades blandas
- Certificaciones y formación
- Logros y proyectos relevantes
"""

import re
import os
from collections import Counter
from typing import Dict, List, Tuple, Any
import json

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


# Criterios de evaluación por puesto
POSITION_CRITERIA = {
    'Responsable de Seguridad y Salud en el Trabajo': {
        'technical_skills': {
            'NOM-STPS': 4,
            'Seguridad industrial': 4,
            'Equipo de protección personal': 3,
            'EPP': 3,
            'Auditorías de seguridad': 3,
            'Capacitación': 3,
            'Brigadas de emergencia': 2,
            'Primeros auxilios': 2,
            'Análisis de riesgos': 4,
            'Investigación de accidentes': 4,
        },
        'soft_skills': {
            'Liderazgo': 3,
            'Comunicación': 3,
            'Trabajo en equipo': 2,
            'Resolución de problemas': 3,
            'Organización': 2,
            'Adaptabilidad': 1,
        },
        'experience_roles': {
            'Supervisor de seguridad': 4,
            'Coordinador de seguridad': 4,
            'Responsable de seguridad': 4,
            'Inspector de seguridad': 3,
            'Técnico de seguridad': 3,
            'Encargado de seguridad': 3,
        },
        'certifications': {
            'NOM': 3,
            'Auditor': 3,
            'ISO 45001': 3,
            'OHSAS': 2,
            'Seguridad Industrial': 3,
            'Primeros Auxilios': 2,
        }
    },
    'Responsable de Control de Calidad': {
        'technical_skills': {
            'Control de calidad': 4,
            'Inspecciones de calidad': 4,
            'Auditorías internas': 3,
            'Auditorías externas': 3,
            'ISO 9001': 4,
            'Sistemas de calidad': 3,
            'Mejora continua': 3,
            'Procedimientos': 3,
            'Indicadores de calidad': 3,
            'No conformidades': 2,
            'Documentación': 2,
        },
        'soft_skills': {
            'Atención al detalle': 3,
            'Comunicación': 2,
            'Resolución de problemas': 3,
            'Liderazgo': 2,
            'Trabajo en equipo': 2,
            'Organización': 3,
        },
        'experience_roles': {
            'Responsable de control de calidad': 4,
            'Inspector de calidad': 4,
            'Supervisor de calidad': 4,
            'Coordinador de calidad': 3,
            'Auditor de calidad': 3,
            'Técnico de calidad': 2,
        },
        'certifications': {
            'ISO 9001': 4,
            'Auditor': 3,
            'IATF': 3,
            'ISO 14001': 2,
            'Calidad': 2,
        }
    },
    'Valuador': {
        'technical_skills': {
            'Valuación automotriz': 4,
            'Diagnóstico automotriz': 4,
            'Hojalatería': 3,
            'Pintura automotriz': 3,
            'Presupuestos': 3,
            'Refacciones automotrices': 3,
            'Reparación de vehículos': 3,
            'Talleres automotrices': 2,
            'Atención al cliente': 2,
            'Cotizaciones': 2,
        },
        'soft_skills': {
            'Comunicación': 3,
            'Atención al cliente': 3,
            'Resolución de problemas': 2,
            'Negociación': 2,
            'Organización': 2,
            'Adaptabilidad': 2,
        },
        'experience_roles': {
            'Valuador automotriz': 4,
            'Perito automotriz': 4,
            'Inspector de daños': 4,
            'Supervisor de taller': 3,
            'Coordinador de taller': 3,
            'Técnico automotriz': 2,
        },
        'certifications': {
            'Valuador': 3,
            'Peritaje automotriz': 3,
            'Técnico automotriz': 2,
        }
    }
}

# Palabras clave para detectar habilidades blandas
SOFT_SKILLS_KEYWORDS = {
    'Liderazgo': ['liderazgo', 'líder', 'liderar', 'conducción de equipos', 'coordinación de grupos'],
    'Comunicación': ['comunicación', 'presentaciones', 'oratoria', 'redacción', 'interpersonal'],
    'Trabajo en equipo': ['trabajo en equipo', 'equipo multidisciplinario', 'colaboración', 'cooperación'],
    'Resolución de problemas': ['resolución de problemas', 'solución de problemas', 'troubleshooting', 'análisis crítico'],
    'Organización': ['organización', 'planificación', 'gestión de tiempo', 'metodología'],
    'Adaptabilidad': ['adaptabilidad', 'flexible', 'versatilidad', 'capacidad de aprendizaje', 'iniciativa'],
    'Atención al detalle': ['atención al detalle', 'precisión', 'minuciosidad', 'calidad'],
    'Negociación': ['negociación', 'persuasión', 'cierre de ventas'],
}

# Patrones para extraer información
EXPERIENCE_PATTERN = r'(?:experiencia|laboral|trabajo|puesto|cargo|rol|position|job)[\s\w:]*(\d+)\s*(?:años|years|a\u00f1os)'
CERTIFICATION_PATTERN = r'(?:certificad|diplom|curso|capacitaci\u00f3n|training|licencia|lic\.?)[\w\s:]*([A-Z][A-Za-z\u00e1\u00e9\u00ed\u00f3\u00fa\s\-\.\d]+)'


class CVAnalyzer:
    """Analizador avanzado de CV con extracción inteligente de información."""
    
    def __init__(self, position: str = None):
        """
        Inicializa el analizador con criterios específicos del puesto.
        
        Args:
            position: Nombre del puesto para aplicar criterios específicos
        """
        self.position = position
        self.criteria = POSITION_CRITERIA.get(position, {}) if position else {}
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extrae texto completo del PDF."""
        if not PDF_AVAILABLE or not os.path.exists(pdf_path):
            return None
        
        try:
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = []
                for page in reader.pages:
                    page_text = page.extract_text() or ''
                    text.append(page_text)
            return '\n'.join(text).strip()
        except Exception as e:
            print(f"Error extrayendo PDF: {e}")
            return None
    
    def normalize_text(self, text: str) -> str:
        """Normaliza texto para búsquedas."""
        return re.sub(r'[^a-záéíóúñ0-9\s]', '', text.lower()).strip()
    
    def find_keywords_with_weights(self, text: str, keywords_dict: Dict[str, int]) -> Dict[str, List[str]]:
        """
        Busca palabras clave y devuelve resultado con peso.
        
        Returns:
            Dict con estructura {'keyword': ['peso', 'encontrado']}
        """
        normalized_text = self.normalize_text(text)
        found = {'matched': {}, 'unmatched': {}}
        
        for keyword, weight in keywords_dict.items():
            normalized_keyword = self.normalize_text(keyword)
            if normalized_keyword and normalized_keyword in normalized_text:
                found['matched'][keyword] = weight
            else:
                found['unmatched'][keyword] = weight
        
        return found
    
    def detect_experience_level(self, text: str) -> Dict[str, Any]:
        """Detecta el nivel de experiencia en el CV."""
        normalized = self.normalize_text(text)
        experience_data = {
            'years_mentioned': None,
            'roles_detected': [],
            'sectors': [],
            'seniority_level': 'Junior'
        }
        
        # Buscar años de experiencia
        years_match = re.search(r'(\d+)\s*(?:\+)?\s*(?:años|years)', normalized)
        if years_match:
            years = int(years_match.group(1))
            experience_data['years_mentioned'] = years
            if years >= 10:
                experience_data['seniority_level'] = 'Senior'
            elif years >= 5:
                experience_data['seniority_level'] = 'Mid-level'
        
        # Detectar roles (si están configurados para el puesto)
        if 'experience_roles' in self.criteria:
            roles_found = self.find_keywords_with_weights(text, self.criteria['experience_roles'])
            experience_data['roles_detected'] = list(roles_found['matched'].keys())
        
        return experience_data
    
    def detect_technical_skills(self, text: str) -> Dict[str, Any]:
        """Detecta habilidades técnicas específicas del puesto."""
        result = {
            'skills_found': [],
            'skills_missing': [],
            'skill_score': 0,
            'max_skill_score': 0,
            'details': {}
        }
        
        if 'technical_skills' not in self.criteria:
            return result
        
        skills_found = self.find_keywords_with_weights(text, self.criteria['technical_skills'])
        
        for skill, weight in skills_found['matched'].items():
            result['skills_found'].append(skill)
            result['skill_score'] += weight
            result['details'][skill] = {'status': 'found', 'weight': weight}
        
        for skill, weight in skills_found['unmatched'].items():
            result['skills_missing'].append(skill)
            result['details'][skill] = {'status': 'missing', 'weight': weight}
        
        result['max_skill_score'] = sum(self.criteria['technical_skills'].values())
        
        return result
    
    def detect_soft_skills(self, text: str) -> Dict[str, Any]:
        """Detecta habilidades blandas en el CV."""
        result = {
            'skills_found': [],
            'skills_score': 0,
            'max_soft_skills_score': 0,
            'details': {}
        }
        
        # Usar criterios del puesto si existen, sino usar criterios generales
        soft_skills_dict = self.criteria.get('soft_skills', {})
        if not soft_skills_dict:
            # Convertir SOFT_SKILLS_KEYWORDS a pesos (todos peso 2)
            soft_skills_dict = {skill: 2 for skill in SOFT_SKILLS_KEYWORDS.keys()}
        
        normalized_text = self.normalize_text(text)
        
        for skill, weight in soft_skills_dict.items():
            keywords = SOFT_SKILLS_KEYWORDS.get(skill, [skill.lower()])
            skill_found = False
            
            for keyword in keywords:
                normalized_keyword = self.normalize_text(keyword)
                if normalized_keyword and normalized_keyword in normalized_text:
                    skill_found = True
                    break
            
            if skill_found:
                result['skills_found'].append(skill)
                result['skills_score'] += weight
            
            result['details'][skill] = {'status': 'found' if skill_found else 'missing', 'weight': weight}
        
        result['max_soft_skills_score'] = sum(soft_skills_dict.values())
        
        return result
    
    def detect_certifications(self, text: str) -> Dict[str, Any]:
        """Detecta certificaciones, cursos y formación."""
        result = {
            'certifications_found': [],
            'cert_score': 0,
            'max_cert_score': 0,
            'details': {}
        }
        
        if 'certifications' not in self.criteria:
            # Búsqueda genérica de certificaciones
            cert_pattern = r'(?:certificad|diplom|curso|capacitaci\u00f3n|training|licencia|lic\.?)[\w\s:,]*([A-Z][A-Za-z\u00e1\u00e9\u00ed\u00f3\u00fa\s\-\.\(\)0-9]+)'
            matches = re.finditer(cert_pattern, text, re.IGNORECASE)
            for match in matches:
                cert = match.group(1).strip()
                if len(cert) > 3 and len(cert) < 100:
                    result['certifications_found'].append(cert)
            return result
        
        certs_found = self.find_keywords_with_weights(text, self.criteria['certifications'])
        
        for cert, weight in certs_found['matched'].items():
            result['certifications_found'].append(cert)
            result['cert_score'] += weight
            result['details'][cert] = {'status': 'found', 'weight': weight}
        
        result['max_cert_score'] = sum(self.criteria['certifications'].values())
        
        return result
    
    def detect_achievements_and_projects(self, text: str) -> Dict[str, List[str]]:
        """Detecta logros y proyectos relevantes."""
        result = {
            'projects': [],
            'achievements': [],
            'improvements': [],
            'implementations': []
        }
        
        normalized_text = self.normalize_text(text)
        
        # Palabras clave para detectar logros
        achievement_keywords = ['logro', 'resultado', 'éxito', 'alcanz', 'realiz', 'complet',
                               'implementada', 'mejorada', 'incremento', 'reducción', 'eficacia']
        
        project_keywords = ['proyecto', 'iniciativa', 'sistema', 'proceso', 'programa']
        improvement_keywords = ['mejora', 'optimización', 'reducción', 'eliminación', 'automatización']
        implementation_keywords = ['implementación', 'implementada', 'sistema', 'proceso', 'metodología']
        
        # Búsqueda simple de líneas relevantes
        lines = text.split('\n')
        for line in lines:
            normalized_line = self.normalize_text(line)
            
            if any(kw in normalized_line for kw in achievement_keywords):
                if len(line.strip()) > 10 and len(line.strip()) < 200:
                    result['achievements'].append(line.strip())
            
            if any(kw in normalized_line for kw in project_keywords):
                if len(line.strip()) > 10 and len(line.strip()) < 200:
                    result['projects'].append(line.strip())
            
            if any(kw in normalized_line for kw in improvement_keywords):
                if len(line.strip()) > 10 and len(line.strip()) < 200:
                    result['improvements'].append(line.strip())
            
            if any(kw in normalized_line for kw in implementation_keywords):
                if len(line.strip()) > 10 and len(line.strip()) < 200:
                    result['implementations'].append(line.strip())
        
        return result
    
    def analyze_cv(self, cv_text: str) -> Dict[str, Any]:
        """
        Realiza análisis completo del CV.
        
        Returns:
            Dict con análisis comprensivo en múltiples dimensiones
        """
        if not cv_text or not cv_text.strip():
            return {'error': 'CV vacío o inválido'}
        
        # Análisis de experiencia
        experience = self.detect_experience_level(cv_text)
        
        # Análisis técnico
        technical_skills = self.detect_technical_skills(cv_text)
        
        # Análisis soft skills
        soft_skills = self.detect_soft_skills(cv_text)
        
        # Análisis de certificaciones
        certifications = self.detect_certifications(cv_text)
        
        # Análisis de logros y proyectos
        achievements = self.detect_achievements_and_projects(cv_text)
        
        # Cálculo de puntuación total
        total_score = technical_skills['skill_score'] + soft_skills['skills_score'] + certifications['cert_score']
        max_total_score = technical_skills['max_skill_score'] + soft_skills['max_soft_skills_score'] + certifications['max_cert_score']
        
        compatibility_percentage = int((total_score / max_total_score * 100)) if max_total_score > 0 else 0
        
        return {
            'experience': experience,
            'technical_skills': technical_skills,
            'soft_skills': soft_skills,
            'certifications': certifications,
            'achievements': achievements,
            'compatibility': {
                'score': total_score,
                'max_score': max_total_score,
                'percentage': compatibility_percentage,
                'breakdown': {
                    'technical_skills': {
                        'score': technical_skills['skill_score'],
                        'max_score': technical_skills['max_skill_score'],
                        'percentage': int((technical_skills['skill_score'] / technical_skills['max_skill_score'] * 100)) if technical_skills['max_skill_score'] > 0 else 0
                    },
                    'soft_skills': {
                        'score': soft_skills['skills_score'],
                        'max_score': soft_skills['max_soft_skills_score'],
                        'percentage': int((soft_skills['skills_score'] / soft_skills['max_soft_skills_score'] * 100)) if soft_skills['max_soft_skills_score'] > 0 else 0
                    },
                    'certifications': {
                        'score': certifications['cert_score'],
                        'max_score': certifications['max_cert_score'],
                        'percentage': int((certifications['cert_score'] / certifications['max_cert_score'] * 100)) if certifications['max_cert_score'] > 0 else 0
                    }
                }
            },
            'strengths': technical_skills['skills_found'][:5],
            'weaknesses': technical_skills['skills_missing'][:5],
            'summary': f"Compatibilidad detectada: {compatibility_percentage}%. "
                      f"Experiencia: {experience.get('seniority_level')}. "
                      f"Habilidades técnicas: {len(technical_skills['skills_found'])}/{len(technical_skills['details'])}. "
                      f"Certificaciones: {len(certifications['certifications_found'])}."
        }
    
    def analyze_cv_from_file(self, cv_file_path: str) -> Dict[str, Any]:
        """Analiza un CV desde un archivo PDF."""
        cv_text = self.extract_text_from_pdf(cv_file_path)
        if not cv_text:
            return {'error': 'No se pudo extraer texto del PDF'}
        return self.analyze_cv(cv_text)


def calculate_final_compatibility(cv_analysis: Dict, interview_score: int, 
                                  total_interview_questions: int) -> Dict[str, Any]:
    """
    Calcula compatibilidad final combinando CV e entrevista.
    
    Pesos:
    - CV: 60%
    - Entrevista: 40%
    """
    cv_compatibility = cv_analysis.get('compatibility', {}).get('percentage', 0)
    interview_compatibility = int((interview_score / total_interview_questions * 100)) if total_interview_questions > 0 else 0
    
    # Ponderación: 60% CV, 40% entrevista
    final_score = int((cv_compatibility * 0.6) + (interview_compatibility * 0.4))
    
    return {
        'final_compatibility': final_score,
        'cv_compatibility': cv_compatibility,
        'interview_compatibility': interview_compatibility,
        'breakdown': {
            'cv_score': {
                'percentage': cv_compatibility,
                'weight': 60
            },
            'interview_score': {
                'percentage': interview_compatibility,
                'weight': 40
            }
        }
    }
