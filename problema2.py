import cv2
import numpy as np
import matplotlib.pyplot as plt

def validar_planilla(img):
    
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
    # por eso haremos: 
    cols = np.where(img_cols_th)[0]
    rows = np.where(img_rows_th)[0]

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

    grupos_cols = agrupar_consecutivos(cols)
    grupos_rows = agrupar_consecutivos(rows)
    ## Funcion para obtener los centros de esas lineas agrupadas.
    def centros_de_grupos(grupos):
        return [(inicio + fin) // 2 for inicio, fin in grupos]
    
    #obtencion final de las lineas. 
    x = centros_de_grupos(grupos_cols) #lineas verticales
    y = centros_de_grupos(grupos_rows) #lineas horizontales

    # DEFINO UNA FUNCION AUXILIAR Para determinar los caracteres validos dentro de una celda.
    def componentes_validas(celda, area_min):
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
        celda.astype(np.uint8),
        connectivity=8
        )
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
                    "area": area
                })
        return componentes
    
    #DEFINO OTRA FUNCION AUXILIAR PARA determinar la cantidad de palabras que hay
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
    
    
    # Luego dos lineas horizontales consecutivas (Y1 , Y2) y verticales (X1 , X2) determinan una celda.
    # Recorrer celdas.
    fila_inicio_datos = 1
    resultado_final = {}
    for i in range(fila_inicio_datos, len(y) - 1):

        resultado_fila = []

        for j in range(1, len(x) - 1):

            celda = img_th[
                y[i] + 1:y[i + 1],
                x[j] + 1:x[j + 1]
            ]

            componentes = componentes_validas(celda, area_min=4)

            # Legajo
            if j == 1:

                cantidad_caracteres = len(componentes)
                palabras = cantidad_palabras(componentes)

                if cantidad_caracteres == 8 and palabras == 1:
                    resultado = "OK"
                else:
                    resultado = "MAL"


            # Nombre y Apellido
            elif j == 2:

                cantidad_caracteres = len(componentes)
                palabras = cantidad_palabras(componentes)

                if cantidad_caracteres <= 12 and palabras >= 2:
                    resultado = "OK"
                else:
                    resultado = "MAL"


            # Parciales 1, 2 y 3
            elif j in [3, 4, 5]:

                cantidad_caracteres = len(componentes)
                palabras = cantidad_palabras(componentes)

                if cantidad_caracteres in [1, 2] and palabras == 1:
                    resultado = "OK"
                else:
                    resultado = "MAL"


            # Condición final
            elif j == 6:

                cantidad_caracteres = len(componentes)

                if cantidad_caracteres == 1:
                    resultado = "OK"
                else:
                    resultado = "MAL"


            resultado_fila.append(resultado)
        
        resultado_final[i] = resultado_fila

    return resultado_final



img = cv2.imread(
    r"C:\Users\facum\OneDrive\Documentos\2.T.U.I.A\Procesamineto Imagenes\TP_1\TP1_PDI_Torres_Sanchez_Magliaro\grade_sheet_2.png",
    cv2.IMREAD_GRAYSCALE)

print(validar_planilla(img))
