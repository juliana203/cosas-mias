# TP3: Estudios de Dinámica Molecular de SIRT1

*Diseño y Descubrimiento de Drogas – FI-UNER 2026*

---

> ## Chequeos antes de entregar (borrar este bloque)
>
> 1. **Máscara "sin extremos".** En C1 el cpptraj usó `:6-270` (excluye 5 residuos N-terminales y 10 C-terminales). Si cortaste 6 y 10, el rango correcto sería `7-270`. Ajustá el texto o la leyenda según lo que hayas corrido. En el apo confirmá la máscara con `cat centrado_RMSD_RMSF_sinCola.ptraj`.
> 2. **Eje X en frames.** Dejá los gráficos como están. En el pie de cada figura aclará "tiempo en frames; 1 frame ≈ 20 ps (2500 frames ≈ 50 ns)" [confirmá el intervalo de guardado en el `mdin`]. C1 tiene 2400 frames (~48 ns) y el apo 3500 (~70 ns).
> 3. **El "RMSD Backbone" no incluye al ligando.** La máscara `:1-281@CA,C,N,O` da 1116 átomos igual que `:1-280@CA,C,N,O`, porque los átomos del ligando no se llaman CA, C, N ni O. El ligando entra en el **RMSD Total** (`:1-281`), pero no en el RMSF (279 residuos).
> 4. **Capturas de tLeap vs. trayectorias analizadas.** Las capturas de tLeap muestran tu preparación (ligando = residuo 512, 12817 aguas, 5 Na⁺). Los sistemas C1–C3 analizados (ligando = residuo 281) son los provistos por la cátedra. El texto de 2.A lo aclara.
> 5. En las capturas de tLeap hay un `Error: ... chain type [H21] must be 1 character`, que aparece porque se usó `loadamberprep` sobre el `.frcmod`. Después se cargó bien con `loadamberparams`. Si te lo preguntan, es por eso.
> 6. **Lo que está entre `[corchetes]` depende de vos:** cómo se obtuvo el apo en el TP1 (1a), la figura 5 de Davenport (1b.ii), las **distancias medidas en PyMOL** sobre las poses representativas de C2 y C3 (sistemas 3 y 4), la tabla de RMSF del bolsillo y los números de figura.
> 7. **Elecciones de 2.D.** Sistema 2 → 2-B (justificado con `hbond`). Sistema 1 → 1-C (tentativa; revisala contra cómo plantea la consigna los "eventos"). Sistemas 3 y 4: asumí que son C2 y C3 [confirmar].
> 8. **Pregunta 2 de la discusión:** la consigna pide conclusiones "para cada ligando", por eso está respondida para C1, C2 y C3. Como referencia de "las interacciones del docking" se usaron los puentes de hidrógeno del **primer frame** de cada simulación (pose de partida, ya minimizada y equilibrada), no un docking nuevo. El texto lo aclara.
> 9. Los valores de RMSD y RMSF están leídos de los gráficos, por eso van con "≈". Los porcentajes de puentes de hidrógeno salen de `hb_avg.dat` y los de clusters de `summary.dat`.
> 10. **Si C1 es tu compuesto del TP2** (mepenzolato sin el metilo en C15), agregá a 2a de C1 lo que decía tu informe del TP2: puente con Tyr49 (2.49 Å) y, en la pose alternativa, con Arg43 (3.07 Å), y la nueva N–H sin anclarse a Ser210. Si no lo es, ignoralo.

---

## 1. Introducción

Las sirtuinas son desacetilasas dependientes de NAD⁺ y SIRT1 es la más estudiada de la familia. Su relevancia en procesos metabólicos, de envejecimiento e inflamatorios la convierte en un blanco terapéutico prometedor. En los trabajos previos se estudió la estructura del receptor (TP1) y los modos de unión de distintos ligandos mediante docking molecular (TP2).

El docking entrega una pose estática, calculada con un receptor tratado en gran medida como rígido y con una descripción simplificada del solvente. Sin embargo, las proteínas se mueven constantemente, presentan regiones con distinta flexibilidad y los ligandos deben acomodarse en el sitio de unión. Además, las moléculas de agua pueden participar de forma decisiva en la estabilización de los complejos. Por eso, el resultado del docking puede verse modificado, a veces de manera significativa, al introducir movimiento y solvente explícito.

En este trabajo se realizaron simulaciones de dinámica molecular (MD) con solvente explícito para (i) evaluar la dinámica de SIRT1 en su forma apo y (ii) evaluar la permanencia en el tiempo de las poses obtenidas por docking para tres ligandos (C1, C2 y C3), analizando la estabilidad global del receptor, la flexibilidad por residuo y las interacciones ligando-receptor, incluidas las mediadas por agua.

El informe incluye la preparación de los sistemas (2.A), el protocolo de simulación (2.B), el control y análisis general de las trayectorias (2.C), el análisis de los modos de unión (2.D) y la discusión.

---

## 2. Procedimiento

### 2.A Preparación de los sistemas

Los estudios se llevaron a cabo con los complejos propuestos por la cátedra para el TP2. La parametrización del ligando se realizó con el paquete AMBER:

