import csv
import cv2
import numpy as np


# Nombres de las columnas de datos, en el mismo orden en que las recorre el bucle (j = 1..6).
# La columna j = 0 es "Nro." y no se valida.
COLUMNAS = ["Legajo",
            "Nombre y Apellido",
            "Parcial 1",
            "Parcial 2",
            "Parcial 3",
            "Condición Final"]

# Colores (en BGR, que es como trabaja OpenCV) del indicador de cada condición.
COLOR_CONDICION = {"R": (0, 165, 255),   # naranja -> debe recuperar
                   "L": (0, 0, 255)}     # rojo    -> queda libre

TITULO_BLOQUE = {"R": "RECUPERAN (R)",
                 "L": "LIBRES (L)"}

FUENTE = cv2.FONT_HERSHEY_SIMPLEX
ANCHO_FRANJA = 44   # ancho en pixeles de la franja de color que lleva cada nombre




# ---------------------------------------------------------------------------------------
# FUNCIONES AUXILIARES COMUNES
# ---------------------------------------------------------------------------------------

## Funcion para agrupar lineas
def agrupar_consecutivos(indices):
    grupos = []

    if len(indices) == 0:
        return grupos

    inicio = indices[0]
    anterior = indices[0]

    for indice in indices[1:]:
        if indice != anterior + 1:
            grupos.append((inicio, anterior))
            inicio = indice

        anterior = indice

    grupos.append((inicio, anterior))

    return grupos


## Funcion para obtener los centros de esas lineas agrupadas.
def centros_de_grupos(grupos):
    return [(inicio + fin) // 2 for inicio, fin in grupos]


# Para determinar los caracteres validos dentro de una celda.
def componentes_validas(celda, area_min):
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
    celda.astype(np.uint8),
    connectivity=8)
    componentes = []

    for i in range(1, num_labels):  # empezamos en 1 porque 0 es el fondo
        x = stats[i, cv2.CC_STAT_LEFT]
        y = stats[i, cv2.CC_STAT_TOP]
        w = stats[i, cv2.CC_STAT_WIDTH]
        h = stats[i, cv2.CC_STAT_HEIGHT]
        area = stats[i, cv2.CC_STAT_AREA]

        if area >= area_min:
            componentes.append({
                "x": x,
                "y": y,
                "w": w,
                "h": h,
                "area": area})

    return componentes


# Para determinar la cantidad de palabras que hay
def cantidad_palabras(componentes, espacio_min=10):
    componentes = sorted(componentes, key=lambda c: c["x"])

    if len(componentes) == 0:
        return 0

    palabras = 1

    for i in range(len(componentes) - 1):
        fin_actual = componentes[i]["x"] + componentes[i]["w"]
        inicio_siguiente = componentes[i + 1]["x"]
        distancia = inicio_siguiente - fin_actual

        if distancia >= espacio_min:
            palabras += 1

    return palabras




# ---------------------------------------------------------------------------------------
# a) VALIDACION DE LA PLANILLA
# ---------------------------------------------------------------------------------------

