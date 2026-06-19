# SDD - Spec Driven Development: ReminderMail

**Versión**: 2.0  
**Fecha**: 2026-06-19  
**Estado**: Implementado

---

## 1. Descripción del Sistema

ReminderMail es una aplicación de escritorio Windows que envía correos de recordatorio
automáticamente. Se ejecuta como tarea programada (Windows Task Scheduler) y permite
gestionar destinatarios, asunto y cuerpo del correo mediante una interfaz gráfica simple.

---

## 2. Requisitos Funcionales

### RF-01: Envío de correo por SMTP
- El sistema DEBE soportar envío de correo usando SMTP con STARTTLS
- Servidores soportados: Hotmail/Outlook.com, Office 365, Gmail, Yahoo
- Puerto por defecto: 587 (STARTTLS)
- El usuario DEBE poder ingresar su email y contraseña
- El sistema DEBE mostrar errores de autenticación de forma clara

### RF-02: Envío de correo por Outlook COM
- El sistema DEBE mantener el método COM de Outlook como opción
- Requiere Microsoft Outlook instalado y configurado en el equipo
- No requiere credenciales adicionales (usa la cuenta de Outlook)

### RF-03: Gestión de destinatarios
- El usuario PUEDE agregar múltiples destinatarios
- El usuario PUEDE eliminar destinatarios seleccionados
- Los destinatarios se persisten en config.json
- El sistema NO debe enviar si no hay destinatarios

### RF-04: Composición del mensaje
- El usuario PUEDE editar el asunto del correo
- El usuario PUEDE editar el cuerpo del correo
- Ambos campos se persisten en config.json

### RF-05: Auto-envío al iniciar
- La aplicación DEBE enviar automáticamente 1 segundo después de iniciarse
- Solo si hay al menos un destinatario configurado
- Este comportamiento permite uso como tarea programada desatendida

### RF-06: Auto-cierre tras envío exitoso
- La aplicación DEBE cerrarse automáticamente 60 segundos después de un envío exitoso
- El usuario PUEDE cerrar manualmente antes de que se cumpla el tiempo

### RF-07: Persistencia de configuración
- Toda la configuración (destinatarios, asunto, cuerpo, método, SMTP) DEBE guardarse
- La configuración se guarda en config.json junto al ejecutable
- Al iniciar, la configuración guardada DEBE cargarse automáticamente

### RF-08: Multi-idioma
- La interfaz DEBE estar disponible en Español e Inglés
- El idioma PUEDE cambiarse en tiempo real desde la UI (botones ES/EN)
- El cambio de idioma DEBE preservar todos los datos ingresados
- El idioma seleccionado DEBE persistir en config.json

### RF-09: Botón de donación
- La UI DEBE incluir un botón "Cómprame una cerveza"
- Al hacer clic DEBE abrir el enlace de PayPal en el navegador predeterminado
- URL: https://www.paypal.com/donate/?hosted_button_id=ZABFRXC2P3JQN

### RF-10: Interfaz no bloqueante
- La GUI NO DEBE congelarse durante el envío de correo
- El envío DEBE ejecutarse en un hilo de fondo (threading.Thread)
- El botón Enviar DEBE deshabilitarse durante el envío para evitar duplicados

---

## 3. Requisitos No Funcionales

### RNF-01: Compatibilidad
- Sistema operativo: Windows 10/11 (64-bit)
- Python 3.8+ (para desarrollo)
- El .exe compilado NO requiere Python instalado

### RNF-02: Compilación
- El sistema DEBE poder compilarse a un único .exe con PyInstaller
- El .exe NO DEBE mostrar ventana de consola (windowed mode)
- Los archivos de localización DEBEN empaquetarse dentro del .exe
- El ícono reminder.ico DEBE usarse si está disponible

### RNF-03: Seguridad
- Las contraseñas SMTP se almacenan en texto plano en config.json (local al equipo)
- Se recomienda usar App Passwords de Hotmail/Gmail (no la contraseña principal)
- config.json NO DEBE subirse a repositorios públicos (incluido en .gitignore)

### RNF-04: Arquitectura
- La lógica de negocio (email_service.py, config_manager.py) DEBE estar separada de la UI
- La UI NO DEBE contener lógica compleja de negocio

### RNF-05: Mantenibilidad
- Todo el código DEBE estar comentado en español
- La estructura de módulos DEBE ser clara y navegable

---

## 4. Arquitectura Técnica

```
main.py → ReminderMailApp(root) → _enviar_correo()
                                 → threading.Thread → send_email(config)
                                                    → send_email_smtp() | send_email_com()
                                 → _save_config_ui() → save_config(config)
                                 → load_config() ← config.json
                                 → load_locale(lang) ← locales/{lang}.json
```

---

## 5. Casos de Uso

### CU-01: Envío automático como tarea programada
**Actor**: Windows Task Scheduler
**Flujo**:
1. Task Scheduler ejecuta ReminderMail.exe
2. La app carga config.json (destinatarios, asunto, cuerpo, credenciales)
3. 1 segundo después del inicio, se dispara el auto-envío
4. Se envía el correo (SMTP o COM)
5. Tras éxito, la app se cierra en 60 segundos

### CU-02: Configuración inicial de SMTP para Hotmail
**Actor**: Usuario
**Flujo**:
1. Usuario abre la app
2. Selecciona método "SMTP directo"
3. Selecciona tipo de cuenta "Hotmail/Outlook.com"
4. Ingresa su email y App Password
5. Hace clic en "Guardar config"
6. Los datos se persisten para el próximo auto-envío

### CU-03: Agregar destinatario
**Actor**: Usuario
**Flujo**:
1. Usuario hace clic en "Agregar"
2. Aparece diálogo para ingresar correo
3. El correo se agrega a la lista
4. Usuario guarda configuración

---

## 6. Plan de Testing

| ID    | Caso de prueba                              | Resultado esperado              |
|-------|---------------------------------------------|----------------------------------|
| T-01  | Envío SMTP con credenciales válidas         | "Correo enviado exitosamente"   |
| T-02  | Envío SMTP con contraseña incorrecta        | Error de autenticación visible  |
| T-03  | Envío sin destinatarios                     | Mensaje de error en barra       |
| T-04  | Envío sin contraseña SMTP                   | Solicitar contraseña            |
| T-05  | Cambio de idioma ES→EN preserva datos       | Campos mantienen sus valores    |
| T-06  | Auto-cierre tras envío exitoso              | App se cierra en ~60 segundos   |
| T-07  | config.json se actualiza tras guardar       | Archivo JSON tiene nuevos datos |
| T-08  | .exe se ejecuta sin consola                 | Solo ventana gráfica            |
| T-09  | Botón cerveza abre PayPal                   | Se abre el navegador            |

---

## 7. Historial de Cambios

| Versión | Fecha      | Cambio                                              |
|---------|------------|-----------------------------------------------------|
| 1.0     | anterior   | Versión original - solo Outlook COM, un archivo     |
| 2.0     | 2026-06-19 | Soporte SMTP (Hotmail fix), multi-idioma, arquitectura modular, threading, botón donación |