1. **Antechamber:** a partir del archivo `.gesp` del ligando se generó el archivo `.prepin` con cargas RESP y tipos atómicos GAFF.
2. **parmchk2:** se generó el archivo `.frcmod` con los parámetros complementarios requeridos por el campo de fuerzas.
3. **tLeap:** se cargó `leaprc.gaff`, los parámetros del ligando (`.prepin` y `.frcmod`) y los parámetros **ZAFF** (`ZAFF.prep` y `ZAFF.frcmod`). Estas dos últimas líneas incorporan los parámetros del campo de fuerzas necesarios para describir el **ion zinc** y su esfera de coordinación (cisteínas del dominio de unión a zinc, tipo CY1), que no están contemplados en el campo de fuerzas estándar de la proteína.

Se cargó el complejo SIRT1-ligando proveniente del docking, se neutralizó el sistema y se solvató:

- `check` inicial: la carga neta del sistema era de aproximadamente −5 (−4.999988), por lo que se agregaron **5 contraiones Na⁺** (`addions SIRT_CN Na+ 0`).
- `solvateoct SIRT_CN TIP3PBOX 9.0`: el complejo se sumergió en una **caja octaédrica truncada de agua** con un margen mínimo de 9.0 Å entre el soluto y el borde de la caja. Se agregaron 12817 moléculas de agua (volumen de la caja ≈ 4.87 × 10⁵ Å³).
- Tras la neutralización y la solvatación, `check` informó 2 advertencias de contactos cercanos entre átomos no enlazados (1.18 y 1.48 Å) y la unidad se consideró correcta (`Unit is OK`). Estos contactos se resuelven en la etapa de minimización.
- Se guardaron los archivos de topología y coordenadas (`SIRT_CN.prmtop` y `SIRT_CN.rst7`) y un `.pdb` del sistema (`SIRT_CN.pdb`).
- **Verificación de los archivos:** se comprobó la correcta creación de `SIRT_CN.prmtop`, `SIRT_CN.rst7` y `SIRT_CN.pdb` [confirmar con `ls -lh SIRT_CN.*`]. Al guardar el `.pdb`, tLeap convirtió los nombres de los residuos terminales (NHIE → HIE y CILE → ILE), lo que es solo un cambio de formato.

**¿Qué tipo de solvente se utilizó?** Se utilizó un **modelo de solvente explícito TIP3P**. Esto surge del comando `solvateoct ... TIP3PBOX 9.0`, que rodea al complejo con moléculas de agua del modelo TIP3P dentro de una caja octaédrica truncada.

**Compuestos trabajados.** [Figura 1: ligando C1 en el sitio de unión de SIRT1] [Figura 2: ligando C2] [Figura 3: ligando C3] [Figura 4: complejo con los residuos del bolsillo resaltados]

**Caja de solvatación.** [Figura 5: complejo (C1) dentro de la caja de solvatación, con las aguas en líneas]

Para el análisis se emplearon las trayectorias provistas por la cátedra, correspondientes al receptor en forma **apo** (partiendo de la estructura cerrada) y a los complejos **C1, C2 y C3**:

| Sistema | Átomos | Moléculas de solvente | Frames analizados | Duración aprox. |
|---|---|---|---|---|
| Apo | [completar] | [completar] | 3500 | ~70 ns |
| C1 | 46349 | 13938 | 2400 | ~48 ns |
| C2 | 43091 | 12858 | 2500 | ~50 ns |
| C3 | 44172 | 13218 | 2500 | ~50 ns |

*(Frames de 20 ps [confirmar]. En todos los casos la caja es un octaedro truncado.)*

### 2.B Protocolo de dinámica molecular

El protocolo constó de las siguientes etapas, con los scripts provistos por la cátedra:

1. Minimización de energía.
2. Termalización (1 ns).
3. Equilibrado (2 ns).
4. Dinámica de producción (50 ns, en corridas de 5 ns). La dinámica del apo se extendió a 70 ns (14 corridas de 5 ns).

---

## 3. Resultados

### 3.1 Control de las simulaciones y análisis generales (2.C)

Las trayectorias se centraron con `cpptraj` (`autoimage`, centrado sobre el centro de masa y la primera molécula como ancla) para que la proteína y todas las moléculas de agua quedaran dentro de la celda unidad. Luego se calcularon, con ajuste por mejor superposición respecto del primer frame:

- **RMSD del backbone** (átomos CA, C, N, O) de los residuos 1–281.
- **RMSD total** de los residuos 1–281 (todos los átomos del receptor y del ligando).
- **RMSD del receptor solo** (residuos 1–280, backbone).
- **RMSD del receptor sin extremos móviles** (residuos 6–270, backbone) [ajustar al rango usado].
- **RMSF por residuo** (átomos C, CA y N).

Las curvas se graficaron con xmgrace (RMSD vs. tiempo en frames y RMSF vs. número de residuo).

[Figura 6: Evolución del RMSD – Apo] [Figura 7: RMSF – Apo] [Figura 8: RMSD del receptor con y sin extremos móviles – Apo]
[Figuras 9–11: Evolución del RMSD, RMSF y RMSD con y sin extremos – C1]
[Figuras 12–14: ídem para C2]
[Figuras 15–17: ídem para C3]

**Tabla 1. Valores aproximados de RMSD (Å), leídos de los gráficos.**

