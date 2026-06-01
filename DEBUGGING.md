# Guía de Solución de Problemas - Flujos de Chatbot

## Problema: Los botones no aparecen después de seleccionar una opción

### Causas Posibles y Soluciones

#### 1. El modelo no está entrenado
**Síntoma:** El bot responde pero con respuestas genéricas
**Solución:**
```bash
python training.py
```
Luego reinicia `python app.py`

#### 2. Intents.json corrupto
**Síntoma:** Errores en consola de Python
**Solución:**
```bash
python -c "import json; json.load(open('intents.json')); print('✓ OK')"
```

#### 3. JavaScript no procesando correctamente la respuesta
**Solución:**
Abre la consola del navegador (F12) y ejecuta:
```javascript
// Verifica que la respuesta contiene los marcadores
const testResponse = "¡Excelente! [MOSTRAR_AREAS]";
console.log(testResponse.toLowerCase().includes('[mostrar_areas]')); // Debería ser true
```

---

## Guía de Testing del Flujo Completo

### Flujo 1: Ver Vacantes → Empleado Operativo

**Paso 1:** Inicia el servidor
```bash
python app.py
```

**Paso 2:** Abre http://localhost:5000

**Paso 3:** Deberías ver 3 botones iniciales
- 💼 Ver Vacantes
- ❓ Información de la empresa
- 📞 Contacto

**Paso 4:** Haz clic en "Ver Vacantes"
- **Esperado:** Aparecen 4 botones de áreas
- **Si no:** Revisa la consola (F12) para errores

**Paso 5:** Selecciona una área (ej. Producción)
- **Esperado:** Aparecen 2 botones de tipo de puesto
- **Si no:** El backend no está detectando el área

**Paso 6:** Selecciona "Empleado Operativo"
- **Esperado:** Aparece pregunta sobre experiencia
- **Si no:** El flujo de entrevista está roto

**Paso 7:** Responde cada pregunta
- Las respuestas se guardan en la sesión
- Al final, deberías recibir confirmación

---

## Debug en Navegador (F12)

### 1. Ver respuestas del backend
```javascript
// En Console, ejecuta:
fetch('/chat', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({message: 'Quiero ver vacantes'})
})
.then(r => r.json())
.then(d => console.log(d))
```

**Esperado:**
```
{response: "¡Excelente! Tenemos vacantes... [MOSTRAR_AREAS]"}
```

### 2. Ver estado de la sesión
```javascript
fetch('/session-info').then(r => r.json()).then(d => console.log(d))
```

### 3. Ver qué intent se detecta
En `chatbot.py`, agrega un print temporal:
```python
def get_contextual_response(message, session_id=None):
    keyword_intent = detect_intent_keywords(message)
    print(f"Mensaje: '{message}' → Intent detectado: {keyword_intent}")  # DEBUG
    if keyword_intent:
        ...
```

---

## Verificación de Palabras Clave

### Test en Python

```python
# En terminal, ejecuta:
python -c "
from chatbot import detect_intent_keywords
print('Test 1:', detect_intent_keywords('Quiero ver vacantes'))  # Debería: vacantes
print('Test 2:', detect_intent_keywords('Producción'))          # Debería: area_produccion
print('Test 3:', detect_intent_keywords('Empleado Operativo'))  # Debería: puesto_operativo
print('Test 4:', detect_intent_keywords('Gerente'))             # Debería: puesto_gerencial
"
```

**Salida esperada:**
```
Test 1: vacantes
Test 2: area_produccion
Test 3: puesto_operativo
Test 4: puesto_gerencial
```

---

## Problema: Botones aparecen pero no responden

**Causa:** Event listeners no están conectados correctamente

**Solución:**
1. Abre F12 → Console
2. Haz clic en un botón
3. Deberías ver el mensaje "Usuario" en el chat
4. Si no pasa, revisa para errores en la consola

---

## Problema: El flujo se "rompe" en una pregunta

**Ejemplo:** Después de "¿Tienes experiencia?", no aparecen botones Sí/No

**Causa:** La respuesta del bot no contiene el marcador correcto

**Solución:**
1. En `intents.json`, verifica que el intent tenga el marcador
2. Ejemplo correcto:
```json
{
  "tag": "entrevista_experiencia_produccion",
  "responses": ["¡Muy bien! ... [PREGUNTA_TURNOS]"]
}
```

---

## Problema: Carga de PDF no funciona

**Síntoma:** Al hacer clic en 📎, no se abre el selector de archivos

**Solución:**
1. Verifica que la carpeta `uploads/` existe
2. En navegador (F12):
```javascript
document.getElementById('file-input').click(); // Debe abrir selector
```

---

## Reiniciar Completamente

Si nada funciona:

```bash
# 1. Detén el servidor (Ctrl+C)

# 2. Borra los archivos del modelo
rm chatbot_model.h5 words.pkl classes.pkl

# 3. Re-entrena
python training.py

# 4. Inicia de nuevo
python app.py

# 5. En navegador: Ctrl+Shift+R (limpia cache)
# Luego abre http://localhost:5000
```

---

## Logs Útiles

### Python (en terminal)
```python
# Agrega este debug en chatbot.py, función get_bot_response()
print(f"User: {message}")
print(f"Response: {response}")
```

### JavaScript (en F12)
```javascript
// Agrega esto en el console log del navegador
console.log('Response:', data.response);
console.log('Has [mostrar_areas]:', data.response.includes('[MOSTRAR_AREAS]'));
```

---

## Verificación Final de Estructura

```bash
# Verifica que todos los archivos existen
ls -la
# Debería mostrar:
# - app.py
# - chatbot.py
# - templates/index.html
# - intents.json
# - chatbot_model.h5 (después de entrenar)
# - uploads/ (carpeta)
```

---

## Contacto / Soporte

Si el problema persiste:
1. Verifica que Python 3.8+ está instalado: `python --version`
2. Verifica que las dependencias están instaladas: `pip list | grep -E "flask|tensorflow|nltk"`
3. Revisa que no hay conflictos de puertos: `netstat -ano | find "5000"`

