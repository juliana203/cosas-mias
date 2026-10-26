# BitacoraBio 2026 — TP3 Arquitectura: opción A vs opción D

Documento de discusión interno del grupo. No es el entregable: sirve para decidir qué estilo y patrón adoptar antes de escribir `docs/architecture/arquitectura.md`.

---

## 1. Punto de partida

**Decisiones ya tomadas**

- Frontend: Flask con plantillas HTML. Backend: Python.
- Hosting en un servidor web.
- Base de datos: PostgreSQL.
- Archivos PDB: guardados como archivos, con la ruta en la base (por el crecimiento de la base).
- Login y roles: fuera de desarrollo (cubierto en los procesos del TP1). Se registra en el documento como aspecto transversal descartado, con su motivo: no es nuevo ni demuestra el valor del sistema.
- El profe pidió no complicarse la vida y no exige cubrir todos los atributos.
- El driver seguro es Mantenibilidad.

**Drivers que se usan en este análisis** (los identificadores `EC-xx` se asignan después)

| Nombre corto | Escenario del TP2 | Estado |
|---|---|---|
| Mant-E2 | Mantenibilidad escenario 2: un integrante nuevo ubica y corrige el Detector de Duplicados en menos de 30 minutos, sin regresiones verificables | Seguro (principal) |
| Mant-E1 | Mantenibilidad escenario 1: agregar una técnica nueva sin tocar el esquema de las tablas existentes | Recomendado agregar |
| Efic-E3 | Eficiencia escenario 3: catálogo con 100.000 experimentos | Opcional, respalda la decisión de los PDB como archivos |
| Fiab-E2/E3 | Fiabilidad: Google Docs caído y recuperación | Opcional |
| AF-E2 | Adecuación funcional escenario 2: coincidencias en una sola pantalla | Dudoso como driver: la consigna dice que lo que se resuelve en la interfaz o en un solo componente no es driver, y que la pertinencia funcional corresponde a requerimientos |

**Glosario mínimo**

- **Estilo:** cómo se organiza el sistema entero. Se ve en la vista de contenedores.
- **Patrón:** cómo se ordena el código dentro de un contenedor. Se ve en la vista de componentes.
- **Táctica:** decisión elemental que ayuda a lograr la respuesta de un escenario.
- **Driver:** escenario de calidad que condiciona la estructura.

---

## 2. Las dos opciones

### Opción A — Cliente-servidor + capas

**Estilo: cliente-servidor.** El navegador pide y Flask responde. La lógica y los datos viven en el servidor.

- Por qué acá: es lo que se va a construir de todos modos, y la consigna lo sugiere como punto de partida.
- Mejora: control centralizado, pocas piezas.
- Sacrifica: el servidor es punto único de falla (aceptable para un laboratorio chico).

**Patrón: capas dentro de Flask.** Presentación (rutas y plantillas), servicios (Detector, registro, búsqueda, vinculación a Google Docs) y acceso a datos (base y archivos PDB). Cada capa usa solo la inmediatamente inferior.

- Por qué: el Detector queda en un solo lugar (capa de servicios), separado de las rutas y del SQL. Ayuda a Mant-E2.
- Mejora: ubicar el código, modificarlo y probarlo por separado.
- Sacrifica: algo de indirección entre capas.

**Contenedores:** Navegador, Aplicación Flask, PostgreSQL, Almacén de archivos PDB, Google Docs (externo).

**Cubre:** Mant-E2, Mant-E1 (modelo clave-valor de ParametroExperimento), Efic-E3.
**No cubre con mecanismo propio:** Fiab-E2/E3. Si falla Google Docs, el experimento queda "no vinculado" y el reintento es manual.
**Cambios en el TP1:** ninguno.

### Opción D — Cliente-servidor + tuberías y filtros en el registro (con capas en el resto)

**Estilos:** cliente-servidor como base; tuberías y filtros solo en la zona del registro de experimentos. El resto de la aplicación sigue en capas.

El registro es una secuencia de pasos de una sola responsabilidad. Cada paso es un "filtro" que recibe un objeto, lo completa y lo pasa al siguiente:

