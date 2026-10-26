# BitacoraBio 2026 — Documento de Especificación de Arquitectura

**Materia:** Ingeniería del Software 2026 (FIUNER) · **Trabajo práctico:** TP3 — Arquitectura del Sistema
**Integrantes:** Nuñez Juliana, Segovia Lucas

---

## 1. Introducción

### 1.1 Propósito

Este documento describe la arquitectura de BitacoraBio 2026, un sistema de gestión y trazabilidad de experimentos computacionales de docking molecular para grupos de investigación. Registra las decisiones estructurales del sistema, las razones que las motivan (los atributos de calidad del TP2) y lo que cada una sacrifica, y las representa con las vistas de contenedores, de componentes y de despliegue del modelo C4.

### 1.2 Alcance

La arquitectura se define en profundidad para los procesos elegidos en el TP1 (`docs/requirements/srs.md`):

| Proceso (DFD nivel 1) | Casos de uso | Tratamiento |
|---|---|---|
| Proceso 1 · Registrar Experimento | CU-01 | En profundidad |
| Proceso 3 · Detectar Duplicado | CU-00 (incluido por CU-01) | En profundidad |
| Proceso 2 · Consultar y Filtrar Experimentos | CU-02 | En profundidad |
| Proceso 4 · Visualizar Pose 3D | RF-10 | Incluido en la primera versión, sin profundizar: lo resuelve la librería externa 3Dmol.js, que corre en el navegador |
| Proceso 5 · Vincular Documento de Notas | Dependencia de CU-01 (pasos 7-8, E1; RF-05 y RF-09) | Incluido en la primera versión, sin profundizar como proceso propio: se documenta como dependencia del Proceso 1 y aparece como la integración con Google Docs |
| Procesos 6, 7, 8 y 9 (gestionar proyecto, modificar estado, eliminar experimento, registrar usuario) | Sin CU propio | Caja negra |

**Nota.** Los procesos elegidos en el SRS para profundizar son el Proceso 1 (con su interacción con el Proceso 3) y el Proceso 2. Para que la primera versión del sistema tenga las funciones necesarias, la arquitectura incluye además el visor 3D (Proceso 4) y la vinculación con Google Docs (Proceso 5). Se sabe y se entiende que estas funciones no fueron profundizadas en las entregas anteriores; se consideraron necesarias para mantener el flujo y el valor del sistema.

Lo que queda fuera de lo anterior se representa como caja negra: un contenedor sin detalle interno o un sistema externo.

**Fuera del alcance de este TP:** las vistas de clases y de código (se trabajan en el TP4). El despliegue se documenta solo para el entorno de producción (sección 8).

### 1.3 Audiencia

Docentes de la materia y integrantes del grupo. También un integrante que se sume más adelante, que debería poder entender y corregir el sistema sin ayuda de quienes lo diseñaron (escenario EC-08, sección 4).

### 1.4 Documentos relacionados

| Documento | Ubicación | Qué aporta a este documento |
|---|---|---|
| SRS (TP1) | `docs/requirements/srs.md` | DFD, modelo de dominio, requerimientos funcionales (RF), casos de uso (CU) e historias de usuario (HU) |
| Atributos de calidad (TP2, parte A) | `docs/requirements/quality-scenarios/atributos-calidad.md` | Escenarios de calidad con identificador `EC-xx` |
| Maquetado e interfaz (TP2, parte B) | `docs/ui/` | Pantallas (mockups), perfiles de usuario y evaluación heurística |
| Registro de uso de IA | `docs/uso_ia.md` | Bitácora de uso de inteligencia artificial |

### 1.5 Convenciones

- Los escenarios de calidad se identifican como `EC-01`, `EC-02`, etc. (la tabla con todos los escenarios está en la sección 4.1).
- Las decisiones de arquitectura se identifican como `DA-01`, `DA-02`, etc. (sección 10).
- Los requerimientos, casos de uso e historias de usuario conservan los identificadores del SRS (`RF-xx`, `CU-xx`, `HU-xx`).
- Los elementos se nombran igual en todas las vistas, decisiones y tablas de trazabilidad. El idioma de todo el documento es el español.

### 1.6 Siglas

| Sigla | Significado |
|---|---|
| API | Interfaz de programación de aplicaciones: las operaciones que un programa ofrece a otros |
| C4 | Modelo de documentación de arquitectura en cuatro niveles: contexto, contenedores, componentes y código |
| CQRS | Separación de responsabilidades entre comandos (escrituras) y consultas (lecturas) |
| CU | Caso de uso |
| DA | Decisión de arquitectura |
| DFD | Diagrama de flujo de datos |
| EC | Escenario de calidad |
| GB, KB | Gigabyte y kilobyte: unidades de tamaño de archivos |
| HTML | Lenguaje con el que se escriben las páginas web |
| HTTPS | Protocolo de la web sobre una conexión cifrada |
| HU | Historia de usuario |
| IA | Inteligencia artificial |
| JSON | Formato de texto para intercambiar datos estructurados |
| ISO/IEC 25010:2023 | Norma sobre el modelo de calidad del producto de software |
| MVC | Modelo-Vista-Controlador |
| MVVM | Modelo-Vista-Modelo de Vista |
| PDB | Formato de archivo de texto que describe la estructura tridimensional de moléculas; es el archivo de resultado de cada experimento de docking |
| RF | Requerimiento funcional |
| SOA | Arquitectura orientada a servicios |
| SQL | Lenguaje para consultar y modificar bases de datos relacionales |
| SRS | Especificación de requerimientos de software (*Software Requirements Specification*) |
| TP | Trabajo práctico |
| FIUNER | Facultad de Ingeniería de la Universidad Nacional de Entre Ríos |

---

## 2. Restricciones

Las restricciones condicionan qué arquitecturas son viables. Cada una se rastrea después a las decisiones que afecta.

### 2.1 Técnicas

| Id | Restricción | Origen |
|---|---|---|
| RT-01 | El frontend se desarrolla con Flask, que entrega páginas HTML a partir de plantillas | Decisión del grupo |
| RT-02 | El backend se desarrolla en Python | Decisión del grupo |
| RT-03 | El sistema se aloja en un servidor web | Decisión del grupo |
| RT-04 | La base de datos es PostgreSQL | Decisión del grupo |
| RT-05 | Los archivos PDB y las capturas de resultado se guardan como archivos y la base guarda solo su ruta, para que la base no crezca con contenido binario | Decisión del grupo, motivada por el crecimiento del catálogo |
| RT-06 | El documento de notas de cada experimento vive en Google Docs, un servicio externo fuera del control del equipo | SRS (RF-05, RF-09) |
| RT-07 | El visor 3D es una librería externa (3Dmol.js) que corre en el navegador y es de solo lectura | SRS (RF-10) |

### 2.2 De equipo y de tiempo

| Id | Restricción | Origen |
|---|---|---|
| RE-01 | El equipo son dos personas | Grupo |
| RE-02 | El tiempo disponible es un cuatrimestre, con ciclo de vida incremental e iterativo | README del proyecto |
| RE-03 | El grupo desarrolla en Python y Flask: la arquitectura debe apoyarse en lo que el equipo ya usa | Decisión del grupo |
| RE-04 | El alcance se mantiene acotado a lo esencial para demostrar el valor del sistema: una arquitectura con pocas piezas que operar | Grupo |

### 2.3 De alcance funcional

| Id | Restricción | Consecuencia |
|---|---|---|
| RA-01 | **Usuario identificado como precondición.** El sistema asume que el usuario ya está identificado (CU-01 y CU-02 declaran "el usuario está autenticado"). La autenticación y la gestión de usuarios (Proceso 9, sin CU propio) quedan fuera del desarrollo | La identificación sustenta RF-02 (el autor se registra automáticamente) y RF-11 (solo el autor de un experimento puede agregar o modificar sus capturas). Se registra como aspecto transversal descartado en la sección 5, con su motivo: es una función estándar que no demuestra el valor del sistema. Durante las pruebas se asume un usuario ya logueado para verificar las funcionalidades del sistema |
| RA-02 | El sistema es de trazabilidad y consulta, no de cálculo: no ejecuta los ensayos de docking, solo guarda sus metadatos y resultados | No hay procesos pesados de cómputo dentro del sistema |
| RA-03 | La detección de duplicados (CU-00) necesita responder en el momento: el investigador/a decide continuar o cancelar con la lista de coincidencias a la vista | El flujo de registro es sincrónico hasta la confirmación |
| RA-04 | El sistema debe quedar preparado para incorporar otros tipos de ensayo (por ejemplo dinámica molecular) en incrementos futuros | Justifica el escenario EC-07 (sección 4) |

---

## 3. Contexto

El diagrama de contexto toma los actores y las entidades externas del DFD de Nivel 0 del TP1, sin agregar ni quitar ninguno. Muestra el sistema como una sola caja.

```mermaid
C4Context
    title Contexto de BitacoraBio 2026
    Person(inv, "Investigador/a - Becario/a", "Registra experimentos y los consulta")
    Person(dir, "Director/a del grupo", "Consulta el historial del grupo, gestiona proyectos y usuarios")
    System(bb, "BitacoraBio 2026", "Catálogo de experimentos de docking molecular con detección de duplicados y visor 3D de solo lectura")
    System_Ext(gdocs, "Google Docs", "Servicio externo que aloja el documento de notas de cada experimento")
    Rel(inv, bb, "Registra y consulta experimentos, adjunta PDB y capturas")
    Rel(dir, bb, "Consulta y filtra experimentos, gestiona proyectos y usuarios")
    Rel(bb, gdocs, "Crea el documento de notas de cada experimento", "HTTPS")
    UpdateLayoutConfig($c4ShapeInRow="2", $c4BoundaryInRow="1")
```

**Actores y sistemas externos**

| Elemento | Tipo | Descripción | Flujos del DFD de Nivel 0 que representa |
|---|---|---|---|
| Investigador/a - Becario/a | Persona | Registra experimentos, modifica su estado y los consulta | Alta de experimento (con parámetros, archivo PDB y capturas); modificación de estado; consulta y filtro; confirmaciones y resultados de búsqueda |
| Director/a del grupo | Persona | Consulta el historial del grupo y gestiona proyectos, usuarios y bajas de experimentos | Alta de usuario y rol; alta y baja de proyecto; eliminación de experimento; consulta y filtro; historial |
| Google Docs | Sistema externo | Crea el documento de notas y devuelve su enlace | Metadatos del experimento (salida); enlace a la bitácora creada (entrada) |

En el diagrama el Director/a y el Investigador/a se muestran como dos personas distintas porque el DFD las distingue. La consulta y el filtrado de experimentos (CU-02) es idéntica para ambos.

---

## 4. Drivers arquitectónicos