| Sistema | Backbone (meseta) | Total (meseta) | Receptor 1–280 | Sin extremos (6–270) | Máximo del backbone |
|---|---|---|---|---|---|
| Apo | ≈ 4.0–4.5 (deriva a ≈ 4.8 al final) | ≈ 4.5–5 (≈ 5.5 al final) | ≈ 4.0–4.7 | ≈ 2.3 (≈ 2.8 al final) | ≈ 4.8 (al final) |
| C1 | ≈ 2.3–2.8 | ≈ 3.0–3.8 | ≈ 2.5 | ≈ 2.2 | ≈ 4.0 (frame ~1600) |
| C2 | ≈ 2.5–2.7 | ≈ 3.2–3.7 | ≈ 2.5 | ≈ 2.0–2.3 | ≈ 3.4 (frame ~2000) |
| C3 | ≈ 1.8–2.2 | ≈ 2.6–3.2 | ≈ 1.9 | ≈ 1.5 | ≈ 3.1 (frame ~2050) |

**Tabla 2. RMSF aproximado (Å).**

| Sistema | Núcleo | Región 40–60 | Región ~170 | N-terminal | C-terminal |
|---|---|---|---|---|---|
| Apo | ≈ 1 | ≈ 2.9 | ≈ 2.7 | ≈ 3.7 | ≈ 7.8 |
| C1 | ≈ 1 | ≈ 2.8 | ≈ 2.5 | ≈ 3.7 | ≈ 9 |
| C2 | ≈ 1 | ≈ 3.2 | ≈ 2.4 | ≈ 3.5 | ≈ 8.5 |
| C3 | ≈ 1 | ≈ 2.3 | ≈ 2.0 | ≈ 4.4 | ≈ 8.7 |

#### El receptor solo vs. el receptor sin considerar los extremos móviles

Los extremos N- y C-terminal de la proteína suelen estar poco restringidos y se mueven mucho en el solvente, lo que aumenta el RMSD global sin que implique un cambio del plegamiento. **Esto se verifica de dos maneras:** (i) el RMSF muestra valores muy altos en ambos extremos (≈ 3.5–4.4 Å en el N-terminal y hasta ≈ 8–9 Å en el C-terminal, contra ≈ 1 Å en el núcleo) y (ii) al excluir esos residuos del cálculo, el RMSD **disminuye y se vuelve más plano**.

- **C1, C2 y C3:** la diferencia es de ≈ 0.3–0.5 Å (hasta ≈ 0.7 Å en C3, donde la curva sin extremos queda casi plana en ≈ 1.5 Å). En C3 los picos de ≈ 500 y ≈ 2000 frames desaparecen en gran parte, por lo que provienen sobre todo de los extremos.
- **Apo:** la diferencia es mucho mayor. El receptor completo ronda ≈ 4–4.7 Å, mientras que sin extremos ronda ≈ 2.3–2.8 Å. En la forma apo, los extremos aportan la mayor parte del RMSD global.

En todos los casos se concluye que el **núcleo de la enzima es estable** y que gran parte del RMSD global proviene de los extremos móviles y no de un desarmado de la proteína.

#### ¿Las MD están convergidas?

- **C3: sí.** El RMSD oscila en torno a un valor estable (≈ 2 Å en el backbone). Tiene dos excursiones transitorias (≈ 500 y ≈ 2050 frames) que vuelven al valor base.
- **C2: sí.** Alcanza una meseta (≈ 2.6 Å en el backbone y ≈ 3.5 Å en el total) con una perturbación puntual cerca del frame 2000 (≈ 40 ns) que se recupera.
- **C1: parcialmente.** Tras una meseta inicial (≈ 2.3–2.6 Å) sube de forma escalonada hasta un máximo cerca del frame 1600 (≈ 32 ns), con un RMSD total de ≈ 4.9 Å. Después desciende solo en parte (≈ 2.8 Å en el backbone al final). Sin extremos la curva es más estable, pero no se puede asegurar una convergencia estricta en 48 ns.
- **Apo:** el RMSD crece rápido durante los primeros ≈ 400 frames (≈ 8 ns), forma una meseta de ≈ 4–4.5 Å y deriva lentamente hacia arriba hasta el final de los 70 ns. Sin extremos la curva es casi plana (≈ 2.3 Å) con un leve aumento final (≈ 2.8 Å), de modo que el núcleo está prácticamente equilibrado y la deriva proviene en buena parte de los extremos.

En todos los casos, una sola trayectoria de 50–70 ns permite hablar de estabilidad en esa escala de tiempo, pero no de convergencia completa del muestreo conformacional.

#### Comportamientos de los RMSD (intra e inter sistemas)

**Intra-sistema.** En los cuatro sistemas, el RMSD total es mayor que el del backbone (≈ 0.7–1 Å en los complejos). Es esperable, porque el RMSD total incluye las cadenas laterales, que tienen mucha más libertad de rotación que el esqueleto, además del ligando y de los átomos de hidrógeno. El RMSD del receptor completo es mayor que el del receptor sin extremos, como se explicó antes.

**Inter-sistemas.** El orden de estabilidad del RMSD del backbone es **C3 < C2 < C1** (C3 el más estable y con la meseta más baja y recta, C1 el menos estable). El **apo** tiene los valores más altos del conjunto (≈ 4–4.7 Å), pero al excluir los extremos queda a un nivel comparable al de los complejos (≈ 2.3 Å frente a ≈ 1.5–2.2 Å). Dos precauciones al comparar:

