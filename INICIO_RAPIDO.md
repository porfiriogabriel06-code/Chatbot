# 🎯 INICIO RÁPIDO - SISTEMA MEJORADO DE RECLUTAMIENTO v2.0

## 📌 Lo Nuevo en Esta Versión

✨ **Análisis avanzado de candidatos** - El sistema ahora analiza múltiples dimensiones del CV  
🎨 **Panel de administración visual** - Sin necesidad de editar archivos JSON  
⚡ **Sincronización automática** - Los cambios aparecen al instante sin reiniciar  
📊 **Reportes detallados** - Correos a RH con desglose completo de compatibilidad  

## 🚀 Primeros Pasos

### 1. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 2. Ejecutar la Aplicación
```bash
python app.py
```

### 3. Acceder al Panel de Administración
Abre tu navegador en:
```
http://localhost:5000/admin
```

## 👥 Crear Tu Primera Vacante

### Paso 1: Crear un Área (opcional si ya existe)
1. Click en **Áreas** → **Nueva Área**
2. Nombre: "Mi Primera Área"
3. Descripción: Breve descripción
4. Icono: 💼 (cualquier emoji)
5. Click **Crear Área**

### Paso 2: Crear una Vacante
1. Click en **Vacantes** → **Nueva Vacante**
2. Completa los campos:
   - **Área:** Selecciona el área que creaste
   - **Nombre del Puesto:** Ej. "Responsable de Calidad"
   - **Descripción:** Describe el puesto en detalle
   - **Requisitos:** Uno por línea (mínimo 1)
   - **Conocimientos Clave:** Uno por línea
   - **Salario:** Opcional (ej. $3,000 - $4,000)

3. Click **Crear Vacante**

### Paso 3: Ver en el Chatbot
1. Abre `http://localhost:5000`
2. Click **Ver Vacantes**
3. Tu nueva área y vacante aparecerán automáticamente

## 📊 Entender la Compatibilidad

Cuando un candidato se postula, el sistema calcula:

```
Compatibilidad Final = 60% Análisis CV + 40% Resultados Entrevista

Análisis CV incluye:
├─ Experiencia laboral
├─ Habilidades técnicas
├─ Habilidades blandas
├─ Certificaciones
└─ Logros y proyectos
```

El correo enviado a RH incluye:
- ✅ Porcentaje de compatibilidad
- ✅ Desglose detallado por componente
- ✅ Evidencias encontradas (qué detectó en el CV)
- ✅ Áreas por mejorar

## 📁 Archivos Clave

| Archivo | Función |
|---------|---------|
| `app.py` | Aplicación Flask principal |
| `chatbot.py` | Lógica del chatbot |
| `cv_analyzer.py` | **[NUEVO]** Análisis avanzado de CV |
| `vacantes_manager.py` | **[NUEVO]** Gestor CRUD de vacantes |
| `vacantes_autosync.py` | **[NUEVO]** Sincronización automática |
| `templates/admin.html` | **[NUEVO]** Panel de administración |
| `vacantes.json` | Base de datos de vacantes (actualizado) |

## 📚 Documentación Completa

Para guía detallada, consulta:
- **Administradores:** Lee `ADMIN_GUIA.md`
- **Desarrolladores:** Lee `MEJORAS_v2.md`

## 🎨 Interfaz del Panel

El panel admin incluye:

**Dashboard:**
- Estadísticas en tiempo real
- Cantidad de áreas y vacantes
- Estado activo/inactivo

**Gestión de Áreas:**
- Crear nuevas categorías
- Editar información
- Eliminar (si no tiene vacantes)

**Gestión de Vacantes:**
- Crear vacantes completas
- Editar detalles
- Cambiar estado
- Eliminar

**Configuración:**
- Exportar datos (backup)
- Ver estado de sincronización
- Información del sistema

## 🔄 Sincronización Automática

El sistema verifica cambios cada 2 segundos:
- ✅ No requiere reinicio
- ✅ No afecta a candidatos en chat
- ✅ Cambios instantáneos

Ver estado en:
```
GET /api/admin/sync-status
```

## 📧 Ejemplo de Correo a RH

Cuando se postula un candidato, RH recibe:

```
🎯 Nueva Postulación de Reclutamiento

👤 Datos del Candidato:
Nombre: Juan Pérez
Fecha: 31/05/2026

💼 Información de Postulación:
Área: Calidad y Seguridad
Puesto: Responsable de Seguridad
CV Adjunto: ✅ Sí

📊 Compatibilidad Estimada: 87%
Desglose:
  • Experiencia relacionada: 20/25
  • Habilidades técnicas: 25/30
  • Habilidades blandas: 12/15
  • Certificaciones: 10/10
  • Resultados entrevista: 20/20

💼 Experiencia detectada:
  • Supervisor de seguridad
  • Coordinador de riesgos

✅ Habilidades detectadas:
  • NOM-STPS
  • Auditorías de seguridad
  • Análisis de riesgos

⚠️ Áreas por fortalecer:
  • Investigación de accidentes
  • Primeros auxilios
```

## 🆘 Solución Rápida de Problemas

**P: Las vacantes no aparecen en el chatbot**
- R: Espera 5 segundos (sincronización automática)
- Recarga la página del chatbot

**P: No puedo crear una vacante**
- R: Asegúrate de:
  1. Haber creado el área primero
  2. Rellenar todos los campos requeridos
  3. Incluir al menos 1 requisito

**P: Se fue la luz, ¿perdí los datos?**
- R: No, todo está en `vacantes.json`
- Simplemente reinicia la app

**P: ¿Puedo usar el panel sin reiniciar la app?**
- R: Sí, la sincronización es automática
- Cambios aparecen al instante

## 📞 Próximos Pasos

1. ✅ Instala y prueba la aplicación
2. ✅ Crea 2-3 vacantes de prueba
3. ✅ Prueba el chatbot como candidato
4. ✅ Revisa los correos que recibe RH
5. ✅ Personaliza según tus necesidades

## 📖 Recursos

- **Admin Guide:** `ADMIN_GUIA.md` - Completa para administradores
- **Cambios v2.0:** `MEJORAS_v2.md` - Detalle técnico de mejoras
- **API Docs:** En `MEJORAS_v2.md` - Endpoints disponibles

---

**¿Listo? Comienza con:**
```bash
python app.py
```
Luego accede a http://localhost:5000/admin

**¡Que disfrutes el nuevo sistema!** 🎉
