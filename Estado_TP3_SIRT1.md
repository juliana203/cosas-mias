# Estado del TP3: Dinámica Molecular de SIRT1

Resumen para coordinar el informe: qué está hecho, qué hay que decidir juntos y qué falta. La idea es **hacer solo lo que pide la guía**, sin análisis extra.

Numeración (igual en VMD, cpptraj y en los paneles de la cátedra): residuos 1–279 = proteína, 280 = Zn, 281 = ligando.

## 1. Mapa general

```mermaid
flowchart LR
  A["2.A Preparación<br/>TIP3P, caja octaédrica 9 Å, 5 Na+"]:::ok --> B["2.B Protocolo<br/>Min, Term 1 ns, Eq 2 ns, Prod 50 ns"]:::ok
  B --> C["2.C Análisis general<br/>solo C1 y apo"]:::warn
  C --> D["2.D Modos de unión<br/>Sistemas 1 a 4"]:::warn
  D --> E1["Discusión 1<br/>apo"]:::todo
  D --> E2["Discusión 2<br/>docking vs MD"]:::warn
  E1 --> E3["Discusión 3<br/>relevancia de la MD"]:::warn
  E2 --> E3
  E3 --> INF["Informe final"]:::todo
  classDef ok fill:#d5eedf,stroke:#2f7d57,color:#12301f
  classDef warn fill:#f6e5c2,stroke:#a86a10,color:#3a2606
  classDef todo fill:#f3d5d5,stroke:#8a3b3b,color:#3a1313
```

Verde = hecho · Amarillo = parcial · Rojo = pendiente

## 2. Qué pide la guía (y qué no)

```mermaid
flowchart TD
  G["Guía TP3"] --> S1["2.C: RMSD y RMSF de<br/>las 2 trayectorias<br/>C1 + apo"]
  G --> S2["2.D: elegir panel<br/>Sistemas 1 y 2"]
  G --> S3["2.D: figura propia<br/>Sistemas 3 y 4"]
  G --> S4["Discusión: 3 preguntas<br/>+ figura de agua"]
  X["NO hace falta"]:::no --> X1["2.C para C2 y C3"]:::no
  X --> X2["Clustering"]:::no
  X --> X3["Conteo de aguas por frame<br/>e interacciones soluto-solvente"]:::no
  X --> X4["Tabla de RMSF del bolsillo"]:::no
  classDef no fill:#eeeeee,stroke:#999999,color:#555555
```

## 3. Análisis general (2.C): archivos de la cátedra

No hay que generar gráficos nuevos: la cátedra ya dejó todo calculado en cada carpeta.

```mermaid
flowchart LR
  C1["C1/"] --> T1["rmsTotal.dat<br/>receptor + ligando"]
  C1 --> T2["rmsBackbone.dat<br/>receptor solo"]
  C1 --> T3["atomic_resCA.apf<br/>RMSF por residuo"]
  AP["apo/"] --> A1["rmsTotal.dat / rmsBackbone.dat"]
  AP --> A2["rms*_sinCola-6aa.dat<br/>sin extremo C-terminal"]
  AP --> A3["atomic_resCA.apf"]
  T1 --> GR["4 gráficos en xmgrace"]
  T2 --> GR
  T3 --> GR
  A1 --> GR
  A2 --> GR
  A3 --> GR
```

| Gráfico | Archivos |
|---|---|
| RMSD receptor + ligando vs receptor solo (C1) | `C1/rmsTotal.dat` + `C1/rmsBackbone.dat` |
| RMSD C1 vs apo | `C1/rmsBackbone.dat` + `apo/rmsBackbone.dat` |
| RMSD apo con y sin extremos | `apo/rmsBackbone.dat` + `apo/rmsBackbone_sinCola-6aa.dat` |
| RMSF C1 vs apo | `C1/atomic_resCA.apf` + `apo/atomic_resCA.apf` |

- Eje X en cuadros: **1 cuadro ≈ 20,8 ps** en C1 (2400 cuadros = 50 ns). Se aclara en el título del eje.
- La verificación de extremos móviles se hace con el RMSF (valores altos en los extremos).
- **Falta:** redactar la interpretación (convergencia, RMSD intra e inter sistemas, RMSF).

## 4. Asignación de sistemas y elecciones de 2.D

```mermaid
flowchart LR
  S1["Sistema 1"] --> APO["apo"] --> P1["Panel 1-C<br/>plegamiento global conservado"]:::ok
  S2["Sistema 2"] --> CC1["C1"] --> P2["2-B o 2-C ?<br/>a decidir"]:::warn
  S3["Sistema 3"] --> CC2["C2"] --> P3["Figura: cuadro 97<br/>~20 ns"]:::ok
  S4["Sistema 4"] --> CC3["C3"] --> P4["Figura: cuadro 64<br/>~13 ns"]:::ok
  classDef ok fill:#d5eedf,stroke:#2f7d57,color:#12301f
  classDef warn fill:#f6e5c2,stroke:#a86a10,color:#3a2606
```

Los cuadros son de VMD cargando con `step 10` (240 cuadros, ~0,21 ns cada uno). El ligando de los paneles 2 se identificó como C1 comparando estructuras (piridina, OH, piperidina, carboxilato).