- Las diferencias de ≈ 0.5–1 Å entre compuestos provienen de una sola trayectoria por sistema y no deben interpretarse como diferencias de afinidad.
- El apo es una simulación distinta (más larga, preparada de forma independiente) y que el apo muestre un RMSD global tan superior podría reflejar tanto la ausencia del ligando como diferencias propias de ese sistema.

Como se verá en 3.2, el orden de estabilidad del receptor **no coincide** con el del anclaje del ligando por puentes de hidrógeno (C2 > C1 > C3): que el receptor se mueva poco no implica que el ligando esté mejor unido.

#### RMSF

Los cuatro perfiles son muy parecidos: núcleo rígido (≈ 0.5–1.5 Å, con un mínimo de ≈ 0.5 Å cerca de los residuos 25 y 205) y picos en las mismas regiones, que corresponden a loops superficiales:

- residuos **≈ 35–60** (≈ 2.3 Å en C3 hasta ≈ 3.2 Å en C2);
- residuos **≈ 170** (≈ 2.0 Å en C3 hasta ≈ 2.7 Å en el apo);
- en menor medida **≈ 88**, **≈ 188** y **≈ 240**;
- y los extremos, sobre todo el C-terminal, que llega a ≈ 8–9 Å.

C3 es el sistema con los picos más bajos (la proteína es más rígida en esas regiones) y C2 y el apo muestran los más altos en la región 40–60.

**Sitio de unión.** Los residuos que interactúan con los ligandos son Ala31, Tyr49, His132, Ser210 y Ser211 (C1); Arg43, Gln114, Lys213, Arg235 y Ser211 (C2); y Arg215, Val181 y Arg43 (C3). Si un ligando rigidizara el sitio activo, el RMSF de estos residuos sería menor en el complejo que en el apo. Los gráficos muestran lo siguiente (valores leídos de las curvas):

- **Arg43 y Tyr49** están en el loop 40–60, el más móvil del sitio (≈ 2–3 Å). En C3 ese loop es más rígido (≈ 2.3 Å), en C1 es parecido al apo (≈ 2.8 Å) y en C2 es incluso más móvil (≈ 3.2 Å) que en el apo (≈ 2.9 Å).
- **Gln114, His132, Val181, Ser210, Ser211, Lys213, Arg215 y Arg235** tienen un RMSF bajo (≈ 0.5–1.7 Å, la mayoría ≈ 1 Å) en los cuatro sistemas, sin diferencias claras entre el apo y los complejos. Ser210 y Ser211 quedan junto al mínimo de RMSF de la región ≈ 205.

**Conclusión.** La presencia del ligando no modifica de forma marcada la flexibilidad del bolsillo, salvo en el loop 40–60, así que no puede afirmarse que algún ligando rigidice el sitio activo. El efecto más visible es la mayor rigidez de ese loop en C3, que es el ligando con menos contactos polares con la proteína; esto refuerza que un receptor más rígido no equivale a una mejor unión. También concuerda con 3.2: los contactos con Tyr49 y Arg43 (en el loop flexible) son los más transitorios, y los de las serinas (en una zona rígida) son los más persistentes.

*(Opcional, para números exactos por residuo: `awk '$1==43 || $1==49 || $1==114 || $1==181 || $1==210 || $1==211 || $1==213 || $1==215' atomic_resCA.apf` en la carpeta de cada sistema.)*

---

### 3.2 Análisis de los modos de unión (2.D)

#### Sistema 1 (apo)

La figura representativa es **1-C**, que superpone frames de la trayectoria coloreados por tiempo. Muestra que el **plegamiento global se conserva** durante la simulación y que la variabilidad se concentra en loops superficiales y en los extremos. Esto es consistente con:

- el RMSD sin extremos, que forma una meseta en ≈ 2.3 Å;
- el RMSF, bajo en el núcleo (≈ 1 Å) y alto solo en los loops (≈ 40–60 y ≈ 170) y los extremos.

Las figuras 1-A y 1-B muestran reordenamientos locales de los residuos del sitio, pero reflejan estados puntuales y no el comportamiento global de la trayectoria.

#### Sistema 2 (C1)

Se muestran tres poses del ligando (2-A, 2-B y 2-C) con las distancias a los residuos del sitio:

| Pose | Tyr49 (OH) | His132 (HE2) | Ser211 (HG) | Ser210 (HG) |
|---|---|---|---|---|
| 2-A | 4.20 Å | ≈ 2.74 Å | 3.85 Å | > 5 Å |
| 2-B | **2.66 Å** | 5.05 Å | 4.60 Å | 6.25 Å |
| 2-C | 4.64 Å | 3.73 Å | > 5 Å | **1.63 Å** |

Para decidir cuál es la más representativa, se analizó la persistencia de los puentes de hidrógeno ligando-proteína a lo largo de los 2400 frames (`cpptraj hbond`, distancia dador–aceptor ≤ 3.0 Å y ángulo ≥ 135°):

**Tabla 3. Puentes de hidrógeno del ligando con la proteína en C1 (fracción de frames).**

