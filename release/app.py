from flask import Flask, render_template, request, jsonify, session
from werkzeug.utils import secure_filename
from chatbot import get_chatbot_response
import chatbot as chatbot_module
from vacantes_manager import get_manager as get_vacantes_manager
from vacantes_autosync import start_autosync
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env (si existe)
load_dotenv()
import os
import json
import uuid
import smtplib
from email.message import EmailMessage
from datetime import datetime

# Creamos la aplicación Flask
app = Flask(__name__)

# Configuración de seguridad y sesiones
app.secret_key = os.environ.get('SECRET_KEY', 'tu-clave-secreta-muy-fuerte-aqui')
app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_CONTENT_LENGTH', 10 * 1024 * 1024))  # Límite de 10MB para archivos
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', 'uploads')

# Crear carpeta de uploads si no existe
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Iniciar sincronización automática de vacantes
try:
    start_autosync(chatbot_module)
    print("✅ Sincronización automática de vacantes iniciada")
except Exception as e:
    print(f"⚠️ Advertencia: No se pudo iniciar la sincronización automática: {e}")

ALLOWED_EXTENSIONS = {'pdf'}


def allowed_file(filename):
    """Verifica si el archivo tiene extensión permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_user_id():
    """Obtiene o crea un ID único para el usuario."""
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    return session['user_id']


def send_recruitment_email(payload):
    """
    Envía un correo de postulación con CV adjunto.
    
    Variables de entorno requeridas:
    - MAIL_HOST: Servidor SMTP (ej: smtp.gmail.com)
    - MAIL_PORT: Puerto SMTP (ej: 587)
    - MAIL_USER: Usuario del correo
    - MAIL_PASS: Contraseña de aplicación (NO contraseña normal)
    - RH_EMAIL: Email donde recibe CVs
    - MAIL_FROM: Email remitente
    
    Args:
        payload: Dict con estructura:
        {
            'from': email remitente,
            'to': email destinatario,
            'subject': asunto,
            'text': cuerpo en texto plano,
            'html': cuerpo en HTML,
            'attachments': lista de archivos
        }
    """
    
    smtp_host = os.environ.get('SMTP_HOST') or os.environ.get('MAIL_HOST')
    smtp_port = os.environ.get('SMTP_PORT') or os.environ.get('MAIL_PORT', '587')
    smtp_user = os.environ.get('EMAIL_USER') or os.environ.get('MAIL_USER')
    smtp_pass = os.environ.get('EMAIL_PASSWORD') or os.environ.get('MAIL_PASS')
    rh_email = os.environ.get('RH_EMAIL')
    mail_from = os.environ.get('EMAIL_FROM') or os.environ.get('MAIL_FROM') or smtp_user

    # Validar configuración
    if not all([smtp_host, smtp_user, smtp_pass, rh_email]):
        missing = []
        if not smtp_host: missing.append('MAIL_HOST')
        if not smtp_user: missing.append('MAIL_USER')
        if not smtp_pass: missing.append('MAIL_PASS')
        if not rh_email: missing.append('RH_EMAIL')
        
        error_msg = f'Variables de entorno faltantes: {", ".join(missing)}'
        print(f'❌ Error de configuración de correo: {error_msg}')
        return {
            'success': False,
            'message': f'El sistema de correo no está configurado correctamente. Verifica tu archivo .env'
        }

    try:
        # Convertir puerto a int
        smtp_port = int(smtp_port)
    except (ValueError, TypeError):
        return {
            'success': False,
            'message': 'MAIL_PORT debe ser un número válido'
        }

    # Crear mensaje de correo
    msg = EmailMessage()
    msg['From'] = payload.get('from', mail_from)
    msg['To'] = rh_email  # Siempre enviar a RH_EMAIL
    msg['Subject'] = payload.get('subject', 'Nueva Postulación')
    
    # Establecer contenido
    msg.set_content(payload.get('text', ''))
    if payload.get('html'):
        msg.add_alternative(payload['html'], subtype='html')

    # Adjuntar archivos (CVs)
    attachments = payload.get('attachments', [])
    for attachment in attachments:
        try:
            filepath = attachment.get('path')
            filename = attachment.get('filename')
            
            if not os.path.exists(filepath):
                print(f'⚠️ Advertencia: Archivo no encontrado: {filepath}')
                continue
            
            with open(filepath, 'rb') as f:
                file_data = f.read()
                msg.add_attachment(
                    file_data,
                    maintype='application',
                    subtype='pdf',
                    filename=filename
                )
                print(f'✅ Archivo adjuntado: {filename}')
                
        except Exception as exc:
            print(f'❌ Error al adjuntar {attachment.get("filename")}: {exc}')

    # Enviar correo
    try:
        print(f'📧 Intentando enviar correo a {rh_email}...')
        print(f'   Host: {smtp_host}:{smtp_port}')
        
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        
        print(f'✅ Correo enviado exitosamente a {rh_email}')
        return {
            'success': True,
            'message': f'Tu CV fue enviado correctamente al área de Recursos Humanos 😊'
        }
        
    except smtplib.SMTPAuthenticationError as e:
        error_msg = 'Error de autenticación: Usuario o contraseña incorrectos'
        print(f'❌ {error_msg}')
        return {
            'success': False,
            'message': 'Error de autenticación. Verifica MAIL_USER y MAIL_PASS en .env'
        }
    except smtplib.SMTPException as e:
        error_msg = f'Error SMTP: {str(e)}'
        print(f'❌ {error_msg}')
        return {
            'success': False,
            'message': 'Error al enviar el correo. Por favor intenta más tarde.'
        }
    except Exception as e:
        error_msg = f'Error inesperado: {str(e)}'
        print(f'❌ {error_msg}')
        return {
            'success': False,
            'message': 'Error inesperado al procesar tu postulación.'
        }


@app.route('/')
def home():
    get_user_id()
    # Pasar el tamaño máximo de archivo al template para validación en el cliente
    max_bytes = app.config.get('MAX_CONTENT_LENGTH', 10 * 1024 * 1024)
    return render_template('index.html', max_upload_bytes=max_bytes)


@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        state = data.get('state', {}) or {}

        if not message:
            return jsonify({'response': 'Escribe algo para comenzar la conversación.', 'buttons': [], 'next_state': state, 'progress': {}})

        result = get_chatbot_response(message, state)
        if result.get('send_email') and result.get('email_payload'):
            email_status = send_recruitment_email(result['email_payload'])
            result['email_status'] = email_status
            if email_status['success']:
                result['response'] += ' Tu información fue enviada correctamente al área de reclutamiento 😊'
            else:
                result['response'] += f' {email_status["message"]}'

        return jsonify(result)
    except Exception as e:
        print(f'Error en /chat: {str(e)}')
        return jsonify({'response': 'Lo siento, ocurrió un error. Por favor, intenta nuevamente.', 'buttons': [], 'next_state': {}, 'progress': {}}), 500


@app.route('/upload-cv', methods=['POST'])
def upload_cv():
    try:
        if 'file' not in request.files:
            return jsonify({'response': 'No se encontró ningún archivo. Por favor, intenta nuevamente.', 'stateUpdates': {}}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'response': 'No seleccionaste ningún archivo. Por favor, intenta nuevamente.', 'stateUpdates': {}}), 400

        if not allowed_file(file.filename):
            return jsonify({'response': 'Solo se permiten archivos PDF. Por favor, carga un PDF válido.', 'stateUpdates': {}}), 400

        filename = secure_filename(f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        state_json = request.form.get('state', '{}')
        try:
            state = json.loads(state_json)
        except Exception:
            state = {}

        state['cvUploaded'] = True
        state['cvFileId'] = filename
        state['cvFilePath'] = file_path

        state_updates = {
            'cvUploaded': True,
            'cvFileId': filename,
            'cvFilePath': file_path
        }

        if state.get('selected_vacante_id'):
            from chatbot import analyze_cv_for_vacante, get_vacante_by_id
            vacante = get_vacante_by_id(state['selected_vacante_id'])
            state_updates['cvAnalysis'] = analyze_cv_for_vacante(file_path, vacante)

        response = f'✅ Perfecto, hemos recibido tu CV ({file.filename}).\n\nGracias por completar tu postulación. Tu información ha sido enviada al área de Recursos Humanos para revisión.\n\nNos pondremos en contacto contigo en breve. ¡Suerte!'

        # Evitar envíos duplicados: usar la sesión para marcar que ya se envió para esta vacante
        user_id = get_user_id()
        vac_id = state.get('selected_vacante_id') or 'unknown'
        sent_key = f'applied_{user_id}_{vac_id}'
        if session.get(sent_key):
            # Ya enviado desde esta sesión
            return jsonify({'response': 'Ya hemos recibido una postulación para esta vacante desde tu sesión. No se enviará otra copia.', 'stateUpdates': state_updates})

        if state.get('selected_vacante_id') and not session.get(sent_key):
            from chatbot import build_email_payload
            payload = build_email_payload(state, cv_file_path=file_path)
            email_status = send_recruitment_email(payload)
            if email_status['success']:
                state_updates['emailSent'] = True
                state_updates['step'] = 'completed'
                session[sent_key] = True
            else:
                response += f' {email_status["message"]}'

        return jsonify({'response': response, 'stateUpdates': state_updates})
    except Exception as e:
        print(f'Error en /upload-cv: {str(e)}')
        return jsonify({'response': 'Lo siento, hubo un error al cargar el archivo. Por favor, intenta nuevamente.', 'stateUpdates': {}}), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({'response': 'El archivo supera el tamaño máximo permitido. Por favor sube un PDF más pequeño.', 'stateUpdates': {}}), 413


@app.route('/restart', methods=['POST'])
def restart():
    """Reinicia la sesión del usuario para una nueva postulación."""
    try:
        # eliminar claves relativas a aplicaciones en la sesión
        keys = [k for k in list(session.keys()) if k.startswith('applied_')]
        for k in keys:
            session.pop(k, None)
        # conservar user_id si existe
        user_id = session.get('user_id')
        session.clear()
        if user_id:
            session['user_id'] = user_id
        return jsonify({'success': True})
    except Exception as e:
        print(f'Error en /restart: {e}')
        return jsonify({'success': False, 'message': 'No fue posible reiniciar la sesión.'}), 500

# ===================== PANEL DE ADMINISTRACIÓN =====================

@app.route('/admin', methods=['GET'])
def admin_panel():
    """Página principal del panel de administración."""
    try:
        manager = get_vacantes_manager()
        stats = manager.get_stats()
        return render_template('admin.html', stats=stats)
    except Exception as e:
        print(f'Error en /admin: {e}')
        return jsonify({'error': 'Error al cargar el panel de administración'}), 500


# =============== API ENDPOINTS PARA ADMINISTRACIÓN ===============

# ----- Endpoints de Áreas -----

@app.route('/api/admin/areas', methods=['GET'])
def api_get_areas():
    """Obtiene todas las áreas."""
    try:
        manager = get_vacantes_manager()
        areas = manager.get_areas()
        return jsonify({'success': True, 'data': areas})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/admin/areas', methods=['POST'])
def api_create_area():
    """Crea una nueva área."""
    try:
        data = request.get_json()
        manager = get_vacantes_manager()
        
        success, msg, area = manager.add_area(
            nombre=data.get('nombre'),
            descripcion=data.get('descripcion', ''),
            icon=data.get('icon', '📁'),
            preguntas_entrevista=data.get('preguntas_entrevista', {})
        )
        
        if success:
            return jsonify({'success': True, 'message': msg, 'data': area})
        else:
            return jsonify({'success': False, 'error': msg}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/admin/areas/<nombre>', methods=['PUT'])
def api_update_area(nombre):
    """Actualiza un área existente."""
    try:
        data = request.get_json()
        manager = get_vacantes_manager()
        
        success, msg = manager.update_area(
            nombre,
            nombre=data.get('nombre'),
            descripcion=data.get('descripcion'),
            icon=data.get('icon'),
            preguntas_entrevista=data.get('preguntas_entrevista')
        )
        
        if success:
            return jsonify({'success': True, 'message': msg})
        else:
            return jsonify({'success': False, 'error': msg}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/admin/areas/<nombre>', methods=['DELETE'])
def api_delete_area(nombre):
    """Elimina un área."""
    try:
        manager = get_vacantes_manager()
        success, msg = manager.delete_area(nombre)
        
        if success:
            return jsonify({'success': True, 'message': msg})
        else:
            return jsonify({'success': False, 'error': msg}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ----- Endpoints de Vacantes -----

@app.route('/api/admin/vacantes', methods=['GET'])
def api_get_vacantes():
    """Obtiene todas las vacantes."""
    try:
        manager = get_vacantes_manager()
        area = request.args.get('area')
        
        if area:
            vacantes = manager.get_vacantes_by_area(area)
        else:
            vacantes = manager.get_vacantes()
        
        return jsonify({'success': True, 'data': vacantes})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/admin/vacantes', methods=['POST'])
def api_create_vacante():
    """Crea una nueva vacante."""
    try:
        data = request.get_json()
        manager = get_vacantes_manager()
        
        success, msg, vacante = manager.add_vacante(
            area=data.get('area'),
            puesto=data.get('puesto'),
            descripcion=data.get('descripcion'),
            requisitos=data.get('requisitos', []),
            conocimientos_clave=data.get('conocimientos_clave', []),
            requisitos_deseados=data.get('requisitos_deseados', []),
            responsabilidades=data.get('responsabilidades', []),
            tipo=data.get('tipo', 'operativo'),
            salario_aproximado=data.get('salario_aproximado', 'Por definir'),
            requerimiento_cv=data.get('requerimiento_cv', True),
            criterios_evaluacion=data.get('criterios_evaluacion', {})
        )
        
        if success:
            return jsonify({'success': True, 'message': msg, 'data': vacante})
        else:
            return jsonify({'success': False, 'error': msg}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/admin/vacantes/<vacante_id>', methods=['GET'])
def api_get_vacante(vacante_id):
    """Obtiene una vacante específica."""
    try:
        manager = get_vacantes_manager()
        vacante = manager.get_vacante_by_id(vacante_id)
        
        if vacante:
            return jsonify({'success': True, 'data': vacante})
        else:
            return jsonify({'success': False, 'error': 'Vacante no encontrada'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/admin/vacantes/<vacante_id>', methods=['PUT'])
def api_update_vacante(vacante_id):
    """Actualiza una vacante existente."""
    try:
        data = request.get_json()
        manager = get_vacantes_manager()
        
        success, msg = manager.update_vacante(
            vacante_id,
            puesto=data.get('puesto'),
            descripcion=data.get('descripcion'),
            requisitos=data.get('requisitos'),
            requisitos_deseados=data.get('requisitos_deseados'),
            conocimientos_clave=data.get('conocimientos_clave'),
            responsabilidades=data.get('responsabilidades'),
            tipo=data.get('tipo'),
            salario_aproximado=data.get('salario_aproximado'),
            requerimiento_cv=data.get('requerimiento_cv'),
            criterios_evaluacion=data.get('criterios_evaluacion'),
            estado=data.get('estado')
        )
        
        if success:
            return jsonify({'success': True, 'message': msg})
        else:
            return jsonify({'success': False, 'error': msg}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/admin/vacantes/<vacante_id>', methods=['DELETE'])
def api_delete_vacante(vacante_id):
    """Elimina una vacante."""
    try:
        manager = get_vacantes_manager()
        success, msg = manager.delete_vacante(vacante_id)
        
        if success:
            return jsonify({'success': True, 'message': msg})
        else:
            return jsonify({'success': False, 'error': msg}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/admin/vacantes/<vacante_id>/toggle', methods=['POST'])
def api_toggle_vacante_state(vacante_id):
    """Cambia el estado de una vacante (activa/inactiva)."""
    try:
        manager = get_vacantes_manager()
        success, msg = manager.toggle_vacante_state(vacante_id)
        
        if success:
            return jsonify({'success': True, 'message': msg})
        else:
            return jsonify({'success': False, 'error': msg}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ----- Endpoints de Estadísticas -----

@app.route('/api/admin/stats', methods=['GET'])
def api_get_stats():
    """Obtiene estadísticas del sistema."""
    try:
        manager = get_vacantes_manager()
        stats = manager.get_stats()
        return jsonify({'success': True, 'data': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/admin/export', methods=['GET'])
def api_export_data():
    """Exporta todos los datos en JSON."""
    try:
        manager = get_vacantes_manager()
        data = manager.export_data()
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/admin/sync-status', methods=['GET'])
def api_sync_status():
    """Obtiene el estado de la sincronización automática."""
    try:
        from vacantes_autosync import get_autosync
        autosync = get_autosync(chatbot_module)
        stats = autosync.get_sync_stats()
        return jsonify({'success': True, 'data': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint no encontrado'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Error interno del servidor'}), 500


if __name__ == '__main__':
    app.run(debug=True)