def validar_planilla(img):
    """Valida cada celda de la planilla.

    Devuelve una lista de registros (uno por fila de datos), donde cada registro es:
        {"nro":      numero de fila de la planilla,
         "campos":   {nombre de columna: "OK" / "MAL"},
         "celdas":   {nombre de columna: (y0, y1, x0, x1)},
         "correcto": True si todos los campos dieron "OK"}

    Las coordenadas de "celdas" son las que despues usa el punto b) para recortar
    el nombre del alumno y leer su condicion final.
    """

    # Con Img_th umbralizamos los valores, los llevamos a "true y false" segun corresponda con nuestro umbral
    # True para menor (<) que 128 y False para mayor (>) a 128
    img_th = img < 128

    # Luego para detectar una linea en una columna tendremos que tiene varios Ture seguidos
    # asi que sumamos los pixeles de cada columna, para detectar las lines verticales.
    img_cols = np.sum(img_th, axis=0)  # Columnas
    img_rows = np.sum(img_th, axis=1)  # Filas

    # Con esto nos vamos dando una idea de nuestro umbral para determinar lines horizontales y verticales
    th_col = 0.8 * max(img_cols)
    th_row = 0.8 * max(img_rows)
    img_cols_th = img_cols > th_col
    img_rows_th = img_rows > th_row

    # Ahora tambien si tenemos varios True consecutivos quiere decir que tenemos una linea gruesa.
    cols = np.where(img_cols_th)[0]
    rows = np.where(img_rows_th)[0]

    grupos_cols = agrupar_consecutivos(cols)
    grupos_rows = agrupar_consecutivos(rows)

    # obtencion final de las lineas.
    x = centros_de_grupos(grupos_cols) # lineas verticales
    y = centros_de_grupos(grupos_rows) # lineas horizontales


    # Luego dos lineas horizontales consecutivas (Y1 , Y2) y verticales (X1 , X2) determinan una celda.
    # Recorrer celdas.
    fila_inicio_datos = 1
    registros = []

    for i in range(fila_inicio_datos, len(y) - 1):
        campos = {}
        celdas = {}

        for j in range(1, len(x) - 1):
            if j - 1 >= len(COLUMNAS):   # por si apareciera una columna de mas
                break

            columna = COLUMNAS[j - 1]

            # Guardamos los limites de la celda para poder recortarla despues.
            limites = (y[i] + 1, y[i + 1], x[j] + 1, x[j + 1])
            celda = img_th[limites[0]:limites[1], limites[2]:limites[3]]

            componentes = componentes_validas(celda, area_min=4)
            resultado = "MAL"

            # Legajo
            if j == 1:
                cantidad_caracteres = len(componentes)
                palabras = cantidad_palabras(componentes)

                if cantidad_caracteres == 8 and palabras == 1:
                    resultado = "OK"

            # Nombre y Apellido
            elif j == 2:
                cantidad_caracteres = len(componentes)
                palabras = cantidad_palabras(componentes)

                if cantidad_caracteres <= 12 and palabras >= 2:
                    resultado = "OK"

            # Parciales 1, 2 y 3
            elif j in [3, 4, 5]:
                cantidad_caracteres = len(componentes)
                palabras = cantidad_palabras(componentes)

                if cantidad_caracteres in [1, 2] and palabras == 1:
                    resultado = "OK"

            # Condición final
            elif j == 6:
                cantidad_caracteres = len(componentes)

                if cantidad_caracteres == 1:
                    resultado = "OK"

            campos[columna] = resultado
            celdas[columna] = limites

        registros.append({
            "nro": i,
            "campos": campos,
            "celdas": celdas,
            "correcto": all(valor == "OK" for valor in campos.values())})

    return registros


def mostrar_resultados(registros):
    """Imprime por terminal el estado de cada campo de cada registro."""

    for registro in registros:
        print(f"Registro {registro['nro']}:")

        for columna, resultado in registro["campos"].items():
            print(f"{columna}: {resultado}")

        print()


def exportar_csv(registros, ruta="resultados.csv"):
    """Guarda los resultados de la validacion en un archivo CSV.

    Una fila por registro de la planilla: el ID (que sigue el orden de la planilla)
    en la primera columna y despues el resultado "OK" / "MAL" de cada campo.
    """

    # newline="" es lo que recomienda el modulo csv para no duplicar saltos de linea en Windows.
    # utf-8-sig agrega el BOM para que Excel muestre bien los acentos de "Condición Final".
    with open(ruta, "w", newline="", encoding="utf-8-sig") as archivo:
        escritor = csv.writer(archivo)

        escritor.writerow(["ID"] + COLUMNAS)

        for registro in registros:
            fila = [registro["campos"][columna] for columna in COLUMNAS]
            escritor.writerow([registro["nro"]] + fila)

    return ruta




# ---------------------------------------------------------------------------------------
# b) IMAGEN DE SALIDA CON LOS ALUMNOS NO APROBADOS
# ---------------------------------------------------------------------------------------

# Cuenta los huecos de una letra ya recortada a su bounding-box.
# Analizamos el FONDO (el negativo de la letra): queda el fondo exterior como una
# componente mas una componente por cada hueco encerrado. Usamos connectivity=4 para
# que un hueco no se "escape" hacia afuera por una diagonal.
def contar_huecos(letra):
    fondo = (~letra).astype(np.uint8)
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(fondo, connectivity=4)

    # num_labels incluye la etiqueta 0 (la tinta) y el fondo exterior, por eso restamos 2.
    return num_labels - 2