| Residuo | Átomo proteína | Átomo ligando | % de frames | Distancia media (Å) |
|---|---|---|---|---|
| SER 211 | N (H) | O5 | 35.2 | 2.86 |
| TYR 49 | OH (HH) | O4 | **35.0** | 2.79 |
| SER 211 | OG (HG) | O6 | 34.1 | 2.70 |
| SER 211 | N (H) | O6 | 29.5 | 2.86 |
| SER 211 | OG (HG) | O5 | 27.8 | 2.71 |
| ALA 31 | N (H) | O6 | 15.1 | 2.85 |
| SER 210 | OG (HG) | O5 | 14.8 | 2.65 |
| SER 210 | OG (HG) | O6 | 14.2 | 2.65 |
| HIE 132 | NE2 (HE2) | N1 | **0.4** | 2.94 |

Los porcentajes se calcularon por puente individual y se superponen, por lo que no pueden sumarse.

**Pose representativa: 2-B.**

- El contacto con **Tyr49** (O4···OH) está presente en el 35 % de los frames y es el puente individual más frecuente de los que muestran las tres poses.
- El contacto con **Ser210**, que muestra 2-C, aparece en ≈ 14–15 % de los frames.
- El contacto con **His132**, que muestra 2-A, es casi inexistente (0.4 %, 10 frames de 2400), por lo que 2-A corresponde a un estado muy poco frecuente.

**Limitación.** El ligando se ancla de forma frecuente a **Ser211** (28–35 % de los frames por puente, ≈ 2.7–2.86 Å), pero ninguna de las tres poses lo muestra a distancia de puente de hidrógeno (3.85, 4.60 y > 5 Å). Se interpreta que el ligando alterna entre estados con contactos a Tyr49 y estados anclados a las serinas, y que las tres figuras son instantáneas de esa dinámica.

Como complemento, el agrupamiento de los frames según la posición del ligando (ver más abajo) indica que existe una pose dominante que ocupa el 78.7 % de la trayectoria (frame representativo 813).

#### Sistemas 3 y 4 (C2 y C3): figura representativa

Para elegir una figura representativa de cada simulación se agruparon los frames según la posición del ligando (`cpptraj cluster`, clustering jerárquico en 4 grupos sobre el RMSD de los átomos pesados del ligando, tras superponer el receptor). La pose representativa es el frame más cercano al centroide del grupo más poblado.

**Tabla 4. Resultado del agrupamiento por posición del ligando.**

| Sistema | Grupo más poblado | Frame representativo | Segundo grupo | RMSD medio dentro del grupo principal |
|---|---|---|---|---|
| C1 | **78.7 %** (1888 de 2400 frames) | 813 | 10.8 % | 1.77 Å |
| C2 | **71.5 %** (1787 de 2500 frames) | 1662 (≈ 33 ns) | 22.8 % | 1.93 Å |
| C3 | **77.5 %** (1937 de 2500 frames) | 641 (≈ 13 ns) | 17.1 % | 1.32 Å |

En los tres sistemas el ligando permanece la mayor parte del tiempo (72–79 %) en una misma familia de poses. En C3 esa familia es la más compacta (1.3 Å) y en C2 la más dispersa (1.9 Å), con un segundo grupo importante (22.8 %).

##### Sistema 3 (C2)

**Tabla 5. Puentes de hidrógeno del ligando con la proteína en C2 (2500 frames).**

| Residuo | Átomo proteína | Átomo ligando | % de frames | Distancia media (Å) |
|---|---|---|---|---|
| GLN 114 | OE1 | O8 (H11) | **94.2** | 2.73 |
| LYS 213 | N (H) | O8 | 53.0 | 2.89 |
| ARG 43 | NE (HE) | O2 | 43.2 | 2.84 |
| ARG 235 | NH1 (HH12) | O6 | 31.7 | 2.81 |
| ARG 235 | NH2 (HH22) | O7 | 31.5 | 2.82 |
| SER 211 | OG (HG) | O7 | 23.2 | 2.73 |
| ARG 43 | NH2 (HH21) | O2 | 22.8 | 2.84 |
| SER 211 | OG (HG) | O6 | 21.4 | 2.73 |

El ligando de C2 queda anclado por **varios puentes simultáneos**, con el contacto con Gln114 presente casi todo el tiempo.

**Figura representativa.** [Figura 18: frame 1002 de C2 (≈ 20 ns), elegido dentro del grupo principal (71.5 % de la trayectoria) porque reúne los 4 puentes persistentes a la vez, con las distancias a Gln114 (OE1···O8) = 2.76 Å, Lys213 (N···O8) = 2.89 Å, Arg43 (NE···O2) = 2.81 Å y Arg235 (NH1···O6) = 2.77 Å.]

**Justificación.** El agrupamiento por posición del ligando identifica la familia de poses más frecuente (71.5 % de los frames), pero no considera los puentes de hidrógeno, y estos aparecen y desaparecen de un frame a otro (por ejemplo, Lys213 está presente en el 53 % de los frames y Arg235 en ≈ 32 %). Por eso, dentro del grupo principal se eligió el frame 1002, que reúne los 4 puentes más persistentes a la vez (Gln114, 94 %; Lys213, 53 %; Arg43, 43 %; Arg235, 32 %), con distancias dador–aceptor de 2.76 a 2.89 Å (≤ 3.0 Å), coherentes con los promedios de la simulación (≈ 2.7–2.9 Å).

