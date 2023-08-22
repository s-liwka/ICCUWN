@echo off
call %localappdata%\ICCUWN\iccuwn-venv\Scripts\activate.bat
start /B pythonw %localappdata%\ICCUWN\iccuwn.py
exit