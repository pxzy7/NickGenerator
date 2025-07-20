@echo off
REM Instala os pacotes necessários direto via pip (ignora se já tiver)
pip install customtkinter requests colorama

REM Roda o script
python gen.py

pause