##### Sistema 4 (C3)

**Tabla 6. Puentes de hidrógeno del ligando con la proteína en C3 (2500 frames).**

| Residuo | Átomo proteína | Átomo ligando | % de frames | Distancia media (Å) |
|---|---|---|---|---|
| ARG 215 | NE (HE) | N1 | 18.0 | 2.92 |
| VAL 181 | O | N1 (H20) | 6.7 | 2.87 |
| ARG 215 | NH2 (HH21) | N1 | 6.6 | 2.92 |
| ARG 43 | NH1 (HH12) | N2 | 2.6 | 2.90 |
| ARG 43 | NH2 (HH22) | N2 | 2.1 | 2.91 |

En C3 el ligando casi no forma puentes de hidrógeno persistentes con la proteína (el más frecuente es el de Arg215, 18 %), pero sí con el agua: N2 recibe puentes de agua en el 62 % de los frames y N1–H20 le dona al agua en el 41 %.

**Figura representativa.** [Figura 19: frame [N] de C3, elegido dentro del grupo principal (77.5 % de la trayectoria) como el que muestra los contactos con la proteína, con las distancias a Arg215 (NE···N1) = [x.xx Å] y Val181 (O···N1) = [x.xx Å], y una molécula de agua próxima a N2.]

**Justificación.** El ligando pertenece a un grupo de poses muy poblado (77.5 % de los frames) y a la familia más compacta de las tres (RMSD medio de 1.3 Å dentro del grupo), lo que indica que conserva una misma posición durante casi toda la simulación. Como los puentes de hidrógeno con la proteína son poco frecuentes (Arg215, 18 %; Val181, 7 %) y fluctúan entre frames, dentro del grupo principal se eligió el frame [N], que muestra [el contacto con Arg215 / ambos contactos] y la hidratación de N2, que es la interacción más consistente (62 % de los frames). La permanencia del ligando en el sitio se apoya en el agrupamiento de poses y no en interacciones polares persistentes. [Completar N y las distancias.]

#### Comparación entre los tres complejos

| | C1 | C2 | C3 |
|---|---|---|---|
| Pose dominante (grupo más poblado) | 78.7 % | 71.5 % | 77.5 % |
| Contacto más persistente con la proteína | Tyr49 (35 %) y Ser211 (28–35 %) | **Gln114 (94 %)** | Arg215 (18 %) |
| Nº de residuos con puentes de hidrógeno ≥ 20 % | 2 (Tyr49, Ser211) | 5 (Gln114, Lys213, Arg43, Arg235, Ser211) | 0 |
| Hidratación del ligando (puentes con agua por frame, mayores) | O6 1.45, O5 1.27 | O7 1.81, O3 1.68, O6 1.49 | N2 0.62, N1–H20 0.41 |
| Interacciones puente únicas soluto-solvente (sistema completo) | 1325 | 1335 | 1232 |

Por anclaje mediante puentes de hidrógeno el orden es **C2 > C1 > C3**, mientras que por estabilidad del receptor (RMSD) es C3 < C2 < C1. Los dos criterios no coinciden, de modo que el RMSD del receptor no debe usarse por sí solo para clasificar a los ligandos.

---

## 4. Discusión

### Pregunta 1: el receptor apo

**1a. ¿Cómo se obtuvo la estructura apo?** [Completar con lo hecho en el TP1. Borrador:] La estructura apo se obtuvo a partir de la estructura cristalográfica de SIRT1 en su forma cerrada, con el cofactor APR unido, eliminando el APR [y las moléculas de agua y ligandos cristalográficos] y conservando el ion zinc estructural. Luego se parametrizó (con ZAFF para el zinc), se neutralizó y se solvató con el mismo procedimiento que los complejos.

**1b. ¿La estructura global se mantuvo durante la MD o hubo cambios importantes? ¿Y cambios menores?**

La estructura global se mantuvo, con cambios menores localizados:

- **Cambio global:** no se observa un desarmado de la proteína. Sin considerar los extremos móviles, el RMSD es bajo y casi plano (≈ 2.3 Å, con un leve ascenso a ≈ 2.8 Å hacia el final) y el núcleo tiene un RMSF de ≈ 1 Å.
- **Cambios menores:** el RMSD del receptor completo es alto (≈ 4–4.7 Å) y lleva una deriva lenta, pero se debe en gran medida a los extremos (RMSF de ≈ 3.7 Å en el N-terminal y ≈ 7.8 Å en el C-terminal). Además hay movilidad localizada en los loops de las regiones ≈ 40–60 (≈ 2.9 Å) y ≈ 170 (≈ 2.7 Å), y en menor medida en ≈ 88, ≈ 188 y ≈ 240.

*i. Análisis que permitieron llegar a estas conclusiones:* RMSD del backbone y total, RMSD del receptor completo frente al receptor sin extremos móviles, RMSF por residuo y la superposición de frames (figura 1-C).

*ii. Estado apo y su evolución, según Davenport et al. (2014).* [Completar con la figura 5: qué regiones o dominios diferencian la forma abierta de la cerrada.]

