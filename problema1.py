import os
import matplotlib
import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
matplotlib.use("Agg")   # Backend sin interfaz grafica: las figuras no abren ventanas, se guardan en archivo.


CARPETA = os.path.dirname(os.path.abspath(__file__))
IMAGEN = os.path.join(CARPETA, "datos", "Imagen_con_detalles_escondidos.tif")

M_ELEGIDA = 7                            # ventana elegida para el punto b)
TAMANIOS = [3, 7, 15, 31, 61, 121]       # ventanas comparadas en el punto c)


# a) Ecualización local de histograma
def ecualizacion_local_hist(img, M, N=None):
    """
    Ecualización local de histograma con ventana MxN (N = M por defecto).
    Se calcula el histograma de cada ventana y se usa su CDF para obtener
    el nuevo nivel del píxel central.
    """
    if N is None:
        N = M
    L = 256
    # Bordes: se replican para poder centrar la ventana en todos los píxeles
    top, bottom = M // 2, M - 1 - M // 2
    left, right = N // 2, N - 1 - N // 2
    pad = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_REPLICATE)

    out = np.zeros_like(img)
    H, W = img.shape
    for i in range(H):
        for j in range(W):
            ventana = pad[i:i + M, j:j + N]
            hist = np.bincount(ventana.ravel(), minlength=L)
            cdf = np.cumsum(hist)
            # Transformación de ecualización: s = (L-1) * CDF(r) / (M*N)
            out[i, j] = np.round((L - 1) * cdf[img[i, j]] / (M * N))
    return out


def resolver_problema1(carpeta_salida, ruta_imagen=IMAGEN, m_elegida=M_ELEGIDA, tamanios=TAMANIOS):
    """Resuelve los puntos b) y c) y guarda todas las imagenes en carpeta_salida.

    No abre ninguna ventana: cada figura se escribe en disco. Devuelve la lista de
    rutas generadas. Si la carpeta ya existe, los archivos se sobrescriben.
    """

    os.makedirs(carpeta_salida, exist_ok=True)
    generadas = []

    # Lectura con Pillow y conversión a escala de grises uint8
    img = np.array(Image.open(ruta_imagen).convert("L"), dtype=np.uint8)

    # Calculamos una sola vez el resultado de cada tamaño de ventana y lo reusamos en
    # los dos puntos, asi no repetimos el procesamiento (que es lento: dos bucles por pixel).
    resultados = {}

    for m in sorted(set(tamanios) | {m_elegida}):
        print(f"  Procesando ventana {m}x{m} ...")
        resultados[m] = ecualizacion_local_hist(img, m)

        ruta = os.path.join(carpeta_salida, f"resultado_ventana_{m}.png")
        Image.fromarray(resultados[m]).save(ruta)
        generadas.append(ruta)

    # b) Resultado con la ventana elegida
    fig = plt.figure(figsize=(12, 6))
    plt.subplot(121), plt.imshow(img, cmap="gray", vmin=0, vmax=255), plt.title("Original")
    plt.subplot(122), plt.imshow(resultados[m_elegida], cmap="gray", vmin=0, vmax=255), plt.title(f"Ecualización local {m_elegida}x{m_elegida}")
    plt.tight_layout()

    ruta = os.path.join(carpeta_salida, f"b_original_vs_ventana_{m_elegida}.png")
    fig.savefig(ruta, dpi=150)
    plt.close(fig)   # cerramos la figura para que no se acumulen en memoria
    generadas.append(ruta)

    # c) Análisis de la influencia del tamaño de ventana
    fig, axs = plt.subplots(2, 3, figsize=(15, 10), sharex=True, sharey=True)

    for ax, m in zip(axs.ravel(), tamanios):
        ax.imshow(resultados[m], cmap="gray", vmin=0, vmax=255)
        ax.set_title(f"Ventana {m}x{m}")

    plt.tight_layout()

    ruta = os.path.join(carpeta_salida, "c_comparacion_ventanas.png")
    fig.savefig(ruta, dpi=150)
    plt.close(fig)
    generadas.append(ruta)

    return generadas


if __name__ == "__main__":
    for ruta in resolver_problema1(os.path.join(CARPETA, "imagenes_problema1")):
        print("Imagen generada:", os.path.relpath(ruta, CARPETA))
