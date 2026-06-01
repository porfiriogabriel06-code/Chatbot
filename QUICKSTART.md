# Guía Rápida de Inicio - Chatbot K83 FYC

## 🚀 Inicio Rápido (3 pasos)

### 1. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 2. Entrenar el Modelo (si no existe chatbot_model.h5)
```bash
python training.py
```

### 3. Ejecutar el Servidor
```bash
python app.py
```

Luego abre: **http://localhost:5000**

---

## 📋 Flujos Disponibles

### Flujo 1: Ver Vacantes → Empleado Operativo
```
Inicio → "Ver Vacantes" → Selecciona área → "Empleado Operativo"
→ Responde preguntas → Se registran respuestas
```

**Preguntas:**
1. ¿Experiencia en líneas de producción?
2. ¿Has trabajado en turnos?
3. ¿Cuál es tu disponibilidad?
4. ¿Experiencia en ensamblaje?

### Flujo 2: Ver Vacantes → Gerente/Supervisor
```
Inicio → "Ver Vacantes" → Selecciona área → "Gerente / Supervisor"
→ Carga CV en PDF → Confirmación
```

---

## 🎨 Interacción con Botones

El chatbot muestra botones automáticamente en estos casos:

| Contexto | Botones |
|----------|---------|
| Inicio | "Ver Vacantes", "Info Empresa", "Contacto" |
| Seleccionar Área | Producción, Calidad, Ingeniería, Logística |
| Seleccionar Puesto | Empleado Operativo, Gerente/Supervisor |
| Preguntas Entrevista | Sí/No con emojis |
| Carga de CV | Botón de clip animado (📎) |

---

## 📁 Estructura de Archivos Importantes

```
chatbot-0.1/
├── intents.json              ← Edita aquí para agregar nuevas respuestas
├── app.py                    ← Servidor Flask
├── chatbot.py                ← Lógica del bot
├── training.py               ← Entrena el modelo
├── requirements.txt          ← Dependencias
├── templates/
│   └── index.html            ← Interfaz del usuario
├── uploads/                  ← Archivos PDF cargados
├── README.md                 ← Documentación completa
└── CHANGELOG.md              ← Historial de cambios
```

---

## ⚙️ Personalización Rápida

### Cambiar nombre del bot
En `templates/index.html`, busca:
```javascript
const BOT_NAME = 'DOT';
```

### Cambiar colores
En `templates/index.html`, busca:
```css
:root {
  --bg: #0f172a;
  --accent: #38bdf8;
  /* ... más variables */
}
```

### Agregar nuevo intent
En `intents.json`, agrega:
```json
{
  "tag": "tu_intent",
  "patterns": ["patrón 1", "patrón 2"],
  "responses": ["respuesta 1", "respuesta 2"]
}
```
Luego ejecuta `python training.py` y reinicia.

---

## 🔧 Debugging

### Ver logs en tiempo real
Abre la consola de navegador (F12) y mira la pestaña Console.

### Mensaje de error en backend
Mira la consola de terminal donde está corriendo `python app.py`.

### Revisar sesión del usuario
Abre: `http://localhost:5000/session-info` para ver los datos actuales.

---

## 📦 Archivos Generados Automáticamente

Después de ejecutar `training.py`:
- `chatbot_model.h5` - Modelo entrenado
- `words.pkl` - Vocabulario
- `classes.pkl` - Clases de intents

---

## 🐛 Problemas Comunes

| Problema | Solución |
|----------|----------|
| "ModuleNotFoundError" | `pip install -r requirements.txt` |
| Bot responde genéricamente | Re-entrena: `python training.py` |
| Botones no aparecen | Verifica consola (F12) para errores JS |
| No puedo cargar PDF | Verifica que sea PDF válido (máx 10MB) |
| Servidor no inicia | Cambia puerto en `app.py` línea 39 |

---

## 📞 Próximos Pasos Recomendados

1. Personaliza `intents.json` con tus preguntas específicas
2. Anade más patrones para mejor detección
3. Integra con base de datos para persistencia
4. Configura envío de correos automáticos
5. Implementa panel administrativo

---

**¿Necesitas ayuda?** Revisa `README.md` para documentación completa.
