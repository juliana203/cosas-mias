# BitacoraBio 2026 · TP4 (HU-01.A1: continuar registro pese a coincidencia)

Diseño detallado, implementación y pruebas de la HU-01.A1 (con HU-01.B1.1 como base). La conexión con Google Docs está fuera de alcance.

Documentos: `docs/design/diseno-detallado.md` (diseño), `docs/design/cobertura.md` (cobertura), `docs/uso-ia.md` (uso de IA).

## Requisitos

Python 3.10 o superior.

## Instalar

```bash
python -m venv .venv
source .venv/bin/activate        # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Ejecutar la interfaz

```bash
python run.py
```

Abrir `http://localhost:5000/registro`. Los datos viven en memoria (se pierden al cerrar) y hay un experimento de ejemplo cargado (#101: Proteasa HIV-1 / Indinavir). Para ver el camino de la HU: cargar un experimento con esa proteína y ese ligando, adjuntar cualquier archivo como PDB y elegir "Continuar de todos modos".

## Ejecutar las pruebas

```bash
pytest
pytest --cov=src --cov-branch --cov-report=term-missing    # con cobertura
```

## Estructura

```text
src/dominio/        entidades, solicitud, técnicas (plug-ins), Registro de técnicas y los pasos del registro
src/servicios/      Ejecutor de registro (sin lógica)
src/acceso_datos/   repositorio y almacén de archivos en memoria
src/presentacion/   Rutas de registro (Flask) y plantillas
src/transversal/    Gestión de excepciones
src/arranque.py     único lugar donde se arman los objetos concretos
tests/              pruebas unitarias (no pasan por la interfaz gráfica)
```

Para cambiar la persistencia (por ejemplo, a PostgreSQL) se implementa `RepositorioExperimentos` en otra clase y se la pasa en `src/arranque.py`; los pasos y el ejecutor no cambian.
