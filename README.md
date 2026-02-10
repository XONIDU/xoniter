# 📄 XONITER

---

## 🎯 Objetivo

XONITER proporciona una interfaz web mínima para enviar y ejecutar comandos en una máquina Linux desde otro dispositivo en la misma red local. Está pensado para agilizar la introducción de comandos en sistemas sin entorno gráfico (terminal pura) desde un móvil o portátil en la LAN.

---

## 🛠️ Instalación (rápida)

Instala Python 3 y Flask:

- Arch Linux:
```bash
sudo pacman -S python-pip
pip install flask
```

- Ubuntu / Debian:
```bash
sudo apt update
sudo apt install python3 python3-pip -y
pip3 install flask
```

- Windows:
```powershell
pip install flask
```

- macOS (Homebrew):
```bash
brew install python3
pip3 install flask
```

---

## ▶️ Ejecución

Desde la carpeta del proyecto:

- Para exponer en la LAN (accesible desde otros dispositivos):
```bash
python start.py
# o
python3 start.py --host 0.0.0.0 --port 5100
```

- Para restringir solo a la máquina local:
```bash
python start.py --host 127.0.0.1 --port 5100
```

Abre en el navegador del dispositivo cliente:
http://<IP_DEL_HOST>:5100/

---

## 🧾 Uso

- Pega o escribe el comando en el área de texto y pulsa "Run".  
- Revisa STDOUT, STDERR y el código de salida que devuelve la página.  
- Usa el campo de timeout para limitar el tiempo de ejecución (opcional).

---

## ❓ ¿Dudas o sugerencias?

Puedes comunicarte con el equipo de **XONIDU** a través de los siguientes medios:

- 📸 **Instagram:** [@xonidu](https://instagram.com/xonidu)  
- 📘 **Facebook:** [xonidu](https://www.facebook.com/profile.php?id=61572209206888)  
- 📧 **Email:** xonidu@gmail.com
