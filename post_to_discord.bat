@echo off
cd /d "%~dp0"
python discord_message.py | python discord_poster.py
pause