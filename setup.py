import sys
from cx_Freeze import setup, Executable
import os


incluir_arquivos = [
    "Recursos",
    "Arquivos"
]

build_exe_options = {
    "packages": ["pygame", "random", "time", "threading", "pyttsx3", "speech_recognition", "json", "os", "math"],
    "include_files": incluir_arquivos
}

setup(
    name="Combate Cósmico",
    version="1.0",
    description="Jogo feito com Pygame",
    options={"build_exe": build_exe_options},
    executables=[Executable("Main.py", base=None)]
)