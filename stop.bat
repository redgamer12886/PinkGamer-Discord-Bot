@echo off
cd /d "e:\5 minute coding adventures\PinkGamer\PinkGamerBot"
start /wait pythonw killtext.py
taskkill /f /im pythonw.exe