1. Validar datos.
2. Detectar duplicados (CU-00). Si hay coincidencias sin confirmar, la cadena se corta y devuelve la lista al usuario.
3. Guardar experimento y archivo PDB.
4. Vincular documento de Google Docs. Si falla, deja el experimento en "no vinculado".

- Mejora: Mant-E2 (el Detector es un paso con nombre propio, fácil de ubicar) y capacidad de prueba (cada filtro se prueba solo, lo que da la verificación de "sin regresiones" que pide la medida). Agregar un paso nuevo es insertar un filtro.
- Fiabilidad: si falla Google Docs, el último filtro lo captura y marca "no vinculado", sin cola ni worker (degradación controlada).
- Sacrifica: hace falta un formato de datos común entre filtros; hay que definir qué pasa cuando un paso falla; solo cubre el registro, no el resto del sistema.

**Contenedores:** los mismos 5 de A.
**Cambios en el TP1:** ninguno. El corte de la cadena coincide con el corte HU-01.B1.1 / HU-01.B1.2.

**Restricciones del estilo (Tabla 4 de la consigna) y cómo se respetan**

| Restricción o regla | Cómo se cumple |
|---|---|
| Un filtro no conoce a los demás ni comparte estado | Los filtros no se importan entre sí; solo reciben el objeto de la solicitud |
| No hay retornos a etapas anteriores | Si hay coincidencias, la cadena se corta; el usuario decide y el formulario se reenvía con `confirmo_duplicado=True`. No hay vuelta atrás dentro de la cadena |
| Cada filtro hace una sola transformación | Un filtro por paso |
| Formato de datos común | Un único objeto `SolicitudRegistro` |

**Riesgo en la defensa:** en la Tabla 3 de la consigna este estilo se ve sobre todo en contenedores separados. Acá vive dentro de Flask, como componentes en cadena. Pueden preguntar por qué se lo llama estilo y no un patrón de diseño interno. Hay que poder contestarlo: es un estilo adicional aplicado solo a una zona, porque el escenario Mant-E2 lo exige para esa zona, y se ve como cadena de componentes en la vista de componentes.

---

## 3. Comparación

| | A | D |
|---|---|---|
| Piezas a operar | 5 | 5 |
| Mant-E2 | bien | muy bien |
| Capacidad de prueba (parte de Mantenibilidad) | bien | muy bien |
| Mant-E1 | bien | bien |
| Efic-E3 | sí | sí |
| Fiab-E2/E3 | solo manual | parcial (degradación controlada, reintento manual) |
| Cambia el TP1 | no | no |
| Código nuevo respecto de A | — | pequeño: solo la carpeta de registro |
| Complejidad | baja | media |
| Riesgo en la defensa | "es lo obvio" | explicar por qué es un estilo y no un patrón |

---

## 4. Cómo se implementa

### 4.1 Estructura del proyecto (común a A y D)

```
bitacorabio/
  app/
    __init__.py          # crea la app Flask
    config.py            # DATABASE_URL, PDB_DIR, credenciales de Google
    presentacion/        # capa 1: rutas + plantillas
      rutas_experimentos.py
      rutas_busqueda.py
      templates/  static/
    servicios/           # capa 2: lógica
      registro/          # en A es registro.py; en D es esta carpeta
      busqueda.py
      vinculacion_docs.py
    datos/               # capa 3: acceso a datos
      repositorio_experimentos.py
      almacen_pdb.py
  tests/
  schema.sql             # definición de tablas de Postgres
```

Regla de las capas: presentación llama a servicios; servicios llama a datos; nunca al revés.

**Lo único que cambia en D:**

```
servicios/registro/
  __init__.py            # arma la cadena y expone registrar_experimento()
  solicitud.py           # objeto que viaja entre filtros
  pipeline.py            # ejecutor
  filtros/
    validar_datos.py
    detectar_duplicados.py
    guardar_experimento.py
    vincular_documento.py
```

En A, ese mismo trabajo es una sola función `registrar(...)` que hace los cuatro pasos en orden.

