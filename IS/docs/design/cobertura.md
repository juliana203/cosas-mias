# Reporte de cobertura y análisis (TP4 · HU-01.A1)

## Cómo se midió

- **Comando recomendado:** `pytest --cov=src --cov-branch --cov-report=term-missing` (usa `.coveragerc`, que excluye la interfaz gráfica y el arranque).
- **Cómo se obtuvieron los números de este reporte:** el entorno donde se armó la entrega no podía instalar `pytest-cov`, así que la cobertura de **líneas** se midió con el módulo `trace` de la biblioteca estándar de Python, sobre las mismas 62 pruebas. La cobertura de **ramas** no la mide esa herramienta: el análisis de decisiones de la sección 3 es manual. Conviene que el grupo vuelva a correr el comando recomendado en su máquina y reemplace la tabla con la salida real.
- **Excluido del cálculo (se indica a propósito):** `src/presentacion/*` (interfaz gráfica: no se prueba por la interfaz, según la consigna) y `src/arranque.py` (arma los objetos y carga datos de ejemplo). La interfaz se verificó a mano con el recorrido de la demostración (sección 4).

## Resultado

62 pruebas, todas pasan al ejecutarlas desde cero (`pytest`, 0,1 s).

| Archivo | Líneas ejecutables cubiertas |
|---|---|
| `src/dominio/entidades.py` | 56/56 (100 %) |
| `src/dominio/solicitud.py` | 41/41 (100 %) |
| `src/dominio/pasos/validar_datos.py` | 39/39 (100 %) |
| `src/dominio/pasos/guardar_experimento.py` | 44/44 (100 %) |
| `src/dominio/pasos/detectar_duplicados.py` | 17/17 (100 %) |
| `src/dominio/pasos/paso.py` | 7/7 (100 %) |
| `src/dominio/registro_tecnicas.py` | 16/16 (100 %) |
| `src/dominio/tecnica.py` | 24/24 (100 %) |
| `src/dominio/tecnica_docking.py` | 22/22 (100 %) |
| `src/dominio/puertos.py` | 24/24 (100 %) |
| `src/servicios/ejecutor_registro.py` | 17/17 (100 %) |
| `src/servicios/servicio_consulta.py` | 10/10 (100 %) |
| `src/acceso_datos/repositorio_en_memoria.py` | 32/32 (100 %) |
| `src/acceso_datos/archivos_en_memoria.py` | 17/17 (100 %) |
| `src/transversal/gestion_excepciones.py` | 29/29 (100 %) |
| **Total** | **395/395 (100 %)** |

## Análisis

### Qué no quedó cubierto y por qué

- **Líneas:** ninguna dentro del alcance medido.
- **Fuera del cálculo:** la interfaz gráfica y el arranque (ver arriba). Son transcripción de formularios a datos y armado de objetos; no tienen reglas de negocio.
- **Ramas que ninguna prueba recorre aunque la línea esté cubierta** (análisis manual):
  - `AccesoArchivosEnMemoria.eliminar_archivos` con un experimento que no tiene archivos: se ejecuta en el rollback, pero solo con archivos presentes.
  - `GuardarExperimento`, rollback cuando falla `guardar_pdb` (en lugar de `guardar_captura`): la prueba de falla usa una captura. El `except` es el mismo para los dos, pero no hay una prueba que falle justo en el PDB.
  - `RepositorioExperimentosEnMemoria.eliminar` de un id inexistente (usa `pop` con valor por defecto, no falla): no tiene prueba propia.

### Pruebas que se agregaron al ver el reporte

La primera corrida dio 99,0 % (391/395): quedaban sin cubrir `RepositorioExperimentosEnMemoria.proyectos` y los tres métodos de `ServicioConsulta`, que alimentan el formulario. Se agregó `test_servicio_consulta.py` y se llegó al 100 %.

### Pruebas que pasan pero verifican poco

Para evaluar si las pruebas realmente verifican, se hizo una **revisión por mutación manual**: se cambió una línea del código por vez y se volvió a correr la suite. Las siete mutaciones fueron detectadas (al menos una prueba falló):

| Mutación | ¿La detectó la suite? |
|---|---|
| Quitar `and not solicitud.confirmada` de *Detectar duplicados* | Sí |
| `puede_ser_coincidencia` siempre verdadero | Sí |
| Quitar `eliminar` del rollback de *Guardar experimento* | Sí |
| Fecha futura: `>` por `>=` | Sí |
| `coincide_con` ignora el tipo | Sí |
| Quitar la exclusión de "Similar a" | Sí |
| Comparar valores sin normalizar mayúsculas ni espacios | Sí |

Aun así, hay pruebas débiles:

- `test_datos_validos_pasan` (*Validar datos*) solo comprueba que no se lance una excepción.
- `CP-11` verifica que el docking "sigue funcionando" con una sola aserción (`obtener("docking").tipo`): confirma que el plug-in sigue registrado, no que registre bien un experimento. Lo cubren `CP-01` y las demás.
- `CP-10` usa pasos espía: verifica el orden y el corte, no el contenido de los pasos reales (que se prueban aparte).

### Lo que la cobertura no dice

100 % de líneas significa que todo se ejecutó, no que todo se verificó. La medida de `EC-07` (0 columnas modificadas en menos de una jornada) no se puede medir con una prueba unitaria: `CP-11` verifica su condición estructural (una técnica nueva se agrega solo registrándola y se guarda con la misma entidad), pero el tiempo de "una jornada" depende de las personas.

## Demostración

La demostración sigue el criterio de aceptación en la interfaz (`python run.py`, `http://localhost:5000/registro`):

1. Completar el formulario con proteína "Proteasa HIV-1", ligando "Indinavir", software, fecha y un PDB: coincide con el experimento de ejemplo #101 y aparece la tabla de coincidencias.
2. **Continuar de todos modos:** se registra el experimento nuevo (#102) y el #101 no cambia.
3. **Cancelar:** no se guarda nada.
4. Dejar la proteína vacía: se rechaza con el mensaje, sin guardar.
