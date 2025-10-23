# Sistema de Control de Acceso con Reconocimiento Facial para Raspberry Pi

Este proyecto utiliza OpenCV para crear un sistema de control de acceso ligero y optimizado para hardware limitado como la Raspberry Pi.

## Pasos para la Puesta en Marcha

### 1. Preparación del Hardware
- Conecta una cámara (USB o CSI) a tu Raspberry Pi.
- Conecta un módulo de relé al pin **GPIO 17** (o el que gustes, deberas cambiarlo en el codigo .py posteriormente).

### 2. Instalación del Software
1.  Clona o copia este repositorio en tu Raspberry Pi.
2.  Abre una terminal en la carpeta del proyecto `face-access-rasPI/`.
3.  Instala las dependencias de Python:
---
    pip3 install -r requirements.txt
---
4.  Descarga el clasificador Haar Cascade:
    - Ve a [este enlace](https://github.com/opencv/opencv/blob/master/data/haarcascades/haarcascade_frontalface_default.xml).
    - Descarga el archivo y reemplazalo en la carpeta `cascades/`.

### 3. Uso del Sistema

#### Paso 1: Añadir un Usuario
- Ejecuta el script de captura para registrar un nuevo rostro. Se te pedirá un ID numérico (ej: 1, 2, 3...).
---
    python3 01_capturar_rostros.py
---
- Sigue las instrucciones y asegúrate de que se guarden 50 imágenes en la carpeta `dataset/`.

#### Paso 2: Entrenar el Modelo
- Una vez que tengas las imágenes, entrena al reconocedor:
---
    python3 02_entrenar_modelo.py
---
- Esto creará o actualizará el archivo `model/trainer.yml`.

#### Paso 3: Iniciar el Reconocimiento
- Ejecuta el script principal. Es necesario usar `sudo` para tener permisos de acceso a los pines GPIO.
---
    sudo python3 03_reconocimiento_facial.py
---
- El sistema se activará, abrirá la cámara y comenzará a reconocer rostros. Al detectar un rostro autorizado, activará el relé en el GPIO 17.

### 4. Panel de Administración Web (Opcional)
- Para ver los registros de acceso y facilitar el re-entrenamiento, puedes usar el panel web.
- Abre una **segunda terminal** y navega a la carpeta `web_panel/`:
---
    python3 app.py
---
- Abre un navegador en **CUALQUIER DISPOSITIVO** de tu red local y ve a la dirección `http://[IP_DE_TU_RASPBERRY_PI]:5000`.