Las sirtuinas se organizan en un dominio grande tipo Rossmann y un dominio pequeño de unión a zinc, y el sitio de unión del cofactor y del sustrato queda en la hendidura entre ambos [verificar con Davenport et al. 2014]. En general, la unión del cofactor se asocia a una conformación más cerrada y su ausencia a una más abierta o flexible.

La simulación parte de la forma cerrada y sin cofactor, por lo que cabe esperar cierta relajación del receptor. Los datos son compatibles con eso: el RMSD global es mayor que en los complejos y deriva lentamente, y los picos de RMSF se concentran en loops [indicar si las regiones ≈ 40–60 y ≈ 170 corresponden a las regiones que según la figura 5 cambian entre abierto y cerrado]. Al mismo tiempo, el núcleo conserva el plegamiento, por lo que, en la escala de 70 ns, se observa una **flexibilidad aumentada** y no una transición completa hacia la forma abierta. Esto debería confirmarse midiendo la distancia entre los dominios que define Davenport a lo largo del tiempo.

### Pregunta 2: comparación docking vs. dinámica para cada ligando

Para cada ligando se responde a las tres sub-preguntas. Las interacciones provienen del análisis de puentes de hidrógeno (`cpptraj hbond`, ≤ 3.0 Å y ≥ 135°). Como referencia de las interacciones adquiridas en el docking se usaron los puentes de hidrógeno del **primer frame** de cada simulación, que corresponde a la pose de partida (ya minimizada y equilibrada), y se compararon con su persistencia durante los 50 ns.

#### C1

**2a. Interacciones del docking.**

Al inicio (frame 1) el ligando forma puentes de hidrógeno con **Arg43** (O5···HH11, O6···N–H y O2···HH22, a 2.7–3.0 Å) y con **Ser211** (O5···HG, 2.82 Å). Durante la simulación:

- **Se mantiene y se refuerza Ser211:** O5 y O6 forman varios puentes con Ser211 (28–35 % de los frames por puente).
- **Se pierden en gran parte los contactos con Arg43:** no figuran entre los 15 puentes más persistentes (cada uno aparece en menos de ≈ 14 % de los frames).
- **Se ganan Tyr49 (35 %), Ser210 (≈ 14–15 %) y Ala31 (≈ 15 %)**, que no estaban en la pose inicial.
- El contacto con **His132** que se ve en la pose 2-A no estaba al inicio y es esporádico (0.4 % de los frames).

[Figura 20: poses 2-A, 2-B y 2-C con las distancias.]

**2b. Interacciones mediadas por solvente.** Sí, y se mantienen en el tiempo (no son esporádicas). Por frame, O6 forma en promedio 1.45 puentes de hidrógeno con agua, O5 1.27, O2 0.89 y N1 0.68, y el grupo O4–H1 le dona al agua en el 57 % de los frames. O5 y O6 tienen a la vez puentes con Ser211 y con agua. El N1 permanece hidratado y no unido a His132. Se detectaron 1325 interacciones puente únicas soluto-solvente en el sistema. [Figura 21: molécula de agua puenteando al ligando y un residuo. Para el gráfico cuantitativo se puede usar un gráfico de barras con los % de `hb_avg.dat`.]

**2c. Cambios en el receptor.**
- *Globales:* RMSD del backbone ≈ 2.3–2.8 Å, con una excursión transitoria a ≈ 4 Å cerca del frame 1600 (≈ 32 ns), de la que se recupera solo en parte (≈ 2.8 Å al final). Sin extremos, ≈ 2.2 Å con un máximo de ≈ 3.8 Å en el mismo momento.
- *Locales:* movilidad en los loops de ≈ 35–60 (≈ 2.8 Å, incluye Tyr49) y ≈ 170 (≈ 2.5 Å). Ser210 y Ser211 quedan junto a un mínimo de RMSF, consistente con su rol de anclaje persistente.

[Figuras 9–11.]

#### C2

**2a. Interacciones del docking.**

Al inicio (frame 1) el ligando forma puentes de hidrógeno con **Tyr49** (O7···HH, 2.65 Å), **Gln114** (O8–H11···OE1, 2.84 Å) y **Arg43** (O3···HH22 y HH12, 2.87–2.90 Å). Durante la simulación:

- **Se mantiene Gln114**, y se vuelve la interacción dominante (94 % de los frames).
- **Se mantiene Arg43**, pero a través de otro oxígeno del ligando (O2, en el 43 % y 23 % de los frames por dos grupos distintos de la arginina; al inicio era O3).
- **Se pierde en gran parte Tyr49:** no figura entre los 15 puentes más persistentes (menos de ≈ 21 % de los frames).
- **Se ganan Lys213 (53 %), Arg235 (≈ 32 % por dos puentes) y Ser211 (≈ 21–23 %)**, que no estaban en la pose inicial.

[Figura 22: frame representativo de C2 con las distancias.]

**2b. Interacciones mediadas por solvente.** Sí, y son persistentes. El ligando es el más hidratado de los tres: O7 forma en promedio 1.81 puentes con agua por frame, O3 1.68, O6 1.49, y O2, O5 y O4 entre 0.77 y 0.81. Se detectaron 1335 interacciones puente únicas soluto-solvente. O6 y O7 combinan puentes con Arg235 y Ser211 con puentes de agua. [Figura 23: agua puenteando al ligando en el frame representativo; gráfico de barras de los % de `hb_avg.dat`.]

