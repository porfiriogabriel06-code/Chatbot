import os
import re
import random
import json
import pickle
import numpy as np
from datetime import datetime

import nltk
from nltk.stem import WordNetLemmatizer
from keras.models import load_model

from cv_analyzer import CVAnalyzer, calculate_final_compatibility

try:
    import PyPDF2
    PDF_LIB_AVAILABLE = True
except ImportError:
    PDF_LIB_AVAILABLE = False

# Cargamos el lematizador, los datos y el modelo entrenado.
lemmatizer = WordNetLemmatizer()
intents = json.loads(open('intents.json', 'r', encoding='utf-8').read())
words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))
model = load_model('chatbot_model.h5')

INTERVIEW_QUESTIONS_BY_AREA = {
    'Calidad y Seguridad': [
        '¿Tienes experiencia previa en seguridad y salud ocupacional?',
        '¿Has trabajado con normativas NOM-STPS?',
        '¿Has participado en auditorías de seguridad?',
        '¿Tienes experiencia investigando accidentes laborales?',
        '¿Has impartido capacitaciones de seguridad?',
        '¿Tienes conocimientos en análisis y prevención de riesgos?',
        '¿Tienes disponibilidad para actividades administrativas y operativas?'
    ],
    'Responsable de Control de Calidad': [
        '¿Tienes experiencia trabajando en áreas de control de calidad?',
        '¿Has realizado inspecciones de calidad en productos o procesos?',
        '¿Tienes experiencia elaborando o llenando registros de calidad?',
        '¿Has participado en auditorías internas o externas?',
        '¿Conoces sistemas de gestión de calidad o mejora continua?',
        '¿Has identificado y reportado no conformidades durante tu trabajo?',
        '¿Tienes experiencia verificando el cumplimiento de procedimientos?',
        '¿Has trabajado con indicadores o métricas de calidad?',
        '¿Tienes disponibilidad para realizar actividades de inspección y seguimiento operativo?',
        '¿Tienes experiencia elaborando reportes relacionados con calidad?',
        '¿Tienes disponibilidad para cambios en horarios o actividades según las necesidades operativas?'
    ],
    'Operaciones / Taller': [
        '¿Tienes experiencia en valuación automotriz?',
        '¿Has trabajado en talleres automotrices?',
        '¿Conoces procesos de hojalatería y pintura?',
        '¿Has elaborado presupuestos de reparación?',
        '¿Has trabajado con aseguradoras o ajustadores?',
        '¿Tienes conocimientos sobre refacciones automotrices?',
        '¿Has dado seguimiento a órdenes de trabajo o reparaciones?'
    ]
}

# Cargamos las vacantes dinámicamente desde el archivo JSON
try:
    vacantes_data = json.loads(open('vacantes.json', 'r', encoding='utf-8').read())
    vacantes = vacantes_data.get('vacantes', [])
    areas = vacantes_data.get('areas', [])
except Exception as e:
    print(f"Advertencia: No se pudo cargar vacantes.json: {e}")
    vacantes = []
    areas = []


def clean_up_sentence(sentence):
    """Tokeniza y normaliza una frase de entrada."""
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words


def bag_of_words(sentence):
    """Convierte una oración en una bolsa de palabras binaria."""
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return np.array(bag)


def predict_class(sentence, threshold=0.5):
    """Predice la etiqueta del intent más probable."""
    bow = bag_of_words(sentence)
    res = model.predict(np.array([bow]))[0]
    max_index = np.argmax(res)
    max_value = res[max_index]

    if max_value < threshold:
        return 'unknown'

    category = classes[max_index]
    return category


def get_response(tag, intents_json):
    """Busca una respuesta aleatoria dentro de los intents cargados."""
    list_of_intents = intents_json['intents']
    for intent in list_of_intents:
        if intent['tag'] == tag:
            return random.choice(intent['responses'])
    return 'Lo siento, no entiendo eso todavía. ¿Puedo ayudarte con algo más?'


def extract_candidate_name(message):
    """Extrae el nombre del candidato si se menciona con un patrón simple."""
    patterns = [r'mi nombre es ([a-záéíóúñ\- ]+)', r'soy ([a-záéíóúñ\- ]+)']
    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            return match.group(1).strip().title()
    return None


def normalize_message(message):
    """Normaliza texto para comparación."""
    return re.sub(r'[^a-z0-9áéíóúñü\s]', '', message.lower())


def get_areas_list():
    """Obtiene la lista de áreas disponibles desde vacantes.json"""
    try:
        return [area['nombre'] for area in areas]
    except:
        return ['Calidad y Seguridad', 'Operaciones / Taller']


def get_area_options():
    """Devuelve la lista de áreas con etiquetas amigables para la interfaz."""
    try:
        opciones = []
        for area in areas:
            nombre = area.get('nombre', '')
            if 'Calidad' in nombre:
                label = 'Calidad'
            elif 'Operaciones' in nombre:
                label = 'Operaciones'
            else:
                label = nombre
            opciones.append({'label': label, 'value': nombre})
        return opciones
    except Exception:
        return [
            {'label': 'Calidad', 'value': 'Calidad y Seguridad'},
            {'label': 'Operaciones', 'value': 'Operaciones / Taller'}
        ]