Los escenarios de calidad del TP2 describen cómo tiene que comportarse el sistema (por ejemplo, qué tan fácil es corregirlo o cuánto tarda una consulta). No todos obligan a organizar el sistema de una forma particular. Los que sí lo hacen se llaman **drivers arquitectónicos**: son los escenarios que condicionan la estructura (qué partes tiene el sistema, cómo se separan y cómo se conectan). Esta sección elige cuáles son los drivers de BitacoraBio 2026 y explica por qué. La sección 5 parte de esta lista.

Los escenarios están descriptos en `atributos-calidad.md`. Como ese archivo no los numera, la sección 4.1 les asigna un identificador `EC-xx` para poder rastrearlos.

### 4.1 Escenarios del TP2 con identificador

Los once escenarios de `atributos-calidad.md` reciben un identificador. La subcaracterística es la de ISO/IEC 25010:2023 asignada en el TP2.

| ID | Atributo (subcaracterística) | Escenario del TP2 | Medida | ¿Driver? |
|---|---|---|---|---|
| `EC-01` | Eficiencia de desempeño (comportamiento temporal) | Eficiencia, escenario 1: consulta con un filtro, ~1.000 experimentos | ≤ 2 s | No |
| `EC-02` | Eficiencia de desempeño (capacidad) | Eficiencia, escenario 2: 20 consultas concurrentes | ≤ 5 s cada una, 0 % de fallas | No |
| `EC-03` | Eficiencia de desempeño (capacidad) | Eficiencia, escenario 3: catálogo de 100.000 experimentos | ≤ 5 s | **Sí** |
| `EC-04` | Fiabilidad (disponibilidad) | Fiabilidad, escenario 1: Google Docs disponible | 100 % vinculados al primer intento | No |
| `EC-05` | Fiabilidad (tolerancia a fallos) | Fiabilidad, escenario 2: Google Docs caído | 0 % de pérdida del registro | No (lo cubre DA-06) |
| `EC-06` | Fiabilidad (capacidad de recuperación) | Fiabilidad, escenario 3: reintento de la vinculación | ≥ 95 % de reintentos exitosos | No (lo cubre DA-06) |
| `EC-07` | Mantenibilidad (modificabilidad) | Mantenibilidad, escenario 1: agregar una técnica nueva | 0 columnas existentes modificadas; < 1 jornada | **Sí** |
| `EC-08` | Mantenibilidad (analizabilidad) | Mantenibilidad, escenario 2: un integrante nuevo corrige el Detector de Duplicados | Módulo ubicado en < 30 min; sin regresiones verificables | **Sí (principal)** |
| `EC-09` | Adecuación funcional (pertinencia funcional) | Adecuación funcional, escenario 1: llegar a la pose desde un listado grande | 1 acción por fila, con 20, 100 y 500 resultados | No |
| `EC-10` | Adecuación funcional (pertinencia funcional) | Adecuación funcional, escenario 2: coincidencias en una sola pantalla | 1 pantalla, con 1, 5 y 10 coincidencias | No |
| `EC-11` | Capacidad de interacción (operabilidad) | Capacidad de interacción, escenario 1: varias coincidencias sin perder lo cargado | 0 campos que recargar | No |

### 4.2 Drivers seleccionados

| Id | Subcaracterística (ISO/IEC 25010:2023) | Atributo del libro (Bass, Clements, Kazman) | Prioridad |
|---|---|---|---|
| `EC-08` | Mantenibilidad: analizabilidad | Modificabilidad y capacidad de prueba | **Principal** |
| `EC-07` | Mantenibilidad: modificabilidad | Modificabilidad | Secundario |
| `EC-03` | Eficiencia de desempeño: capacidad | Desempeño | Secundario |

#### EC-08 — Mantenibilidad: corregir el Detector de Duplicados sin conocer el diseño original

| Campo | Contenido |
|---|---|
| Fuente del estímulo | Un/a nuevo/a integrante del equipo, que no participó del diseño original |
| Estímulo | Debe corregir un error reportado en la lógica de detección de duplicados |
| Entorno | Degradado — sin acceso a quienes diseñaron el sistema originalmente, solo con la documentación disponible |
| Artefacto | Detector de Duplicados |
| Respuesta | El/la integrante localiza el módulo responsable apoyándose únicamente en el SRS y en el código, y aplica la corrección sin afectar otros procesos |
| Medida de respuesta | Identifica el módulo responsable en menos de 30 minutos, y la corrección no introduce regresiones verificables en el resto del sistema |

**Por qué condiciona la estructura.** Para que alguien nuevo encuentre el Detector en menos de 30 minutos, su código tiene que estar en un lugar propio y claro, separado de las pantallas y del acceso a la base. Para corregirlo sin romper nada, tiene que poder probarse solo, sin depender del resto. Eso depende de cómo se divide el sistema en partes y de qué parte puede usar a cuál, no de cómo se escribe una sola parte.
**Se relaciona con:** RF-03, RF-04, CU-00, CU-01, HU-01.B1.1, HU-01.A1, HU-01.E3.

#### EC-07 — Mantenibilidad: agregar una técnica nueva de experimento

| Campo | Contenido |
|---|---|
| Fuente del estímulo | Desarrollador/a del equipo |
| Estímulo | Necesita agregar dinámica molecular como nueva técnica de experimento soportada |
| Entorno | Mantenimiento planificado, con acceso completo a la documentación y al modelo de dominio original |
| Artefacto | Modelo de datos de Experimento y ParametroExperimento |
| Respuesta | La nueva técnica se agrega definiendo sus parámetros como nuevas filas de ParametroExperimento, sin modificar el esquema de las tablas ya existentes (Experimento, Proyecto) |
| Medida de respuesta | La extensión no requiere alterar ni una sola columna de las tablas existentes; se implementa en menos de una jornada de trabajo |

**Por qué condiciona la estructura.** Para sumar una técnica nueva sin cambiar las tablas, los parámetros de cada experimento se guardan como pares nombre-valor (con su unidad, si la tienen) y no como una columna por parámetro. Eso define cómo es la base de datos y cómo la usan todas las partes que leen o escriben parámetros. Responde a la restricción RA-04.
**Se relaciona con:** RF-01, RF-12, modelo de dominio (ParametroExperimento), HU-01.B1.1, HU-02.B2.

#### EC-03 — Eficiencia de desempeño: consulta con gran volumen de datos

| Campo | Detalle |
|---|---|
| Fuente del estímulo | Investigador/a (mismo estímulo que el EC-01, sin concurrencia) |
| Estímulo | Consulta el catálogo filtrando por el mismo criterio simple (proteína) |
| Entorno | Catálogo con 100.000 experimentos registrados (en vez de ~1.000), 1 usuario conectado |
| Artefacto | Módulo de consulta y filtro |
| Respuesta | El sistema devuelve los experimentos que coinciden con el filtro |
| Medida de respuesta | Se completa en 5 segundos o menos |

**Por qué condiciona la estructura.** Con 100.000 experimentos y un archivo PDB por cada uno, el contenido binario llegaría a decenas de GB (orden de magnitud estimado). Guardarlo dentro de la base la haría crecer sin control y complicaría los respaldos y el mantenimiento; por eso la base guarda solo los datos del experimento y la ruta de cada archivo, y los archivos viven aparte. Además, a ese volumen la consulta tiene que resolverse en la base, con índices por los campos de filtro, y devolver un listado liviano (solo las columnas que se muestran, sin archivos ni parámetros) en lugar de traer cada experimento completo. No se pagina: `EC-09` pide llegar a la pose desde el listado sin paginar. Esto define dónde vive cada tipo de dato y obliga a tener una parte del sistema que acceda a los archivos.
**Se relaciona con:** RF-07, RF-10, RF-11, HU-02.B1, restricción RT-05.

### 4.3 Escenarios que no se toman como drivers

Un escenario no es un driver si se resuelve dentro de un solo componente o solo en la interfaz, sin afectar la estructura. Para cada uno de los demás se indica el motivo.

| Escenario | Por qué no es un driver |
|---|---|
| `EC-01` Eficiencia: consulta simple con ~1.000 experimentos | Se cumple con una base relacional con índices; no requiere ningún mecanismo estructural |
| `EC-02` Eficiencia: 20 consultas concurrentes | PostgreSQL atiende esa concurrencia con los índices ya previstos; no requiere réplicas, caché ni otra estructura |
| `EC-04`, `EC-05`, `EC-06` Fiabilidad: Google Docs caído y recuperación | Se resuelve dentro de un solo componente (el que vincula el documento), que marca el experimento como "no vinculado" y ofrece el reintento (RF-09). No agrega contenedores ni cambia la estructura |
| `EC-09` Adecuación funcional: acceso a la pose desde un listado grande | Se resuelve en la interfaz (una fila del listado lleva al detalle con el visor); no afecta la estructura |
| `EC-10` Adecuación funcional: varias coincidencias en una sola pantalla | Se resuelve en la interfaz y en un único componente (el detector devuelve la lista completa); la consigna indica que la pertinencia funcional corresponde a los requerimientos y no a decisiones de arquitectura |
| `EC-11` Capacidad de interacción: múltiples coincidencias | Se resuelve en la interfaz, sin afectar la estructura |

### 4.4 Cobertura de los drivers sobre los requerimientos

| Driver | Procesos que condiciona | Requerimientos relacionados |
|---|---|---|
| `EC-08` | Proceso 1 y Proceso 3 (Registrar y Detectar Duplicado) | RF-03, RF-04, RF-08 |
| `EC-07` | Proceso 1 y Proceso 2 (datos de los experimentos) | RF-01, RF-06, RF-12 |
| `EC-03` | Proceso 2 (Consulta y Filtro), Proceso 1 (guardado de los archivos de resultado) y Proceso 4 (lectura del PDB para el visor) | RF-07, RF-10, RF-11 |

Las restricciones de la sección 2 (equipo de dos personas, un cuatrimestre, pocas piezas que operar) descartan de entrada estructuras con muchos procesos independientes. La sección 5 parte de esta lista de drivers.

---

## 5. Estrategia de solución

Esta sección recorre el camino que va de los drivers (sección 4) a la estructura del sistema: primero las tácticas que permiten alcanzar la medida de cada escenario, después el estilo y el patrón que las agrupan, y por último los aspectos transversales. Al final se verifica que cada driver quede cubierto y qué se sacrifica.

### 5.1 Tácticas por driver

Las tácticas son las de la bibliografía de la materia (Bass, Clements y Kazman). Cuando el grupo agrega una decisión que no figura en esas tablas, se aclara.

#### EC-08 — Corregir el Detector de Duplicados sin conocer el diseño original

Atributos del libro: Modificabilidad y Capacidad de prueba.

**Tácticas elegidas**

