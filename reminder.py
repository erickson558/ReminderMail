import tkinter as tk
from tkinter import simpledialog
import json
import os
import sys
import win32com.client as win32

CONFIG_FILE = "config.json"

# Determinar la ruta base: si el programa está congelado (ejecutable) o en modo script.
if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE_PATH = os.path.join(base_path, CONFIG_FILE)

def load_config():
    """Carga la configuración guardada si existe."""
    if os.path.exists(CONFIG_FILE_PATH):
        with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"destinatarios": [], "asunto": "", "cuerpo": ""}

def update_status(message, color="black"):
    """Actualiza el mensaje de la barra de estado."""
    status_label.config(text=message, fg=color)

def save_config():
    """Guarda la configuración actual en un archivo JSON."""
    config = {
        "destinatarios": listbox_destinatarios.get(0, tk.END),
        "asunto": entry_asunto.get(),
        "cuerpo": text_cuerpo.get("1.0", tk.END).strip()
    }
    try:
        with open(CONFIG_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        update_status("Configuración guardada.", "green")
    except Exception as e:
        update_status(f"Error al guardar la configuración: {e}", "red")

def agregar_destinatario():
    """Agrega un destinatario a la lista."""
    nuevo = simpledialog.askstring("Agregar destinatario", "Ingrese el correo del destinatario:")
    if nuevo:
        listbox_destinatarios.insert(tk.END, nuevo)
        update_status("Destinatario agregado.", "green")

def eliminar_destinatario():
    """Elimina el destinatario seleccionado."""
    seleccion = listbox_destinatarios.curselection()
    if not seleccion:
        update_status("Seleccione un destinatario para eliminar.", "red")
        return
    for index in seleccion[::-1]:
        listbox_destinatarios.delete(index)
    update_status("Destinatario(s) eliminado(s).", "green")

def enviar_correo():
    """Envía el correo utilizando Outlook 365."""
    destinatarios = ";".join(listbox_destinatarios.get(0, tk.END))
    asunto = entry_asunto.get()
    cuerpo = text_cuerpo.get("1.0", tk.END).strip()
    
    if not destinatarios:
        update_status("Agregue al menos un destinatario.", "red")
        return

    try:
        outlook = win32.Dispatch('Outlook.Application')
        mail = outlook.CreateItem(0)  # 0 corresponde a un correo
        mail.To = destinatarios
        mail.Subject = asunto
        mail.Body = cuerpo
        mail.Send()
        update_status("Correo enviado exitosamente. Se cerrará en 1 minuto.", "green")
        # Espera 60,000 milisegundos (1 minuto) y simula el clic en el botón "Salir"
        root.after(60000, btn_salir.invoke)
    except Exception as e:
        update_status(f"No se pudo enviar el correo. Error: {e}", "red")

def salir():
    """Cierra la aplicación."""
    root.destroy()

# Configuración de la ventana principal con Tkinter
root = tk.Tk()
root.title("Enviar Correo Outlook 365")

# Lista de destinatarios
frame_destinatarios = tk.Frame(root)
frame_destinatarios.pack(pady=(10, 0), fill=tk.X, padx=10)

label_destinatarios = tk.Label(frame_destinatarios, text="Destinatarios:")
label_destinatarios.pack(anchor="w")

listbox_destinatarios = tk.Listbox(frame_destinatarios, width=50, height=5)
config = load_config()
for destinatario in config.get("destinatarios", []):
    listbox_destinatarios.insert(tk.END, destinatario)
listbox_destinatarios.pack(pady=5)

frame_buttons_dest = tk.Frame(frame_destinatarios)
frame_buttons_dest.pack()

btn_agregar = tk.Button(frame_buttons_dest, text="Agregar", width=15, command=agregar_destinatario)
btn_agregar.pack(side=tk.LEFT, padx=5)

btn_eliminar = tk.Button(frame_buttons_dest, text="Eliminar", width=15, command=eliminar_destinatario)
btn_eliminar.pack(side=tk.LEFT, padx=5)

# Campo para el asunto
label_asunto = tk.Label(root, text="Asunto:")
label_asunto.pack(pady=(10, 0))
entry_asunto = tk.Entry(root, width=50)
entry_asunto.insert(0, config.get("asunto", ""))
entry_asunto.pack(pady=5)

# Campo para el cuerpo del correo
label_cuerpo = tk.Label(root, text="Cuerpo del correo:")
label_cuerpo.pack(pady=(10, 0))
text_cuerpo = tk.Text(root, width=50, height=10)
text_cuerpo.insert("1.0", config.get("cuerpo", ""))
text_cuerpo.pack(pady=5)

# Frame para los botones de acción
frame_buttons = tk.Frame(root)
frame_buttons.pack(pady=10)

btn_enviar = tk.Button(frame_buttons, text="Enviar", width=20, command=enviar_correo)
btn_enviar.pack(side=tk.LEFT, padx=5)

btn_guardar = tk.Button(frame_buttons, text="Guardar configuración", width=20, command=save_config)
btn_guardar.pack(side=tk.LEFT, padx=5)

btn_salir = tk.Button(frame_buttons, text="Salir", width=20, command=salir)
btn_salir.pack(side=tk.LEFT, padx=5)

# Barra de estado en la parte inferior
status_label = tk.Label(root, text="", bd=1, relief=tk.SUNKEN, anchor=tk.W)
status_label.pack(side=tk.BOTTOM, fill=tk.X)

# Simular el clic en el botón "Enviar" 1 segundo después de iniciar la aplicación
root.after(1000, enviar_correo)

root.mainloop()
