# =============================================================================
# config_manager.py - Gestión de configuración de la aplicación ReminderMail
# Responsabilidad: Cargar y guardar la configuración persistente en config.json.
# =============================================================================

import json
import os
import sys
from typing import Any, Iterable, List

# Nombre del archivo de configuración (siempre ubicado junto al ejecutable/script)
CONFIG_FILE = "config.json"

# ── Valores por defecto de configuración ──
# Se usan cuando el archivo no existe o cuando faltan claves en el JSON guardado.
DEFAULT_CONFIG = {
    "destinatarios": [],               # Lista de correos destinatarios
    "asunto": "",                      # Asunto del correo recordatorio
    "cuerpo": "",                      # Cuerpo/texto del correo
    "segundos_cierre": 60,            # Segundos de countdown antes del auto-cierre
    "metodo_envio": "com",             # Método: "com" (Outlook COM) o "smtp" (STARTTLS)
    "smtp_servidor": "smtp-mail.outlook.com",  # Servidor SMTP por defecto (Hotmail)
    "smtp_puerto": 587,                # Puerto STARTTLS estándar
    "smtp_usuario": "",                # Email del remitente (para SMTP)
    "smtp_password": "",               # Contraseña SMTP (almacenada en texto plano localmente)
    "idioma": "es"                     # Idioma de la interfaz: "es" o "en"
}


def normalize_recipients(raw_recipients: Any) -> List[str]:
    """
    Normaliza destinatarios para aceptar listas JSON y texto separado por
    comas, punto y coma o saltos de línea.
    """
    if raw_recipients is None:
        return []

    if isinstance(raw_recipients, str):
        candidate_items: Iterable[Any] = raw_recipients.replace(";", "\n").replace(",", "\n").splitlines()
    elif isinstance(raw_recipients, (list, tuple, set)):
        candidate_items = raw_recipients
    else:
        return []

    normalized = []
    seen = set()
    for item in candidate_items:
        email = str(item).strip()
        if not email:
            continue
        email_key = email.casefold()
        if email_key in seen:
            continue
        seen.add(email_key)
        normalized.append(email)

    return normalized


def normalize_close_delay_seconds(raw_value: Any, default: int = 60) -> int:
    """
    Normaliza el countdown de auto-cierre para garantizar un entero >= 1.
    """
    try:
        seconds = int(str(raw_value).strip())
    except (TypeError, ValueError, AttributeError):
        seconds = default

    return max(1, seconds)


def get_base_path() -> str:
    """
    Retorna la ruta base de la aplicación según el modo de ejecución:
    - Modo ejecutable (PyInstaller .exe): directorio que contiene el .exe
    - Modo script (desarrollo): directorio raíz del proyecto (padre de src/)
    """
    if getattr(sys, 'frozen', False):
        # sys.executable apunta al .exe en modo congelado
        return os.path.dirname(sys.executable)
    else:
        # __file__ es config_manager.py en src/, subimos un nivel al directorio raíz
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_config_path() -> str:
    """Retorna la ruta absoluta completa al archivo config.json."""
    return os.path.join(get_base_path(), CONFIG_FILE)


def load_config() -> dict:
    """
    Carga la configuración desde config.json.

    - Si el archivo no existe, retorna una copia de DEFAULT_CONFIG.
    - Si el archivo existe pero le faltan claves, las completa con DEFAULT_CONFIG.
    - Si el archivo está corrupto, retorna DEFAULT_CONFIG y no lanza excepción.

    Returns:
        dict: Configuración completa con todas las claves garantizadas.
    """
    config_path = get_config_path()

    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                saved = json.load(f)

            # Combinar defaults con valores guardados para garantizar todas las claves
            config = DEFAULT_CONFIG.copy()
            config.update(saved)
            config["destinatarios"] = normalize_recipients(config.get("destinatarios", []))
            config["segundos_cierre"] = normalize_close_delay_seconds(
                config.get("segundos_cierre", DEFAULT_CONFIG["segundos_cierre"])
            )
            return config

        except (json.JSONDecodeError, IOError, OSError):
            # Archivo corrupto o sin permisos de lectura → usar defaults
            return DEFAULT_CONFIG.copy()

    # Archivo no existe → usar defaults
    return DEFAULT_CONFIG.copy()


def save_config(config: dict) -> tuple:
    """
    Guarda la configuración en config.json con codificación UTF-8.

    Args:
        config: Diccionario con la configuración a persistir.

    Returns:
        tuple: (True, None) si tuvo éxito, (False, mensaje_error) si falló.
    """
    config_path = get_config_path()

    try:
        config_to_save = DEFAULT_CONFIG.copy()
        config_to_save.update(config)
        config_to_save["destinatarios"] = normalize_recipients(config_to_save.get("destinatarios", []))
        config_to_save["segundos_cierre"] = normalize_close_delay_seconds(
            config_to_save.get("segundos_cierre", DEFAULT_CONFIG["segundos_cierre"])
        )
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config_to_save, f, indent=4, ensure_ascii=False)
        return True, None

    except (IOError, OSError) as e:
        return False, str(e)
