"""Entry point de la API de tareas con bugs intencionales para debuggear."""
from flask import Flask

from flask_debugging_example_api.routes.tareas import tareas_bp


app = Flask(__name__)
app.register_blueprint(tareas_bp, url_prefix='/flask_debugging_example_api/tareas')


@app.route('/')
def health():
    return {'status': 'ok'}


if __name__ == '__main__':
    # debug=True activa el reloader + el debugger de Werkzeug en el navegador.
    # Para usar el debugger de VS Code, levantar con la config de launch.json.
    app.run(host='0.0.0.0', port=5000, debug=True)
