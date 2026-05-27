"""Rutas de la API de tareas."""
from flask import Blueprint, jsonify, request

from flask_debugging_example_api.services import tareas as servicio


tareas_bp = Blueprint('tareas', __name__)


@tareas_bp.route('', methods=['GET'])
def listar():
    """
    GET /tareas?completada=true&orden=vence

    Soporta:
        - `completada=true|false` para filtrar por estado.
        - `orden=vence` para ordenar por fecha de vencimiento.
    """
    filtros = {}

    # Aca esta el BUG #1: pasamos el string 'true'/'false' tal cual, no como bool.
    # Para arreglarlo habria que castear: filtros['completada'] = (request.args.get('completada') == 'true')
    if 'completada' in request.args:
        filtros['completada'] = request.args.get('completada')

    if request.args.get('orden'):
        filtros['orden'] = request.args.get('orden')

    return jsonify(servicio.listar(filtros))


@tareas_bp.route('/<tarea_id>', methods=['GET'])
def obtener(tarea_id):
    """
    GET /tareas/<id>

    BUG #3: la ruta deberia ser `/<int:tarea_id>` para que Flask convierta el
    parametro a int. Como esta, llega como string al servicio.
    """
    tarea = servicio.obtener(tarea_id)
    if tarea is None:
        return jsonify({'error': 'No encontrada'}), 404
    return jsonify(tarea)


@tareas_bp.route('', methods=['POST'])
def crear():
    """
    POST /tareas
    Body: { "titulo": "...", "vence": "YYYY-MM-DD", "prioridad": 1|2|3, "completada": true|false }
    """
    datos = request.get_json()
    if not datos or 'titulo' not in datos:
        return jsonify({'error': 'titulo es obligatorio'}), 400
    nueva = servicio.crear(datos)
    return jsonify(nueva), 201


@tareas_bp.route('/<tarea_id>', methods=['DELETE'])
def eliminar(tarea_id):
    """DELETE /tareas/<id>."""
    if servicio.eliminar(tarea_id):
        return '', 204
    return jsonify({'error': 'No encontrada'}), 404


@tareas_bp.route('/stats', methods=['GET'])
def stats():
    """GET /tareas/stats — estadisticas agregadas."""
    return jsonify(servicio.estadisticas())