| Táctica | Grupo | Cómo contribuye a la medida |
|---|---|---|
| Dividir módulos | Modificabilidad: aumentar cohesión | El registro se parte en pasos de una sola responsabilidad (validar, detectar duplicados, guardar, vincular). El Detector es un módulo propio, y por eso se lo ubica rápido |
| Encapsular | Modificabilidad: reducir acoplamiento | El Detector se usa a través de una interfaz estable (recibe los datos del experimento y devuelve las coincidencias). Corregir su interior no afecta a quien lo usa |
| Restringir dependencias | Modificabilidad: reducir acoplamiento | Cada capa usa solo a la inferior, así que un cambio en el Detector no se propaga hacia las pantallas |
| Abstraer fuentes de datos | Capacidad de prueba | El Detector consulta los experimentos a través de un repositorio. En las pruebas se lo reemplaza por uno simulado, y el Detector se prueba sin la base real |
| Limitar la complejidad estructural | Capacidad de prueba | Cada paso es simple y tiene pocas dependencias, por lo que se prueba por separado. Eso permite verificar que una corrección no introduce regresiones |

**Tácticas descartadas**

| Táctica | Motivo |
|---|---|
| Usar un intermediario (por ejemplo una cola entre la aplicación y el Detector) | CU-00 necesita la respuesta en el momento (RA-03), y un intermediario haría más difícil seguir el flujo, lo contrario de lo que pide EC-08 |
| Plug-ins, publicación-suscripción, parametrización (diferir el enlace) | La lógica de duplicados no cambia en tiempo de ejecución ni por configuración: solo agregaría complejidad |
| Interfaces especializadas, grabar y reproducir, aserciones ejecutables | No hacen falta para la medida: alcanza con pruebas que usan un repositorio simulado |

#### EC-07 — Agregar una técnica nueva de experimento

Atributo del libro: Modificabilidad.

**Tácticas elegidas**

| Táctica | Grupo | Cómo contribuye a la medida |
|---|---|---|
| Parametrización (dentro de diferir el enlace) | Modificabilidad | Los parámetros de cada técnica se definen como datos (filas nombre-valor-unidad en ParametroExperimento) y no como columnas ni como código. Una técnica nueva se agrega sin tocar el esquema |
| Encapsular | Modificabilidad: reducir acoplamiento | El acceso a los parámetros queda detrás del repositorio de experimentos. Los demás componentes no dependen de cómo se guardan |

**Tácticas descartadas**

| Táctica | Motivo |
|---|---|
| Plug-ins (un módulo por técnica) | La técnica nueva cambia los datos, no el comportamiento. Un mecanismo de plug-ins sumaría código sin un escenario que lo pida. Si en el futuro una técnica tuviera lógica propia, se reevalúa |
| Dividir módulos por técnica | Mismo motivo: duplicaría código para algo que se resuelve con datos |

#### EC-03 — Consulta con 100.000 experimentos

Atributo del libro: Desempeño.

**Tácticas elegidas**

| Táctica | Grupo | Cómo contribuye a la medida |
|---|---|---|
| Reducir sobrecarga | Desempeño: controlar la demanda | La consulta se resuelve en la base con índices por los campos de filtro (molécula, ligando, proyecto, fecha, autor) y devuelve un listado liviano (sin archivos ni parámetros), sin paginar por `EC-09`. La base no almacena ni recorre contenido binario: guarda solo la ruta de cada archivo |

**Aclaración.** Guardar los archivos PDB y las capturas fuera de la base es una decisión propia del grupo (RT-05) que no figura como táctica literal en el libro; se apoya en "reducir sobrecarga", porque evita que la base cargue con trabajo y volumen que no le corresponden.

**Tácticas descartadas**

| Táctica | Motivo |
|---|---|
| Aumentar recursos | No cambia la estructura, y con índices no hace falta para un solo usuario |
| Mantener copias de datos o de cómputo (caché, réplicas de lectura) | Suma piezas que operar para un escenario de un solo usuario con 5 segundos de margen |
| Introducir concurrencia | El escenario es de un solo usuario, sin concurrencia |
| Limitar o priorizar eventos, acotar colas, planificar recursos | No hay cola ni recursos compartidos que planificar |
| Acotar tiempos de ejecución | La medida ya es un tiempo máximo y un límite de consulta no cambia la estructura |

### 5.2 Estilos (decisión global)

#### 5.2.1 Estilo base: cliente-servidor

El navegador solicita páginas y archivos, y la aplicación del catálogo responde. Toda la lógica y los datos compartidos viven en el servidor.

| Aspecto | Detalle |
|---|---|
| Por qué | Es lo que ya definen las restricciones técnicas: Flask entrega páginas desde el servidor (RT-01 a RT-03), con pocas piezas que operar (RE-04). Concentra la lógica y los datos en un solo lugar, lo que permite detectar duplicados entre todos los experimentos del grupo |
| Qué mejora | Control centralizado de los datos y de la lógica; simplicidad |
| Qué sacrifica | El servidor es un punto único de falla; la carga se concentra en él |
| Dónde aplica | Todo el sistema. La aplicación se despliega como una sola unidad, pero cliente-servidor es lo que describe la estructura global: un navegador que solicita y un servidor que responde |

**Comprobación de las restricciones del estilo (Tabla 4 de la consigna)**

| Restricción o regla | Cómo se cumple |
|---|---|
| Los clientes no se comunican entre sí | Cada navegador habla solo con la aplicación |
| El servidor no inicia la comunicación con el cliente | La aplicación solo responde a lo que el navegador solicita |
| El cliente no accede directamente a la base de datos | El navegador no tiene conexión con la base ni con el almacén de archivos; todo pasa por la aplicación |
| El cliente inicia siempre la comunicación | Toda interacción empieza con una solicitud del navegador |
| El servidor expone una interfaz definida | Las rutas de la aplicación (HTTPS) son la única entrada |
| La lógica y los datos compartidos viven en el servidor | Reglas, detección de duplicados y datos están en la aplicación y sus almacenes |

#### 5.2.2 Estilo adicional, solo en la zona de registro: tuberías y filtros

El registro de un experimento es una secuencia de pasos, cada uno con una sola responsabilidad. Se organiza como una cadena de filtros: cada uno recibe los datos de la solicitud de registro, los completa o los verifica, y se los pasa al siguiente.

| Filtro | Responsabilidad | Origen en el SRS |
|---|---|---|
| 1. Validar datos | Verifica que los campos obligatorios estén completos y que el formato sea válido | RF-08, CU-01 paso 2 |
| 2. Detectar duplicados | Busca coincidencias de tipo y molécula/ligando. Si hay coincidencias que el investigador/a no confirmó, corta la cadena y devuelve la lista | RF-03, RF-04, CU-00 |
| 3. Guardar experimento | Registra autor y fecha, guarda los datos en la base y los archivos PDB y capturas en el almacén | RF-02, CU-01 pasos 5-6 |
| 4. Vincular documento | Crea el documento de notas en Google Docs y guarda el enlace. Si falla, deja el experimento "no vinculado" | RF-05, RF-09, CU-01 paso 7, E1 |

| Aspecto | Detalle |
|---|---|
| Qué escenario responde | EC-08: el Detector es un paso con nombre propio, fácil de ubicar, y cada filtro se prueba por separado. Se elige por la prueba por etapa que la Tabla 3 asocia al estilo; no por concurrencia ni por volumen de datos |
| Qué mejora | Analizabilidad y capacidad de prueba del registro; agregar un paso nuevo es insertar un filtro |
| Qué sacrifica | Hace falta un formato de datos común entre filtros; hay que definir qué pasa cuando un paso falla; solo cubre el registro, no el resto del sistema |
| Dónde aplica | Solo en el registro de experimentos (CU-01 con CU-00). La búsqueda, el detalle y el resto siguen el estilo base |
| Cómo se conecta con el estilo base | La ruta de registro de la aplicación (zona cliente-servidor) invoca con una llamada interna a un componente de la capa de servicios, el ejecutor de registro, que arma y ejecuta la cadena. Los filtros son componentes de un mismo contenedor, no procesos separados: por eso este estilo se ve en la vista de componentes (sección 7) y no en la de contenedores |

**Comprobación de las restricciones del estilo (Tabla 4 de la consigna)**

| Restricción o regla | Cómo se cumple |
|---|---|
| Un filtro no conoce a los demás ni comparte estado con ellos | Los filtros no se invocan entre sí. Solo reciben y devuelven la solicitud de registro; el orden lo conoce únicamente el ejecutor de registro |
| No hay retornos hacia etapas anteriores | Si hay coincidencias sin confirmar, la cadena se corta y devuelve la lista al usuario. Si el investigador/a decide continuar, vuelve a enviar el registro con esa confirmación y la cadena corre otra vez desde el principio. Nunca se vuelve atrás dentro de una misma ejecución |
| Cada filtro hace una sola transformación | Validar, detectar, guardar y vincular son cuatro filtros distintos |
| La salida de un filtro es la entrada del siguiente, en un formato de datos común | Todos reciben y devuelven el mismo objeto: la solicitud de registro |
| Cómo comprobarlo en el diagrama | Una cadena de flechas en un solo sentido, sin atajos entre filtros (sección 7). La flecha entre dos filtros indica el sentido del flujo de datos, no una llamada directa |

**Qué pasa cuando un paso falla**

| Situación | Qué ocurre | Caso del SRS |
|---|---|---|
| Campo obligatorio vacío o formato inválido | El filtro 1 corta la cadena e indica el campo | E5, E6 |
| Coincidencia detectada | El filtro 2 corta la cadena y devuelve la lista; el usuario decide continuar o cancelar | A1, E3 |
| Se interrumpe la conexión durante el guardado | El filtro 3 revierte lo guardado; no queda un experimento a medias | E2 |
| Google Docs no responde | El filtro 4 captura el error y deja el experimento "no vinculado"; el reintento se hace desde el detalle del experimento | E1, RF-09 |

#### 5.2.3 Estilos descartados

| Estilo | Motivo |
|---|---|
| Orientada a eventos (como base o en la zona de Google Docs) | El flujo principal necesita la respuesta en el momento (RA-03), y seguir el flujo se haría más difícil, lo contrario de EC-08. No hay tareas lentas ni picos de carga que lo justifiquen, y los escenarios de Fiabilidad no se toman como drivers |
| Tuberías y filtros como estilo base | La mayor parte del sistema es consulta, no transformación de datos. Solo encaja en el registro (5.2.2) |
| Entre pares (bases locales por investigador) | El valor del sistema es un catálogo compartido: detectar duplicados exige ver los experimentos de todos |
| Microservicios | Complejidad operativa desproporcionada para un equipo de dos personas (RE-01, RE-04) |

No se tuvieron en cuenta, por saberse inadecuados para este sistema y sus drivers: repositorio, microkernel y SOA.

### 5.3 Patrón (decisión local)

| Contenedor | Patrón | Motivo |
|---|---|---|
| Aplicación del catálogo | Capas | Responde a EC-08 y EC-07 |
| Navegador | Ninguno | Muestra HTML generado por el servidor y el visor externo 3Dmol.js |
| Base de datos de experimentos, Almacén de archivos de resultados | No aplica | Son almacenes de datos |

