"""
Punto de entrada legado para compatibilidad.

Este archivo existía como implementación monolítica original. Ahora delega al
entrypoint principal para que cualquier ejecución o compilación basada en
`reminder.py` use la misma aplicación modular y las mismas correcciones.
"""

from main import main


if __name__ == "__main__":
    main()
