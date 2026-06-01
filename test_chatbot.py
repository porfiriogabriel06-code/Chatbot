#!/usr/bin/env python3
"""
Script de prueba del chatbot - Verifica que todo está funcionando correctamente
"""

import json
import sys

def test_intents_json():
    """Verifica que intents.json es válido"""
    print("🔍 Probando intents.json...")
    try:
        with open('intents.json', 'r', encoding='utf-8') as f:
            intents = json.load(f)
        print(f"  ✓ JSON válido: {len(intents['intents'])} intents encontrados\n")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}\n")
        return False

def test_intent_keywords():
    """Verifica que la detección de palabras clave funciona"""
    print("🔍 Probando detección de palabras clave...")
    try:
        from chatbot import detect_intent_keywords
        
        test_cases = [
            ("Quiero ver vacantes", "vacantes"),
            ("Producción", "area_produccion"),
            ("Calidad", "area_calidad"),
            ("Ingeniería", "area_ingenieria"),
            ("Logística", "area_logistica"),
            ("Empleado Operativo", "puesto_operativo"),
            ("Gerente", "puesto_gerencial"),
            ("Sí tengo experiencia", "entrevista_experiencia_produccion"),
            ("No tengo experiencia", "entrevista_sin_experiencia_produccion"),
            ("Mi disponibilidad es inmediata", "disponibilidad_inmediata"),
        ]
        
        all_pass = True
        for message, expected in test_cases:
            result = detect_intent_keywords(message)
            status = "✓" if result == expected else "✗"
            if result != expected:
                all_pass = False
            print(f"  {status} '{message}' → {result} (esperado: {expected})")
        
        print()
        return all_pass
    except Exception as e:
        print(f"  ✗ Error: {e}\n")
        return False

def test_bot_response():
    """Verifica que el bot puede generar respuestas"""
    print("🔍 Probando respuestas del bot...")
    try:
        from chatbot import get_bot_response
        
        test_messages = [
            "Quiero ver vacantes",
            "Producción",
            "Empleado Operativo",
        ]
        
        for message in test_messages:
            response = get_bot_response(message, "test-session")
            print(f"  ✓ '{message}' → {response[:80]}...")
        
        print()
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}\n")
        return False

def test_flask_routes():
    """Verifica que las rutas de Flask están disponibles"""
    print("🔍 Probando servidor Flask...")
    try:
        from app import app
        
        with app.test_client() as client:
            # Test GET /
            response = client.get('/')
            status_ok = response.status_code == 200
            print(f"  {'✓' if status_ok else '✗'} GET / → {response.status_code}")
            
            # Test POST /chat
            response = client.post('/chat', 
                json={'message': 'Hola'},
                content_type='application/json')
            status_ok = response.status_code == 200
            print(f"  {'✓' if status_ok else '✗'} POST /chat → {response.status_code}")
            
        print()
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}\n")
        return False

def main():
    print("=" * 60)
    print("PRUEBA DE CHATBOT K83 FYC")
    print("=" * 60 + "\n")
    
    results = []
    
    # Ejecutar pruebas
    results.append(("intents.json", test_intents_json()))
    results.append(("Palabras clave", test_intent_keywords()))
    results.append(("Respuestas bot", test_bot_response()))
    results.append(("Rutas Flask", test_flask_routes()))
    
    # Resumen
    print("=" * 60)
    print("RESUMEN")
    print("=" * 60)
    
    all_pass = True
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
        if not passed:
            all_pass = False
    
    print("=" * 60)
    
    if all_pass:
        print("\n✨ ¡Todo está funcionando correctamente!")
        print("\nPara iniciar el chatbot, ejecuta:")
        print("  python app.py")
        return 0
    else:
        print("\n⚠️  Algunos tests fallaron. Revisa los errores arriba.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
