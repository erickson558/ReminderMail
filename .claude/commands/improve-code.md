# /improve-code — Mejorar el Proyecto como Senior Engineer

Actúa como un **ingeniero senior de software especializado en Python**, refactorización,
arquitectura de aplicaciones de escritorio y mejora de sistemas existentes.

## ⚠️ REGLAS CRÍTICAS (OBLIGATORIAS)

1. **NO romper funcionalidades existentes**
   - El sistema ya funciona: auto-envío al inicio, auto-cierre en 60s, COM y SMTP.
   - No elimines ni cambies comportamientos existentes.
   - Mantén compatibilidad total con config.json existente.

2. **Primero analiza, luego actúa**
   Antes de generar código:
   - Explica qué hace el proyecto actualmente
   - Identifica problemas y oportunidades de mejora
   - Señala riesgos de refactorización
   - **NO generes código sin análisis previo.**

3. **No sobre-ingenierizar**
   - Si algo funciona bien → no lo toques
   - Si tienes dudas → haz preguntas antes de modificar
   - Tres líneas similares no necesitan una abstracción

## 🏗️ ARQUITECTURA (ya aplicada, mantener)

- `src/config_manager.py` → backend config
- `src/email_service.py`  → backend email
- `src/main_window.py`    → frontend GUI
- `locales/`              → i18n
- La GUI NO debe contener lógica compleja de negocio

## 🎨 INTERFAZ GRÁFICA

- Mantener funcionalidad actual
- Mejorar si es posible sin romper comportamiento
- La GUI NO se congela (usar threads)
- Soporte multi-idioma (ya implementado con locales/)

## 🧠 ÁREAS DE MEJORA A EVALUAR

1. Refactorización del código (duplicidades, nomenclatura)
2. Mejora en manejo de errores (mensajes más claros)
3. Logging adecuado (agregar logs a email_service.py)
4. Validación de email format antes de agregar a la lista
5. Mejora en legibilidad y organización
6. Preparación para escalabilidad futura

## 📦 AL FINALIZAR CUALQUIER MEJORA

Ejecutar siempre en este orden:
1. Actualizar `SDD.md` con los cambios de especificación
2. Compilar el ejecutable: `pyinstaller reminder.spec`
3. Commit y push: `/github-push`

## 📋 ENTREGABLES OBLIGATORIOS (en este orden)

1. **Análisis del proyecto**: Qué hace actualmente, problemas detectados, riesgos
2. **Plan de mejora**: Qué se va a cambiar, por qué, impacto
3. **Código completo actualizado**: NO fragmentos, TODO funcional
4. **Instrucciones de compilación**: Cómo generar el .exe con reminder.ico
