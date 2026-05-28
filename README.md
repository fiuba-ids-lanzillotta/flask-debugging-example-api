# Flask Debugging Example - API

> **Aviso:** API didactica con bugs intencionales para practicar el uso del debugger en Flask.

## Motivacion

API JSON minima (sin DB, todo en memoria) que sirve un CRUD de tareas. Tiene
varios bugs realistas en las rutas y en el servicio, ideales para debuggear
con el debugger de VS Code (`debugpy`).

Esta pensada para usarse junto a `flask-debugging-example-web`, que es el
frontend que consume estos endpoints (y tiene sus propios bugs en JavaScript).

## Estructura

```
flask-debugging-example-api/
├── app.py
├── requirements.txt
├── requests.http                       # Casos de prueba listos para REST Client / Thunder Client
└── flask_debugging_example_api/
    ├── routes/
    │   └── tareas.py                   # /tareas, /tareas/<id>, /tareas/stats
    └── services/
        └── tareas.py                   # Logica + estado in-memory CON BUGS
```

## Setup

**Opcion A — script automatico (recomendado):**

```bash
setup_virtualenv.bat        # Windows
./setup_virtualenv.sh       # Linux/macOS
```

Tambien estan `setup_pipenv.bat` / `.sh` si preferis pipenv.

**Opcion B — manual:**

```bash
python -m venv .venv
.venv\Scripts\activate           # Windows
source .venv/bin/activate        # Linux/macOS
pip install -r requirements.txt
```

## Correr

**Sin debugger** (modo normal):

```bash
flask --app app.py run --host=0.0.0.0 --port=5000
```

**Con el debugger de VS Code**: abrir `app.py` y presionar **F5** → seleccionar
**"Python Debugger: Debug Python File"**. Asegurarse de que `FLASK_DEBUG=1` este
seteado para activar tambien el debugger interactivo de Werkzeug en el navegador.

La API queda en `http://localhost:5000/flask_debugging_example_api/tareas`.

## Endpoints

| Metodo | Endpoint                            | Descripcion                             |
|--------|-------------------------------------|-----------------------------------------|
| GET    | `/`                                 | Health check                            |
| GET    | `/flask_debugging_example_api/tareas?completada=&orden=` | Listar/filtrar/ordenar |
| GET    | `/flask_debugging_example_api/tareas/<id>` | Detalle                          |
| POST   | `/flask_debugging_example_api/tareas` | Crear                                 |
| DELETE | `/flask_debugging_example_api/tareas/<id>` | Eliminar                         |
| GET    | `/flask_debugging_example_api/tareas/stats` | Estadisticas agregadas          |

El archivo `requests.http` tiene cada caso listo para ejecutar desde la
extension **REST Client** o **Thunder Client** de VS Code.

## Bugs intencionales

Hay 8 bugs en total, listados con detalle en [`INSTRUCTOR.md`](INSTRUCTOR.md).
Resumen:

| # | Donde                         | Sintoma observable                                                  |
|---|-------------------------------|---------------------------------------------------------------------|
| 1 | `services/tareas.py::listar`  | `?completada=true` devuelve TODAS las tareas en vez de las completadas |
| 2 | `services/tareas.py::listar`  | Sort por fecha funciona "por casualidad" (formato ISO)              |
| 3 | `routes/tareas.py` + servicio | `GET /tareas/3` devuelve 404 aunque la tarea exista                 |
| 4 | `services/tareas.py::crear`   | Si se borra una tarea, el nuevo id colisiona con otro existente     |
| 5 | `services/tareas.py::crear`   | `completada` se guarda como `null` si no se manda                   |
| 6 | `services/tareas.py::crear`   | `vence` se guarda sin normalizar el formato                         |
| 7 | `services/tareas.py::stats`   | Division por cero si no hay tareas                                  |
| 8 | `services/tareas.py::stats`   | La tarea "urgente" incluye completadas                              |

## Como debuggear

1. Levantar la API con el debugger: abrir `app.py` y presionar **F5**.
2. Poner un breakpoint en, por ej., `services/tareas.py::obtener` (linea del `if`).
3. Desde `requests.http` ejecutar `GET /tareas/3`.
4. El debugger se detiene. Inspeccionar `t['id']` y `tarea_id` en el panel
   "Variables". Probar en la Debug Console:

   ```python
   type(t['id'])
   type(tarea_id)
   t['id'] == tarea_id
   ```

5. Repetir con cada bug.

## Ver tambien

- [`flask-debugging-example-web`](../flask-debugging-example-web) — frontend con
  JavaScript que consume esta API y tiene sus propios bugs.
- [`INSTRUCTOR.md`](INSTRUCTOR.md) — guion sugerido para el profe.
