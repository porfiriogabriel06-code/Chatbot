# CHANGELOG - Chatbot K83 FYC

## [0.2] - Mayo 2026

### Agregado
- **Nuevos Intents de Reclutamiento**
  - 23 nuevos intents para flujos completos de reclutamiento
  - Detección mejorada de palabras clave
  - Respuestas contextuales dinámicas

- **Sistema de Flujos Conversacionales**
  - Flujo para selección de área de trabajo (Producción, Calidad, Ingeniería, Logística)
  - Flujo para selección de nivel de puesto (Operativo vs Gerente/Supervisor)
  - Entrevista interactiva para Empleado Operativo
  - Carga de CV para Gerente/Supervisor

- **Interfaz Mejorada**
  - Botones interactivos contextuales (`.interactive-button`)
  - Sistema de botones dinámicos que cambia según el contexto
  - Indicador de escritura animado (typing indicator)
  - Botón de carga de archivos con icono clip animado (📎)
  - Mejor organización visual con grid responsive

- **Gestión de Sesiones**
  - ID único por usuario/sesión
  - Rastreo de área seleccionada
  - Rastreo de tipo de puesto
  - Almacenamiento de respuestas de entrevista
  - Registro de CV cargado

- **Carga de Archivos**
  - Ruta `/upload-cv` para cargar archivos PDF
  - Validación de tipo de archivo (solo PDF)
  - Límite de tamaño de 10MB
  - Nombres de archivo seguros con timestamp e ID de usuario
  - Carpeta `uploads/` para almacenamiento

- **Mejoras en Backend**
  - Función `detect_intent_keywords()` para detección más precisa
  - Función `get_contextual_response()` para respuestas dinámicas
  - Gestión de sesiones con `init_session()`, `update_session()`, `get_session()`
  - Manejo de errores mejorado en Flask

- **Rutas API adicionales**
  - `GET /session-info` - Obtener información de la sesión
  - `POST /reset-chat` - Reiniciar la conversación
  - Manejo de errores 404 y 500

### Mejorado
- **Lógica del Chatbot**
  - Cambio de `predict_class()` para soportar threshold de confianza
  - Integración de detección de palabras clave con red neuronal
  - Respuestas más dinámicas y contextuales

- **Interfaz HTML**
  - Rediseño completo del sistema de botones
  - Mejor mensajes de bienvenida con opciones iniciales
  - Animaciones más suaves
  - Mejor manejo de estados

- **Servidor Flask**
  - Soporte para sesiones con `flask.session`
  - Mejor manejo de CORS (base para futuras integraciones)
  - Logging mejorado de errores

### Fijo
- Duplicación de función `sendMessage()` en HTML
- Mejor gestión de eventos de teclado (Enter)

### Notas de Implementación
- Los botones dinámicos se muestran usando marcadores especiales en las respuestas: `[MOSTRAR_AREAS]`, `[MOSTRAR_PUESTOS]`, `[SOLICITAR_CV]`, etc.
- Las sesiones se mantienen en memoria (usar BD en producción)
- El sistema de detección de intents usa tanto red neuronal como palabras clave para máxima precisión

### Próximas Mejoras Recomendadas
1. Integración con base de datos (MongoDB, PostgreSQL)
2. Análisis de CV con IA (PyPDF2, LLMs como OpenAI)
3. Envío de correos automáticos a candidatos
4. Panel administrativo para ver candidatos
5. Soporte para múltiples idiomas
6. Análisis de sentimientos en respuestas
7. Recomendaciones personalizadas de puestos
8. Integración con sistemas de RRHH

---

## [0.1] - Versión Inicial

### Características Base
- Chatbot con red neuronal simple
- 2 intents básicos (saludo, nombre)
- Interfaz HTML/CSS moderna
- Servidor Flask simple
