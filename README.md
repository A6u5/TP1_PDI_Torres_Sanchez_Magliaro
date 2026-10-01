# TRABAJO PRÁCTICO N° 1 - Año 2026 - 2° Semestre
# Procesamiendo de imagenes

Consigna completa en [TUIA_PDI_TP1_2026_C2.pdf](TUIA_PDI_TP1_2026_C2.pdf).



# Alumnos

Agustin Torres
Facundo Ángel Magliaro
Aldana Desiré Sánchez

## Instalación

Requiere Python 3 y las dependencias de [requirements.txt](requirements.txt):

```bash
pip install -r requirements.txt
```

## Ejecución

```bash
python main.py
```

`main.py` corre ambos problemas de forma secuencial (primero el problema 1, después el
problema 2) y guarda todas las salidas en disco. No abre ninguna ventana emergente.

## Estructura

```
TP1_PDI_Torres_Sanchez_Magliaro/
├── datos/                       # imágenes de entrada (provistas por la cátedra)
│   ├── Imagen_con_detalles_escondidos.tif
│   └── planillas/
│       ├── grade_sheet_1.png … grade_sheet_4.png
│       └── grade_sheet_empty.png
├── imagenes_problema1/          # salidas del problema 1 (se regeneran en cada corrida)
├── imagenes_problema2/          # salidas del problema 2 (se regeneran en cada corrida)
├── csv/                         # resultados de validación del problema 2 (se regeneran en cada corrida)
├── problema1.py
├── problema2.py
└── main.py                      # orquesta la ejecución de ambos problemas
```

Las carpetas `imagenes_problema1/`, `imagenes_problema2/` y `csv/` se crean solas al
correr `main.py` si no existen. Los archivos que generan tienen siempre el mismo
nombre, así que cada corrida sobrescribe los resultados de la anterior.

## Problema 1 — Ecualización local de histograma

[problema1.py](problema1.py) implementa `ecualizacion_local_hist(img, M, N=None)`, que
recorre la imagen con una ventana deslizante de `M x N` píxeles y, para cada píxel
central, calcula el histograma de su ventana y usa la CDF de ese histograma para
remapear su nivel de gris. Se usa para revelar detalles ocultos por bajo contraste en
`datos/Imagen_con_detalles_escondidos.tif` que una ecualización global no distingue.

`resolver_problema1(carpeta_salida)` genera y guarda:

- `resultado_ventana_<M>.png`: el resultado de la ecualización local para cada tamaño
  de ventana evaluado (3, 7, 15, 31, 61 y 121 por defecto).
- `b_original_vs_ventana_7.png`: comparación lado a lado entre la imagen original y el
  resultado con la ventana elegida (7x7).
- `c_comparacion_ventanas.png`: grilla con el resultado de los seis tamaños de ventana,
  para analizar cómo influye el tamaño de ventana sobre el resultado.

## Problema 2 — Validación de planillas de calificaciones

[problema2.py](problema2.py) procesa planillas de calificaciones escaneadas
(`datos/planillas/grade_sheet_<id>.png`), detecta su grilla a partir de las líneas
horizontales y verticales, y valida el contenido de cada celda contando sus componentes
conectadas (caracteres) y palabras.

- `validar_planilla(img)`: devuelve, por cada fila de la planilla, el resultado
  (`"OK"` / `"MAL"`) de los campos Legajo, Nombre y Apellido, Parcial 1, Parcial 2,
  Parcial 3 y Condición Final, junto con las coordenadas de cada celda.
- `mostrar_resultados(registros)`: imprime por consola el detalle de cada registro.
- `exportar_csv(registros, ruta)`: guarda los resultados en un CSV (un registro por
  fila, con ID y el estado de cada campo).
- `generar_imagen_no_aprobados(img, registros)`: a partir de los registros cargados
  correctamente, arma una única imagen con el nombre de los alumnos no aprobados,
  agrupados en dos bloques — **Recuperan (R)** en naranja y **Libres (L)** en rojo —,
  distinguiendo la letra de la Condición Final por su cantidad de huecos (número de
  componentes conectadas en su negativo) y la forma de su trazo izquierdo.

`main.py` corre este proceso de forma cíclica sobre las cuatro planillas
(`grade_sheet_1.png` a `grade_sheet_4.png`), informando por consola la cantidad de
registros válidos de cada una y generando su CSV y su imagen de no aprobados
correspondientes.
