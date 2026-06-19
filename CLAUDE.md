# ReminderMail - Documentación del Proyecto

## Descripción
Aplicación de escritorio Windows para enviar correos recordatorio automáticamente.
Soporta dos métodos de envío: **Outlook COM** (escritorio) y **SMTP directo** (Hotmail, Gmail, Office 365).
Interfaz en Español e Inglés, con botón de donación integrado.

## Arquitectura

```
ReminderMail/
├── main.py                   # Punto de entrada: inicializa Tkinter y lanza la app
├── config.json               # Configuración persistente (destinatarios, SMTP, idioma)
├── requirements.txt          # Dependencias Python
├── reminder.spec             # Configuración de PyInstaller para compilar a .exe
├── reminder.py               # Versión original (backup, no usar en desarrollo)
├── .gitignore
├── CLAUDE.md                 # Este archivo
├── SDD.md                    # Especificación del sistema (Spec Driven Development)
│
├── src/                      # Código fuente (backend + frontend separados)
│   ├── __init__.py
│   ├── config_manager.py     # Gestión de config.json (carga/guardado)
│   ├── email_service.py      # Lógica de envío: SMTP (smtplib) y COM (win32com)
│   └── main_window.py        # GUI Tkinter (ventana principal, i18n, threading)
│
├── locales/                  # Archivos de traducción (i18n)
│   ├── es.json               # Español (idioma por defecto)
│   └── en.json               # English
│
└── .claude/
    ├── settings.json         # Permisos y configuración de Claude Code
    ├── agents/
    │   └── remindermail-dev.md   # Agente especializado en este proyecto
    └── commands/             # Skills personalizados (slash commands)
        ├── github-push.md    # /github-push  → commit + compile + push
        ├── comment-code.md   # /comment-code → comentar código
        └── improve-code.md   # /improve-code → mejora como senior engineer
```

## Setup de Desarrollo

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Post-install de pywin32 (requerido en Windows)
python -m pywin32_postinstall -install

# 3. Ejecutar en modo desarrollo
python main.py
```

## Métodos de Envío

### SMTP (Hotmail / Outlook.com)
1. En la UI, seleccionar **"SMTP directo"**
2. Tipo de cuenta: **Hotmail/Outlook.com**
3. Servidor: `smtp-mail.outlook.com`, Puerto: `587`
4. Usuario: tu cuenta `@hotmail.com` o `@outlook.com`
5. Contraseña: usar una **App Password** (ver nota abajo)

> **Nota Hotmail**: Ve a https://account.microsoft.com/security → Seguridad adicional
> → Contraseñas de aplicación → Crear nueva contraseña de aplicación.
> Usa esa contraseña en el campo Contraseña (no tu contraseña principal).

### Outlook COM (Office 365)
Requiere Microsoft Outlook instalado y configurado en el equipo.
Usa la cuenta por defecto configurada en Outlook.

## Compilar a .exe

```bash
# Asegurarse de tener pyinstaller instalado
pip install pyinstaller

# Compilar (genera reminder.exe en dist/)
pyinstaller reminder.spec

# El .exe queda en: dist/ReminderMail.exe
```

**Nota**: Para el ícono, colocar `reminder.ico` en el directorio raíz antes de compilar.

## Skills Disponibles

| Comando          | Descripción                                              |
|------------------|----------------------------------------------------------|
| `/github-push`   | Commit, compila .exe y hace push a GitHub (erickson558) |
| `/comment-code`  | Agrega comentarios detallados a todo el código          |
| `/improve-code`  | Análisis y mejoras como senior engineer                 |

## Configuración (config.json)

| Clave            | Tipo     | Descripción                                  |
|------------------|----------|----------------------------------------------|
| `destinatarios`  | array    | Lista de correos destinatarios               |
| `asunto`         | string   | Asunto del correo                            |
| `cuerpo`         | string   | Cuerpo del correo                            |
| `metodo_envio`   | string   | `"com"` o `"smtp"`                           |
| `smtp_servidor`  | string   | Hostname del servidor SMTP                   |
| `smtp_puerto`    | int      | Puerto SMTP (generalmente 587)               |
| `smtp_usuario`   | string   | Email del remitente                          |
| `smtp_password`  | string   | Contraseña SMTP (almacenada localmente)      |
| `idioma`         | string   | `"es"` o `"en"`                              |

## Notas Técnicas

- **Threading**: El envío de correo se ejecuta en un hilo daemon para evitar que la GUI se congele.
- **Auto-envío**: La app envía automáticamente 1 segundo después de iniciarse (si hay destinatarios).
- **Auto-cierre**: Tras un envío exitoso, la app se cierra en 60 segundos.
- **i18n**: Los strings de la UI se cargan desde `locales/{idioma}.json`. Agregar nuevos idiomas creando el archivo JSON correspondiente.
- **PyInstaller**: Los `locales/` se empaquetan dentro del .exe (extraídos a `sys._MEIPASS`). El `config.json` se lee/escribe siempre desde el directorio del .exe (persistente).