**Capas dentro de la aplicación del catálogo**

| Capa | Responsabilidad |
|---|---|
| Presentación | Recibe las solicitudes del navegador y arma las respuestas. Son las rutas de Flask; las plantillas HTML pertenecen a esta capa, pero no se dibujan como componente porque no tienen lógica propia |
| Servicios | La lógica del sistema: el registro (el ejecutor y la cadena de cuatro filtros) la consulta (búsqueda, detalle y entrega de archivos) y la gestión de capturas (agregar o reemplazar las de un experimento ya registrado, solo su autor) |
| Acceso a datos y servicios externos | Lee y escribe en la base y en el almacén de archivos, y habla con Google Docs |

| Aspecto | Detalle |
|---|---|
| Qué escenario responde | EC-08 (módulos separados y dependencias acotadas) y EC-07 (el acceso a parámetros queda encapsulado en la capa de acceso a datos) |
| Qué mejora | Modificabilidad y capacidad de prueba: un cambio en una capa afecta poco a las demás |
| Qué sacrifica | Indirección y algo de rendimiento (despreciable frente a los márgenes de EC-03) |
| Relación con tuberías y filtros | Los cuatro filtros viven dentro de la capa de servicios |

**Comprobación de las restricciones del patrón (Tabla 6 de la consigna).** Se adopta la variante de capas estrictas: cada capa usa solo a la inmediatamente inferior.

| Restricción o regla | Cómo se cumple |
|---|---|
| Una capa no depende de las superiores | Los servicios no conocen las rutas, y el acceso a datos no conoce a los servicios |
| No se saltean capas sin justificarlo | Las rutas llaman a los servicios, y los servicios llaman al acceso a datos |
| Cada capa tiene una responsabilidad | Ver la tabla de capas |
| Todas las flechas entre capas van hacia abajo | Se verifica en el diagrama de componentes (sección 7) |

**Patrones descartados**

| Patrón | Motivo |
|---|---|
| MVC | No separa la lógica de negocio en una capa propia, que es lo que EC-08 necesita. Flask ya separa rutas y plantillas sin que haga falta declararlo como patrón |
| Hexagonal | Suma interfaces y adaptadores, con riesgo de sobreingeniería para dos personas, y combinarlo con capas dificultaría comprobar las reglas de la Tabla 6 |
| Broker (cola de mensajes con un proceso que la consume) | No responde a ningún driver: CU-00 es síncrono y el reintento de la vinculación lo dispara el usuario. Suma un contenedor que operar |

No se tuvieron en cuenta, por saberse inadecuados para este sistema y sus drivers: CQRS, MVVM, pizarra y serverless.

### 5.4 Aspectos transversales

| Aspecto | Decisión | Motivo |
|---|---|---|
| Autenticación y autorización | **Descartado** | Se asume un usuario identificado como precondición (RA-01); la autenticación no demuestra el valor del sistema. En las pruebas se asume un usuario ya logueado |
| Auditoría | **Descartado como componente propio** | El autor y la fecha y hora de cada experimento son datos del experimento (RF-02) y los guarda Guardar experimento. Un registro general de todas las acciones se descarta: ningún driver lo exige |
| Gestión de excepciones | **Adoptado** | Los errores previstos (validación, coincidencias, falla de Google Docs, interrupción al guardar; ver 5.2.2) se tratan de forma común, en un componente propio |
| Interoperabilidad | **Adoptado** | La integración con Google Docs queda encapsulada en un componente propio de la capa de acceso a datos y servicios externos (táctica: adaptar la interfaz), de modo que un cambio en el servicio externo afecta solo a ese componente |
| Instrumentación (monitoreo) | **Descartado** | Ningún driver lo exige |
| Notificaciones | **Descartado** | La aplicación informa el resultado en pantalla (confirmaciones y errores); no avisa fuera de ella |

### 5.5 Cobertura de los drivers y sacrificios

| Driver | Cómo lo cubre la arquitectura | Dónde se ve | Qué sacrifica |
|---|---|---|---|
| `EC-08` | Capas más cadena de filtros: el Detector es un componente propio, usado a través de una interfaz estable y probado con un repositorio simulado | Componentes: Detectar duplicados, Repositorio de experimentos (sección 7) | Indirección entre capas; hay que mantener un formato de datos común entre filtros; la cadena solo cubre el registro |
| `EC-07` | Parámetros guardados como filas nombre-valor-unidad, detrás del repositorio de experimentos | Base de datos de experimentos (tabla ParametroExperimento); componente Repositorio de experimentos | Filtrar por parámetro es más costoso que por columna; el valor se guarda como texto, sin validación de tipo a nivel de esquema |
| `EC-03` | Archivos PDB y capturas fuera de la base; consultas con índices y listados livianos | Contenedores Base de datos de experimentos y Almacén de archivos de resultados; componente Acceso a archivos; nodos Servidor web y Volumen de archivos (sección 8) | Hay dos almacenes que mantener consistentes: se guarda primero el experimento y después el archivo, revirtiendo si falla, y se respalda todo junto |

### 5.6 Conflictos entre tácticas

| Conflicto | Cómo se resuelve |
|---|---|
| EC-07 (parámetros clave-valor) contra EC-03 (desempeño): filtrar por parámetro exige unir tablas y es más lento que filtrar por una columna | El filtro del escenario EC-03 usa campos propios del experimento (molécula, ligando, proyecto, fecha, autor), que son columnas con índice. Los parámetros llevan un índice por experimento y por (nombre, valor). Se acepta que filtrar por parámetro sea más lento |
| EC-08 (capas y cadena) contra EC-03 (desempeño): más pasos y llamadas entre componentes | Las llamadas entre componentes del mismo proceso son internas y muy rápidas; el costo es despreciable frente al margen de 5 segundos |
| EC-03 (volumen) contra EC-09 (llegar a la pose sin paginar): paginar acotaría el listado, pero obligaría a recorrer páginas para llegar a una pose | No se pagina. El filtro del escenario EC-03 es simple y devuelve pocas filas, y el listado trae solo columnas livianas (nunca archivos ni parámetros), así que sin paginar alcanza con los índices. Si un filtro llegara a devolver demasiado, se reevalúa (plan B) |
| EC-03 (archivos fuera de la base) contra la consistencia de los datos | Se guarda primero el experimento y después el archivo; si falla alguno, se revierte lo hecho. Los respaldos de la base y del almacén se hacen juntos |

Ningún driver queda sin cubrir.

---

## 6. Vista de contenedores

Es la única vista de contenedores y es global: muestra todo el sistema. Los procesos elegidos se ven detallados en la aplicación del catálogo (la vista de componentes está en la sección 7); los procesos de gestión de proyectos, estado, bajas y usuarios (Procesos 6 a 9) quedan como caja negra dentro de la misma aplicación.

### 6.1 Diagrama

```mermaid
C4Container
    title Contenedores de BitacoraBio 2026
    Person(inv, "Investigador/a - Becario/a", "Registra experimentos y los consulta")
    Person(dir, "Director/a del grupo", "Consulta el historial del grupo, gestiona proyectos y usuarios")
    System_Boundary(bb, "BitacoraBio 2026") {
        Container(nav, "Navegador", "HTML / JavaScript / 3Dmol.js", "Muestra las pantallas y el visor 3D de solo lectura")
        Container(app, "Aplicación del catálogo", "Python / Flask", "Registra y valida experimentos, detecta duplicados, busca y vincula documentos de notas")
        ContainerDb(bd, "Base de datos de experimentos", "PostgreSQL", "Guarda proyectos, experimentos, parámetros y rutas de archivos")
        ContainerDb(arch, "Almacén de archivos de resultados", "Sistema de archivos", "Guarda los archivos PDB y las capturas de cada experimento")
    }
    System_Ext(gdocs, "Google Docs", "Aloja el documento de notas de cada experimento")
    Rel(inv, nav, "Usa", "HTTPS")
    Rel(dir, nav, "Usa", "HTTPS")
    Rel(nav, app, "Solicita páginas, PDB y capturas", "HTTPS")
    Rel(app, bd, "Lee y escribe datos", "SQL")
    Rel(app, arch, "Lee y escribe archivos", "Sistema de archivos")
    Rel(app, gdocs, "Crea documentos de notas", "HTTPS")
    UpdateLayoutConfig($c4ShapeInRow="2", $c4BoundaryInRow="1")
```

### 6.2 Catálogo de contenedores

| Contenedor | Tecnología | Responsabilidad |
|---|---|---|
| Navegador | HTML, JavaScript, 3Dmol.js | Muestra las pantallas al usuario y el visor 3D de solo lectura |
| Aplicación del catálogo | Python, Flask | Registra y valida experimentos, detecta duplicados, busca y consulta, y vincula el documento de notas |
| Base de datos de experimentos | PostgreSQL | Guarda los proyectos, los experimentos, sus parámetros y la ruta de cada archivo |
| Almacén de archivos de resultados | Sistema de archivos | Guarda los archivos PDB y las capturas de cada experimento |

Sistema externo: **Google Docs**, que aloja el documento de notas de cada experimento.

### 6.3 Catálogo de relaciones

| Origen | Destino | Qué se comunica | Tipo | Protocolo |
|---|---|---|---|---|
| Investigador/a - Becario/a | Navegador | Uso de las pantallas | Persona hacia contenedor | HTTPS |
| Director/a del grupo | Navegador | Uso de las pantallas | Persona hacia contenedor | HTTPS |
| Navegador | Aplicación del catálogo | Solicitudes de páginas, de archivos PDB y de capturas, y envío del formulario de registro | Síncrona | HTTPS |
| Aplicación del catálogo | Base de datos de experimentos | Lectura y escritura de proyectos, experimentos y parámetros | Acceso a datos | SQL |
| Aplicación del catálogo | Almacén de archivos de resultados | Lectura y escritura de archivos PDB y capturas | Acceso a datos | Sistema de archivos |
| Aplicación del catálogo | Google Docs | Creación del documento de notas y recepción de su enlace | Integración con un sistema externo | HTTPS |

### 6.4 Comprobación de las reglas de la vista

