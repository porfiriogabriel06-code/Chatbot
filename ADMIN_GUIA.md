# 📖 GUÍA DEL PANEL DE ADMINISTRACIÓN DE VACANTES

## Introducción

El nuevo panel de administración permite que el equipo de Recursos Humanos gestione vacantes de forma sencilla y sin conocimientos técnicos. Los cambios se aplican automáticamente sin necesidad de reiniciar la aplicación.

## 🚀 Acceso al Panel

1. **URL:** `http://localhost:5000/admin` (o tu dominio en producción)
2. **Acceso:** Sin contraseña requerida (en versión actual)
3. **Navegadores compatibles:** Chrome, Firefox, Safari, Edge

## 📋 Funcionalidades Principales

### 1. Dashboard

El dashboard muestra estadísticas en tiempo real:
- **Total de Áreas:** Número de categorías de empleo
- **Total de Vacantes:** Cantidad total de posiciones disponibles
- **Vacantes Activas:** Posiciones abiertas actualmente
- **Vacantes Inactivas:** Posiciones cerradas o pausadas

### 2. Gestión de Áreas

Las áreas son categorías de empleos. Ejemplos: "Calidad y Seguridad", "Operaciones / Taller"

#### Crear una Nueva Área

1. Ir a **Áreas** → **Nueva Área**
2. Rellenar los campos:
   - **Nombre del Área** (requerido): Ej. "Recursos Humanos"
   - **Descripción:** Breve resumen del área
   - **Icono:** Emoji o símbolo (ej: 👥, 💼, 🏭)
3. Hacer clic en **Crear Área**

#### Editar/Eliminar Áreas

- Ir a **Áreas** → **Gestionar Áreas**
- Tabla muestra todas las áreas disponibles
- Botón **Eliminar:** Solo si no hay vacantes asociadas

### 3. Gestión de Vacantes

Las vacantes son posiciones específicas dentro de un área.

#### Crear una Nueva Vacante

1. Ir a **Vacantes** → **Nueva Vacante**
2. Rellenar todos los campos requeridos:

**Información Básica:**
- **Área** (requerido): Seleccionar de las áreas disponibles
- **Nombre del Puesto** (requerido): Ej. "Supervisor de Calidad"
- **Descripción** (requerido): Descripción detallada del puesto

**Requisitos y Habilidades:**
- **Requisitos** (requerido): Uno por línea, mínimo 1
  ```
  Experiencia en control de calidad
  Conocimiento en ISO 9001
  Disponibilidad para cambios de horario
  ```
- **Conocimientos Clave** (requerido): Uno por línea
  ```
  Control de calidad
  ISO 9001
  Auditorías internas
  ```

**Información Adicional:**
- **Salario Aproximado:** Ej. "$3,000 - $4,000"
- **Tipo:** Operativo, Administrativo o Gerencial

3. Hacer clic en **Crear Vacante**

#### Gestionar Vacantes Existentes

1. Ir a **Vacantes** → **Vacantes**
2. Tabla muestra todas las vacantes:
   - **Puesto:** Nombre de la posición
   - **Área:** Categoría a la que pertenece
   - **Estado:** Activa o Inactiva

**Acciones disponibles:**
- **Desactivar/Activar:** Cambiar estado (sin eliminar datos)
- **Eliminar:** Borrar vacante permanentemente

### 4. Dashboard de Estadísticas

El panel muestra en tiempo real:
- Distribución de vacantes por área
- Cantidad de vacantes activas vs inactivas
- Últimas vacantes creadas/modificadas

## ✨ Características Especiales

### Sincronización Automática

Los cambios se aplican automáticamente:
- No requiere reinicio de la aplicación
- Los candidatos ven las vacantes actualizadas al instante
- Las preguntas de entrevista se actualizan según la vacante

### Análisis Inteligente de Candidatos

El sistema analiza automáticamente:
- **Experiencia laboral** en CV
- **Habilidades técnicas** específicas del puesto
- **Habilidades blandas** (liderazgo, comunicación, etc.)
- **Certificaciones** relevantes
- **Logros y proyectos**

La compatibilidad se calcula como:
- 60% basado en análisis del CV
- 40% basado en respuestas de entrevista

### Reportes Detallados en Correos

Cuando un candidato se postula, RH recibe un correo con:
- **Compatibilidad porcentual** (0-100%)
- **Desglose por componentes:**
  - Experiencia relacionada
  - Habilidades técnicas
  - Habilidades blandas
  - Certificaciones
  - Resultados de entrevista
- **Evidencias encontradas** (qué detectó el sistema en el CV)
- **Áreas por fortalecer** (habilidades que le faltan)

