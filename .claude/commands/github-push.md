# /github-push — Commit, Compilar y Publicar en GitHub

Sube el proyecto ReminderMail a GitHub usando la cuenta **erickson558**.

## Pasos a seguir

### 1. Verificar estado del repositorio
```bash
git status
git log --oneline -5
```

### 2. Inicializar git si es necesario
Si el directorio no tiene repositorio git:
```bash
git init
git branch -M main
```

### 3. Configurar remoto si no existe
Verificar si hay un remote configurado. Si no:
```bash
gh repo create ReminderMail --public --source=. --remote=origin
```
O si el repo ya existe en GitHub:
```bash
git remote add origin https://github.com/erickson558/ReminderMail.git
```

### 4. Compilar el .exe antes de commitear
```bash
pyinstaller reminder.spec
```
Verificar que se generó `dist/ReminderMail.exe`.

### 5. Staging selectivo (no incluir credenciales ni binarios pesados)
```bash
git add main.py
git add src/
git add locales/
git add .claude/
git add reminder.spec
git add requirements.txt
git add .gitignore
git add CLAUDE.md
git add SDD.md
git add reminder.py
git add matarreminder.xml
# NO agregar: config.json (tiene contraseñas), dist/, build/, *.exe grande
```

### 6. Commit con mensaje descriptivo
```bash
git commit -m "feat: soporte SMTP Hotmail, multi-idioma ES/EN, threading, botón donación

- Agregar src/email_service.py con soporte SMTP (smtplib STARTTLS)
- Agregar src/config_manager.py para gestión de config.json  
- Agregar src/main_window.py con GUI refactorizada y threading
- Agregar locales/es.json y locales/en.json para i18n
- Agregar botón 'Cómprame una cerveza' (PayPal)
- Actualizar reminder.spec para nuevo entry point main.py
- Agregar CLAUDE.md, SDD.md y .claude/ para Claude Code

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

### 7. Push a GitHub
```bash
git push -u origin main
```

### 8. Verificar
```bash
gh repo view erickson558/ReminderMail --web
```

## Notas
- Cuenta GitHub: erickson558 (ya autenticada con keyring)
- Si el push falla por historial divergente: usar `git pull origin main --rebase` primero
- Si el repo es nuevo: el primer push requiere `-u origin main`
