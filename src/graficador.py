import numpy as np
import sympy as sp

from src.analizador import x

def graficar(funcion, figura, canvas):
    """Dibuja una función en el lienzo de Matplotlib integrado en Tkinter."""

    figura.clear()
    eje = figura.add_subplot(111)
    valores_x = np.linspace(-10, 10, 500)

    funcion_numerica = sp.lambdify(x, funcion, modules=["numpy"])

    with np.errstate(all="ignore"):
        valores_y = funcion_numerica(valores_x)

    if np.isscalar(valores_y):
        valores_y = np.full_like(valores_x, valores_y, dtype=float)
    else:
        valores_y = np.asarray(valores_y)

    valores_y = np.real_if_close(valores_y)

    if np.iscomplexobj(valores_y):
        raise ValueError(
            "La función no entrega valores reales en el intervalo mostrado."
        )

    valores_y = np.asarray(valores_y, dtype=float)
    valores_y[~np.isfinite(valores_y)] = np.nan

    eje.plot(valores_x, valores_y, label=str(funcion), color="blue")
    eje.axhline(0, color="black", linewidth=0.8)
    eje.axvline(0, color="black", linewidth=0.8)
    eje.set_title("Gráfico de la función")
    eje.set_xlabel("Eje X")
    eje.set_ylabel("Eje Y")
    eje.grid(True)
    eje.legend()

    figura.tight_layout()
    canvas.draw()


def limpiar_grafico(figura, canvas):
    figura.clear()
    canvas.draw()
