# =============================================================================
# main_window.py - Interfaz gráfica principal de ReminderMail
# Responsabilidad: Gestionar toda la interacción visual con el usuario.
# Usa threading para enviar correos sin congelar la GUI.
# =============================================================================

import tkinter as tk
from tkinter import simpledialog
import threading
import webbrowser
import json
import os
import sys

from src.config_manager import load_config, save_config
from src.email_service import send_email

# ── URL del botón "Cómprame una cerveza" (PayPal Donate) ──
BEER_URL = "https://www.paypal.com/donate/?hosted_button_id=ZABFRXC2P3JQN"

# ── Servidores SMTP predefinidos con sus puertos STARTTLS ──
# Permite al usuario seleccionar rápidamente por tipo de cuenta.
SMTP_PRESETS = {
    "Hotmail/Outlook.com": {"server": "smtp-mail.outlook.com", "port": 587},
    "Office 365":          {"server": "smtp.office365.com",    "port": 587},
    "Gmail":               {"server": "smtp.gmail.com",         "port": 587},
    "Yahoo Mail":          {"server": "smtp.mail.yahoo.com",    "port": 587},
}


def load_locale(lang: str) -> dict:
    """
    Carga el archivo de traducción JSON para el idioma indicado.

    En modo ejecutable (PyInstaller), los locales se encuentran en sys._MEIPASS
    porque son archivos de datos empaquetados dentro del .exe.
    En modo script (desarrollo), se leen desde la carpeta locales/ del proyecto.

    Args:
        lang: Código de idioma ("es" para español, "en" para inglés)

    Returns:
        dict: Diccionario con los strings traducidos, o {} si no se encontró el archivo.
    """
    # Determinar la ruta base según el modo de ejecución
    if getattr(sys, 'frozen', False):
        # PyInstaller extrae archivos de datos al directorio temporal sys._MEIPASS
        base = sys._MEIPASS
    else:
        # En desarrollo, locales/ está en la raíz del proyecto (padre de src/)
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    locale_path = os.path.join(base, "locales", f"{lang}.json")

    if os.path.exists(locale_path):
        try:
            with open(locale_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass  # Si el archivo está corrupto, usar el fallback

    # Fallback: retornar diccionario vacío (la función t() usará la clave como texto)
    return {}


class ReminderMailApp:
    """
    Clase principal de la aplicación ReminderMail.

    Encapsula toda la lógica de interfaz gráfica separada del backend.
    Usa threads para operaciones de red (envío de correo) sin bloquear la UI.
    """

    def __init__(self, root: tk.Tk):
        """
        Inicializa la aplicación: carga configuración, idioma y construye la UI.

        Args:
            root: Ventana raíz de Tkinter ya creada por main.py
        """
        self.root = root

        # ── Estado interno ──
        self.config = load_config()                                        # Configuración desde config.json
        self.lang = self.config.get("idioma", "es")                        # Idioma activo
        self.strings = load_locale(self.lang)                              # Strings traducidos
        self._auto_sent = False                                            # Bandera: ¿ya se hizo el auto-envío?

        # ── Variables de Tkinter (se crean antes de _build_ui) ──
        self.send_method_var = tk.StringVar(value=self.config.get("metodo_envio", "com"))
        self.smtp_preset_var = tk.StringVar(value="Hotmail/Outlook.com")

        # ── Construir interfaz y poblar campos ──
        self._build_ui()
        self._populate_fields_from(self.config)

        # ── Auto-enviar 1 segundo después del inicio (comportamiento original) ──
        self.root.after(1000, self._auto_send)

    # =========================================================================
    # SECCIÓN: TRADUCCIÓN (i18n)
    # =========================================================================

    def t(self, key: str, **kwargs) -> str:
        """
        Retorna el string traducido para la clave dada.

        Si la clave no existe en el archivo de idioma, retorna la clave misma
        como texto fallback. Soporta interpolación de variables con {nombre}.

        Args:
            key:    Clave del string en el archivo de idioma JSON
            kwargs: Variables para interpolación en el string (ej: error="msg")

        Returns:
            str: String traducido e interpolado.
        """
        text = self.strings.get(key, key)
        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError:
                pass  # Si la interpolación falla, retornar el texto sin formatear
        return text

    # =========================================================================
    # SECCIÓN: CONSTRUCCIÓN DE LA UI
    # =========================================================================

    def _build_ui(self):
        """
        Construye todos los widgets de la interfaz gráfica.

        Organización visual:
        1. Barra superior (título + selector de idioma)
        2. Sección de destinatarios (listbox + botones Agregar/Eliminar)
        3. Sección de asunto
        4. Sección de cuerpo del correo
        5. Sección de método de envío (COM / SMTP con campos condicionales)
        6. Botones de acción (Enviar, Guardar, Salir)
        7. Botón "Cómprame una cerveza"
        8. Barra de estado
        """
        self.root.title(self.t("title"))
        self.root.resizable(False, False)

        # ── 1. BARRA SUPERIOR: Título + selector de idioma ──
        frame_top = tk.Frame(self.root, bg="#2c3e50")
        frame_top.pack(fill=tk.X)

        self._lbl_title = tk.Label(
            frame_top,
            text=self.t("title"),
            font=("Segoe UI", 11, "bold"),
            bg="#2c3e50", fg="white", pady=8
        )
        self._lbl_title.pack(side=tk.LEFT, padx=12)

        # Botones de cambio de idioma (ES / EN) alineados a la derecha
        frame_lang = tk.Frame(frame_top, bg="#2c3e50")
        frame_lang.pack(side=tk.RIGHT, padx=10)

        self._btn_es = tk.Button(
            frame_lang, text="ES", width=4,
            relief=tk.SUNKEN if self.lang == "es" else tk.RAISED,
            command=lambda: self._change_language("es")
        )
        self._btn_es.pack(side=tk.LEFT, padx=2, pady=5)

        self._btn_en = tk.Button(
            frame_lang, text="EN", width=4,
            relief=tk.SUNKEN if self.lang == "en" else tk.RAISED,
            command=lambda: self._change_language("en")
        )
        self._btn_en.pack(side=tk.LEFT, padx=2, pady=5)

        # ── 2. SECCIÓN DE DESTINATARIOS ──
        self._frame_dest = tk.LabelFrame(
            self.root, text=self.t("recipients"), padx=10, pady=5
        )
        self._frame_dest.pack(fill=tk.X, padx=10, pady=(10, 0))

        self.listbox_destinatarios = tk.Listbox(
            self._frame_dest, width=55, height=5
        )
        self.listbox_destinatarios.pack(pady=5)

        frame_dest_btns = tk.Frame(self._frame_dest)
        frame_dest_btns.pack()

        self.btn_agregar = tk.Button(
            frame_dest_btns, text=self.t("add"), width=15,
            command=self._agregar_destinatario
        )
        self.btn_agregar.pack(side=tk.LEFT, padx=5)

        self.btn_eliminar = tk.Button(
            frame_dest_btns, text=self.t("delete"), width=15,
            command=self._eliminar_destinatario
        )
        self.btn_eliminar.pack(side=tk.LEFT, padx=5)

        # ── 3. SECCIÓN DE ASUNTO ──
        self._frame_asunto = tk.LabelFrame(
            self.root, text=self.t("subject"), padx=10, pady=5
        )
        self._frame_asunto.pack(fill=tk.X, padx=10, pady=(5, 0))

        self.entry_asunto = tk.Entry(self._frame_asunto, width=57)
        self.entry_asunto.pack(pady=5)

        # ── 4. SECCIÓN DEL CUERPO DEL CORREO ──
        self._frame_cuerpo = tk.LabelFrame(
            self.root, text=self.t("body"), padx=10, pady=5
        )
        self._frame_cuerpo.pack(fill=tk.X, padx=10, pady=(5, 0))

        self.text_cuerpo = tk.Text(self._frame_cuerpo, width=57, height=7)
        self.text_cuerpo.pack(pady=5)

        # ── 5. SECCIÓN DE MÉTODO DE ENVÍO ──
        self._frame_method = tk.LabelFrame(
            self.root, text=self.t("send_method"), padx=10, pady=5
        )
        self._frame_method.pack(fill=tk.X, padx=10, pady=(5, 0))

        # Radio buttons para elegir entre COM (Outlook) o SMTP (Hotmail/Gmail)
        rb_frame = tk.Frame(self._frame_method)
        rb_frame.pack(anchor="w")

        self._rb_com = tk.Radiobutton(
            rb_frame, text=self.t("com_method"),
            variable=self.send_method_var, value="com",
            command=self._toggle_smtp_fields
        )
        self._rb_com.pack(side=tk.LEFT, padx=(0, 15))

        self._rb_smtp = tk.Radiobutton(
            rb_frame, text=self.t("smtp_method"),
            variable=self.send_method_var, value="smtp",
            command=self._toggle_smtp_fields
        )
        self._rb_smtp.pack(side=tk.LEFT)

        # ── Subsección de configuración SMTP (visible solo cuando método = smtp) ──
        self.frame_smtp = tk.Frame(self._frame_method, padx=5)
        # No se empaca aquí; _toggle_smtp_fields controla su visibilidad

        # Selector rápido de cuenta (preset)
        row0 = tk.Frame(self.frame_smtp)
        row0.pack(fill=tk.X, pady=2)
        self._lbl_smtp_preset = tk.Label(row0, text=self.t("account_type"), width=14, anchor="w")
        self._lbl_smtp_preset.pack(side=tk.LEFT)
        self.combo_smtp_preset = tk.OptionMenu(
            row0, self.smtp_preset_var, *SMTP_PRESETS.keys(),
            command=self._on_smtp_preset_change
        )
        self.combo_smtp_preset.config(width=20)
        self.combo_smtp_preset.pack(side=tk.LEFT)

        # Campo de servidor SMTP
        row1 = tk.Frame(self.frame_smtp)
        row1.pack(fill=tk.X, pady=2)
        self._lbl_smtp_server = tk.Label(row1, text=self.t("smtp_server"), width=14, anchor="w")
        self._lbl_smtp_server.pack(side=tk.LEFT)
        self.entry_smtp_server = tk.Entry(row1, width=36)
        self.entry_smtp_server.pack(side=tk.LEFT)

        # Campo de puerto SMTP
        row2 = tk.Frame(self.frame_smtp)
        row2.pack(fill=tk.X, pady=2)
        self._lbl_smtp_port = tk.Label(row2, text=self.t("smtp_port"), width=14, anchor="w")
        self._lbl_smtp_port.pack(side=tk.LEFT)
        self.entry_smtp_port = tk.Entry(row2, width=8)
        self.entry_smtp_port.pack(side=tk.LEFT)

        # Campo de usuario/email remitente
        row3 = tk.Frame(self.frame_smtp)
        row3.pack(fill=tk.X, pady=2)
        self._lbl_smtp_user = tk.Label(row3, text=self.t("smtp_user"), width=14, anchor="w")
        self._lbl_smtp_user.pack(side=tk.LEFT)
        self.entry_smtp_user = tk.Entry(row3, width=36)
        self.entry_smtp_user.pack(side=tk.LEFT)

        # Campo de contraseña (show="*" para enmascarar caracteres)
        row4 = tk.Frame(self.frame_smtp)
        row4.pack(fill=tk.X, pady=2)
        self._lbl_smtp_pass = tk.Label(row4, text=self.t("smtp_password"), width=14, anchor="w")
        self._lbl_smtp_pass.pack(side=tk.LEFT)
        self.entry_smtp_pass = tk.Entry(row4, width=36, show="*")
        self.entry_smtp_pass.pack(side=tk.LEFT)

        # Nota informativa sobre App Passwords para Hotmail/Gmail
        self._lbl_smtp_note = tk.Label(
            self.frame_smtp,
            text=self.t("smtp_note"),
            font=("Segoe UI", 8),
            fg="#7f8c8d", wraplength=380, justify="left"
        )
        self._lbl_smtp_note.pack(anchor="w", pady=(3, 0))

        # ── 6. BOTONES DE ACCIÓN ──
        frame_buttons = tk.Frame(self.root)
        frame_buttons.pack(pady=10)

        self.btn_enviar = tk.Button(
            frame_buttons, text=self.t("send"), width=17,
            bg="#27ae60", fg="white", font=("Segoe UI", 9, "bold"),
            command=self._enviar_correo
        )
        self.btn_enviar.pack(side=tk.LEFT, padx=5)

        self.btn_guardar = tk.Button(
            frame_buttons, text=self.t("save_config"), width=17,
            command=self._save_config_ui
        )
        self.btn_guardar.pack(side=tk.LEFT, padx=5)

        self.btn_salir = tk.Button(
            frame_buttons, text=self.t("exit"), width=17,
            bg="#e74c3c", fg="white",
            command=self._salir
        )
        self.btn_salir.pack(side=tk.LEFT, padx=5)

        # ── 7. BOTÓN "CÓMPRAME UNA CERVEZA" ──
        # Abre el enlace de donación PayPal en el navegador predeterminado
        self._btn_beer = tk.Button(
            self.root,
            text=self.t("buy_beer"),
            font=("Segoe UI", 9),
            fg="#e67e22",
            relief=tk.FLAT,
            cursor="hand2",  # Cursor de mano para indicar que es clickable
            command=lambda: webbrowser.open(BEER_URL)
        )
        self._btn_beer.pack(pady=(0, 6))

        # ── 8. BARRA DE ESTADO ──
        self.status_label = tk.Label(
            self.root, text="", bd=1,
            relief=tk.SUNKEN, anchor=tk.W, padx=5, font=("Segoe UI", 9)
        )
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

        # Mostrar/ocultar campos SMTP según el método inicial
        self._toggle_smtp_fields()

    # =========================================================================
    # SECCIÓN: GESTIÓN DE CAMPOS Y CONFIGURACIÓN
    # =========================================================================

    def _populate_fields_from(self, config: dict):
        """
        Llena todos los campos de la UI con los valores del diccionario config.

        Se usa tanto al inicializar como al cambiar de idioma (para restaurar datos).

        Args:
            config: Diccionario de configuración con los valores a mostrar
        """
        # ── Poblar lista de destinatarios ──
        self.listbox_destinatarios.delete(0, tk.END)  # Limpiar primero
        for email in config.get("destinatarios", []):
            self.listbox_destinatarios.insert(tk.END, email)

        # ── Asunto ──
        self.entry_asunto.delete(0, tk.END)
        self.entry_asunto.insert(0, config.get("asunto", ""))

        # ── Cuerpo ──
        self.text_cuerpo.delete("1.0", tk.END)
        self.text_cuerpo.insert("1.0", config.get("cuerpo", ""))

        # ── Configuración SMTP ──
        saved_server = config.get("smtp_servidor", "smtp-mail.outlook.com")
        self.entry_smtp_server.delete(0, tk.END)
        self.entry_smtp_server.insert(0, saved_server)

        self.entry_smtp_port.delete(0, tk.END)
        self.entry_smtp_port.insert(0, str(config.get("smtp_puerto", 587)))

        self.entry_smtp_user.delete(0, tk.END)
        self.entry_smtp_user.insert(0, config.get("smtp_usuario", ""))

        self.entry_smtp_pass.delete(0, tk.END)
        self.entry_smtp_pass.insert(0, config.get("smtp_password", ""))

        # ── Preseleccionar el tipo de cuenta según el servidor guardado ──
        for preset_name, preset_data in SMTP_PRESETS.items():
            if preset_data["server"] == saved_server:
                self.smtp_preset_var.set(preset_name)
                break

    def _get_config_from_ui(self) -> dict:
        """
        Lee todos los campos de la UI y construye el diccionario de configuración.

        Returns:
            dict: Configuración completa lista para guardar en config.json
        """
        # Leer puerto como entero; si es inválido, usar 587 como default
        try:
            port = int(self.entry_smtp_port.get().strip())
        except (ValueError, AttributeError):
            port = 587

        return {
            "destinatarios":  list(self.listbox_destinatarios.get(0, tk.END)),
            "asunto":         self.entry_asunto.get().strip(),
            "cuerpo":         self.text_cuerpo.get("1.0", tk.END).strip(),
            "metodo_envio":   self.send_method_var.get(),
            "smtp_servidor":  self.entry_smtp_server.get().strip(),
            "smtp_puerto":    port,
            "smtp_usuario":   self.entry_smtp_user.get().strip(),
            "smtp_password":  self.entry_smtp_pass.get(),  # Sin strip: la contraseña puede tener espacios
            "idioma":         self.lang
        }

    def _toggle_smtp_fields(self):
        """
        Muestra u oculta el panel de configuración SMTP según el método seleccionado.

        Si el método es "smtp" → muestra los campos de servidor, puerto, usuario y contraseña.
        Si el método es "com"  → oculta esos campos (no son necesarios para Outlook COM).
        """
        if self.send_method_var.get() == "smtp":
            self.frame_smtp.pack(fill=tk.X, pady=(5, 5))
        else:
            self.frame_smtp.pack_forget()

    def _on_smtp_preset_change(self, selection: str):
        """
        Actualiza los campos de servidor y puerto cuando el usuario selecciona un preset.

        Args:
            selection: Nombre del preset seleccionado (ej: "Hotmail/Outlook.com")
        """
        if selection in SMTP_PRESETS:
            preset = SMTP_PRESETS[selection]
            self.entry_smtp_server.delete(0, tk.END)
            self.entry_smtp_server.insert(0, preset["server"])
            self.entry_smtp_port.delete(0, tk.END)
            self.entry_smtp_port.insert(0, str(preset["port"]))

    # =========================================================================
    # SECCIÓN: BARRA DE ESTADO
    # =========================================================================

    def _update_status(self, message: str, color: str = "black"):
        """
        Actualiza el texto y color de la barra de estado inferior.

        Args:
            message: Texto a mostrar en la barra de estado
            color:   Color del texto ("green" éxito, "red" error, "blue" en proceso)
        """
        self.status_label.config(text=message, fg=color)

    # =========================================================================
    # SECCIÓN: GESTIÓN DE DESTINATARIOS
    # =========================================================================

    def _agregar_destinatario(self):
        """
        Muestra un diálogo de texto simple para que el usuario ingrese
        un nuevo correo electrónico y lo agrega a la listbox.
        """
        nuevo = simpledialog.askstring(
            self.t("msg_add_title"),
            self.t("msg_add_prompt")
        )
        if nuevo and nuevo.strip():
            self.listbox_destinatarios.insert(tk.END, nuevo.strip())
            self._update_status(self.t("msg_recipient_added"), "green")

    def _eliminar_destinatario(self):
        """
        Elimina los destinatarios seleccionados en la listbox.
        Elimina en orden inverso para evitar que los índices se desplacen.
        """
        seleccion = self.listbox_destinatarios.curselection()
        if not seleccion:
            self._update_status(self.t("msg_select_to_delete"), "red")
            return

        # Orden inverso: al eliminar de abajo hacia arriba los índices superiores no cambian
        for index in reversed(seleccion):
            self.listbox_destinatarios.delete(index)

        self._update_status(self.t("msg_recipient_deleted"), "green")

    # =========================================================================
    # SECCIÓN: ENVÍO DE CORREO (con threading para no bloquear la GUI)
    # =========================================================================

    def _enviar_correo(self):
        """
        Valida los datos y lanza el envío del correo en un hilo de fondo.

        El envío se hace en un thread separado para que la ventana de Tkinter
        no se congele mientras se establece la conexión SMTP o se habla con Outlook.
        """
        config = self._get_config_from_ui()
        destinatarios = config["destinatarios"]

        # ── Validación: al menos un destinatario ──
        if not destinatarios:
            self._update_status(self.t("msg_no_recipients"), "red")
            return

        # ── Validación específica para SMTP ──
        if config["metodo_envio"] == "smtp":
            if not config.get("smtp_usuario"):
                self._update_status(self.t("msg_no_smtp_user"), "red")
                return
            if not config.get("smtp_password"):
                self._update_status(self.t("msg_no_smtp_pass"), "red")
                return

        # ── Deshabilitar botón Enviar para evitar clics duplicados ──
        self.btn_enviar.config(state=tk.DISABLED)
        self._update_status(self.t("msg_sending"), "blue")

        # ── Ejecutar envío en hilo daemon (muere si la app se cierra) ──
        thread = threading.Thread(
            target=self._send_in_background,
            args=(config, destinatarios, config["asunto"], config["cuerpo"]),
            daemon=True
        )
        thread.start()

    def _send_in_background(self, config: dict, recipients: list, subject: str, body: str):
        """
        Ejecutado en hilo de fondo: llama al servicio de email.

        Al finalizar, usa root.after(0, ...) para actualizar la UI en el
        hilo principal de Tkinter (único hilo que puede tocar widgets).

        Args:
            config:     Configuración completa con método y credenciales
            recipients: Lista de destinatarios
            subject:    Asunto del correo
            body:       Cuerpo del correo
        """
        try:
            send_email(config, recipients, subject, body)
            # Programar callback de éxito en el hilo principal de Tkinter
            self.root.after(0, self._on_send_success)
        except Exception as exc:
            # Programar callback de error en el hilo principal de Tkinter
            self.root.after(0, self._on_send_error, str(exc))

    def _on_send_success(self):
        """
        Callback ejecutado en el hilo principal después de un envío exitoso.
        Actualiza la UI y programa el cierre automático en 60 segundos.
        """
        self._update_status(self.t("msg_email_sent"), "green")
        # Guardar configuración automáticamente tras un envío exitoso
        self._save_config_ui(silent=True)
        # Cerrar la aplicación después de 60 segundos (comportamiento original mantenido)
        self.root.after(60000, self._salir)

    def _on_send_error(self, error_msg: str):
        """
        Callback ejecutado en el hilo principal cuando el envío falla.
        Re-habilita el botón Enviar y muestra el mensaje de error.

        Args:
            error_msg: Descripción del error para mostrar al usuario
        """
        self.btn_enviar.config(state=tk.NORMAL)  # Re-habilitar para que el usuario pueda reintentar
        self._update_status(self.t("msg_email_error", error=error_msg), "red")

    def _auto_send(self):
        """
        Envío automático al iniciar la app (se dispara 1 segundo después del inicio).

        Solo ejecuta si:
        - No se ha hecho auto-envío previamente (bandera _auto_sent)
        - Hay al menos un destinatario configurado

        Mantiene el comportamiento original del reminder automático.
        """
        if self._auto_sent:
            return  # Evitar re-envío si el usuario cambió de idioma

        self._auto_sent = True
        destinatarios = list(self.listbox_destinatarios.get(0, tk.END))
        if destinatarios:
            self._enviar_correo()

    # =========================================================================
    # SECCIÓN: GUARDAR CONFIGURACIÓN
    # =========================================================================

    def _save_config_ui(self, silent: bool = False):
        """
        Lee la UI, construye el config dict y lo guarda en config.json.

        Args:
            silent: Si True, no muestra mensaje de éxito (para auto-guardado tras envío)
        """
        config = self._get_config_from_ui()
        success, error_msg = save_config(config)

        if success:
            self.config = config  # Actualizar configuración en memoria
            if not silent:
                self._update_status(self.t("msg_config_saved"), "green")
        else:
            self._update_status(self.t("msg_config_error", error=error_msg), "red")

    # =========================================================================
    # SECCIÓN: MULTI-IDIOMA (cambio de idioma en tiempo real)
    # =========================================================================

    def _change_language(self, lang: str):
        """
        Cambia el idioma de la interfaz y reconstruye la UI completa.

        Preserva todos los datos ingresados por el usuario antes de reconstruir.
        La bandera _auto_sent evita que se dispare un nuevo auto-envío.

        Args:
            lang: Código de idioma ("es" o "en")
        """
        if lang == self.lang:
            return  # Ya está en el idioma solicitado, no hacer nada

        # ── Guardar datos actuales antes de destruir la UI ──
        current_config = self._get_config_from_ui()
        current_config["idioma"] = lang

        # ── Actualizar idioma y recargar strings ──
        self.lang = lang
        self.strings = load_locale(lang)

        # ── Destruir todos los widgets y reconstruir la UI en el nuevo idioma ──
        for widget in self.root.winfo_children():
            widget.destroy()

        # Recrear variables de Tkinter (se pierden al destruir widgets)
        self.send_method_var = tk.StringVar(value=current_config.get("metodo_envio", "com"))
        self.smtp_preset_var = tk.StringVar(value="Hotmail/Outlook.com")
        self.config = current_config

        self._build_ui()
        self._populate_fields_from(current_config)
        # _auto_sent sigue siendo True si ya se envió → no re-dispara el auto-envío

    # =========================================================================
    # SECCIÓN: SALIDA
    # =========================================================================

    def _salir(self):
        """Cierra la aplicación destruyendo la ventana raíz de Tkinter."""
        self.root.destroy()