| Regla | Cómo se cumple |
|---|---|
| Título y sistema descripto | El diagrama se titula "Contenedores de BitacoraBio 2026" y el límite del sistema encierra los contenedores |
| Dentro del límite solo hay contenedores; personas y sistemas externos van fuera | Las dos personas y Google Docs están fuera del límite |
| Cada contenedor indica nombre, tecnología y responsabilidad | Ver el diagrama y el catálogo |
| Almacenes de datos como contenedores | La base de datos y el almacén de archivos son contenedores de datos |
| Un contenedor existe solo si se ejecuta por separado y hay una razón | El Almacén de archivos de resultados es un almacén de datos con su razón en `DA-04`; el Navegador, la aplicación y la base se ejecutan por separado. Los filtros de registro, que no se ejecutan por separado, son componentes |
| Un contenedor no contiene otros; no hay componentes dentro | Se cumple; los componentes están en la sección 7 |
| No hay elementos aislados | Todo elemento tiene al menos una relación |
| Hasta unos diez elementos | Hay siete: dos personas, cuatro contenedores y un sistema externo |
| Relaciones con verbo, desde quien inicia, con protocolo al cruzar un proceso | Todas las flechas siguen esa regla y no se dibujan respuestas |
| La estructura respeta el estilo base (cliente-servidor) | No hay flechas entre navegadores ni del navegador hacia la base o el almacén; ninguna flecha sale de la base o del almacén hacia el navegador |
| Nombres por rol, sin tecnología y sin nombres genéricos | Navegador, Aplicación del catálogo, Base de datos de experimentos, Almacén de archivos de resultados |

**Dónde se ven los estilos y los drivers en esta vista**

- **Cliente-servidor (estilo base):** se ve en la separación entre el Navegador y la Aplicación del catálogo, que es el único punto de entrada a los datos.
- **Tuberías y filtros (zona de registro):** no aparece acá, porque los filtros son componentes de la aplicación; se ve en la sección 7.
- **EC-03:** se ve en la existencia del Almacén de archivos de resultados como contenedor separado de la base de datos (decisión DA-04, sección 10).
- **EC-07:** se ve en la Base de datos de experimentos, que guarda los parámetros como pares nombre-valor.
- **EC-08:** se ve en la sección 7, en los componentes de la aplicación.

*Nota sobre el diagrama:* la sintaxis C4 de Mermaid es experimental y tiene limitaciones de disposición. Se prioriza la claridad del contenido por sobre el formato visual.

---

## 7. Vista de componentes

Se hace una sola vista de componentes: la de la **Aplicación del catálogo**, que es el único contenedor con lógica de los procesos elegidos. No se hace vista de componentes del Navegador (muestra HTML generado por el servidor y usa una librería externa), de la Base de datos ni del Almacén de archivos (son almacenes de datos).

### 7.1 Diagrama

```mermaid
C4Component
    title Componentes de la Aplicación del catálogo
    Boundary(cli, "Cliente") {
        Container(nav, "Navegador", "HTML / JavaScript / 3Dmol.js", "Muestra las pantallas y el visor 3D")
    }
    Container_Boundary(app, "Aplicación del catálogo") {
        Component(rreg, "Rutas de registro", "Flask", "Capa de presentación: recibe el formulario de registro, el reintento de vinculación y las capturas de un experimento ya registrado")
        Component(rcon, "Rutas de consulta", "Flask", "Capa de presentación: recibe filtros y pedidos de detalle, PDB y capturas")
        Component(exc, "Gestión de excepciones", "Python", "Aspecto transversal: traduce los errores previstos en respuestas al usuario")
        Component(reg, "Ejecutor de registro", "Python", "Capa de servicios: arma y ejecuta la cadena de registro")
        Component(val, "Validar datos", "Python", "Filtro 1: verifica obligatoriedad y formato")
        Component(dup, "Detectar duplicados", "Python", "Filtro 2: busca coincidencias y corta la cadena si no fueron confirmadas")
        Component(gua, "Guardar experimento", "Python", "Filtro 3: registra autor y fecha y guarda datos y archivos")
        Component(vin, "Vincular documento", "Python", "Filtro 4: crea el documento de notas y guarda el enlace")
        Component(gcap, "Gestión de capturas", "Python", "Capa de servicios: agrega o reemplaza capturas si quien lo pide es el autor")
        Component(con, "Servicio de consulta", "Python", "Capa de servicios: busca, filtra, arma el detalle y entrega los archivos")
        Component(rep, "Repositorio de experimentos", "Python", "Capa de acceso a datos: consultas y escrituras en la base")
        Component(arc, "Acceso a archivos", "Python", "Capa de acceso a datos: lee y escribe PDB y capturas")
        Component(gdc, "Cliente de Google Docs", "Python", "Capa de acceso a servicios externos: crea documentos de notas")
    }
    Boundary(ext, "Almacenes y servicio externo") {
        ContainerDb(bd, "Base de datos de experimentos", "PostgreSQL", "Proyectos, experimentos, parámetros y rutas de archivos")
        ContainerDb(arch, "Almacén de archivos de resultados", "Sistema de archivos", "Archivos PDB y capturas")
        System_Ext(gdocs, "Google Docs", "Documento de notas de cada experimento")
    }
    Rel(nav, rreg, "Envía el registro y las capturas", "HTTPS")
    Rel(nav, rcon, "Solicita páginas, PDB y capturas", "HTTPS")
    Rel(rreg, reg, "Invoca")
    Rel(rreg, gcap, "Invoca")
    Rel(rreg, exc, "Delega el manejo de errores")
    Rel(rcon, con, "Invoca")
    Rel(rcon, exc, "Delega el manejo de errores")
    Rel(reg, val, "Ejecuta")
    Rel(val, dup, "Entrega la solicitud")
    Rel(dup, gua, "Entrega la solicitud")
    Rel(gua, vin, "Entrega la solicitud")
    Rel(dup, rep, "Consulta coincidencias")
    Rel(gua, rep, "Guarda el experimento")
    Rel(gua, arc, "Guarda PDB y capturas")
    Rel(vin, rep, "Guarda el enlace y el estado")
    Rel(vin, gdc, "Solicita el documento")
    Rel(vin, exc, "Señala la falla de Google Docs")
    Rel(gcap, rep, "Verifica autoría y guarda rutas")
    Rel(gcap, arc, "Guarda o reemplaza capturas")
    Rel(con, rep, "Consulta experimentos")
    Rel(con, arc, "Obtiene PDB y capturas")
    Rel(rep, bd, "Lee y escribe", "SQL")
    Rel(arc, arch, "Lee y escribe archivos", "Sistema de archivos")
    Rel(gdc, gdocs, "Crea el documento", "HTTPS")
    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

### 7.2 Catálogo de componentes

| Componente | Capa | Tecnología | Responsabilidad | Se rastrea a |
|---|---|---|---|---|
| Rutas de registro | Presentación | Flask | Recibe el formulario de registro, el pedido de reintentar la vinculación y las capturas que se agregan a un experimento ya registrado; invoca al ejecutor de registro o a la gestión de capturas y arma la respuesta (errores, coincidencias o confirmación) | CU-01; RF-11; HU-01.B1.1, B1.2, A1, E3, E1 |
| Rutas de consulta | Presentación | Flask | Recibe los filtros y los pedidos de detalle, PDB y capturas, y arma las páginas | CU-02; HU-02.B1, B2, A1; RF-10, RF-11 |
| Ejecutor de registro | Servicios | Python | Arma y ejecuta la cadena de registro (los cuatro filtros) y, para el reintento de vinculación, una cadena de un solo filtro: Vincular documento | CU-01; RF-09; EC-08 |
| Validar datos | Servicios (filtro 1) | Python | Verifica que los campos obligatorios estén completos y que el formato sea válido | RF-08; CU-01 paso 2 |
| Detectar duplicados | Servicios (filtro 2) | Python | Busca experimentos del mismo tipo y molécula/ligando, excluye los inválidos y los ya declarados en "Similar a", y corta la cadena si hay coincidencias sin confirmar | RF-03, RF-04; CU-00; HU-01.A1, E3; EC-08 |
| Guardar experimento | Servicios (filtro 3) | Python | Registra autor y fecha, guarda los datos en la base y los archivos PDB y capturas en el almacén, y revierte si algo falla | RF-01, RF-02, RF-11; CU-01 pasos 5-6; HU-01.B1.1 |
| Vincular documento | Servicios (filtro 4) | Python | Pide el documento de notas y guarda el enlace; si falla, señala el error a Gestión de excepciones y deja el experimento "no vinculado" | RF-05, RF-09; CU-01 paso 7, E1; HU-01.B1.2, E1 |
| Gestión de capturas | Servicios | Python | Agrega o reemplaza las capturas de un experimento ya registrado, solo si el usuario actual es su autor (el usuario identificado es la precondición RA-01) | RF-11; EC-03 |
| Servicio de consulta | Servicios | Python | Busca y filtra experimentos, arma el detalle (con unidades y estados) y entrega los archivos PDB y las capturas | RF-06, RF-07, RF-10, RF-11, RF-12; CU-02 |
| Repositorio de experimentos | Acceso a datos | Python | Consulta y escribe proyectos, experimentos y parámetros (nombre, valor, unidad) en la base | RF-01, RF-03, RF-06, RF-07; EC-07, EC-03 |
| Acceso a archivos | Acceso a datos | Python | Lee y escribe los archivos PDB y las capturas en el almacén | RF-10, RF-11; EC-03 |
| Cliente de Google Docs | Acceso a servicios externos | Python | Crea el documento de notas en Google Docs y devuelve su enlace | RF-05, RF-09; aspecto de interoperabilidad (5.4) |
| Gestión de excepciones | Transversal | Python | Define los errores previstos (validación, coincidencias, falla de Google Docs, interrupción al guardar) y los traduce en respuestas al usuario | CU-01 E1 a E6; aspecto transversal (5.4) |

### 7.3 Catálogo de relaciones

| Origen | Destino | Qué se comunica | Tipo | Protocolo |
|---|---|---|---|---|
| Navegador | Rutas de registro | Formulario de registro, pedido de reintento de vinculación y capturas | Síncrona, entre contenedores | HTTPS |
| Navegador | Rutas de consulta | Solicitudes de páginas, PDB y capturas | Síncrona, entre contenedores | HTTPS |
| Rutas de registro | Ejecutor de registro | Datos del formulario | Llamada interna | — |
| Rutas de registro | Gestión de capturas | Capturas a agregar y usuario actual | Llamada interna | — |
| Rutas de registro | Gestión de excepciones | Errores previstos para traducir en respuesta | Llamada interna | — |
| Rutas de consulta | Servicio de consulta | Filtros y pedidos de detalle o de archivos | Llamada interna | — |
| Rutas de consulta | Gestión de excepciones | Errores previstos para traducir en respuesta | Llamada interna | — |
| Ejecutor de registro | Validar datos | Inicio de la cadena con la solicitud de registro | Llamada interna | — |
| Validar datos | Detectar duplicados | Solicitud de registro validada | Flujo de datos de la cadena | — |
| Detectar duplicados | Guardar experimento | Solicitud de registro sin coincidencias, o confirmada | Flujo de datos de la cadena | — |
| Guardar experimento | Vincular documento | Solicitud de registro con el experimento ya guardado | Flujo de datos de la cadena | — |
| Detectar duplicados | Repositorio de experimentos | Consulta de coincidencias | Llamada interna | — |
| Guardar experimento | Repositorio de experimentos | Datos y parámetros del experimento | Llamada interna | — |
| Guardar experimento | Acceso a archivos | Archivo PDB y capturas | Llamada interna | — |
| Vincular documento | Repositorio de experimentos | Enlace y estado de vinculación | Llamada interna | — |
| Vincular documento | Cliente de Google Docs | Pedido de creación del documento | Llamada interna | — |
| Vincular documento | Gestión de excepciones | Falla de Google Docs | Llamada interna | — |
| Gestión de capturas | Repositorio de experimentos | Verificación de autoría y rutas de las capturas | Llamada interna | — |
| Gestión de capturas | Acceso a archivos | Capturas a guardar o reemplazar | Llamada interna | — |
| Servicio de consulta | Repositorio de experimentos | Consultas de experimentos | Llamada interna | — |
| Servicio de consulta | Acceso a archivos | Pedido de PDB y capturas | Llamada interna | — |
| Repositorio de experimentos | Base de datos de experimentos | Lectura y escritura de datos | Acceso a datos, entre contenedores | SQL |
| Acceso a archivos | Almacén de archivos de resultados | Lectura y escritura de archivos | Acceso a datos, entre contenedores | Sistema de archivos |
| Cliente de Google Docs | Google Docs | Creación del documento y recepción del enlace | Integración externa, entre contenedores | HTTPS |

### 7.4 Comprobación de las reglas de la vista

| Regla | Cómo se cumple |
|---|---|
| Una vista por cada contenedor que implementa los procesos elegidos | Solo la Aplicación del catálogo implementa lógica; los demás son almacenes de datos o el cliente |
| Los componentes van dentro del límite de ese contenedor y lo externo va fuera, sin sus componentes | Navegador, base, almacén y Google Docs están fuera del límite y se dibujan como contenedores o sistema externo |
| Un componente pertenece a un solo contenedor y no contiene otros | Se cumple |
| Un componente es una agrupación coherente de funcionalidad, no una clase | Cada uno agrupa una responsabilidad (por ejemplo, "Validar datos"); no se modelan clases ni métodos |
| Nombre y responsabilidad de cada componente | Ver el catálogo |
| Respeta las restricciones del patrón de capas (Tabla 6) | Las flechas entre capas van solo hacia abajo: las rutas llaman a los servicios, y los servicios llaman al acceso a datos. Ningún servicio llama a una ruta y el acceso a datos no conoce a los servicios. Las rutas no llaman directamente al acceso a datos: lo hacen a través de los servicios |
| Respeta las restricciones de tuberías y filtros (Tabla 4) en el registro | Los cuatro filtros forman una cadena en un solo sentido, sin atajos ni retornos; ninguno invoca a otro |
| Aspectos transversales como componentes propios | Gestión de excepciones e interoperabilidad (Cliente de Google Docs). Los filtros 1 y 2 informan el corte de la cadena a quien los ejecuta y las rutas lo traducen con Gestión de excepciones; Vincular documento captura su propia falla y la señala directamente. Autenticación y autorización se descartaron (5.4) |
| Las plantillas de página no se dibujan | Son parte de la capa de presentación, pero son HTML sin lógica propia; los componentes de la vista son los que agrupan lógica |
| Ningún componente huérfano | Cada componente se rastrea a un requerimiento, caso de uso o escenario (columna "Se rastrea a") |
| Comunicación entre componentes: verbo, sin protocolo | Las relaciones internas llevan verbo y no protocolo; solo las que cruzan un contenedor indican protocolo |

**Dónde se ven los drivers en esta vista**

- **EC-08:** el Detector es el componente "Detectar duplicados", propio y ubicable en la capa de servicios. Se usa a través del ejecutor y consulta los datos por el "Repositorio de experimentos", que en las pruebas se reemplaza por uno simulado.
- **EC-07:** los parámetros nombre-valor-unidad se leen y escriben solo a través del "Repositorio de experimentos".
- **EC-03:** el "Acceso a archivos" es un componente separado del "Repositorio de experimentos", porque la base guarda solo la ruta y los archivos viven en el almacén.

*Nota sobre el diagrama:* la sintaxis C4 de Mermaid es experimental y tiene limitaciones de disposición. Se prioriza la claridad del contenido por sobre el formato visual.

---

## 8. Vista de despliegue

Es la única vista de despliegue y corresponde al **entorno de producción**. Muestra en qué infraestructura se ejecuta cada contenedor de la sección 6. No crea contenedores nuevos, no dibuja personas ni sistemas externos (Google Docs está en la vista de contenedores) y cada relación es una de la sección 6, con el mismo protocolo.

### 8.1 Diagrama

```mermaid
C4Deployment
    title Despliegue de BitacoraBio 2026 - Producción
    Deployment_Node(pc, "Computadora del investigador/a", "Navegador web") {
        Container(nav, "Navegador", "HTML / JavaScript / 3Dmol.js", "Muestra las pantallas y el visor 3D de solo lectura")
    }
    Deployment_Node(srv, "Servidor web", "Linux") {
        Container(app, "Aplicación del catálogo", "Python / Flask", "Registra y valida experimentos, detecta duplicados, busca y vincula documentos de notas")
        ContainerDb(bd, "Base de datos de experimentos", "PostgreSQL", "Guarda proyectos, experimentos, parámetros y rutas de archivos")
        Deployment_Node(vol, "Volumen de archivos", "Disco de 50 GB como mínimo") {
            ContainerDb(arch, "Almacén de archivos de resultados", "Sistema de archivos", "Guarda los archivos PDB y las capturas de cada experimento")
        }
    }
    Rel(nav, app, "Solicita páginas, PDB y capturas", "HTTPS")
    Rel(app, bd, "Lee y escribe datos", "SQL")
    Rel(app, arch, "Lee y escribe archivos", "Sistema de archivos")
    UpdateRelStyle(app, bd, $offsetX="-90", $offsetY="-40")
    UpdateRelStyle(app, arch, $offsetX="170", $offsetY="-30")
    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

