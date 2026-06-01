# 🚀 Configuración para Railway - Guía de Despliegue

## ✅ Archivos creados/modificados para Railway

1. **requirements.txt** - Agregado `gunicorn` para servidor de producción
2. **app.py** - Modificado para usar puerto de Railway (variable de entorno `PORT`)
3. **Procfile** - Archivo de configuración de procesos
4. **Dockerfile** - Para despliegue en Railway
5. **.railway** - Configuración de entorno
6. **.env.railway** - Variables de entorno de ejemplo
7. **railway.json** - Configuración específica de Railway

## 📋 Pasos para desplegar en Railway

### Paso 1: Crear cuenta en Railway
- Ir a https://railway.app
- Registrarse con GitHub (recomendado)

### Paso 2: Conectar tu repositorio
1. En Railway Dashboard, clic en "New Project"
2. Seleccionar "Deploy from GitHub"
3. Autorizar Railway en tu cuenta de GitHub
4. Seleccionar tu repositorio

### Paso 3: Configurar variables de entorno
En el dashboard de Railway:

1. Ir a "Variables"
2. Agregar las siguientes variables:

```
FLASK_ENV=production
SECRET_KEY=genera-una-clave-segura-aqui
UPLOAD_FOLDER=/tmp/uploads
MAX_CONTENT_LENGTH=10485760
```

#### Si usas correos (opcional):
```
MAIL_FROM=tu-email@gmail.com
MAIL_PASSWORD=tu-app-password
MAIL_HOST=smtp.gmail.com
MAIL_PORT=587
MAIL_USER=tu-email@gmail.com
RH_EMAIL=email-rh@empresa.com
```

### Paso 4: Deploy automático
- Railway automáticamente:
  - Detecta que es Python
  - Instala dependencias de `requirements.txt`
  - Construye la imagen Docker
  - Inicia la aplicación

### Paso 5: Configurar dominio (opcional)
1. En Railway, ir a "Settings"
2. En "Domains", clic en "Generate Domain"
3. Railway te dará un dominio público

## 🔧 Cambios importantes realizados

### En `app.py`:
```python
# Ahora usa Puerto de Railway automáticamente
port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port, debug=False)
```

### En `requirements.txt`:
- Agregado: `gunicorn>=21.0`

### Carpeta de uploads:
- Cambiada a `/tmp/uploads` (volátil en Railway)
- Si necesitas persistencia, deberías usar:
  - Railway Volumes
  - Almacenamiento en S3/Azure Blob

## ⚠️ Consideraciones importantes

### 1. **Almacenamiento persistente**
Los archivos en `/tmp/uploads` se pierden al reiniciar. Opciones:
- Usar Railway Volumes
- Implementar S3 (AWS)
- Usar Azure Blob Storage

### 2. **Autosync de vacantes**
La sincronización automática funciona, pero:
- Se reiniciará si el contenedor se reinicia
- Considera usar un job separado en Railway para esto

### 3. **Base de datos**
Si tu proyecto usa una BD en local (JSON), migra a:
- PostgreSQL (Railway lo ofrece como servicio)
- MongoDB Atlas

### 4. **Modelo de IA**
El archivo `chatbot_model.h5` será incluido en el contenedor.

## 📊 Monitoreo en Railway

Dentro de Dashboard:
- **Logs**: Ver salida de la aplicación
- **Metrics**: CPU, memoria, solicitudes
- **Deployments**: Historial de despliegues

## 🆘 Solución de problemas

### La aplicación no inicia
```
Ver Logs en Railway Dashboard -> Deployment Logs
```

### Puerto no accesible
- Railway asigna el puerto automáticamente en `PORT`
- Verificar que `app.py` usa `0.0.0.0:PORT`

### Archivos no se guardan
- Los `/tmp` son efímeros
- Implementar persistencia con Volumes

## ✨ Próximos pasos

1. Hacer commit y push a GitHub:
```bash
git add .
git commit -m "Configuración para Railway"
git push origin main
```

2. En Railway, desplegar automáticamente
3. Monitorear logs y métricas
4. Configurar dominio personalizado (opcional)

---

¿Preguntas? Consulta: https://docs.railway.app
