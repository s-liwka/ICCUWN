@echo off
mkdir %localappdata%\ICCUWN
curl -o %localappdata%\ICCUWN\iccuwn.py https://raw.githubusercontent.com/s-liwka/ICCUWN/main/iccuwn.py
curl -o %localappdata%\ICCUWN\run.bat https://raw.githubusercontent.com/s-liwka/ICCUWN/main/WindowsInstaller/run.bat
python -m venv %localappdata%\ICCUWN\iccuwn-venv
call %localappdata%\ICCUWN\iccuwn-venv\Scripts\activate.bat
curl -o %localappdata%\ICCUWN\requirements.txt https://raw.githubusercontent.com/s-liwka/ICCUWN/main/requirements.txt
pip install -r requirements.txt
set "source=%localappdata%\ICCUWN\run.bat"
set "destination=%userprofile%\Desktop\ICCUWN.lnk"
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%destination%'); $Shortcut.TargetPath = '%source%'; $Shortcut.Save()"
%localappdata%\ICCUWN\run.bat
