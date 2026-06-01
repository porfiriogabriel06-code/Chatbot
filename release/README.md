# Chatbot de Reclutamiento K83 FYC

Un chatbot inteligente de reclutamiento para la empresa automotriz K83 FYC, diseñado para guiar a los candidatos a través del proceso de selección.

## Características

### 1. **Flujos Conversacionales Dinámicos**
- Saludos personalizados y presentación del bot
- Información sobre la empresa
- Búsqueda de vacantes por área

### 2. **Selección de Áreas de Trabajo**
Después de seleccionar "Ver Vacantes", el usuario puede elegir entre:
- 🏭 **Producción**
- ✅ **Calidad**
- ⚙️ **Ingeniería**
- 📦 **Logística**

### 3. **Selección de Nivel de Puesto**
- 👤 **Empleado Operativo** - Roles a nivel operativo
- 👨‍💼 **Gerente / Supervisor** - Roles de liderazgo

### 4. **Flujo para Gerente / Supervisor**
- Solicita carga de CV en formato PDF
- Icono animado de clip (📎) en la barra de entrada
- Confirmación de recepción del archivo
- Preparado para análisis futuro con IA

### 5. **Entrevista Interactiva para Empleado Operativo**
Preguntas dinámicas sobre:
- Experiencia en líneas de producción
- Disponibilidad para trabajar en turnos
- Flexibilidad y disponibilidad
- Experiencia en ensamblaje o manufactura

Las respuestas se guardan en el contexto de la sesión.

### 6. **Interfaz Moderna**
- Diseño responsive y atractivo
- Botones interactivos contextuales
- Indicador de escritura (typing indicator)
- Hora y fecha actualizadas en tiempo real
- Animaciones suaves
- Soporte para carga de archivos

## Estructura del Proyecto

```
chatbot-0.1/
├── app.py                   # Servidor Flask
├── chatbot.py              # Lógica del chatbot con NLP
├── training.py             # Script para entrenar el modelo
├── intents.json            # Definición de intents y respuestas
├── requirements.txt        # Dependencias del proyecto
├── chatbot_model.h5        # Modelo neural entrenado
├── templates/
│   └── index.html          # Interfaz del chatbot
├── uploads/                # Carpeta para archivos PDF cargados
└── words.pkl, classes.pkl  # Archivos pickled del modelo
```

## Instalación

### Requisitos
- Python 3.8+
- pip

### Pasos

1. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

2. **Entrenar el modelo** (si es necesario)
```bash
python training.py
```

3. **Ejecutar la aplicación**
```bash
python app.py
```

4. **Acceder al chatbot**
Abre tu navegador en: `http://localhost:5000`

## Dependencias Principales

- **Flask**: Framework web para el servidor
- **TensorFlow/Keras**: Red neuronal para clasificación de intents
- **NLTK**: Procesamiento de lenguaje natural
- **Werkzeug**: Utilidades para Flask

Ver `requirements.txt` para la lista completa.

## Archivos Clave

### `intents.json`
Define los intents (temas) y patrones de entrada/respuesta. Estructura:
```json
{
  "intents": [
    {
      "tag": "nombre_del_intent",
      "patterns": ["patrón 1", "patrón 2"],
      "responses": ["respuesta 1", "respuesta 2"]
    }
  ]
}
```

**Intents Disponibles:**
- `saludo` - Saludos iniciales
- `presentacion` - Información del bot
- `vacantes` - Búsqueda de empleos
- `area_*` - Áreas específicas (producción, calidad, ingeniería, logística)
- `puesto_operativo` - Empleado operativo
- `puesto_gerencial` - Gerente/Supervisor
- `entrevista_*` - Preguntas de entrevista
- `disponibilidad_*` - Disponibilidad laboral
- `cargar_cv` - Carga de CV
- `ayuda` - Asistencia general
- `empresa` - Información de K83 FYC
- `contacto` - Información de contacto
- `despedida` - Cierre de conversación
- `agradecimiento` - Agradecimientos

### `chatbot.py`
Contiene la lógica del bot:
- Tokenización y procesamiento de texto
- Red neuronal para clasificación de intents
- Detección de palabras clave para mejor precisión
- Gestión de sesiones de usuario
- Manejo contextual de respuestas

