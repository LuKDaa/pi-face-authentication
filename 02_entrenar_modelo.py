import cv2
import numpy as np
from PIL import Image
import os

# --- RUTAS Y CONFIGURACIÓN ---
path = 'dataset'
model_path = 'model'
recognizer = cv2.face.LBPHFaceRecognizer_create()

if not os.path.exists(model_path):
    os.makedirs(model_path)
    print(f"Directorio '{model_path}' creado.")
    
# --- FUNCIÓN PARA OBTENER DATOS ---
def getImagesAndLabels(path):
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
    faceSamples = []
    ids = []

    for imagePath in imagePaths:
        # Ignora cualquier archivo que no sea .jpg
        if not imagePath.endswith('.jpg'):
            continue

        # Abre la imagen en escala de grises
        PIL_img = Image.open(imagePath).convert('L') 
        img_numpy = np.array(PIL_img, 'uint8')

        # Obtiene el ID del nombre del archivo
        id = int(os.path.split(imagePath)[-1].split(".")[1])
        
        faceSamples.append(img_numpy)
        ids.append(id)

    return faceSamples, ids

# --- ENTRENAMIENTO ---
print("\n [INFO] Entrenando el modelo con los rostros. Esto puede tardar unos segundos...")
faces, ids = getImagesAndLabels(path)

if not faces:
    print("[ERROR] No se encontraron rostros en el dataset. Ejecuta primero '01_capturar_rostros.py'")
else:
    recognizer.train(faces, np.array(ids))

    # Guardar el modelo entrenado
    recognizer.write(f'{model_path}/trainer.yml')

    # Imprimir el número de usuarios entrenados
    print(f"\n [INFO] {len(np.unique(ids))} rostros entrenados. Saliendo del programa.")
