#!/bin/bash

mkdir $HOME/.config/ICCUWN/
curl -o $HOME/.config/ICCUWN/iccuwn.py https://raw.githubusercontent.com/s-liwka/ICCUWN/main/iccuwn.py
curl -o /tmp/requirements.txt https://raw.githubusercontent.com/s-liwka/ICCUWN/main/requirements.txt
curl -o $HOME/.config/ICCUWN/run.sh https://raw.githubusercontent.com/s-liwka/ICCUWN/main/LinuxInstaller/run.sh
curl -o $HOME/.local/share/applications/ICCUWN.desktop https://raw.githubusercontent.com/s-liwka/ICCUWN/main/LinuxInstaller/iccuwn.desktop
chmod +x $HOME/.local/share/applications/ICCUWN.desktop
python -m venv $HOME/.config/ICCUWN/iccuwn-venv
pip install -r /tmp/requirements.txt
$HOME/.config/ICCUWN/run.sh