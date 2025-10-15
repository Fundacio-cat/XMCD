sudo apt update
sudo apt install -y python3 python3-pip
sudo apt install -y firefox-esr
sudo apt install -y chromium-chromedriver
sudo apt install -y xvfb

# Configurar pip per permetre instal·lació sense entorn virtual
mkdir -p ~/.config/pip
echo "[global]" > ~/.config/pip/pip.conf
echo "break-system-packages = true" >> ~/.config/pip/pip.conf

pip install --upgrade setuptools wheel
pip install -r requeriments.txt

chmod +x /home/catalanet/XMCD/Controladors/*