### `app.py`
Servidor Flask con rutas:
- `GET /` - Página principal
- `POST /chat` - Enviar mensaje y recibir respuesta
- `POST /upload-cv` - Cargar archivo PDF
- `GET /session-info` - Información de la sesión
- `POST /reset-chat` - Reiniciar conversación

### `templates/index.html`
Interfaz del usuario con:
- Sistema de botones dinámicos
- Carga de archivos con animación
- Chat responsive
- Indicador de escritura
- Actualización de fecha y hora

## Flujos Principales

### Flujo 1: Búsqueda de Vacante - Empleado Operativo
```
Usuario: "Ver Vacantes"
  ↓
Bot: "¿En qué área?" + Botones (Producción, Calidad, etc.)
  ↓
Usuario: Selecciona área
  ↓
Bot: "¿Qué tipo de puesto?" + Botones (Operativo, Gerente)
  ↓
Usuario: Selecciona "Empleado Operativo"
  ↓
Bot: Inicia entrevista con preguntas
  ↓
Usuario: Responde preguntas (experiencia, turnos, disponibilidad, ensamblaje)
  ↓
Bot: Confirma y solicita que lo contactaremos pronto
```

### Flujo 2: Búsqueda de Vacante - Gerente/Supervisor
```
Usuario: "Ver Vacantes"
  ↓
Bot: "¿En qué área?" + Botones
  ↓
Usuario: Selecciona área
  ↓
Bot: "¿Qué tipo de puesto?" + Botones
  ↓
Usuario: Selecciona "Gerente / Supervisor"
  ↓
Bot: "Adjunta tu CV en PDF" + Botón con clip animado (📎)
  ↓
Usuario: Carga archivo PDF
  ↓
Bot: Confirma recepción y próximos pasos
```

## Personalización

### Agregar Nuevos Intents
1. Edita `intents.json`
2. Agrega un nuevo intent con `tag`, `patterns` y `responses`
3. Re-entrena el modelo: `python training.py`
4. Reinicia la aplicación

### Mejorar Detección de Palabras Clave
En `chatbot.py`, función `detect_intent_keywords()`:
```python
if any(word in message_lower for word in ['nueva_palabra_clave']):
    return 'mi_intent'
```

### Cambiar Estilos
- Edita las variables CSS en `templates/index.html`
- Busca la sección `:root` con variables como `--accent`, `--bg`, etc.

## Sesiones de Usuario

El chatbot mantiene sesiones separadas para cada usuario:
- ID único por sesión
- Rastreo de área seleccionada
- Rastreo de tipo de puesto
- Almacenamiento de respuestas de entrevista
- Registro de CV cargado

*Nota: En producción, usar una base de datos real en lugar de diccionarios en memoria.*

## Carga de Archivos

- Carpeta de destino: `uploads/`
- Extensiones permitidas: `.pdf`
- Tamaño máximo: 10MB
- Nombres de archivo: Únicos con timestamp y ID de usuario

## Mejoras Futuras

- [ ] Integración con base de datos (MongoDB, PostgreSQL)
- [ ] Análisis de CV con IA (PyPDF2, LLMs)
- [ ] Envío de correos a candidatos
- [ ] Panel administrativo para ver candidatos
- [ ] Múltiples idiomas (i18n)
- [ ] Análisis de sentimientos
- [ ] Recomendaciones personalizadas
- [ ] Integración con sistemas de RRHH

## Solución de Problemas

### Error: "No module named 'keras'"
```bash
pip install tensorflow
```

### Error: "No module named 'nltk'"
```bash
pip install nltk
```

### El bot no responde correctamente
- Verifica que `intents.json` esté correctamente formado
- Re-entrena el modelo: `python training.py`
- Revisa la consola de Flask para errores

### Los archivos no se cargan
- Verifica que la carpeta `uploads/` exista
- Confirma que el archivo sea PDF
- Revisa el tamaño (máximo 10MB)

## Contribución y Soporte

Para mejoras o reportar bugs, contacta al equipo de desarrollo de K83 FYC.

---

**Última actualización**: Mayo 2026  
**Versión**: 0.1
