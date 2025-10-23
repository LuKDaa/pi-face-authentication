import cv2
import RPi.GPIO as GPIO
import time
import sqlite3
import os
import json

# --- CONFIGURACIÓN DE GPIO PARA EL SERVO ---
SERVO_PIN = 17 # Usar el pin GPIO 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
GPIO.setwarnings(False)

# Configurar PWM en el pin del servo con una frecuencia de 50Hz
pwm = GPIO.PWM(SERVO_PIN, 50) 
pwm.start(0) # Iniciar el servo en una posición neutral

# --- FUNCIÓN PARA MOVER EL SERVO A UN ÁNGULO ESPECÍFICO ---
def set_angle(angle):
    duty = angle / 18 + 2
    GPIO.output(SERVO_PIN, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(1) # Esperar 1 segundo para que el servo llegue a la posición
    GPIO.output(SERVO_PIN, False)
    pwm.ChangeDutyCycle(0)

# --- CONFIGURACIÓN DE LA BASE DE DATOS ---
DB_PATH = 'database/logs.db'

def setup_database():
    if not os.path.exists('database'):
        os.makedirs('database')
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS access_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL,
            access_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def log_access(user_name):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO access_logs (user_name) VALUES (?)", (user_name,))
        conn.commit()
        conn.close()
        print(f"[LOG] Acceso concedido a {user_name}")
    except Exception as e:
        print(f"[ERROR] No se pudo escribir en la base de datos: {e}")

# --- CARGAR NOMBRES DE USUARIOS DESDE JSON ---
def load_user_names():
    try:
        with open('users.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("[ERROR] El archivo users.json no se encontró.")
        return {}

# --- CONFIGURACIÓN DE RECONOCIMIENTO FACIAL ---
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('model/trainer.yml')
cascadePath = "cascades/haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascadePath)
font = cv2.FONT_HERSHEY_SIMPLEX

# Nombres asociados a los IDs (cargados desde JSON)
names = load_user_names()
if not names:
    print("[ADVERTENCIA] No se cargaron nombres de usuario. Revisa el archivo users.json")

# --- INICIALIZACIÓN DE CÁMARA ---
cam = cv2.VideoCapture(0)
cam.set(3, 640) # Ancho
cam.set(4, 480) # Alto

minW = 0.1 * cam.get(3)
minH = 0.1 * cam.get(4)

# --- FUNCIÓN PRINCIPAL ---
def main():
    setup_database()
    door_open_time = 0
    door_duration = 2 # segundos que la puerta permanecerá abierta
    
    print("[INFO] Calibrando servo a posición de cerrado...")
    set_angle(0)

    while True:
        ret, img = cam.read()
        if not ret:
            break

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(int(minW), int(minH)),
        )

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            id, confidence = recognizer.predict(gray[y:y+h, x:x+w])

            if confidence < 50:
                user_id_str = str(id)
                user_name = names.get(user_id_str, "Desconocido")
                
                if door_open_time == 0:
                    print(f"[INFO] Acceso autorizado para {user_name}. Abriendo puerta...")
                    set_angle(90) # Mover el servo a 90 grados para "abrir"
                    door_open_time = time.time()
                    log_access(user_name)
            else:
                user_name = "Desconocido"

            confidence_text = "  {0}%".format(round(100 - confidence))
            cv2.putText(img, user_name, (x + 5, y - 5), font, 1, (255, 255, 255), 2)
            cv2.putText(img, confidence_text, (x + 5, y + h - 5), font, 1, (255, 255, 0), 1)

        if door_open_time > 0 and (time.time() - door_open_time) > door_duration:
            print("[INFO] Tiempo de acceso finalizado. Cerrando puerta...")
            set_angle(0) # Mover el servo de vuelta a 0 grados para "cerrar"
            door_open_time = 0
            
        cv2.imshow('Reconocimiento Facial', img)
        
        k = cv2.waitKey(10) & 0xff
        if k == 27: # Presionar 'ESC' para salir
            break

    # --- LIMPIEZA FINAL ---
    print("\n[INFO] Saliendo del programa y limpiando...")
    set_angle(0) # Dejar la puerta cerrada
    pwm.stop()
    GPIO.cleanup()
    cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
