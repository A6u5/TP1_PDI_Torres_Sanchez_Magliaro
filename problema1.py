import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image


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


# b) Resultado con la ventana elegida

# Lectura con Pillow y conversión a escala de grises uint8
img = np.array(Image.open("Imagen_con_detalles_escondidos.tif").convert("L"), dtype=np.uint8)

m_elegida = 7   
res_b = ecualizacion_local_hist(img, m_elegida)

plt.figure(figsize=(12, 6))
plt.subplot(121), plt.imshow(img, cmap="gray", vmin=0, vmax=255), plt.title("Original")
plt.subplot(122), plt.imshow(res_b, cmap="gray", vmin=0, vmax=255), plt.title(f"Ecualización local {m_elegida}x{m_elegida}")
plt.tight_layout()
plt.show()


# c) Análisis e la influencia del tamaño de ventana

# Distintos tamaños de ventana
tamanios = [3, 7, 15, 31, 61, 121]

fig, axs = plt.subplots(2, 3, figsize=(15, 10), sharex=True, sharey=True)
for ax, m in zip(axs.ravel(), tamanios):
    res = ecualizacion_local_hist(img, m)
    Image.fromarray(res).save(f"resultado_ventana_{m}.png")
    ax.imshow(res, cmap="gray", vmin=0, vmax=255)
    ax.set_title(f"Ventana {m}x{m}")
plt.tight_layout()
plt.show()