### 8.2 Catálogo de nodos

| Nodo | Tipo o tecnología | Contenedores que ejecuta | Instancias | Escenario o decisión que lo justifica |
|---|---|---|---|---|
| Computadora del investigador/a | Navegador web | Navegador | Una por usuario | Es el cliente: no depende de una decisión de infraestructura |
| Servidor web | Linux | Aplicación del catálogo, Base de datos de experimentos | 1 | `RT-03`, `RE-01` y `RE-04` (pocas piezas que operar); `EC-02` y `EC-03` se cumplen con índices, sin más infraestructura (5.1). Decisión `DA-07` |
| Volumen de archivos | Disco de 50 GB como mínimo, dentro del Servidor web | Almacén de archivos de resultados | 1 | `EC-03`: 100.000 PDB de unos 250 KB son del orden de 25 GB, más las capturas. La cifra de 50 GB es una estimación del grupo. Decisión `DA-04` |

La base de datos solo acepta conexiones de la propia máquina: la Aplicación del catálogo es el único acceso a los datos, como exige el estilo cliente-servidor (Tabla 4).

### 8.3 Contraste con los escenarios y sacrificios

Se parte del despliegue más simple, un solo servidor, y se lo contrasta con los escenarios de la sección 4.1:

| Escenario | ¿Lo cumple un solo servidor? | Cómo |
|---|---|---|
| `EC-03` (100.000 experimentos, 5 s) | Sí | Índices y listados livianos (`DA-05`); los archivos no pasan por la base (`DA-04`). El recurso a vigilar es el disco |
| `EC-02` (20 consultas concurrentes, 5 s) | Sí | Una base relacional con índices atiende esa concurrencia; no hace falta réplica ni balanceador |
| `EC-08`, `EC-07` | No dependen de la infraestructura | Se ven en los componentes y en el modelo de datos |
| `EC-04`, `EC-05`, `EC-06` (Google Docs) | No dependen de la infraestructura | Los resuelve un componente (`DA-06`) |

Sacrificios asumidos (registrados en `DA-07`):

- **Un solo nodo es un punto único de falla.** Si el Servidor web cae, el sistema completo deja de estar disponible: no se pueden registrar ni consultar experimentos, ni descargar PDB. Los datos no se pierden mientras haya respaldo conjunto de la base y del volumen de archivos (`DA-04`); la recuperación es restaurar y volver a levantar el servidor.
- La aplicación, la base y los archivos comparten procesador, memoria y disco: un pico en una puede demorar a las otras.
- Si la medida de `EC-03` no se cumple con la carga real, el paso siguiente es pasar la base de datos a un nodo propio.

### 8.4 Comprobación de las reglas de la vista

| Regla | Cómo se cumple |
|---|---|
| Un solo diagrama, del entorno de producción | Es el único; no hay diagramas de desarrollo ni de pruebas |
| Todo contenedor aparece al menos una vez, dentro de un nodo; no se crean contenedores nuevos | Aparecen los cuatro contenedores de la sección 6: Navegador, Aplicación del catálogo, Base de datos de experimentos y Almacén de archivos de resultados |
| Los contenedores y las relaciones coinciden con los de la vista de contenedores, con el mismo protocolo | Las tres flechas son las de la sección 6.3: HTTPS, SQL y sistema de archivos |
| Sin personas ni sistemas externos; sí el nodo del cliente | Google Docs y las personas no se dibujan; sí la computadora del investigador/a |
| Nodos con nombre de rol y tipo o tecnología; capacidad cuando importa | Ver el catálogo de nodos; la capacidad del disco se indica por `EC-03` |
| Hasta dos niveles de nodos | Servidor web contiene un Volumen de archivos |
| Instancias | Un solo Servidor web: no se replica (ver 8.3) |
| Cada decisión de despliegue relevante es una decisión de arquitectura | `DA-07` |

---

## 9. Historias de usuario sobre las vistas

Cada historia se recorre sobre la vista de contenedores (sección 6) y la de componentes (sección 7), para comprobar que la estructura la soporta de punta a punta.

