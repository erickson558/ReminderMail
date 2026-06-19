# =============================================================================
# email_service.py - Servicio de envío de correos electrónicos
# Responsabilidad: Enviar correos por SMTP (Hotmail/Gmail/etc.) o Outlook COM.
# Separa la lógica de negocio del envío de correo de la interfaz gráfica.
# =============================================================================

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List


def send_email_smtp(
    smtp_server: str,
    smtp_port: int,
    username: str,
    password: str,
    recipients: List[str],
    subject: str,
    body: str
) -> None:
    """
    Envía un correo electrónico usando el protocolo SMTP con cifrado STARTTLS.

    Compatible con:
    - Hotmail / Outlook.com  → smtp-mail.outlook.com:587
    - Office 365             → smtp.office365.com:587
    - Gmail                  → smtp.gmail.com:587 (requiere App Password)
    - Yahoo Mail             → smtp.mail.yahoo.com:587

    Args:
        smtp_server:  Hostname del servidor SMTP (ej: "smtp-mail.outlook.com")
        smtp_port:    Puerto del servidor SMTP (generalmente 587 para STARTTLS)
        username:     Dirección de correo del remitente
        password:     Contraseña o App Password de la cuenta
        recipients:   Lista de correos destinatarios
        subject:      Asunto del correo
        body:         Cuerpo del correo en texto plano

    Raises:
        smtplib.SMTPAuthenticationError: Si las credenciales son incorrectas
        smtplib.SMTPConnectError: Si no se puede conectar al servidor
        smtplib.SMTPException: Para otros errores de protocolo SMTP
        TimeoutError: Si la conexión tarda más de 30 segundos
    """
    # ── Construir el mensaje MIME multipart con codificación UTF-8 ──
    message = MIMEMultipart()
    message["From"] = username
    message["To"] = ", ".join(recipients)
    message["Subject"] = subject

    # Adjuntar el cuerpo como texto plano en UTF-8
    message.attach(MIMEText(body, "plain", "utf-8"))

    # ── Conectar al servidor SMTP con STARTTLS (cifrado en transporte) ──
    # El context manager garantiza que la conexión se cierra aunque haya error.
    with smtplib.SMTP(smtp_server, smtp_port, timeout=30) as server:
        server.ehlo()            # Presentarse al servidor SMTP (requerido por RFC 2821)
        server.starttls()        # Negociar cifrado TLS para la sesión
        server.ehlo()            # Re-presentarse después del handshake TLS
        server.login(username, password)            # Autenticar con usuario y contraseña
        server.sendmail(username, recipients, message.as_string())  # Enviar el mensaje


def send_email_com(
    recipients: List[str],
    subject: str,
    body: str
) -> None:
    """
    Envía un correo usando la automatización COM de Microsoft Outlook.

    Requiere que Outlook esté instalado y configurado en el sistema Windows.
    Usa la cuenta por defecto configurada en Outlook para el envío.

    Args:
        recipients: Lista de correos destinatarios
        subject:    Asunto del correo
        body:       Cuerpo del correo

    Raises:
        RuntimeError: Si pywin32 no está instalado
        Exception:   Si Outlook no está disponible o el envío falla
    """
    # ── Importación tardía de win32com: solo disponible en Windows con pywin32 ──
    # Se hace aquí para que el módulo se pueda importar en sistemas sin pywin32
    # (por ejemplo, en Mac/Linux al ejecutar el módulo de email_service en tests).
    try:
        import win32com.client as win32
    except ImportError:
        raise RuntimeError(
            "pywin32 no está instalado. "
            "Instale con: pip install pywin32\n"
            "O cambie el método de envío a SMTP en la configuración."
        )

    # ── Crear y enviar el correo vía Outlook COM Automation ──
    outlook = win32.Dispatch('Outlook.Application')   # Obtener instancia de Outlook
    mail = outlook.CreateItem(0)                       # 0 = olMailItem (correo electrónico)
    mail.To = ";".join(recipients)                     # Múltiples destinatarios separados por ";"
    mail.Subject = subject
    mail.Body = body
    mail.Send()                                        # Encolar el correo en la bandeja de salida


def send_email(config: dict, recipients: List[str], subject: str, body: str) -> None:
    """
    Función principal de envío: delega al método configurado (SMTP o COM).

    Actúa como fachada (Facade pattern) sobre los dos métodos de envío.
    Lee la configuración para decidir qué backend usar.

    Args:
        config:     Diccionario de configuración cargado desde config.json
        recipients: Lista de correos destinatarios
        subject:    Asunto del correo
        body:       Cuerpo del correo

    Raises:
        ValueError: Si el método de envío es desconocido o faltan credenciales SMTP
        Exception:  Si el envío falla (propagada desde send_email_smtp/send_email_com)
    """
    method = config.get("metodo_envio", "com")

    if method == "smtp":
        # ── Validar campos obligatorios de SMTP antes de intentar conectar ──
        smtp_user = config.get("smtp_usuario", "").strip()
        smtp_password = config.get("smtp_password", "").strip()

        if not smtp_user:
            raise ValueError("Usuario/email SMTP no configurado. Ingrese su correo en la sección SMTP.")
        if not smtp_password:
            raise ValueError("Contraseña SMTP no configurada. Ingrese su contraseña en la sección SMTP.")

        send_email_smtp(
            smtp_server=config.get("smtp_servidor", "smtp-mail.outlook.com"),
            smtp_port=int(config.get("smtp_puerto", 587)),
            username=smtp_user,
            password=smtp_password,
            recipients=recipients,
            subject=subject,
            body=body
        )

    elif method == "com":
        # ── Modo Outlook COM: no requiere credenciales adicionales ──
        send_email_com(recipients=recipients, subject=subject, body=body)

    else:
        raise ValueError(f"Método de envío desconocido: '{method}'. Use 'smtp' o 'com'.")