**2c. Cambios en el receptor.**
- *Globales:* RMSD del backbone en meseta (≈ 2.5–2.7 Å), con una perturbación puntual cerca del frame 2000 (≈ 40 ns; ≈ 3.4 Å) de la que se recupera. Sin extremos ≈ 2.0–2.3 Å.
- *Locales:* el pico de RMSF de la región ≈ 40–60 es el más alto de los complejos (≈ 3.2 Å), y esa región incluye Arg43, que interactúa con el ligando. [Hipótesis: esta movilidad podría estar relacionada con la interacción de ese loop con el ligando; verificar.]

[Figuras 12–14.]

#### C3

**2a. Interacciones del docking.**

Al inicio (frame 1) el único puente de hidrógeno del ligando con la proteína es el de **Arg43** (N2···HH22, 2.79 Å). Durante la simulación:

- **Se pierde Arg43:** el contacto aparece solo en el 2–3 % de los frames.
- **Se ganan Arg215 (≈ 18 % y 6.6 % por dos grupos de la arginina) y Val181 (≈ 6.7 %)**, ambos con N1.
- En conjunto los puentes de hidrógeno con la proteína son pocos y poco persistentes. Esto no implica que el ligando haya salido del sitio: el agrupamiento muestra que se mantiene en una pose dominante (77.5 % de los frames) y podría estar unido por contactos hidrofóbicos o electrostáticos que no miden los puentes de hidrógeno.

[Figura 24: frame representativo de C3 con las distancias.]

**2b. Interacciones mediadas por solvente.** Sí, y son las más importantes para este ligando. N2 recibe puentes de agua en el 62 % de los frames y N1–H20 le dona al agua en el 41 %; además N1 recibe agua en el 25 %. Se detectaron 1232 interacciones puente únicas soluto-solvente. El ligando está más expuesto al solvente que C1 y C2. [Figura 25: agua cerca de N2 y N1.]

**2c. Cambios en el receptor.**
- *Globales:* el receptor es el más estable de los tres (RMSD del backbone ≈ 1.8–2.2 Å), con dos excursiones transitorias (≈ 500 y ≈ 2050 frames) que se recuperan. Sin extremos queda casi plano en ≈ 1.5 Å.
- *Locales:* los picos de RMSF de las regiones ≈ 40–60 (≈ 2.3 Å) y ≈ 170 (≈ 2.0 Å) son los más bajos de los cuatro sistemas.

[Figuras 15–17.]

#### Conclusión comparativa

- **C2** es el ligando mejor anclado por puentes de hidrógeno (cinco residuos con ≥ 20 % y un contacto con Gln114 casi permanente) y también el más hidratado.
- **C1** tiene un anclaje intermedio, centrado en Ser211 y Tyr49, y un receptor menos estable (excursión del RMSD hacia el frame 1600).
- **C3** tiene el receptor más estable, pero casi sin puentes de hidrógeno persistentes con la proteína y con un ligando principalmente hidratado.
- En los tres casos el ligando permanece la mayor parte del tiempo (72–79 %) en una pose dominante, aunque las interacciones puntuales del docking cambian: se pierden unas (Arg43 en C1 y C3, Tyr49 en C2), se mantienen otras (Ser211, Gln114) y se ganan otras.
- Estas conclusiones salen de una sola trayectoria por sistema y consideran solo puentes de hidrógeno, por lo que son indicios y no una clasificación de afinidad.

### Pregunta 3: relevancia de la MD luego del docking

El docking aporta una pose estática, con un receptor casi rígido y una descripción simplificada del solvente, y permite una evaluación aproximada de la afinidad. La MD agrega temperatura, flexibilidad del receptor y solvente explícito, y permite verificar si la pose propuesta **sobrevive en el tiempo**.

En este sistema, la MD aportó información que el docking no podía dar:

- Mostró que las interacciones de la pose inicial no siempre se sostienen: los contactos con Arg43 prácticamente desaparecen en C1 y C3, y el de Tyr49 en C2, mientras que aparecen otros nuevos (Tyr49 y las serinas en C1, Lys213 y Arg235 en C2, Arg215 en C3).
- Mostró que los tres ligandos están muy hidratados, con puentes de agua persistentes, algo que un docking con solvente implícito no captura, y que en C3 la interacción con el solvente domina sobre la interacción con la proteína.
- Permitió comparar los tres complejos y el apo, y mostró que la estabilidad del receptor (C3) y el anclaje del ligando (C2) no coinciden, por lo que un solo criterio no alcanza para clasificar ligandos.

Como limitación, una trayectoria de 50 ns por sistema no alcanza para estimar afinidades ni para afirmar convergencia del muestreo, de modo que la MD complementa al docking y no lo reemplaza. Para clasificar ligandos con rigor harían falta réplicas, simulaciones más largas y cálculos de energía libre (por ejemplo, MM-PBSA/GBSA).

---

## Referencias

- Davenport AM, Huber FM, Hoelz A. Structural and functional analysis of human SIRT1. *J Mol Biol.* 2014;426(3):526-541.
- Roe DR, Cheatham TE III. PTRAJ and CPPTRAJ: Software for Processing and Analysis of Molecular Dynamics Trajectory Data. *J Chem Theory Comput.* 2013;9(7):3084-3095.
