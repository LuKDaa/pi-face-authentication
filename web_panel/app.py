from flask import Flask, render_template, request, redirect, url_for, flash
import json
import os
import subprocess
import sqlite3

app = Flask(__name__)
app.secret_key = 'admin123'

# Ruta al archivo de usuarios (relativa a la carpeta del proyecto)
USERS_FILE = '../users.json'
DB_PATH = '../database/logs.db'
def read_users():
    """Lee los usuarios del archivo JSON."""
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {} # Retorna un diccionario vacío si el JSON está corrupto o vacío

def write_users(users):
    """Escribe los usuarios en el archivo JSON."""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

@app.route('/')
def index():
    users = read_users()
    # Ordena los usuarios por ID numérico para una mejor visualización
    try:
        sorted_users = sorted(users.items(), key=lambda item: int(item[0]))
    except ValueError:
        sorted_users = users.items() # Si hay IDs no numéricos, no los ordena
    return render_template('index.html', users=sorted_users)

@app.route('/add_user', methods=['POST'])
def add_user():
    user_id = request.form['user_id']
    user_name = request.form['user_name'].strip()

    if not user_id.isdigit() or not user_name:
        flash('El ID debe ser un número y el nombre no puede estar vacío.', 'error')
        return redirect(url_for('index'))

    users = read_users()
    
    if user_id in users:
        flash(f'El ID {user_id} ya existe.', 'error')
        return redirect(url_for('index'))

    users[user_id] = user_name
    write_users(users)
    
    flash(f'Usuario "{user_name}" (ID: {user_id}) añadido. Ahora debes capturar su rostro.', 'success')
    return redirect(url_for('index'))

@app.route('/train_model')
def train_model():
    """Ejecuta el script de entrenamiento."""
    flash('Iniciando entrenamiento del modelo... Esto puede tardar.', 'info')
    try:
        # La ruta es relativa a la ubicación de app.py
        subprocess.run(['python3', '02_entrenar_modelo.py'], cwd='..', check=True, capture_output=True, text=True)
        flash('Modelo entrenado exitosamente. Reinicia el script de reconocimiento para aplicar los cambios.', 'success')
    except subprocess.CalledProcessError as e:
        flash(f'Error durante el entrenamiento: {e.stdout} {e.stderr}', 'error')
    
    return redirect(url_for('index'))

@app.route('/logs')
def view_logs():
    """Muestra los registros de acceso desde la base de datos."""
    try:
        # Comprueba si la base de datos existe
        if not os.path.exists(DB_PATH):
            flash('La base de datos de registros aún no existe. Aún no se ha detectado ningún acceso.', 'info')
            return render_template('logs.html', logs=[]) # Envía lista vacía

        conn = sqlite3.connect(DB_PATH)
        # Esto es clave: permite que la plantilla acceda a los datos por nombre
        conn.row_factory = sqlite3.Row
        
        c = conn.cursor()
        # Trae los logs, del más reciente al más antiguo
        c.execute("SELECT user_name, access_time FROM access_logs ORDER BY access_time DESC")
        logs = c.fetchall()
        conn.close()
        
        # Pasa la variable 'logs' a la plantilla
        return render_template('logs.html', logs=logs)

    except Exception as e:
        flash(f'Error al leer la base de datos de logs: {e}', 'error')
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
