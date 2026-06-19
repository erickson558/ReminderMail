# /comment-code — Agregar Comentarios Detallados al Código

Revisa y agrega comentarios educativos y profesionales a todos los archivos Python del proyecto.

## Archivos a comentar

- `main.py`
- `src/config_manager.py`
- `src/email_service.py`
- `src/main_window.py`

## Estilo de comentarios

### Encabezado de módulo
```python
# =============================================================================
# nombre_archivo.py - Título del módulo
# Responsabilidad: Descripción clara de qué hace este módulo y por qué existe.
# =============================================================================
```

### Docstrings de funciones/métodos
```python
def nombre_funcion(param1: tipo, param2: tipo) -> tipo_retorno:
    """
    Descripción concisa de qué hace la función.

    Explicar el WHY (por qué existe) más que el WHAT (qué hace, que ya se ve en el código).

    Args:
        param1: Descripción del parámetro
        param2: Descripción del parámetro

    Returns:
        Descripción del valor retornado

    Raises:
        ExceptionType: Cuándo se lanza esta excepción
    """
```

### Secciones dentro de funciones largas
```python
    # ── Validar campos obligatorios antes de conectar ──
    ...
    
    # ── Conectar al servidor y autenticar ──
    ...
```

### Comentarios inline (solo para lógica no obvia)
```python
    server.ehlo()      # Presentarse al servidor (requerido por RFC 2821)
    server.starttls()  # Negociar cifrado TLS para la sesión
```

## Reglas

1. **Idioma**: Español (consistente con el proyecto)
2. **WHY no WHAT**: Explicar por qué existe el código, no qué hace (el código ya lo dice)
3. **No redundante**: `i = i + 1  # incrementar i` ← esto NO
4. **Secciones visuales**: Usar `# ── Título ──` para separar bloques lógicos en funciones largas
5. **Sin over-documenting**: Una función de 2 líneas no necesita 10 líneas de docstring
6. **Explicar decisiones de arquitectura**: ¿Por qué threading? ¿Por qué importación tardía de win32com?

## Resultado esperado

Después de ejecutar este skill, cualquier desarrollador nuevo que lea el código debe entender:
- Qué hace cada módulo y por qué existe
- Cómo fluye la ejecución principal
- Por qué se tomaron ciertas decisiones técnicas
- Qué excepciones pueden ocurrir y cuándo
