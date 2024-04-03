from flask import Flask, request, jsonify, abort  # Importa las clases y funciones necesarias de Flask para crear la aplicación y manejar solicitudes.
from flask_sqlalchemy import SQLAlchemy  # Importa SQLAlchemy para utilizarlo como ORM.
from dotenv import load_dotenv  # Importa la función para cargar variables de entorno desde un archivo .env.
import os  # Importa el módulo os para interactuar con el sistema operativo, como leer variables de entorno.

load_dotenv()  # Carga las variables de entorno desde un archivo .env, si está presente.

app = Flask(__name__)  # Crea una instancia de la aplicación Flask.
# Configura la URI de la base de datos y desactiva el seguimiento de modificaciones en SQLAlchemy.
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)  # Crea una instancia de SQLAlchemy vinculada a la aplicación Flask.

class Task(db.Model):  # Define un modelo de datos para 'Task' usando SQLAlchemy.
    id = db.Column(db.Integer, primary_key=True)  # Define un campo de identificación como clave primaria y entero.
    name = db.Column(db.String(80), nullable=False)  # Define un campo para el nombre de la tarea, obligatorio.
    status = db.Column(db.Boolean, default=False)  # Define un campo para el estado de la tarea, por defecto en falso.

    def to_dict(self):  # Método que convierte la instancia en un diccionario para facilitar la serialización JSON.
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status
        }

@app.route('/')  # Define la ruta raíz o endpoint de la aplicación.
def index():
    return 'Welcome to my ORM App'  # Devuelve un mensaje de bienvenida.

@app.route('/create_task', methods=['POST'])  # Define la ruta para crear una nueva tarea, aceptando solo POST.
def create_task():
    # Verifica que la solicitud contenga JSON y el campo 'name'.
    if not request.json or not 'name' in request.json:
        abort(400)  # Si no es así, aborta con el código de estado 400 (Bad Request).
    # Crea una instancia de Task con los datos proporcionados.
    task = Task(name=request.json['name'], status=request.json.get('status', False))
    db.session.add(task)  # Añade la tarea a la sesión de la base de datos.
    db.session.commit()  # Guarda los cambios en la base de datos.
    return jsonify(task.to_dict()), 201  # Devuelve la tarea creada y el código de estado 201 (Created).

@app.route('/tasks', methods=['GET'])  # Define la ruta para obtener todas las tareas, aceptando solo GET.
def get_tasks():
    tasks = Task.query.all()  # Obtiene todas las tareas de la base de datos.
    # Serializa las tareas a JSON y las devuelve.
    return jsonify([task.to_dict() for task in tasks])


@app.route('/tasks/<int:task_id>', methods=['GET'])  # Define la ruta para obtener una tarea específica por su ID.
def get_task(task_id):
    task = Task.query.get(task_id)  # Intenta obtener la tarea por su ID.
    if task is None:  # Si la tarea no existe, aborta con el código de estado 404 (Not Found).
        abort(404)
    return jsonify(task.to_dict())  # Devuelve la tarea encontrada.

@app.route('/tasks_update/<int:task_id>', methods=['GET'])  # Ruta para actualizar el estado de una tarea específica.
def update_task(task_id):
    task = Task.query.get(task_id)  # Busca la tarea por su ID.
    if task is None:  # Si no encuentra la tarea, aborta con 404.
        abort(404)
    task.status = not task.status  # Cambia el estado de la tarea.
    return jsonify(task.to_dict())  # Devuelve la tarea actualizada.

@app.route('/tasks_delete/<int:task_id>', methods=['DELETE'])  # Ruta para eliminar una tarea específica.
def delete_task(task_id):
    task = Task.query.get(task_id)  # Busca la tarea por su ID.
    if task is None:  # Si la tarea no existe, aborta con 404.
        abort(404)
    db.session.delete(task)  # Elimina la tarea de la sesión de la base de datos.
    db.session.commit()  # Guarda los cambios en la base de datos.
    return jsonify({'status': True}), 201  # Devuelve un estado de éxito.

if __name__ == '_main_':  # Verifica si el archivo se ejecuta como script principal.
    with app.app_context():  # Crea un contexto de aplicación para operaciones que necesitan el contexto.
        db.create_all()  # Crea las tablas de la base de datos basándose en los modelos definidos.
        print("Tables created...")

    app.run(debug=True)  # Inicia la aplicación en modo de depuración.