## 📊 Ejemplo: Crear una Vacante Completa

### Paso 1: Crear el Área (si no existe)

1. Áreas → Nueva Área
2. Nombre: "Logística"
3. Descripción: "Equipo de gestión de almacenes y distribución"
4. Icono: 📦
5. Crear

### Paso 2: Crear la Vacante

1. Vacantes → Nueva Vacante
2. Rellenar:

```
Área: Logística
Nombre del Puesto: Encargado de Almacén
Descripción: Responsable de gestión de inventario, 
recepción y despacho de materiales en almacén. 
Coordinación con transportistas.

Requisitos:
- Experiencia mínima 3 años en almacenes
- Conocimiento de sistemas de inventario
- Disponibilidad para horarios flexibles
- Licencia de conducir vigente
- Experiencia con montacargas

Conocimientos Clave:
- Gestión de inventarios
- Sistemas de almacenamiento
- Seguridad industrial
- Coordinación logística

Salario Aproximado: $2,500 - $3,200
Tipo: Operativo
```

3. Crear Vacante

## 🔍 Búsqueda de Vacantes en el Chatbot

Los candidatos verán automáticamente:
- La nueva área "Logística" al seleccionar área
- El puesto "Encargado de Almacén" al seleccionar puesto
- Descripción y requisitos al ver detalles
- Preguntas de entrevista específicas para esta vacante

## 💡 Consejos Prácticos

### ✅ Buenas Prácticas

1. **Requisitos claros:** Ser específico en lo que se busca
2. **Conocimientos organizados:** Listar del más al menos importante
3. **Descripción atractiva:** Incluir beneficios y oportunidades
4. **Actualizar regularmente:** Cambiar estado de vacantes cerradas a inactivas
5. **Revisión periódica:** Eliminar vacantes obsoletas

### ⚠️ Errores Comunes a Evitar

1. ❌ Crear vacantes sin área (crear área primero)
2. ❌ Requisitos muy vagos o genéricos
3. ❌ Olvidar activar vacantes después de crearlas
4. ❌ Dejar vacantes inactivas sin limpiar periódicamente

## 📱 Funciones Avanzadas

### Exportar Datos

1. Ir a **Configuración**
2. Botón **Exportar Datos**
3. Se descarga archivo `vacantes-FECHA.json` con todos los datos

Use para:
- Backup de información
- Compartir con otros sistemas
- Análisis histórico

### Recargar Datos

1. Ir a **Configuración**
2. Botón **Recargar Datos**
3. Actualiza panel con datos más recientes

## 🔧 Configuración de Desarrollo

### Variables de Entorno

Si desea cambiar rutas o configuración:

```bash
# .env
ADMIN_ROUTE=/admin  # Ruta del panel
ADMIN_AUTH_REQUIRED=false  # Autenticación
VACANTES_FILE=vacantes.json  # Archivo de datos
```

### API Endpoints

El sistema proporciona endpoints para integración:

```
GET  /api/admin/areas              # Listar áreas
POST /api/admin/areas              # Crear área
PUT  /api/admin/areas/<nombre>     # Actualizar área
DEL  /api/admin/areas/<nombre>     # Eliminar área

GET  /api/admin/vacantes           # Listar vacantes
POST /api/admin/vacantes           # Crear vacante
GET  /api/admin/vacantes/<id>      # Obtener vacante
PUT  /api/admin/vacantes/<id>      # Actualizar vacante
DEL  /api/admin/vacantes/<id>      # Eliminar vacante
POST /api/admin/vacantes/<id>/toggle # Cambiar estado

GET  /api/admin/stats              # Estadísticas
GET  /api/admin/export             # Exportar datos
GET  /api/admin/sync-status        # Estado de sincronización
```

## ❓ Preguntas Frecuentes

**P: ¿Se pierden los datos si reinicio la aplicación?**  
R: No, todos los datos se guardan en `vacantes.json` de forma automática.

**P: ¿Puedo cambiar el nombre de un área que ya tiene vacantes?**  
R: Sí, pero asegúrese de actualizar las vacantes asociadas después.

**P: ¿Cuánto tarda en aparecer una vacante nueva en el chatbot?**  
R: Menos de 5 segundos (sincronización automática).

**P: ¿Puedo volver a activar una vacante después de desactivarla?**  
R: Sí, solo haga clic en el botón "Activar".

**P: ¿Qué pasa si elimino una vacante accidentalmente?**  
R: Tendrá que crearla de nuevo. Se recomienda desactivar en lugar de eliminar.

## 📞 Soporte

Para problemas técnicos o sugerencias, contacte al equipo de desarrollo.

---

**Última actualización:** Mayo 2026  
**Versión:** 1.0.0