### 4.2 Base de datos

- PostgreSQL es un proceso aparte (no un archivo dentro del proyecto). Va en la misma máquina del servidor web, con el puerto 5432 cerrado al exterior: solo Flask le habla (táctica "limitar acceso").
- Flask toma la conexión de una variable de entorno (`DATABASE_URL`).
- En el repositorio queda `schema.sql` con las tablas.

Esquema de referencia (ajustar al modelo de dominio del TP1):

```sql
Proyecto(id, nombre)
Experimento(id, proyecto_id, tipo, fecha, software, molecula, ligando,
            similar_a_id, ruta_pdb, estado_validez, estado_analisis,
            doc_url, estado_vinculacion, creado_en)
ParametroExperimento(id, experimento_id, clave, valor)   -- clave-valor
-- índice para el Detector: (molecula, ligando)
```

`estado_vinculacion` toma valores como `vinculado` o `no_vinculado`; es lo que usa el botón de reintento.

### 4.3 Archivos PDB

- **Dónde:** carpeta fuera del código, definida en `PDB_DIR` (por ejemplo `/var/lib/bitacorabio/pdb/`).
- **Nombre:** el id del experimento (`123.pdb`), nunca el nombre original. En la base, `ruta_pdb` guarda la ruta relativa.
- **Cómo lo ve el visor 3D:** una ruta de Flask (`/experimentos/<id>/pdb`) devuelve el archivo; el navegador no accede directo a la carpeta.
- **Orden al guardar:** insertar la fila (para obtener el id), escribir el archivo, confirmar la transacción. Si falla la escritura, se revierte la fila. Si falla la confirmación, se borra el archivo.
- **Backup:** respaldar `pg_dump` y la carpeta de PDB siempre juntos.

### 4.4 Formato de datos entre filtros (solo D)

Un objeto único que recorre toda la cadena y que cada filtro completa:

```python
# solicitud.py
from dataclasses import dataclass, field

@dataclass
class SolicitudRegistro:
    # lo que llega del formulario
    proyecto_id: int
    tipo: str
    fecha: str
    software: str
    molecula: str
    ligando: str
    parametros: dict
    archivo_pdb: object            # archivo subido
    similar_a_id: int | None = None
    confirmo_duplicado: bool = False
    # lo que van completando los filtros
    coincidencias: list = field(default_factory=list)
    experimento_id: int | None = None
    doc_url: str | None = None
    estado_vinculacion: str = "pendiente"
```

### 4.5 Filtros y ejecutor (solo D)

```python
# filtros/detectar_duplicados.py
def detectar_duplicados(sol, repo):
    previos = repo.buscar_por_molecula_ligando(sol.molecula, sol.ligando)
    # ignorar las coincidencias ya declaradas en "Similar a"
    sol.coincidencias = [e for e in previos if e.id != sol.similar_a_id]
    if sol.coincidencias and not sol.confirmo_duplicado:
        raise PideConfirmacion(sol.coincidencias)   # corta la cadena
    return sol
```

```python
# filtros/vincular_documento.py
def vincular_documento(sol, repo, docs):
    try:
        sol.doc_url = docs.crear_y_vincular(sol.experimento_id)
        sol.estado_vinculacion = "vinculado"
    except ErrorGoogleDocs:
        sol.estado_vinculacion = "no_vinculado"
    repo.actualizar_vinculacion(sol)
    return sol
```

```python
# pipeline.py
def ejecutar(filtros, solicitud):
    for filtro in filtros:
        solicitud = filtro(solicitud)
    return solicitud

# servicios/registro/__init__.py
def registrar_experimento(sol, repo, almacen, docs):
    cadena = [
        validar_datos,
        partial(detectar_duplicados, repo=repo),
        partial(guardar_experimento, repo=repo, almacen=almacen),
        partial(vincular_documento, repo=repo, docs=docs),
    ]
    return ejecutar(cadena, sol)
```

**Manejo de errores (la ruta de Flask captura las dos excepciones):**