def get_area_label(area_name):
    """Obtiene una etiqueta de área simplificada para mostrar al usuario."""
    if area_name == 'Calidad y Seguridad':
        return 'Calidad'
    if area_name == 'Operaciones / Taller':
        return 'Operaciones'
    return area_name


def get_vacantes_by_area(area):
    """Obtiene todas las vacantes de un área específica"""
    return [v for v in vacantes if v.get('area') == area]


def get_vacante_by_id(vacante_id):
    """Obtiene una vacante por su id."""
    for vacante in vacantes:
        if vacante.get('id') == vacante_id:
            return vacante
    return None


def format_vacante_info(vacante):
    """Formatea la información de una vacante para mostrar al usuario"""
    return {
        'id': vacante.get('id'),
        'puesto': vacante.get('puesto'),
        'area': vacante.get('area'),
        'tipo': vacante.get('tipo'),
        'descripcion': vacante.get('descripcion'),
        'requisitos': vacante.get('requisitos', []),
        'requerimiento_cv': vacante.get('requerimiento_cv', True)
    }


def get_requisitos_text(vacante):
    """Retorna los requisitos en formato texto legible."""
    requisitos = vacante.get('requisitos', [])
    if not requisitos:
        return "No se especificaron requisitos particulares."
    if isinstance(requisitos, str):
        return requisitos
    return "\n".join([f"• {req}" for req in requisitos])


def match_area_from_message(message):
    """Intenta emparejar el mensaje del usuario con un área disponible"""
    normalized = normalize_message(message)
    
    keywords_map = {
        'Calidad y Seguridad': [
            'calidad', 'seguridad', 'salud ocupacional', 'ssyo', 'nom stps', 'nom-stps',
            'normativa', 'auditoría', 'auditoria', 'capacitación', 'capacitacion'
        ],
        'Operaciones / Taller': [
            'operaciones', 'taller', 'valuador', 'valuación', 'valuacion', 'hojalatería',
            'hojalateria', 'pintura', 'presupuesto', 'aseguradoras', 'ajustadores'
        ]
    }

    for area, keywords in keywords_map.items():
        if area.lower() == normalized.strip():
            return area
        if any(keyword in normalized for keyword in keywords):
            return area
    return None


def is_positive_response(message):
    """Detecta respuestas afirmativas simples."""
    normalized = normalize_message(message)
    return any(token in normalized for token in ['sí', 'si', 'claro', 'por supuesto', 'sí,', 'si,', 'vale', 'correcto', 'listo', 'ok'])


def is_negative_response(message):
    """Detecta respuestas negativas simples."""
    normalized = normalize_message(message)
    return any(token in normalized for token in ['no', 'nop', 'nunca', 'aún', 'aun'])


def is_admin_access_command(message):
    """Detecta comandos administrativos escritos en el chat."""
    normalized = message.strip().lower()
    return normalized in ['/admin', '/administrador', '/configuracion']


def get_admin_code_from_env():
    return os.environ.get('ADMIN_CODE', '').strip()


def is_admin_code_valid(code):
    admin_code = get_admin_code_from_env()
    if not admin_code:
        return False
    return code.strip() == admin_code


def extract_text_from_pdf(pdf_path):
    """Extrae texto de un CV en PDF cuando la librería está disponible."""
    if not PDF_LIB_AVAILABLE or not os.path.exists(pdf_path):
        return None

    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = []
            for page in reader.pages:
                page_text = page.extract_text() or ''
                text.append(page_text)
        return '\n'.join(text).strip()
    except Exception:
        return None


def analyze_cv_for_vacante(cv_file_path, selected_vacante):
    """
    Analiza un CV contra los requisitos específicos de la vacante seleccionada.
    Usa el módulo cv_analyzer para análisis profundo.
    """
    if not selected_vacante or not os.path.exists(cv_file_path):
        return {'error': 'CV o vacante no válidos'}
    
    puesto = selected_vacante.get('puesto', '')
    
    # Crear analizador específico para el puesto
    analyzer = CVAnalyzer(position=puesto)
    cv_analysis = analyzer.analyze_cv_from_file(cv_file_path)
    
    if 'error' in cv_analysis:
        return cv_analysis
    
    # Adaptar resultado al formato esperado
    return {
        'analysis': cv_analysis,
        'detected_keywords': cv_analysis.get('strengths', []),
        'detected_certifications': cv_analysis.get('certifications', {}).get('certifications_found', []),
        'detected_experience': cv_analysis.get('experience', {}).get('roles_detected', []),
        'compatibility_percent': cv_analysis.get('compatibility', {}).get('percentage', 0),
        'strengths': cv_analysis.get('strengths', []),
        'weaknesses': cv_analysis.get('weaknesses', []),
        'summary': cv_analysis.get('summary', 'Análisis completado'),
        'detailed_breakdown': {
            'technical_skills': cv_analysis.get('technical_skills', {}),
            'soft_skills': cv_analysis.get('soft_skills', {}),
            'certifications': cv_analysis.get('certifications', {}),
            'experience': cv_analysis.get('experience', {}),
            'achievements': cv_analysis.get('achievements', {})
        }
    }