| Historia de usuario | Criterio de aceptación | Contenedores | Componentes |
|---|---|---|---|
| `HU-01.B1.1` Registrar experimento | *Given* un proyecto existente, campos válidos y sin coincidencias; *When* confirma; *Then* se registran autor y fecha y se guarda el experimento | Navegador → Aplicación del catálogo → Base de datos de experimentos y Almacén de archivos de resultados | Rutas de registro → Ejecutor de registro → Validar datos → Detectar duplicados → Guardar experimento → Repositorio de experimentos y Acceso a archivos |
| `HU-01.B1.1` (criterio de exclusión) | *Given* un experimento previo con la misma molécula/ligando pero inválido; *Then* no se reporta como coincidencia | Aplicación del catálogo → Base de datos de experimentos | Detectar duplicados → Repositorio de experimentos (excluye el estado inválido y los declarados "Similar a") |
| `HU-01.B1.2` Vincular documento | *Given* un experimento recién guardado; *When* se crea el documento; *Then* se asocia el enlace y se muestra el resumen | Aplicación del catálogo → Google Docs y Base de datos de experimentos | Guardar experimento → Vincular documento → Cliente de Google Docs → (Google Docs); Vincular documento → Repositorio de experimentos |
| `HU-01.A1` Continuar pese a coincidencia | *Given* una coincidencia mostrada; *When* elige continuar; *Then* se registra como experimento nuevo | Navegador → Aplicación del catálogo (dos solicitudes) → Base de datos de experimentos y Almacén de archivos de resultados | 1.ª solicitud: Rutas de registro → Ejecutor de registro → Validar datos → Detectar duplicados; la cadena se corta y Rutas de registro pide a Gestión de excepciones la respuesta con la lista de coincidencias. 2.ª solicitud, con la confirmación: la cadena completa hasta Vincular documento |
| `HU-01.E3` Cancelar por coincidencia | *Given* una coincidencia mostrada; *When* cancela; *Then* no se guarda nada ni se crea documento | Navegador → Aplicación del catálogo | La cadena se cortó en Detectar duplicados: Guardar experimento y Vincular documento nunca se ejecutan. Para ver el existente: Rutas de consulta → Servicio de consulta |
| `HU-01.E1` Falla al crear el documento | *Given* un experimento guardado y una falla de Google Docs; *Then* queda guardado, "no vinculado", con aviso | Aplicación del catálogo → Google Docs (falla) → Base de datos de experimentos | Vincular documento → Cliente de Google Docs (falla); Vincular documento → Gestión de excepciones; Vincular documento → Repositorio de experimentos (estado "no vinculado") |
| `HU-01.E1` (reintento) | *Given* un experimento "no vinculado"; *When* dispara el reintento; *Then* se crea el documento sin recargar datos | Navegador → Aplicación del catálogo → Google Docs y Base de datos de experimentos | Rutas de registro → Ejecutor de registro (cadena de un solo filtro) → Vincular documento → Cliente de Google Docs y Repositorio de experimentos |
| `HU-02.B1` Filtrar experimentos | *Given* experimentos cargados; *When* filtra por autor; *Then* ve solo los de ese autor | Navegador → Aplicación del catálogo → Base de datos de experimentos | Rutas de consulta → Servicio de consulta → Repositorio de experimentos |
| `HU-02.B2` Ver detalle | *Given* un experimento seleccionado; *Then* se muestran sus campos, parámetros con unidad, estados, capturas y enlace | Navegador → Aplicación del catálogo → Base de datos de experimentos y Almacén de archivos de resultados | Rutas de consulta → Servicio de consulta → Repositorio de experimentos y Acceso a archivos. El visor 3D pide el PDB a Rutas de consulta |
| `HU-02.A1` Sin resultados | *Given* un filtro sin coincidencias; *Then* se muestra "sin resultados" | Navegador → Aplicación del catálogo → Base de datos de experimentos | Rutas de consulta → Servicio de consulta → Repositorio de experimentos |
| RF-11 Adjuntar capturas (todavía sin historia de usuario en el SRS) | El autor agrega capturas a un experimento ya registrado; otro usuario no puede modificarlas | Navegador → Aplicación del catálogo → Base de datos de experimentos y Almacén de archivos de resultados | Rutas de registro → Gestión de capturas → Repositorio de experimentos (verifica autoría) y Acceso a archivos |

---

## 10. Decisiones de arquitectura

### DA-01 — Cliente-servidor como estilo base, con capas en la Aplicación del catálogo

- **Escenario que la motiva:** `EC-08`, `EC-07` y `EC-03` (los tres drivers) y las restricciones del proyecto (RT-01 a RT-04, RE-01, RE-04).
- **Contexto:** hay que elegir cómo se organiza el sistema entero. El equipo es de dos personas, tiene un cuatrimestre y domina Python y SQL; la interfaz se arma con plantillas de Flask; los datos van en PostgreSQL.
- **Decisión:**
  - Tácticas: restringir dependencias y encapsular (Modificabilidad); abstraer fuentes de datos (Capacidad de prueba).
  - Estilo: cliente-servidor como base, para todo el sistema.
  - Patrón: capas (presentación, servicios, acceso a datos y servicios externos) en la Aplicación del catálogo.
- **Alternativas consideradas:**
  - Orientada a eventos como base — descartada: el flujo principal necesita respuesta inmediata y la ejecución es más difícil de seguir, lo que empeora `EC-08`.
  - Microservicios — descartada: complejidad operativa desproporcionada para dos personas.
  - Tuberías y filtros como estilo base — descartada: la mayor parte del sistema es consulta, no transformación; solo encaja en el registro (DA-02).
  - MVC como único patrón — descartada: no separa una capa de lógica propia, que es lo que necesita `EC-08`.
  - Hexagonal — descartada: sobreingeniería para este tamaño y dificulta comprobar la Tabla 6.
- **Consecuencias:**
  - A favor: pocas piezas que operar; el Detector queda en la capa de servicios, separado de las rutas y del SQL.
  - En contra: el servidor es punto único de falla; algo de indirección entre capas.
- **Elementos afectados:** contenedores Navegador, Aplicación del catálogo y Base de datos de experimentos; capas de la aplicación.
- **Cómo se verifica:** las medidas de los tres escenarios se verifican en `DA-02`, `DA-03`, `DA-04` y `DA-05`. Además, revisar en cada pull request que los servicios no importen a las rutas y que el acceso a datos no importe a los servicios, que es lo que exigen las capas (Tabla 6).

### DA-02 — Tuberías y filtros en la zona de registro, con un ejecutor que arma la cadena

- **Escenario que la motiva:** `EC-08`: un integrante nuevo ubica y corrige el Detector de Duplicados en menos de 30 minutos, sin regresiones verificables.
- **Contexto:** el registro es una secuencia de pasos con una sola responsabilidad cada uno. La medida pide poder comprobar que la corrección de uno no rompe los demás. Los tres primeros pasos corresponden a `HU-01.B1.1` (sin servicios externos) y el cuarto a `HU-01.B1.2` (depende de Google Docs): el corte de la cadena coincide con el corte de esas dos historias.
- **Decisión:**
  - Tácticas: dividir módulos y encapsular (Modificabilidad); abstraer fuentes de datos y limitar la complejidad estructural (Capacidad de prueba).
  - Estilo: tuberías y filtros, solo en la zona de registro, dentro de la Aplicación del catálogo. El resto sigue en capas.
  - Patrón: ninguno adicional.
  - Un componente propio, el Ejecutor de registro, conoce el orden y arma la cadena; los filtros no se invocan entre sí. Todos reciben y devuelven la solicitud de registro. Detectar duplicados corta la cadena si hay coincidencias sin confirmar y el formulario se reenvía con la confirmación; para el reintento de vinculación el ejecutor corre una cadena de un solo filtro.
- **Alternativas consideradas:**
  - Una única función que hace los cuatro pasos — descartada: el Detector se ubica, pero probarlo exige ejecutar o reescribir los demás pasos.
  - Hexagonal para aislar el Detector — descartada: más interfaces y adaptadores para lograr algo parecido.
  - Cada filtro como proceso o contenedor aparte — descartada: agrega red y operación sin que ningún escenario lo pida.
- **Consecuencias:**
  - A favor: el Detector tiene nombre propio y una prueba que corre con un repositorio simulado; agregar un paso es insertar un filtro.
  - En contra: hace falta un formato común entre pasos y definir qué pasa si uno falla; solo cubre el registro; hay un componente más (el ejecutor).
- **Elementos afectados:** componentes Ejecutor de registro, Validar datos, Detectar duplicados, Guardar experimento, Vincular documento y Gestión de excepciones.
- **Cómo se verifica:** pedir a una persona ajena al diseño que ubique el Detector solo con el SRS y el código, y cronometrar (medida de `EC-08`: menos de 30 minutos). Probar el Detector aislado con un repositorio simulado y correr las pruebas de todo el registro antes y después de la corrección: los resultados de los otros filtros no deben cambiar (sin regresiones verificables).

### DA-03 — Parámetros del experimento como pares nombre-valor, con unidad

- **Escenario que la motiva:** `EC-07`: agregar una técnica nueva sin modificar el esquema de las tablas existentes.
- **Contexto:** el riesgo principal del proyecto es el cambio de requerimientos (RA-04): sumar dinámica molecular u otras técnicas. RF-12 pide mostrar la unidad de cada parámetro.
- **Decisión:**
  - Tácticas: parametrización y encapsular (Modificabilidad).
  - Estilo y patrón: no cambian. La decisión se ve en el modelo de datos y en el componente Repositorio de experimentos.
  - Los parámetros son filas de `ParametroExperimento` con nombre, valor y unidad (la unidad puede estar vacía). Los datos que valen para cualquier técnica (objetivo, hardware, tiempo de procesamiento) son columnas del experimento.
- **Alternativas consideradas:**
  - Columnas fijas por técnica — descartada: obliga a migrar el esquema con cada técnica nueva.
  - Una tabla por técnica (herencia) — descartada: cada técnica nueva exige migración.
  - Una columna JSON en el experimento — descartada: complica filtrar por parámetro y mostrar su unidad, y el escenario del TP2 habla de filas.
- **Consecuencias:**
  - A favor: sumar una técnica es cargar filas; no se toca ninguna columna existente.
  - En contra: sin tipado fuerte en la base; filtrar por parámetro exige uniones y es más lento.
- **Elementos afectados:** componentes Repositorio de experimentos, Guardar experimento y Servicio de consulta; contenedor Base de datos de experimentos.
- **Cómo se verifica:** agregar dinámica molecular cargando solo filas de `ParametroExperimento` (por ejemplo paso de tiempo y duración) y comprobar, con el historial de migraciones, que ninguna columna existente cambió (medida de `EC-07`); cronometrar que se hace en menos de una jornada.

### DA-04 — Archivos PDB y capturas fuera de la base, en un Almacén de archivos de resultados

- **Escenario que la motiva:** `EC-03`: el filtro responde en 5 segundos o menos con 100.000 experimentos.
- **Contexto:** un PDB pesa del orden de 250 KB (el del mockup, 245 KB). Con 100.000 experimentos son unos 25 GB solo de PDB, sin contar las capturas. Es la restricción RT-05.
- **Decisión:**
  - Tácticas: reducir sobrecarga (Desempeño; con la aclaración de la sección 5.1: guardar fuera de la base es decisión propia del grupo).
  - Estilo y patrón: no cambian.
  - Los archivos van en el Almacén de archivos de resultados, en carpetas separadas para PDB y capturas. La base guarda solo la ruta. El nombre del archivo es el identificador, nunca el original. El navegador no accede al almacén: la aplicación entrega cada archivo. Se respalda la base y el almacén siempre juntos. Las capturas solo las agrega o reemplaza su autor (RF-11), lo verifica Gestión de capturas.
