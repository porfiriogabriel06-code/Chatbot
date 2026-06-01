# 🚀 Railway Deployment Checklist

## ✅ Configuración completada

- [x] `requirements.txt` actualizado con Gunicorn
- [x] `app.py` configurado para usar puertos dinámicos
- [x] `Procfile` creado
- [x] `Dockerfile` optimizado para Railway
- [x] `railway.json` con configuración
- [x] `.railway` archivo de configuración
- [x] Variables de entorno documentadas
- [x] `.gitignore` optimizado

## 📝 Antes de hacer Deploy

1. **Commit de cambios**
```bash
git add .
git commit -m "🚀 Configuración de Railway"
git push origin main
```

2. **Verificar dependencias locales**
```bash
pip install -r requirements.txt
python app.py
```

3. **Ir a Railway.app**
- Crear nuevo proyecto
- Conectar con GitHub
- Seleccionar este repositorio

## 🔐 Variables de entorno necesarias

En Railway Dashboard → Settings → Variables:

| Variable | Valor | Ejemplo |
|----------|-------|---------|
| `FLASK_ENV` | production | production |
| `SECRET_KEY` | Clave fuerte | generá-una-clave-randomica |
| `UPLOAD_FOLDER` | Ruta temp | /tmp/uploads |

### Opcionales (si usas correo):
| Variable | Valor |
|----------|-------|
| `MAIL_FROM` | Tu email |
| `MAIL_PASSWORD` | App password |
| `MAIL_HOST` | smtp.gmail.com |
| `MAIL_PORT` | 587 |
| `MAIL_USER` | Tu email |
| `RH_EMAIL` | Email destino |

## 🎯 Resultado esperado

Después del deploy, tu aplicación estará en:
```
https://[tu-proyecto].railway.app
```

## 📚 Recursos

- [Documentación Railway](https://docs.railway.app)
- [Railway Python Guide](https://docs.railway.app/reference/start-here)
- [Flask + Railway](https://docs.railway.app/guides/flask)

---

**¿Preguntas?** Revisa `RAILWAY_SETUP.md`