| Sistema | Elección | Datos clave |
|---|---|---|
| 1 (apo) | **1-C** | El bolsillo se mantiene compacto; la superposición muestra el plegamiento conservado. Se respalda con el RMSD sin cola. |
| 2 (C1) | **2-B o 2-C** | Ver sección 5. |
| 3 (C2) | Cuadro 97 | Arg235 con el carboxilato (2,56 y 2,81 Å, puente salino bidentado); Lys213 NH → O8 (1,94 Å); OH del ligando → Gln114 (1,68 Å); Arg43 → O2 (2,86 Å). Lys213 y Arg43 se mantienen casi todo el tiempo; Arg235 fluctúa (por momentos hasta ~11 Å). |
| 4 (C3) | Cuadro 64 | Solo Arg215 interacciona con N1 (3,02 Å; 3,78 Å). Arg43 lejos (10–11 Å), Val181 a 4,58 Å. Sistema muy móvil, las argininas van y vienen. |

## 5. Decisiones para acordar juntos

```mermaid
flowchart TD
  Q1{"Sistema 2:<br/>2-B o 2-C?"} --> V1["Mirar cuadros 180, 200, 220 de C1<br/>solo distancias a Ser210 y Ser211"]
  V1 -->|"serines cerca de 2 Å"| R1["2-C<br/>el ligando se asienta anclado<br/>por el carboxilato"]:::ok
  V1 -->|"van y vienen"| R2["2-B<br/>Tyr49 es lo más frecuente"]:::ok
  Q2{"¿Se corrieron de verdad<br/>hbond y cluster?<br/>hb_avg.dat, summary.dat"} -->|"sí"| R3["Usar los % solo como respaldo"]:::ok
  Q2 -->|"no"| R4["No incluir esos números"]:::warn
  Q3{"Máscara sin extremos de C1"} --> R5["Usar una sola y nombrarla igual<br/>en texto y leyendas"]:::warn
  classDef ok fill:#d5eedf,stroke:#2f7d57,color:#12301f
  classDef warn fill:#f6e5c2,stroke:#a86a10,color:#3a2606
```

Datos de C1 medidos en VMD (cuadros con `step 10`):

| Cuadro | Tyr49 | His132 | Ser211 | Ser210 |
|---|---|---|---|---|
| 0 | 4,00 | 3,55 | 1,86 | 6,20 |
| 120 | 3,50 | 6,12 | 2,58 | 5,88 |
| 163 (~34 ns) | 2,81 | 5,75 | 8,37 | 10,05 |
| 239 (final) | 4,38 | 7,73 | 1,56 | 1,97 |

El final se parece a 2-C, el cuadro 163 a 2-B. Los porcentajes de puentes de hidrógeno (tanto del borrador como de la trazabilidad) muestran Tyr49 como lo más frecuente y Ser210 poco frecuente (14–20 %), lo que favorece 2-B.

## 6. Correcciones al borrador del informe

| Dice el borrador | Corrección |
|---|---|
| C1: 2400 frames ≈ 48 ns | Son **50 ns** (1 cuadro ≈ 20,8 ps) |
| C2 y C3: 2500 frames | Verificar: la trazabilidad dice 2400 |
| Centrado con `autoimage` | El script de la cátedra usa `center :1-281@CA` e `image center familiar com` |
| Sin extremos: residuos 6–270 | Poner la máscara realmente usada (apo de la cátedra: `:1-274`) |
| Val181 "lo más consistente" en C3 | Según sus propios datos es 6,7 %: interacción rara; mejor no mencionarla o decir que no interacciona |
| Sistema 2 = 2-B | Pendiente de acordar (sección 5) |
| C3 figura en cuadro 641 | Coincide: es el cuadro 64 con `step 10` |
| Docking = primer cuadro de la MD | Aceptable, pero mejor comparar con las interacciones del informe del TP2 |
| 2.C para los 4 sistemas | La guía pide solo C1 y apo |

## 7. Pendientes

```mermaid
flowchart LR
  P1["Decidir 2-B o 2-C"]:::todo --> P6
  P2["Redactar interpretación de 2.C"]:::todo --> P6
  P3["Disc. 1a: cómo se obtuvo la apo<br/>informe del TP1"]:::todo --> P6
  P4["Disc. 1b.ii: comparar con<br/>Fig. 5 de Davenport 2014"]:::todo --> P6
  P5["Disc. 2a: interacciones ganadas y perdidas<br/>vs docking del TP2, por ligando"]:::todo --> P6
  W["Figura de agua C3<br/>N2 a 2,98 Å de un agua, cuadro 64"]:::ok --> P6
  P6["Armar informe recortado"]:::todo
  classDef ok fill:#d5eedf,stroke:#2f7d57,color:#12301f
  classDef todo fill:#f3d5d5,stroke:#8a3b3b,color:#3a1313
```

Nota sobre la figura de agua de C3: el agua está unida al N2 pero no conecta con ningún residuo, así que es **hidratación del ligando**, no un puente agua–proteína. El agua ocupa el lugar que dejó Arg43 al alejarse.
