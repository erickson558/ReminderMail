# =============================================================================
# main.py - Punto de entrada principal de la aplicación ReminderMail
# Responsabilidad: Inicializar Tkinter y lanzar la ventana principal.
# =============================================================================

import tkinter as tk
import sys
import os

# ── Ajustar sys.path para importaciones relativas en modo script ──
# En modo ejecutable (PyInstaller), esto no es necesario pero no hace daño.
# En modo script (desarrollo), garantiza que los módulos de src/ se encuentren.
if not getattr(sys, 'frozen', False):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.main_window import ReminderMailApp  # Importar la clase principal de la GUI


def main():
    """
    Función principal de la aplicación.
    Crea la ventana raíz de Tkinter, configura el ícono y lanza el bucle de eventos.
    """
    # Crear la ventana raíz de Tkinter
    root = tk.Tk()

    # ── Intentar establecer el ícono de la ventana (.ico) ──
    # Si no existe el archivo de ícono, continuar sin él (no es un error fatal).
    try:
        if getattr(sys, 'frozen', False):
            # Modo ejecutable: el ícono está junto al .exe
            icon_path = os.path.join(os.path.dirname(sys.executable), "reminder.ico")
        else:
            # Modo script: el ícono está en la raíz del proyecto
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reminder.ico")

        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)
    except Exception:
        pass  # Si falla la asignación de ícono, continuar normalmente

    # ── Crear y lanzar la aplicación principal ──
    app = ReminderMailApp(root)  # noqa: F841 - La instancia mantiene referencias a widgets
    root.mainloop()              # Bucle principal de eventos de Tkinter


if __name__ == "__main__":
    main()