- **Alternativas consideradas:**
  - Guardar los archivos dentro de PostgreSQL — descartada: la base crecería decenas de GB y se respaldaría con más dificultad.
  - Un servicio de almacenamiento en la nube — descartada: agrega una dependencia externa y costo.
  - Un contenedor aparte para las capturas — descartada: ningún escenario lo justifica; basta con otra carpeta.
- **Consecuencias:**
  - A favor: la base crece solo con metadatos y las consultas no leen archivos.
  - En contra: la coherencia entre base y archivos depende del orden de escritura (primero el experimento, después el archivo, revirtiendo si falla) y del respaldo conjunto.
- **Elementos afectados:** contenedor Almacén de archivos de resultados; componentes Acceso a archivos, Guardar experimento, Gestión de capturas y Servicio de consulta.
- **Cómo se verifica:** cargar 100.000 experimentos de prueba con PDB de unos 250 KB y comprobar que la base crece solo con metadatos y rutas, que el tamaño de los archivos queda en el volumen y que una consulta no lee archivos (`EC-03`).

### DA-05 — Consultas con índices y listados livianos, sin paginar

- **Escenario que la motiva:** `EC-03`, con el límite que impone `EC-09`.
- **Contexto:** los listados y el Detector consultan por molécula, ligando, proyecto, fecha y autor sobre un catálogo que crece. `EC-09` pide llegar a la pose de cualquier fila sin paginar.
- **Decisión:**
  - Tácticas: reducir sobrecarga (Desempeño: índices sobre las columnas de filtro y sobre el par molécula/ligando del Detector; listados que no traen archivos ni parámetros).
  - Estilo y patrón: no cambian.
  - No se pagina.
- **Alternativas consideradas:**
  - Paginación — descartada por `EC-09`; se reevalúa si algún filtro devuelve demasiado.
  - Caché de resultados — descartada: agrega invalidación y no hace falta con índices.
  - Más recursos del servidor — descartada por ahora; queda como plan B si la medida no se cumple.
- **Consecuencias:**
  - A favor: sin componentes ni contenedores nuevos; el mismo índice acelera el Detector.
  - En contra: los índices ocupan espacio y enlentecen las escrituras (despreciable a este volumen); filtrar por parámetro (DA-03) sigue siendo más lento.
- **Elementos afectados:** componentes Repositorio de experimentos y Servicio de consulta; contenedor Base de datos de experimentos.
- **Cómo se verifica:** con los 100.000 experimentos de prueba, repetir 20 veces el filtro por proteína y comprobar que cada una tarda 5 segundos o menos (`EC-03`), y que el plan de la consulta usa el índice. Para el límite de `EC-09`, comprobar con listados de 20, 100 y 500 resultados que ver la pose cuesta una sola acción.

### DA-06 — Google Docs sin cola: captura de la falla y reintento manual

- **Escenario que la motiva:** `EC-05` y `EC-06` (no son drivers, pero la falta de cola hay que justificarla).
- **Contexto:** Google Docs está fuera del control del grupo. RF-05, RF-09 y la historia `HU-01.E1` ya definen que el experimento queda guardado "no vinculado" y que el reintento lo dispara el investigador/a. Dos personas y un cuatrimestre.
- **Decisión:**
  - Tácticas: detección de excepciones, manejo de excepciones, degradación controlada y reintento manual iniciado por el usuario (Disponibilidad); acotar tiempos de ejecución, con un tiempo máximo de espera en la llamada (Desempeño); adaptar la interfaz, porque el Cliente de Google Docs oculta la API (Interoperabilidad).
  - Estilo y patrón: ninguno adicional.
  - Vincular documento, último filtro de la cadena, captura la falla, deja el experimento "no vinculado" y la pantalla lo avisa. La misma lógica corre desde el reintento.
- **Alternativas consideradas:**
  - Cola con proceso de trabajo y reintento automático — descartada: ningún escenario exige reintentar sin intervención y suma un contenedor que operar.
  - Estilo orientado a eventos solo en esa zona — descartada: solo se justificaría si Fiabilidad fuera driver; cambiaría `HU-01.B1.2`.
  - Llamar a Google Docs dentro de la misma transacción del guardado — descartada: una falla externa revertiría el registro y violaría `EC-05`.
- **Consecuencias:**
  - A favor: simple de construir y explicar; el guardado nunca se revierte por Google Docs.
  - En contra: el reintento depende de que alguien lo dispare; si Google Docs está caído, quien registra espera hasta el tiempo máximo.
- **Elementos afectados:** componentes Vincular documento, Cliente de Google Docs y Gestión de excepciones.
- **Cómo se verifica:** simular que Google Docs no responde y comprobar que el experimento queda guardado y "no vinculado", sin pérdida de datos (`EC-05`); restablecer el servicio y repetir 20 reintentos, de los que 19 o más deben resolverse bien (`EC-06`).

### DA-07 — Despliegue en un único servidor web

- **Escenario que la motiva:** `EC-03` (capacidad con 100.000 experimentos) y, sin ser driver, `EC-02` (20 consultas concurrentes); además las restricciones `RT-03`, `RE-01` y `RE-04`.
- **Contexto:** hay que decidir en qué infraestructura corre cada contenedor. El equipo son dos personas y el sistema lo usa un grupo de investigación. La restricción `RT-03` pide alojarlo en un servidor web. Los datos crecen del orden de 25 GB solo en PDB.
- **Decisión:**
  - Tácticas: ninguna nueva de infraestructura. Se descartan aumentar recursos, mantener copias y réplicas (sección 5.1), porque con índices alcanza para el volumen del escenario.
  - Estilo y patrón: no cambian.
  - Un solo nodo, el Servidor web, ejecuta la Aplicación del catálogo y la Base de datos de experimentos, y contiene el Volumen de archivos con el Almacén de archivos de resultados. La base solo acepta conexiones de la propia máquina. Cada usuario ejecuta el Navegador en su computadora.
- **Alternativas consideradas:**
  - Un servidor de base de datos aparte — descartada: suma una máquina que operar y una red entre la aplicación y la base, sin que un escenario lo exija.
  - Varias instancias de la aplicación con un balanceador — descartada: `EC-02` se cumple con índices y no hay escenario de disponibilidad que sea driver.
  - Servicio de almacenamiento en la nube para los archivos — descartada por lo mismo que en `DA-04`: agrega una dependencia externa y costo.
- **Consecuencias:**
  - A favor: una sola máquina que operar y respaldar; no hay red entre la aplicación y la base.
  - En contra: punto único de falla (si cae el servidor, el sistema deja de estar disponible); aplicación, base y archivos comparten procesador, memoria y disco; el disco es el recurso a vigilar. Si no se cumple la medida de `EC-03`, el paso siguiente es pasar la base a un nodo propio.
- **Elementos afectados:** nodos Servidor web y Volumen de archivos; contenedores Aplicación del catálogo, Base de datos de experimentos y Almacén de archivos de resultados.
- **Cómo se verifica:** con los 100.000 experimentos de prueba en el servidor elegido, medir el filtro por proteína (5 segundos o menos) y 20 consultas simultáneas (cada una en 5 segundos o menos, sin fallas), y controlar el espacio usado del volumen frente a los 50 GB. Probar además la recuperación: restaurar un respaldo conjunto de la base y del volumen en un servidor limpio.

---

## 11. Trazabilidad

**Escenario → táctica → estilo o patrón → decisión → elemento C4**

| Escenario (TP2) | Atributo | Tácticas | Estilo o patrón | Decisión | Elemento C4 |
|---|---|---|---|---|---|
| `EC-08` | Modificabilidad y capacidad de prueba | Dividir módulos; encapsular; restringir dependencias; abstraer fuentes de datos; limitar la complejidad estructural | Cliente-servidor + capas; tuberías y filtros en el registro | `DA-01`, `DA-02` | Componentes Ejecutor de registro, Validar datos, Detectar duplicados, Guardar experimento, Vincular documento, Repositorio de experimentos |
| `EC-07` | Modificabilidad | Parametrización; encapsular | Capas (el repositorio oculta el almacenamiento) | `DA-01`, `DA-03` | Componente Repositorio de experimentos; contenedor Base de datos de experimentos |
| `EC-03` | Desempeño | Reducir sobrecarga | Cliente-servidor | `DA-04`, `DA-05`, `DA-07` | Contenedor Almacén de archivos de resultados; nodos Servidor web y Volumen de archivos; componentes Acceso a archivos, Gestión de capturas, Servicio de consulta, Repositorio de experimentos |
| `EC-05`, `EC-06` (no drivers) | Disponibilidad | Detección de excepciones; manejo de excepciones; degradación controlada; reintento; acotar tiempos de ejecución; adaptar la interfaz | Tuberías y filtros (último paso) | `DA-06` | Componentes Vincular documento, Cliente de Google Docs, Gestión de excepciones |

**Historia de usuario → elementos:** ver la sección 9.

**Responsabilidad → elemento:** la columna "Se rastrea a" de los catálogos de las secciones 6 y 7, y el catálogo de nodos de la sección 8, vinculan cada contenedor y cada componente con sus requerimientos, escenarios o decisiones. Todo driver llega a al menos un contenedor, componente o nodo de despliegue.

---

## 12. Glosario y bibliografía

Las siglas usadas están en la sección 1.6 (Anexo D de la consigna).

| Término | Significado |
|---|---|
| Driver arquitectónico | Escenario de calidad que condiciona la estructura del sistema (sección 4) |
| Táctica | Decisión de diseño que ayuda a alcanzar la medida de un escenario de calidad |
| Estilo | Forma de organizar el sistema entero y las reglas con que se comunican sus partes |
| Patrón | Forma de organizar un contenedor por dentro |
| Contenedor | Aplicación o almacén de datos que se ejecuta por separado (vista de contenedores) |
| Componente | Agrupación coherente de funcionalidad dentro de un contenedor (vista de componentes) |
| Nodo de despliegue | Infraestructura donde se ejecutan los contenedores: un servidor, el navegador del usuario o un volumen de disco |
| Entorno de producción | El entorno real en el que el sistema funcionaría para sus usuarios |
| Filtro | Paso de la cadena de registro: recibe la solicitud, la completa y la devuelve |
| Solicitud de registro | Objeto único que recorre la cadena de registro y que cada filtro completa |
| Ejecutor de registro | Componente que conoce el orden de los filtros y arma y ejecuta la cadena |
| "No vinculado" | Estado de un experimento guardado cuyo documento de notas no pudo crearse todavía |
| Repositorio simulado | Reemplazo del repositorio de experimentos que se usa en las pruebas para no depender de la base real |

**Bibliografía**

- Bass, L., Clements, P. y Kazman, R. *Software Architecture in Practice*. Addison-Wesley. Catálogo de tácticas por atributo de calidad.
- ISO/IEC 25010:2023. *Systems and software Quality Requirements and Evaluation (SQuaRE) — Product quality model*.
- Brown, S. El modelo C4 para visualizar la arquitectura de software.
- Material teórico de la materia sobre arquitectura de software y consigna del TP3.