- `ErrorValidacion`: corta la cadena; se devuelve el formulario con los campos marcados.
- `PideConfirmacion`: corta la cadena; se devuelve la lista de coincidencias para la pantalla de posibles coincidencias. Si el usuario elige continuar, el formulario se reenvía con `confirmo_duplicado=True`. El archivo PDB no se pierde porque sigue en el formulario del navegador.

### 4.6 Pruebas

El Detector se prueba solo, con un repositorio falso en memoria, sin levantar Postgres:

```python
def test_detecta_coincidencia():
    repo = RepoFalso([Experimento(id=1, molecula="X", ligando="Y")])
    sol = SolicitudRegistro(..., molecula="X", ligando="Y")
    with pytest.raises(PideConfirmacion):
        detectar_duplicados(sol, repo)
```

En A se puede hacer lo mismo si el repositorio se pasa como parámetro. En D es la forma natural, porque cada filtro ya viene aislado.

---

## 5. Cómo se vería en el modelo C4

**Vista de contenedores (igual en A y D)**

- Persona: Investigador/a-Director/a.
- Contenedores: Navegador, Aplicación Flask, Base de datos (PostgreSQL), Almacén de archivos PDB.
- Sistema externo: Google Docs.
- Relaciones: Navegador → Flask (HTTPS), Flask → PostgreSQL (SQL), Flask → Almacén PDB (lee y escribe archivos), Flask → Google Docs (HTTPS, API). El navegador no accede a la base ni al almacén.

**Vista de componentes de la Aplicación Flask**

- Opción A: Rutas, Servicio de registro, Servicio de búsqueda, Servicio de vinculación a documentos, Repositorio de experimentos, Acceso a PDB, Cliente de Google Docs. Las flechas van solo hacia abajo.
- Opción D: lo mismo, pero "Servicio de registro" se reemplaza por Validar datos → Detectar duplicados → Guardar experimento → Vincular documento, en cadena y en un solo sentido.

---

## 6. Otras opciones evaluadas y descartadas (para la sección de alternativas de las DA)

| Opción | Por qué se descarta |
|---|---|
| Orientada a eventos como base | El flujo principal necesita respuesta inmediata (CU-00); además dificulta seguir el código, lo que empeora Mant-E2 |
| 3 capas + worker/cola | La cola no responde a ningún escenario actual; los escenarios de Fiabilidad dicen que el reintento lo dispara el investigador |
| Híbrido cliente-servidor + eventos en la zona de Google Docs | Solo se justifica si se agrega Fiabilidad como driver y se cambia el escenario 3 a reintento automático; además suma un worker y un canal de eventos, y cambia la HU-01.B1.2 (el enlace aparecería segundos después) |
| Cliente-servidor + hexagonal | Refuerza Mant-E2 y aísla dependencias (base, archivos, Google Docs), pero es el patrón menos familiar y puede ser excesivo para el tamaño del sistema |
| MVC solo | Ordena la presentación pero no el Detector, que es lo central de Mant-E2 |
| Microservicios | Complejidad operativa desproporcionada para dos personas |
| Tuberías y filtros como estilo base | La mayor parte del sistema es consulta, no transformación; solo encaja en el registro (opción D) |

---

## 7. Preguntas para discutir entre ustedes

1. ¿Priorizamos terminar rápido y simple (A) o tener una justificación más fuerte para "sin regresiones verificables" (D)?
2. Si elegimos D, ¿podemos explicar con claridad por qué es un estilo adicional y no solo un patrón interno?
3. ¿Sumamos más drivers además de Mantenibilidad (Mant-E1 y Efic-E3 son baratos con cualquiera de las dos)? ¿Agregamos Fiabilidad?
4. ¿Mantenemos AF-E2 como driver o lo dejamos afuera, dado que se resuelve en la interfaz?
5. ¿Consultamos al profe si acepta tuberías y filtros aplicado a una zona dentro de un solo contenedor?

**Siguiente paso una vez decidido:** tabla de drivers con `EC-xx`, decisiones `DA-xx` (con alternativas descartadas de la sección 6), diagramas C4 en Mermaid y tabla de trazabilidad.
