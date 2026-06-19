# -*- mode: python ; coding: utf-8 -*-
# =============================================================================
# reminder.spec - Configuración de PyInstaller para compilar ReminderMail a .exe
#
# Uso: pyinstaller reminder.spec
# Genera: dist/ReminderMail.exe
#
# Notas:
# - console=False → sin ventana de consola (aplicación de escritorio)
# - onefile → un único ejecutable portátil
# - locales/ se empaqueta dentro del .exe (extraídos a sys._MEIPASS en runtime)
# - config.json NO se empaqueta (se lee/escribe junto al .exe, es persistente)
# - Coloca reminder.ico en el directorio raíz para personalizar el ícono
# =============================================================================

import os

block_cipher = None

# ── Buscar el ícono .ico en el directorio del proyecto ──
# Prioridad: reminder.ico → primer .ico encontrado → None (sin ícono)
_base_dir = os.path.dirname(os.path.abspath('reminder.spec'))
_icon = None
for _ico_name in ['reminder.ico', 'reminder_electronicclock_recordatori_6071.ico']:
    _candidate = os.path.join(_base_dir, _ico_name)
    if os.path.exists(_candidate):
        _icon = _candidate
        break

a = Analysis(
    ['main.py'],                      # Nuevo punto de entrada (antes era reminder.py)
    pathex=['.'],                     # Directorio raíz del proyecto en sys.path
    binaries=[],
    datas=[
        ('locales/', 'locales/'),     # Empaquetar traducciones dentro del .exe
    ],
    hiddenimports=[
        'win32com',
        'win32com.client',
        'win32api',
        'pywintypes',
        'pythoncom',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ReminderMail',              # Nombre del ejecutable final
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,                        # Comprimir con UPX para reducir tamaño
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,                    # Sin ventana de consola (aplicación de escritorio)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=_icon,                       # Ícono del ejecutable (None si no existe reminder.ico)
)
