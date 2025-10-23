import cv2
import os

# --- CREACIÓN DE CARPETAS ---
dataset_path = 'dataset'
if not os.path.exists(dataset_path):
    os.makedirs(dataset_path)
    print(f"Directorio '{dataset_path}' creado.")

# --- CONFIGURACIÓN ---
cam = cv2.VideoCapture(0)
cam.set(3, 640) # Ancho
cam.set(4, 480) # Alto

face_detector = cv2.CascadeClassifier('cascades/haarcascade_frontalface_default.xml')

# --- ENTRADA DE USUARIO ---
face_id = input('\n Ingresa el ID de usuario (el mismo que en la web) y presiona <enter> ==>  ')
print("\n [INFO] Iniciando captura de rostro. Mira a la cámara y espera...")

# --- CAPTURA DE IMÁGENES ---
count = 0
while True:
    ret, img = cam.read()
    if not ret:
        print("[ERROR] No se pudo capturar la imagen de la cámara.")
        break
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_detector.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
        count += 1

        # Guardar la imagen del rostro capturado
        cv2.imwrite(f"{dataset_path}/User.{face_id}.{count}.jpg", gray[y:y+h, x:x+w])
        
        # Muestra el frame en una ventana
        cv2.imshow('Capturando Rostro', img)

    # Condición de salida
    k = cv2.waitKey(100) & 0xff
    if k == 27: # Presionar 'ESC' para salir
        break
    elif count >= 50: # Tomar 50 muestras de rostro y salir
         break

# --- LIMPIEZA ---
print("\n [INFO] Finalizando captura.")
cam.release()
cv2.destroyAllWindows()
