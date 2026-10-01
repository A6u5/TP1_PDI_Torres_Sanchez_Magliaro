import os
import glob
import cv2
from problema1 import resolver_problema1
from problema2 import (validar_planilla,
                       mostrar_resultados,
                       exportar_csv,
                       generar_imagen_no_aprobados)


carpeta = os.path.dirname(os.path.abspath(__file__))

# Carpetas de salida. exist_ok=True hace que no falle si ya existen, y como los archivos
# conservan el mismo nombre en cada corrida, se sobrescriben solos.
carpeta_planillas = os.path.join(carpeta, "datos", "planillas")
carpeta_problema1 = os.path.join(carpeta, "imagenes_problema1")
carpeta_csv = os.path.join(carpeta, "csv")
carpeta_imagenes = os.path.join(carpeta, "imagenes_problema2")

os.makedirs(carpeta_problema1, exist_ok=True)
os.makedirs(carpeta_csv, exist_ok=True)
os.makedirs(carpeta_imagenes, exist_ok=True)


# ---------------------------------------------------------------------------------------
# PROBLEMA 1 - Ecualizacion local de histograma
# ---------------------------------------------------------------------------------------

print("=" * 50)
print("PROBLEMA 1")
print("=" * 50)

for ruta_imagen in resolver_problema1(carpeta_problema1):
    print(f"Imagen generada: {os.path.relpath(ruta_imagen, carpeta)}")

print()


# ---------------------------------------------------------------------------------------
# PROBLEMA 2 - Validacion de planillas de calificaciones
# ---------------------------------------------------------------------------------------

# Buscamos todas las planillas con registros: grade_sheet_<id>.png.
# Nos quedamos solo con las que tienen un <id> numerico, asi descartamos grade_sheet_empty.png.
planillas = []

for ruta in glob.glob(os.path.join(carpeta_planillas, "grade_sheet_*.png")):
    identificador = os.path.splitext(os.path.basename(ruta))[0].replace("grade_sheet_", "")

    if identificador.isdigit():
        planillas.append((int(identificador), ruta))

planillas.sort()


# Aplicamos el algoritmo de forma ciclica sobre cada planilla.
for identificador, ruta in planillas:

    print("=" * 50)
    print(f"PROBLEMA 2 - PLANILLA {identificador}  ({os.path.basename(ruta)})")
    print("=" * 50)

    img = cv2.imread(ruta, cv2.IMREAD_GRAYSCALE)

    if img is None:
        print("No se pudo leer la imagen.\n")
        continue

    # a) Validacion de los campos de cada registro
    registros = validar_planilla(img)
    mostrar_resultados(registros)

    correctos = sum(registro["correcto"] for registro in registros)
    print(f"Registros cargados correctamente: {correctos} de {len(registros)}")

    # CSV con los resultados de la validacion
    ruta_csv = exportar_csv(registros, os.path.join(carpeta_csv, f"resultados_{identificador}.csv"))
    print(f"CSV generado: {os.path.relpath(ruta_csv, carpeta)}")

    # b) Imagen unica con los alumnos no aprobados
    salida = generar_imagen_no_aprobados(img, registros)

    if salida is None:
        print("No hay alumnos no aprobados entre los registros cargados correctamente.\n")
        continue

    ruta_salida = os.path.join(carpeta_imagenes, f"no_aprobados_{identificador}.png")
    cv2.imwrite(ruta_salida, salida)
    print(f"Imagen generada: {os.path.relpath(ruta_salida, carpeta)}\n")


print("Listo. Todas las salidas quedaron guardadas en las carpetas del TP.")