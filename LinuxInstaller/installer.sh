#!/bin/bash

mkdir $HOME/.config/ICCUWN/
echo "Downloading stuff..."
curl -o $HOME/.config/ICCUWN/iccuwn.py https://raw.githubusercontent.com/s-liwka/ICCUWN/main/iccuwn.py
curl -o /tmp/requirements.txt https://raw.githubusercontent.com/s-liwka/ICCUWN/main/requirements.txt
curl -o $HOME/.config/ICCUWN/run.sh https://raw.githubusercontent.com/s-liwka/ICCUWN/main/LinuxInstaller/run.sh
curl -o $HOME/.local/share/applications/ICCUWN.desktop https://raw.githubusercontent.com/s-liwka/ICCUWN/main/LinuxInstaller/iccuwn.desktop
chmod +x $HOME/.local/share/applications/ICCUWN.desktop
echo "Creating the virtual enviroment..."
python -m venv $HOME/.config/ICCUWN/iccuwn-venv
source  $HOME/.config/ICCUWN/iccuwn-venv/bin/activate
echo "Installing requirements..."
pip install -r /tmp/requirements.txt
echo "*****************************************************************"
echo "Finished! ICCUWN.desktop should be in ~/.local/share/applications"
echo "You should be able to look it up using your application Launcher"
echo "Press Enter to exit..."
echo "*****************************************************************"
read
exit