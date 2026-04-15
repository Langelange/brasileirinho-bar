#!/usr/bin/env python3
"""
Script para gerar o executável do Brasileirinho Bar.
Uso: python build.py
"""

import subprocess
import sys
import os

# Instalar PyInstaller se não tiver
subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller", "customtkinter", "Pillow"])

# Caminhos
base_dir = os.path.dirname(os.path.abspath(__file__))
main_py = os.path.join(base_dir, "main.py")
icon = os.path.join(base_dir, "assets", "logo.ico")
assets_dir = os.path.join(base_dir, "assets")

# Encontrar pasta do customtkinter para incluir
import customtkinter
ctk_path = os.path.dirname(customtkinter.__file__)

cmd = [
    sys.executable, "-m", "PyInstaller",
    "--noconfirm",
    "--onefile",
    "--windowed",                          # sem janela de console
    "--name", "BrasileirinhoBar",
    "--icon", icon,
    "--add-data", f"{assets_dir}{os.pathsep}assets",
    "--add-data", f"{ctk_path}{os.pathsep}customtkinter",
    "--hidden-import", "customtkinter",
    "--hidden-import", "PIL",
    "--hidden-import", "PIL._tkinter_finder",
    main_py
]

print("Gerando executável...")
print(" ".join(cmd))
subprocess.check_call(cmd)

print("\n[OK] Executavel gerado em: dist/BrasileirinhoBar.exe")
print("     Copie o .exe para qualquer pasta e execute!")
