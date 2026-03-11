@echo off
cd /d "%~dp0"
python compose_message.py | python send_message.py
pause