def build_email_payload(state, cv_file_path=None):
    """
    Construye un correo detallado con análisis completo del CV para RH.
    Incluye desglose por dimensiones: experiencia, habilidades técnicas, blandas, certificaciones.
    """
    candidate_name = state.get('candidateName', 'Nombre no proporcionado')
    area = state.get('selected_area', state.get('area', 'No especificado'))
    puesto = state.get('selected_position', state.get('puestoTipo', state.get('position_type', 'No especificado')))
    interview_answers = state.get('interviewAnswers', [])
    interview_score = state.get('interview_score', 0)
    cv_analysis = state.get('cvAnalysis', {})
    fecha = datetime.now().strftime('%d/%m/%Y %H:%M')

    # Obtener información de la vacante
    vacante_info = ''
    vacante = None
    if state.get('selected_vacante_id'):
        vacante = get_vacante_by_id(state['selected_vacante_id'])
    if not vacante:
        for item in vacantes:
            if item.get('area') == area and item.get('puesto') == puesto:
                vacante = item
                break

    # Extraer análisis detallado del CV
    analysis = cv_analysis.get('analysis', {})
    technical_skills = analysis.get('technical_skills', {})
    soft_skills = analysis.get('soft_skills', {})
    certifications = analysis.get('certifications', {})
    experience = analysis.get('experience', {})
    achievements = analysis.get('achievements', {})
    compatibility_data = analysis.get('compatibility', {})
    
    # Calcular compatibilidad final
    cv_compatibility = compatibility_data.get('percentage', 0)
    total_interview_questions = len(state.get('interviewAnswers', []))
    interview_compatibility = int((interview_score / total_interview_questions * 100)) if total_interview_questions > 0 else 0
    
    # Ponderación: 60% CV + 40% Entrevista
    final_compatibility = int((cv_compatibility * 0.6) + (interview_compatibility * 0.4))

    # Construcción del desglose de compatibilidad
    breakdown_data = {
        'experiencia_relacionada': {
            'max': 25,
            'score': min(25, len(experience.get('roles_detected', [])) * 5 + (experience.get('years_mentioned', 0) * 2)),
            'evidencia': experience.get('roles_detected', [])
        },
        'habilidades_tecnicas': {
            'max': 30,
            'score': technical_skills.get('skill_score', 0),
            'evidencia': technical_skills.get('skills_found', [])[:8]
        },
        'habilidades_blandas': {
            'max': 15,
            'score': soft_skills.get('skills_score', 0),
            'evidencia': soft_skills.get('skills_found', [])[:5]
        },
        'certificaciones': {
            'max': 10,
            'score': certifications.get('cert_score', 0),
            'evidencia': certifications.get('certifications_found', [])[:5]
        },
        'resultados_entrevista': {
            'max': 20,
            'score': interview_score * 2 if interview_score < 10 else 20,
            'evidencia': [f"{q.split(': ')[1] if ': ' in q else q}" for q in interview_answers[-3:]]
        }
    }
    
    total_score = sum(item['score'] for item in breakdown_data.values())
    max_score = sum(item['max'] for item in breakdown_data.values())

    # Preparar texto del análisis
    analysis_text = f"\n\n{'='*70}\n"
    analysis_text += f"ANÁLISIS DETALLADO Y COMPATIBILIDAD\n"
    analysis_text += f"{'='*70}\n\n"
    analysis_text += f"COMPATIBILIDAD ESTIMADA: {final_compatibility}%\n"
    analysis_text += f"Desglose por componentes:\n"
    analysis_text += f"  • Análisis CV: {cv_compatibility}% (peso: 60%)\n"
    analysis_text += f"  • Resultados Entrevista: {interview_compatibility}% (peso: 40%)\n\n"

    analysis_text += "DESGLOSE DETALLADO:\n"
    analysis_text += f"  1. Experiencia relacionada: {breakdown_data['experiencia_relacionada']['score']}/{breakdown_data['experiencia_relacionada']['max']}\n"
    analysis_text += f"  2. Habilidades técnicas: {breakdown_data['habilidades_tecnicas']['score']}/{breakdown_data['habilidades_tecnicas']['max']}\n"
    analysis_text += f"  3. Habilidades blandas: {breakdown_data['habilidades_blandas']['score']}/{breakdown_data['habilidades_blandas']['max']}\n"
    analysis_text += f"  4. Certificaciones y formación: {breakdown_data['certificaciones']['score']}/{breakdown_data['certificaciones']['max']}\n"
    analysis_text += f"  5. Resultados de entrevista: {breakdown_data['resultados_entrevista']['score']}/{breakdown_data['resultados_entrevista']['max']}\n"
    analysis_text += f"─────────────────────────────────\n"
    analysis_text += f"  TOTAL: {total_score}/{max_score}\n\n"

    # Experiencia
    if breakdown_data['experiencia_relacionada']['evidencia']:
        analysis_text += "Experiencia detectada:\n"
        for exp in breakdown_data['experiencia_relacionada']['evidencia']:
            analysis_text += f"  • {exp}\n"
        if experience.get('years_mentioned'):
            analysis_text += f"  • Experiencia total mencionada: {experience.get('years_mentioned')} años\n"
        analysis_text += f"\n"

    # Habilidades técnicas
    if breakdown_data['habilidades_tecnicas']['evidencia']:
        analysis_text += "Habilidades técnicas detectadas:\n"
        for skill in breakdown_data['habilidades_tecnicas']['evidencia']:
            analysis_text += f"  • {skill}\n"
        if technical_skills.get('skills_missing'):
            analysis_text += f"\nÁreas por fortalecer (habilidades técnicas):\n"
            for skill in technical_skills.get('skills_missing', [])[:4]:
                analysis_text += f"  • {skill}\n"
        analysis_text += f"\n"

    # Habilidades blandas
    if breakdown_data['habilidades_blandas']['evidencia']:
        analysis_text += "Habilidades blandas detectadas:\n"
        for skill in breakdown_data['habilidades_blandas']['evidencia']:
            analysis_text += f"  • {skill}\n"
        analysis_text += f"\n"

    # Certificaciones
    if breakdown_data['certificaciones']['evidencia']:
        analysis_text += "Certificaciones y formación detectada:\n"
        for cert in breakdown_data['certificaciones']['evidencia']:
            analysis_text += f"  • {cert}\n"
        analysis_text += f"\n"

    # Respuestas de entrevista (últimas 3)
    if interview_answers:
        analysis_text += "Respuestas destacadas de entrevista:\n"
        for answer in interview_answers[-3:]:
            analysis_text += f"  • {answer}\n"

    text_body = (
        f"{'='*70}\n"
        f"NUEVA POSTULACIÓN DE RECLUTAMIENTO\n"
        f"{'='*70}\n\n"
        f"DATOS DEL CANDIDATO:\n"
        f"Nombre: {candidate_name}\n"
        f"Fecha de postulación: {fecha}\n\n"
        f"INFORMACIÓN DE LA POSTULACIÓN:\n"
        f"Área: {area}\n"
        f"Puesto: {puesto}\n"
        f"CV Adjunto: {'Sí' if cv_file_path else 'No'}\n"
        f"\nRESPUESTAS DE ENTREVISTA:\n"
        f"{chr(10).join(interview_answers) if interview_answers else 'Sin respuestas'}"
        f"{analysis_text}"
    )

    # HTML mejorado con desglose detallado
    compatibility_section = f"""
    <div class="compatibility-section">
        <h3 style="color: #0ea5e9; border-bottom: 2px solid #0ea5e9; padding-bottom: 10px;">Compatibilidad Estimada</h3>
        <div style="text-align: center; margin: 20px 0;">
            <div style="font-size: 48px; font-weight: bold; color: #22c55e;">{final_compatibility}%</div>
            <p style="color: #666; margin: 10px 0;">Evaluación combinada: 60% CV + 40% Entrevista</p>
        </div>
        
        <h4 style="color: #0ea5e9; margin-top: 20px;">Desglose por componentes:</h4>
        <table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
            <tr style="background-color: #f0f7ff;">
                <td style="padding: 12px; border: 1px solid #ccc; font-weight: bold;">Componente</td>
                <td style="padding: 12px; border: 1px solid #ccc; font-weight: bold; text-align: center;">Puntuación</td>
                <td style="padding: 12px; border: 1px solid #ccc; font-weight: bold; text-align: right;">Máximo</td>
            </tr>
            <tr>
                <td style="padding: 12px; border: 1px solid #ccc;">1. Experiencia relacionada</td>
                <td style="padding: 12px; border: 1px solid #ccc; text-align: center;">{breakdown_data['experiencia_relacionada']['score']}</td>
                <td style="padding: 12px; border: 1px solid #ccc; text-align: right;">{breakdown_data['experiencia_relacionada']['max']}</td>
            </tr>
            <tr style="background-color: #f9f9f9;">
                <td style="padding: 12px; border: 1px solid #ccc;">2. Habilidades técnicas</td>
                <td style="padding: 12px; border: 1px solid #ccc; text-align: center;">{breakdown_data['habilidades_tecnicas']['score']}</td>
                <td style="padding: 12px; border: 1px solid #ccc; text-align: right;">{breakdown_data['habilidades_tecnicas']['max']}</td>
            </tr>
            <tr>
                <td style="padding: 12px; border: 1px solid #ccc;">3. Habilidades blandas</td>
                <td style="padding: 12px; border: 1px solid #ccc; text-align: center;">{breakdown_data['habilidades_blandas']['score']}</td>
                <td style="padding: 12px; border: 1px solid #ccc; text-align: right;">{breakdown_data['habilidades_blandas']['max']}</td>
            </tr>
            <tr style="background-color: #f9f9f9;">
                <td style="padding: 12px; border: 1px solid #ccc;">4. Certificaciones y formación</td>
                <td style="padding: 12px; border: 1px solid #ccc; text-align: center;">{breakdown_data['certificaciones']['score']}</td>
                <td style="padding: 12px; border: 1px solid #ccc; text-align: right;">{breakdown_data['certificaciones']['max']}</td>
            </tr>
            <tr>
                <td style="padding: 12px; border: 1px solid #ccc;">5. Resultados de entrevista</td>
                <td style="padding: 12px; border: 1px solid #ccc; text-align: center;">{breakdown_data['resultados_entrevista']['score']}</td>
                <td style="padding: 12px; border: 1px solid #ccc; text-align: right;">{breakdown_data['resultados_entrevista']['max']}</td>
            </tr>
            <tr style="background-color: #e8f4f8; font-weight: bold;">
                <td style="padding: 12px; border: 2px solid #0ea5e9;">TOTAL</td>
                <td style="padding: 12px; border: 2px solid #0ea5e9; text-align: center; color: #0ea5e9;">{total_score}</td>
                <td style="padding: 12px; border: 2px solid #0ea5e9; text-align: right; color: #0ea5e9;">{max_score}</td>
            </tr>
        </table>
    </div>
    """

    # Secciones de evidencia
    evidence_sections = ""
    
    if breakdown_data['experiencia_relacionada']['evidencia']:
        evidence_sections += f"""
    <div class="section">
        <h4 style="color: #0ea5e9;">Experiencia Detectada</h4>
        <ul style="list-style: none; padding-left: 0;">
            {"".join([f'<li style="padding: 6px 0;">• {exp}</li>' for exp in breakdown_data['experiencia_relacionada']['evidencia']])}
        </ul>
    </div>
    """

    if breakdown_data['habilidades_tecnicas']['evidencia']:
        evidence_sections += f"""
    <div class="section">
        <h4 style="color: #0ea5e9;">Habilidades Técnicas Detectadas</h4>
        <ul style="list-style: none; padding-left: 0;">
            {"".join([f'<li style="padding: 6px 0;">• {skill}</li>' for skill in breakdown_data['habilidades_tecnicas']['evidencia']])}
        </ul>
    </div>
    """

    if breakdown_data['habilidades_blandas']['evidencia']:
        evidence_sections += f"""
    <div class="section">
        <h4 style="color: #0ea5e9;">Habilidades Blandas Detectadas</h4>
        <ul style="list-style: none; padding-left: 0;">
            {"".join([f'<li style="padding: 6px 0;">• {skill}</li>' for skill in breakdown_data['habilidades_blandas']['evidencia']])}
        </ul>
    </div>
    """

    if breakdown_data['certificaciones']['evidencia']:
        evidence_sections += f"""
    <div class="section">
        <h4 style="color: #0ea5e9;">Certificaciones y Formación Detectada</h4>
        <ul style="list-style: none; padding-left: 0;">
            {"".join([f'<li style="padding: 6px 0;">• {cert}</li>' for cert in breakdown_data['certificaciones']['evidencia']])}
        </ul>
    </div>
    """

    if technical_skills.get('skills_missing'):
        evidence_sections += f"""
    <div class="section" style="background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107;">
        <h4 style="color: #856404; margin-top: 0;">Áreas por fortalecer (habilidades técnicas)</h4>
        <ul style="list-style: none; padding-left: 0; color: #856404;">
            {"".join([f'<li style="padding: 6px 0;">• {skill}</li>' for skill in technical_skills.get('skills_missing', [])[:5]])}
        </ul>
    </div>
    """

    html_body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f5f5; }}
            .container {{ background-color: white; padding: 30px; border-radius: 8px; max-width: 800px; margin: 0 auto; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            h2 {{ color: #333; border-bottom: 3px solid #0ea5e9; padding-bottom: 15px; margin-bottom: 25px; }}
            h3 {{ color: #0ea5e9; }}
            h4 {{ color: #666; margin-top: 15px; margin-bottom: 10px; }}
            .section {{ margin-top: 20px; }}
            .section-title {{ font-weight: bold; color: #0ea5e9; margin-top: 15px; margin-bottom: 10px; font-size: 14px; }}
            p {{ margin: 5px 0; line-height: 1.7; color: #333; }}
            strong {{ color: #333; }}
            ul {{ margin: 10px 0; padding-left: 20px; }}
            li {{ margin: 5px 0; }}
            .compatibility-section {{ background-color: #e8f4f8; padding: 20px; border-radius: 8px; margin: 20px 0; border: 2px solid #0ea5e9; }}
            table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
            td {{ padding: 10px; border: 1px solid #ddd; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Nueva Postulación de Reclutamiento</h2>
            
            <div class="section">
                <strong>Datos del candidato:</strong>
                <p>Nombre: {candidate_name}</p>
                <p>Fecha: {fecha}</p>
            </div>
            
            <div class="section">
                <strong>Información de postulación:</strong>
                <p>Área: {area}</p>
                <p>Puesto: {puesto}</p>
                <p>CV Adjunto: {'Sí' if cv_file_path else 'No'}</p>
            </div>
            
            <div class="section">
                <strong>Respuestas de entrevista:</strong>
                <p>{'<br>'.join(interview_answers) if interview_answers else 'Sin respuestas registradas'}</p>
            </div>
            
            {compatibility_section}
            {evidence_sections}
            
            <div class="section" style="background-color: #f0f7ff; padding: 15px; border-left: 4px solid #0ea5e9; margin-top: 25px;">
                <p><strong>Observaciones del sistema:</strong></p>
                <p>El candidato ha completado la postulación inicial. La compatibilidad de {final_compatibility}% se basa en el análisis integral del CV y las respuestas de entrevista. Se recomienda revisar la evidencia detectada para una evaluación más profunda.</p>
            </div>
        </div>
    </body>
    </html>
    """

    email_payload = {
        'from': os.environ.get('MAIL_FROM', 'reclutamiento@k83fyc.com'),
        'to': os.environ.get('RH_EMAIL', 'reclutamiento@k83fyc.com'),
        'subject': f'[K83 FYC] Nueva Postulación - {candidate_name} ({puesto}) - Compatibilidad: {final_compatibility}%',
        'text': text_body,
        'html': html_body,
        'attachments': []
    }

    if cv_file_path and os.path.exists(cv_file_path):
        email_payload['attachments'].append({
            'filename': os.path.basename(cv_file_path),
            'path': cv_file_path
        })

    return email_payload


def get_vacante_by_message(message, area=None):
    """Resuelve una vacante por id o por nombre del puesto."""
    vacante = get_vacante_by_id(message.strip())
    if vacante:
        return vacante

    normalized = normalize_message(message)
    for vacante in vacantes:
        if area and vacante.get('area') != area:
            continue
        puesto_normalized = normalize_message(vacante.get('puesto', ''))
        if puesto_normalized == normalized or normalized in puesto_normalized:
            return vacante
    return None


def get_chatbot_response(message, state=None):
    """
    Genera la respuesta del bot con estado conversacional simplificado.
    
    Estados principales:
    - None/inicio: Usuario acaba de llegar
    - area_selection: Esperando selección de área
    - position_selection: Esperando selección de puesto
    - profile_confirmation: Confirmar iniciar entrevista
    - interview: En proceso de entrevista
    - cv_upload: Esperando carga de CV
    - completed: Postulación completada
    """

    if not message or not message.strip():
        return {
            'response': 'Por favor, escribe tu consulta para que pueda ayudarte.',
            'buttons': [],
            'next_state': state or {},
            'progress': {},
            'send_email': False,
            'email_payload': None,
            'show_upload_button': False
        }

    state = state or {}
    next_state = dict(state)
    response = ''
    buttons = []
    progress = {}
    show_upload_button = False

    normalized = normalize_message(message)

    candidate_name = extract_candidate_name(message)
    if candidate_name:
        next_state['candidateName'] = candidate_name

    # Comandos administrativos desde el chat
    if is_admin_access_command(message):
        next_state['admin_step'] = 'request_code'
        next_state['admin_access_attempts'] = 0
        response = 'Acceso Administrativo\n\nIngresa tu código de acceso.'
        return {
            'response': response,
            'buttons': [],
            'next_state': next_state,
            'progress': progress,
            'send_email': False,
            'email_payload': None,
            'show_upload_button': False
        }

    if next_state.get('admin_step') == 'request_code':
        if is_admin_code_valid(message):
            next_state.pop('admin_step', None)
            next_state['admin_access_granted'] = True
            response = 'Acceso concedido. Redirigiendo al panel administrativo...'
            return {
                'response': response,
                'buttons': [],
                'next_state': next_state,
                'progress': progress,
                'send_email': False,
                'email_payload': None,
                'show_upload_button': False,
                'redirect_to_admin': True,
                'redirect_url': '/admin'
            }

        next_state['admin_access_attempts'] = next_state.get('admin_access_attempts', 0) + 1
        response = 'Código incorrecto. Intenta nuevamente.'
        return {
            'response': response,
            'buttons': [],
            'next_state': next_state,
            'progress': progress,
            'send_email': False,
            'email_payload': None,
            'show_upload_button': False
        }

    if next_state.get('current_flow') != 'vacantes' and ((not next_state.get('flow_started') and not any(trigger in normalized for trigger in ['vacante', 'empleo', 'trabajo', 'puesto', 'ver vacantes', 'empresa', 'informacion', 'información', 'contacto', 'recursos humanos', 'rh']))
            or 'hola' in normalized or 'inicio' in normalized):
        response = (
            'Hola. Bienvenido a K83 FYC.\n\n'
            'Estamos enfocados en vacantes reales para reclutamiento especializado. '
            '¿Qué te gustaría hacer hoy?'
        )
        next_state['flow_started'] = True
        next_state['current_flow'] = None
        next_state['step'] = None
        buttons = [
            {'label': 'Ver vacantes', 'value': 'Ver vacantes'},
            {'label': 'Información de la empresa', 'value': 'Información de la empresa'},
            {'label': 'Contacto con recursos humanos', 'value': 'Contacto con recursos humanos'}
        ]

    elif 'vacante' in normalized or 'empleo' in normalized or 'trabajo' in normalized or 'puesto' in normalized or 'ver vacantes' in normalized:
        response = 'Tenemos vacantes disponibles. ¿En cuál de estas áreas te gustaría postularte?\n\n'
        next_state['current_flow'] = 'vacantes'
        next_state['flow_started'] = True
        next_state['step'] = 'area_selection'
        next_state.pop('selected_area', None)
        next_state.pop('selected_vacante_id', None)
        next_state.pop('selected_position', None)
        next_state.pop('interview_question_index', None)
        next_state.pop('interviewAnswers', None)
        next_state.pop('interview_score', None)
        next_state.pop('compatibility_percent', None)
        next_state.pop('cvUploaded', None)
        next_state.pop('cvFilePath', None)
        next_state.pop('emailSent', None)

        buttons = get_area_options()

    elif next_state.get('current_flow') == 'vacantes' and next_state.get('step') == 'area_selection':
        matched_area = match_area_from_message(message)
        if matched_area:
            vacantes_area = get_vacantes_by_area(matched_area)
            if vacantes_area:
                next_state['selected_area'] = matched_area
                next_state['step'] = 'position_selection'
                response = f"Has elegido el área de {get_area_label(matched_area)}.\n\n"
                response += 'Puestos disponibles en esta área:\n'
                for vacante in vacantes_area:
                    response += f"- {vacante.get('puesto')}\n"
                response += '\nSelecciona el puesto que te interesa para ver su descripción y requisitos.'
                buttons = [{'label': vacante.get('puesto'), 'value': vacante.get('id')} for vacante in vacantes_area]
            else:
                response = 'Lo siento, por el momento no hay vacantes en esa área. Por favor elige otra opción.'
                buttons = get_area_options()
        else:
            response = 'No reconocí esa área. Por favor elige una de las vacantes reales disponibles.'
            buttons = get_area_options()

    elif next_state.get('current_flow') == 'vacantes' and next_state.get('step') == 'position_selection':
        selected_vacante = get_vacante_by_message(message, area=next_state.get('selected_area'))
        if selected_vacante:
            next_state['selected_vacante_id'] = selected_vacante.get('id')
            next_state['selected_position'] = selected_vacante.get('puesto')
            next_state['step'] = 'profile_confirmation'
            response = (
                f"Has seleccionado: {selected_vacante.get('puesto')}\n\n"
                f"Descripción: {selected_vacante.get('descripcion')}\n\n"
                f"Requisitos:\n{get_requisitos_text(selected_vacante)}\n\n"
                "¿Deseas iniciar tu postulación para este puesto?"
            )
            buttons = [
                {'label': 'Sí, iniciar postulación', 'value': 'Sí iniciar postulación'},
                {'label': 'No por ahora', 'value': 'No por ahora'}
            ]
        else:
            response = 'No encontré ese puesto en el área seleccionada. Por favor elige uno de los puestos disponibles.'
            buttons = [{'label': vacante.get('puesto'), 'value': vacante.get('id')} for vacante in get_vacantes_by_area(next_state.get('selected_area'))]

    elif next_state.get('current_flow') == 'vacantes' and next_state.get('step') == 'profile_confirmation':
        if is_positive_response(message):
            next_state['step'] = 'interview'
            next_state['interview_question_index'] = 0
            next_state['interview_score'] = 0
            next_state['interviewAnswers'] = []
            # Usar el puesto seleccionado para obtener las preguntas correctas
            position = next_state.get('selected_position')
            questions = INTERVIEW_QUESTIONS_BY_AREA.get(position, INTERVIEW_QUESTIONS_BY_AREA.get(next_state.get('selected_area'), []))
            response = f"Iniciamos la entrevista. Pregunta 1 de {len(questions)}:\n\n{questions[0]}"
            buttons = [
                {'label': 'Sí', 'value': 'Sí'},
                {'label': 'No', 'value': 'No'}
            ]
        elif is_negative_response(message):
            response = (
                'Entendido. Cuando quieras continúo con la entrevista o puedes revisar otra vacante. '
                'Escribe "Ver vacantes" para ver las áreas disponibles nuevamente.'
            )
            buttons = [
                {'label': 'Ver vacantes', 'value': 'Ver vacantes'},
                {'label': 'Otra pregunta', 'value': 'Otra pregunta'}
            ]
        else:
            response = 'Por favor responde sí o no: ¿Deseas iniciar tu postulación para este puesto?'
            buttons = [
                {'label': 'Sí', 'value': 'Sí'},
                {'label': 'No', 'value': 'No'}
            ]

    elif next_state.get('current_flow') == 'vacantes' and next_state.get('step') == 'interview':
        # Usar el puesto seleccionado para obtener las preguntas correctas
        position = next_state.get('selected_position')
        questions = INTERVIEW_QUESTIONS_BY_AREA.get(position, INTERVIEW_QUESTIONS_BY_AREA.get(next_state.get('selected_area'), []))
        index = next_state.get('interview_question_index', 0)
        answers = next_state.get('interviewAnswers', [])

        if index < len(questions) and len(answers) == index:
            answer_text = 'Sí' if is_positive_response(message) else 'No'
            next_state.setdefault('interviewAnswers', []).append(
                f"Pregunta {index + 1}: {questions[index]} - {answer_text}"
            )
            if answer_text == 'Sí':
                next_state['interview_score'] = next_state.get('interview_score', 0) + 1

            index += 1
            next_state['interview_question_index'] = index

        if index < len(questions):
            response = f"Pregunta {index + 1} de {len(questions)}:\n\n{questions[index]}"
            buttons = [
                {'label': 'Sí', 'value': 'Sí'},
                {'label': 'No', 'value': 'No'}
            ]
        else:
            total_questions = len(questions)
            score = next_state.get('interview_score', 0)
            next_state['compatibility_percent'] = score
            next_state['step'] = 'cv_upload'
            next_state['interview_question_index'] = None
            response = (
                "Gracias por completar la entrevista inicial.\n\n"
                "Ahora necesitamos tu CV en formato PDF para continuar con la postulación. "
                "Tu información será enviada al área de Recursos Humanos para su revisión. "
                "Utiliza el botón de adjuntar CV cuando esté disponible."
            )
            buttons = []

    elif next_state.get('current_flow') == 'vacantes' and next_state.get('step') == 'cv_upload':
        response = (
            'Estamos listos para recibir tu CV en formato PDF. Por favor sube el archivo y con gusto revisaremos tu postulación. '
            'Puedes adjuntar tu CV en formato PDF usando el botón de carga en la barra de chat.'
        )
        buttons = []

    elif 'empresa' in normalized or 'informacion' in normalized or 'información' in normalized:
        response = (
            'K83 FYC\n\n'
            'Somos un equipo especializado en reclutamiento para áreas reales y roles específicos. '
            'Actualmente nuestras vacantes activas son Calidad y Seguridad y Operaciones / Taller.\n\n'
            '¿Te gustaría ver las vacantes disponibles?'
        )
        buttons = [
            {'label': 'Ver vacantes', 'value': 'Ver vacantes'},
            {'label': 'Otra consulta', 'value': 'Otra consulta'}
        ]

    elif 'contacto' in normalized or 'recursos humanos' in normalized or 'rh' in normalized:
        response = (
            'Contacto con Recursos Humanos\n\n'
            'Si tienes dudas sobre el proceso de selección o necesitas ayuda con tu postulación, estamos para apoyarte.\n\n'
            '¿Deseas ver las vacantes disponibles?'
        )
        buttons = [
            {'label': 'Ver vacantes', 'value': 'Ver vacantes'},
            {'label': 'Otra pregunta', 'value': 'Tengo otra pregunta'}
        ]

    else:
        tag = predict_class(message)
        response = get_response(tag, intents)
        buttons = [
            {'label': 'Ver vacantes', 'value': 'Ver vacantes'},
            {'label': 'Información', 'value': 'Información'},
            {'label': 'Contacto', 'value': 'Contacto'}
        ]

    progress['areaSelected'] = bool(next_state.get('selected_area'))
    progress['positionSelected'] = bool(next_state.get('selected_position'))
    progress['interviewCompleted'] = next_state.get('step') == 'cv_upload' or next_state.get('step') == 'completed'
    progress['cvAttached'] = bool(next_state.get('cvUploaded'))
    progress['emailSent'] = bool(next_state.get('emailSent'))
    progress['compatibilityPercent'] = next_state.get('compatibility_percent', 0)

    show_upload_button = next_state.get('current_flow') == 'vacantes' and next_state.get('step') == 'cv_upload' and not next_state.get('cvUploaded')

    return {
        'response': response,
        'buttons': buttons,
        'next_state': next_state,
        'progress': progress,
        'send_email': False,
        'email_payload': None,
        'show_upload_button': show_upload_button
    }



def get_bot_response(message):
    """Función pública simple de compatibilidad."""
    if not message or not message.strip():
        return 'Por favor, escribe algo para que pueda ayudarte.'
    tag = predict_class(message)
    return get_response(tag, intents)


def main():
    """Permite ejecutar el bot en consola si se ejecuta directamente."""
    print('Bot iniciado. Escribe un mensaje y presiona Enter. Ctrl+C para salir.')
    while True:
        try:
            message = input('Tú: ')
        except EOFError:
            break
        if not message:
            continue
        response = get_bot_response(message)
        print('Bot:', response)


if __name__ == '__main__':
    main()
