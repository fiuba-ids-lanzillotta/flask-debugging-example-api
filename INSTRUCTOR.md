# Guion para el instructor — API

> **Aviso:** este archivo tiene las soluciones.

## Setup previo

1. Tener instalada la extension **REST Client** o **Thunder Client** en VS Code
   (para ejecutar `requests.http` con un click).
2. Levantar la API con el debugger: abrir `app.py` y presionar **F5** → seleccionar
   **"Python Debugger: Debug Python File"**.

## Bug #1 — filtro `completada` no funciona

**Donde:** `services/tareas.py::listar`.

**Demo:**
1. Ejecutar `GET /tareas?completada=true`.
2. La API devuelve las 5 tareas (incluyendo las pendientes).
3. Breakpoint en la linea `if 'completada' in filtros:`.
4. Inspeccionar `filtros['completada']` -> `'true'` (string).
5. Inspeccionar `t['completada']` -> `True` (bool).
6. En Debug Console: `'true' == True` -> `False`.

**Fix:**
En `routes/tareas.py`, castear:
```python
filtros['completada'] = request.args.get('completada', '').lower() == 'true'
```

## Bug #2 — sort por fecha funciona "por casualidad"

**Donde:** `services/tareas.py::listar`.

**Demo:**
1. Mostrar `GET /tareas?orden=vence`: las tareas vienen ordenadas correctamente.
2. Explicar: como el formato es ISO ('YYYY-MM-DD'), el orden lexicografico
   coincide con el cronologico. Pero el codigo NO esta haciendo sort por fecha,
   sino por string.
3. POST de una tarea con `vence: "01/07/2026"` (formato distinto):

   ```http
   POST /tareas
   { "titulo": "Test", "vence": "01/07/2026" }
   ```

4. Re-listar con orden por fecha. Ahora aparece donde no corresponde.

**Fix:**
```python
from datetime import datetime
resultado.sort(key=lambda t: datetime.fromisoformat(t['vence']))
```
Y normalizar el formato al crear (ver bug #6).

## Bug #3 — `GET /tareas/<id>` devuelve 404 siempre

**Donde:** ruta + servicio (`obtener`).

**Demo:**
1. `GET /tareas/3` -> 404.
2. Breakpoint en `for t in _TAREAS:` dentro del servicio.
3. En la Debug Console:
   ```python
   type(tarea_id)    # <class 'str'>
   type(t['id'])     # <class 'int'>
   '3' == 3          # False
   ```

**Fix (en la ruta):**
```python
@tareas_bp.route('/<int:tarea_id>', methods=['GET'])  # <- agregar int:
```

## Bug #4 — IDs duplicados al crear despues de borrar

**Donde:** `services/tareas.py::crear`.

**Demo:**
1. Listar tareas, hay 5 (ids 1-5).
2. Eliminar la tarea 3 (despues de arreglar bug #3, claro).
3. Crear una tarea nueva -> el ID asignado es `5` (porque `len(_TAREAS) = 4`).
4. **Pero ya existe una tarea con id 5.**

**Fix:**
```python
nueva = {
    'id': (max(t['id'] for t in _TAREAS) + 1) if _TAREAS else 1,
    ...
}
```

## Bug #5 — `completada: null` en el JSON

**Donde:** `services/tareas.py::crear`.

**Demo:**
1. POST sin `completada` -> response: `"completada": null`.
2. Algunos clientes lo manejan, otros no.

**Fix:**
```python
'completada': bool(datos.get('completada', False)),
```

## Bug #6 — `vence` sin normalizar

**Donde:** `services/tareas.py::crear`.

**Demo:**
1. POST con `vence: "30/06/2026"`.
2. Listar: la tarea queda con la fecha en formato `dd/mm/yyyy`, distinto al
   resto.
3. Esto rompe el sort (bug #2).

**Fix:** parsear y normalizar:
```python
from datetime import datetime
def _normalizar_fecha(s):
    for fmt in ('%Y-%m-%d', '%d/%m/%Y'):
        try:
            return datetime.strptime(s, fmt).strftime('%Y-%m-%d')
        except (ValueError, TypeError):
            continue
    raise ValueError(f'Fecha invalida: {s}')
```

## Bug #7 — division por cero en stats

**Donde:** `services/tareas.py::estadisticas`.

**Demo:**
1. Eliminar todas las tareas.
2. `GET /tareas/stats` -> `ZeroDivisionError`.
3. Activar el breakpoint "Raised Exceptions" para detenerse al levantar la
   excepcion (sin que la atrapen `try/except`).

**Fix:**
```python
if total == 0:
    return { 'total': 0, ... }
promedio_prioridad = sum(...) / total
```

## Bug #8 — "urgente" incluye completadas

**Donde:** `services/tareas.py::estadisticas`.

**Demo:**
1. `GET /tareas/stats` -> `urgente` muestra la tarea 2 ("Llamar al dentista")
   que vence el 28/05 pero **ya esta completada**.
2. Breakpoint en `urgente = min(...)` e inspeccionar la lista.

**Fix:**
```python
pendientes_lista = [t for t in _TAREAS if not t['completada']]
urgente = min(pendientes_lista, key=lambda t: t['vence']) if pendientes_lista else None
```

## Tip transversal

Mostrar el **debugger de Werkzeug** (la pantalla de error interactiva que aparece
en el browser cuando hay un 500). Cada frame del stack tiene un boton "console"
que abre un REPL en ese contexto. Es muy util cuando no tenes el IDE a mano.

Para activarlo: setear `FLASK_DEBUG=1` antes de correr la app (en Windows:
`$env:FLASK_DEBUG=1; python app.py`).
