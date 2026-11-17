# Registro del uso de IA — TP4

> Borrador para unir a `docs/uso_ia.md`. Las columnas "Qué decidió el grupo" las completan Juliana y Lucas: la consigna pide registrar qué se aceptó, modificó o descartó y por qué, y eso solo lo saben ustedes. Antes de la defensa conviene tener al menos un caso real en que rechazaron una sugerencia (la consigna lo pide).

| # | Qué se pidió | Qué propuso la IA | Qué decidió el grupo y por qué |
|---|---|---|---|
| 1 | Opciones de diseño para las capas tras la devolución del profesor | Tres opciones (5 capas, 4 capas, esquema aplicación-dominio-infraestructura), recomendando 5 capas | *(completar)* Se eligió 4 capas por indicación del profesor; la propuesta de 5 se descartó |
| 2 | Recomendar una HU para el TP4 | Recomendó HU-01.A1 (con B1.1 de base) y HU-01.E1 como alternativa | *(completar)* Se eligió A1 y se dejó Google Docs fuera de alcance |
| 3 | Aplicar el cambio de capas a `arquitectura.md` | Redactó los cambios en 5.2.2, 5.3, 5.5, 7 y DA-01 | *(completar)* |
| 4 | Diseño detallado de A1 (robustez, secuencias, clases) | Propuso `EjecutorRegistro` sin lógica, reglas de coincidencia en `Experimento`, clave en el plug-in | *(completar)* |
| 5 | Implementar y probar | Escribió el código, las 62 pruebas y una revisión por mutación manual | *(completar: qué revisaron, qué cambiaron)* |

## Qué hay que verificar (consigna, sección 8)

- Los diagramas cumplen las reglas de la Referencia (Pasos 3 a 5): se renderizaron todos y se revisaron las reglas de conexión.
- El código coincide con el diagrama de clases: los nombres de clases y operaciones del diagrama están en `src/`.
- Las pruebas verifican comportamiento real: ver el análisis por mutación en `docs/design/cobertura.md`.
- Limitación a mencionar: la cobertura se midió con `trace` porque no se pudo instalar `pytest-cov`; conviene volver a medirla con `pytest-cov`.
