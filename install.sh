#!/bin/bash

echo "=========================================="
echo "Instal·lació XMCD per a Raspberry Pi"
echo "=========================================="

# Actualitzar sistema
echo "Actualitzant el sistema..."
sudo apt update

# Instal·lar dependències del sistema
echo "Instal·lant dependències del sistema..."
sudo apt install -y python3 python3-pip python3-venv python3-full
sudo apt install -y firefox-esr
sudo apt install -y chromium-chromedriver
sudo apt install -y xvfb

# Crear entorn virtual
echo "Creant entorn virtual..."
python3 -m venv venv

# Activar entorn virtual i instal·lar paquets
echo "Instal·lant paquets Python..."
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requeriments.txt

# Configurar permisos
if [ -d "Controladors" ]; then
    chmod +x Controladors/*
fi

echo ""
echo "=========================================="
echo "✓ Instal·lació completada!"
echo "=========================================="
echo ""
echo "Per executar el programa:"
echo "  1. Activa l'entorn virtual:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Executa el monitor:"
echo "     python monitor.py -c config.json"
echo ""
echo "  O amb camoufox:"
echo "     python monitor_camoufox.py -c config.json"
echo ""

