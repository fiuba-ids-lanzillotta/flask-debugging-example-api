"""
Servicio in-memory de tareas con BUGS INTENCIONALES.

Ver INSTRUCTOR.md para la lista de bugs y como debuggearlos.
"""
from datetime import datetime


# Estado in-memory. En un sistema real esto seria una base.
_TAREAS = [
    {'id': 1, 'titulo': 'Comprar pan',        'vence': '2026-06-01', 'completada': False, 'prioridad': 2},
    {'id': 2, 'titulo': 'Llamar al dentista', 'vence': '2026-05-28', 'completada': True,  'prioridad': 1},
    {'id': 3, 'titulo': 'Pagar la luz',       'vence': '2026-06-10', 'completada': False, 'prioridad': 3},
    {'id': 4, 'titulo': 'Estudiar Python',    'vence': '2026-05-30', 'completada': False, 'prioridad': 1},
    {'id': 5, 'titulo': 'Ordenar el escritorio', 'vence': '2026-06-15', 'completada': True, 'prioridad': 2},
]


def listar(filtros=None):
    """
    Lista tareas, opcionalmente filtrando por `completada` y/o ordenando por `vence`.

    BUG #1: el filtro `completada` viene como string desde la query
    ('true' / 'false') pero se compara con un bool. Resultado: el filtro NUNCA
    matchea, porque `'true' == True` es False en Python.

    BUG #2: el sort por fecha de vencimiento usa el string directamente. Como
    el formato es ISO ('YYYY-MM-DD'), POR CASUALIDAD el orden lexicografico
    coincide con el cronologico. Pero si alguien cargara una tarea con
    formato '01/06/2026', el orden seria erroneo. Como esta hoy parece andar:
    el bug esta latente.
    """
    filtros = filtros or {}
    resultado = list(_TAREAS)

    if 'completada' in filtros:
        resultado = [t for t in resultado if t['completada'] == filtros['completada']]

    if filtros.get('orden') == 'vence':
        resultado.sort(key=lambda t: t['vence'])

    return resultado


def obtener(tarea_id):
    """
    Devuelve la tarea con `id == tarea_id`, o None.

    BUG #3: el parametro viene como string desde la URL ('/tareas/3') pero
    los ids en `_TAREAS` son int. La comparacion `t['id'] == tarea_id` da
    False siempre, asi que la API devuelve 404 para TODAS las tareas.

    Para detectarlo: breakpoint en el `if`, inspeccionar `t['id']` y
    `tarea_id` en la Debug Console (o en el panel Variables) y comparar
    sus TIPOS con `type(t['id'])` y `type(tarea_id)`.
    """
    for t in _TAREAS:
        if t['id'] == tarea_id:
            return t
    return None


def crear(datos):
    """
    Crea una nueva tarea.

    BUG #4: el ID nuevo se asigna como `len(_TAREAS) + 1`. Si en algun momento
    se borra una tarea del medio (por ej. la 3), `len(_TAREAS)` queda en 4 y
    al crear una nueva se le asigna `5`, que YA EXISTE -> tareas duplicadas
    con el mismo ID. Bug latente: dificil de detectar hasta que alguien borra
    una tarea.

    BUG #5: si el caller no manda 'completada', se asume `False`. Pero el codigo
    usa `datos.get('completada')` que devuelve `None`, y `None` se serializa a
    JSON como `null`. Algunos clientes esperan `false`. Hay que normalizarlo.

    BUG #6 (subtil): `vence` se guarda tal cual venga del cliente. Si viene
    como `'2026-06-30T15:00:00Z'` o `'30/06/2026'` queda inconsistente con el
    resto de los datos. Falta normalizar a 'YYYY-MM-DD'.
    """
    nueva = {
        'id':         len(_TAREAS) + 1,
        'titulo':     datos['titulo'],
        'vence':      datos.get('vence'),
        'completada': datos.get('completada'),
        'prioridad':  datos.get('prioridad', 2),
    }
    _TAREAS.append(nueva)
    return nueva


def eliminar(tarea_id):
    """
    Borra la tarea con `id == tarea_id`. Devuelve True si la elimino, False
    si no la encontro.

    BUG: misma raiz que el #3: comparacion entre string y int por el id que
    viene de la URL. La eliminacion nunca encuentra la tarea.
    """
    global _TAREAS
    largo_inicial = len(_TAREAS)
    _TAREAS = [t for t in _TAREAS if t['id'] != tarea_id]
    return len(_TAREAS) < largo_inicial


def estadisticas():
    """
    Devuelve stats de las tareas: cantidad total, completadas, pendientes,
    promedio de prioridad, y la tarea mas urgente (la que vence antes).

    BUG #7: division por cero si no hay tareas (no hay handling).
    BUG #8: 'urgente' usa `min(..., key=lambda t: t['vence'])` sobre TODAS
    las tareas, incluyendo las completadas. Lo correcto es filtrar primero
    las pendientes.
    """
    total = len(_TAREAS)
    completadas = sum(1 for t in _TAREAS if t['completada'])
    pendientes = total - completadas
    promedio_prioridad = sum(t['prioridad'] for t in _TAREAS) / total
    urgente = min(_TAREAS, key=lambda t: t['vence'])

    return {
        'total':              total,
        'completadas':        completadas,
        'pendientes':         pendientes,
        'promedio_prioridad': promedio_prioridad,
        'urgente':            urgente,
    }