# Indica si el trazo vertical izquierdo de la letra esta completo de arriba a abajo.
# Es lo que distingue a la "R" (y a la "L") de la "A", cuyo trazo izquierdo es diagonal.
def columna_izquierda_llena(letra, tolerancia=0.9):
    return letra[:, 0].mean() >= tolerancia


def clasificar_condicion(celda):
    """Devuelve 'L', 'R' o None (None = aprobado o celda no reconocible)."""

    componentes = componentes_validas(celda, area_min=4)

    if len(componentes) != 1:
        return None

    # Recortamos la letra a su bounding-box.
    c = componentes[0]
    letra = celda[c["y"]:c["y"] + c["h"], c["x"]:c["x"] + c["w"]]

    if letra.size == 0:
        return None

    # La "L" no tiene huecos.
    if contar_huecos(letra) == 0:
        return "L"

    # Tiene hueco: es "R" si ademas su trazo izquierdo es vertical. Si no, es la "A".
    if columna_izquierda_llena(letra):
        return "R"

    return None


# Arma la fila de salida de un alumno: franja de color con la letra + crop del nombre + borde.
def armar_fila(img, celda_nombre, condicion):
    y0, y1, x0, x1 = celda_nombre

    # Recortamos la celda completa y la pasamos a color para poder dibujar encima.
    crop = cv2.cvtColor(img[y0:y1, x0:x1], cv2.COLOR_GRAY2BGR)
    alto, ancho = crop.shape[:2]
    color = COLOR_CONDICION[condicion]

    # Franja de color a la izquierda, con la letra de la condicion escrita encima.
    franja = np.full((alto, ANCHO_FRANJA, 3), color, dtype=np.uint8)
    (ancho_texto, alto_texto), _ = cv2.getTextSize(condicion, FUENTE, 0.9, 2)
    cv2.putText(franja, condicion,
                ((ANCHO_FRANJA - ancho_texto) // 2, (alto + alto_texto) // 2),
                FUENTE, 0.9, (255, 255, 255), 2, cv2.LINE_AA)

    fila = np.hstack([franja, crop])

    # Borde del color de la condicion alrededor de toda la fila.
    cv2.rectangle(fila, (0, 0), (fila.shape[1] - 1, alto - 1), color, thickness=2)

    return fila


# Arma la banda de titulo que encabeza cada bloque.
def armar_encabezado(ancho, condicion, alto=34):
    color = COLOR_CONDICION[condicion]
    banda = np.full((alto, ancho, 3), color, dtype=np.uint8)

    texto = TITULO_BLOQUE[condicion]
    (ancho_texto, alto_texto), _ = cv2.getTextSize(texto, FUENTE, 0.6, 2)
    cv2.putText(banda, texto,
                ((ancho - ancho_texto) // 2, (alto + alto_texto) // 2),
                FUENTE, 0.6, (255, 255, 255), 2, cv2.LINE_AA)

    return banda


def generar_imagen_no_aprobados(img, registros):
    """Genera una unica imagen con los nombres de los alumnos no aprobados.

    Solo se consideran los registros cargados correctamente (todos los campos "OK").
    La salida queda agrupada en dos bloques: primero los que recuperan, despues los libres.
    Devuelve None si no hay ningun alumno para mostrar.
    """

    img_th = img < 128
    no_aprobados = {"R": [], "L": []}

    for registro in registros:
        if not registro["correcto"]:
            continue

        y0, y1, x0, x1 = registro["celdas"]["Condición Final"]
        condicion = clasificar_condicion(img_th[y0:y1, x0:x1])

        if condicion in no_aprobados:
            no_aprobados[condicion].append(registro["celdas"]["Nombre y Apellido"])

    bloques = []

    for condicion in ["R", "L"]:
        if len(no_aprobados[condicion]) == 0:
            continue

        filas = [armar_fila(img, celda, condicion) for celda in no_aprobados[condicion]]
        bloques.append(armar_encabezado(filas[0].shape[1], condicion))
        bloques.extend(filas)

    if len(bloques) == 0:
        return None

    return np.vstack(bloques)