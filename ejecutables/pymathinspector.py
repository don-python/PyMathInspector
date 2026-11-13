
import tkinter as tk
from tkinter import ttk, messagebox

import sympy as sp
import numpy as np
import matplotlib.pyplot as plt

from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor
)
# hola 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

x = sp.symbols("x")

# Permite escribir:
# 2x en lugar de 2*x
# x^2 en lugar de x**2
# 3(x+2) en lugar de 3*(x+2)

transformaciones = standard_transformations + (
    implicit_multiplication_application,
    convert_xor
)

# ==========================================
# FUNCION PARA ANALIZAR
# ==========================================

def analizar():

    expresion = entrada.get().strip()

    if not expresion:
        messagebox.showwarning(
            "Aviso",
            "Debes ingresar una función matemática."
        )
        return

    try:

        # Interpretar la expresion ingresada
        funcion = parse_expr(
            expresion,
            local_dict={"x": x},
            transformations=transformaciones
        )

        # Validar que no existan variables desconocidas
        if funcion.free_symbols - {x}:
            raise ValueError("Entrada no válida")

        # Comprobar que sea una expresion polinomica
        polinomio = sp.Poly(funcion, x)

        grado = polinomio.degree()

        # Identificar tipo de funcion
        if grado == 0:
            tipo = "Función constante"

        elif grado == 1:
            tipo = "Función lineal (primer grado)"

        elif grado == 2:
            tipo = "Función cuadrática (segundo grado)"

        elif grado == 3:
            tipo = "Función cúbica (tercer grado)"

        else:
            raise ValueError("Solo se permiten funciones de grado 1, 2 y 3")


        # Calcular interseccion con eje Y
        interseccion_y = funcion.subs(x, 0)

        # Preparar resultados
        resultado = (
            f"Función: {sp.expand(funcion)}\n"
            f"Tipo: {tipo}\n"
            f"Grado: {grado}\n"
            f"Intersección eje Y: {interseccion_y}\n"
        )

        # Calcular vertice si es cuadratica
        if grado == 2:

            a, b, c = polinomio.all_coeffs()

            vertice_x = -b / (2 * a)
            vertice_y = funcion.subs(x, vertice_x)

            resultado += (
                f"Vértice: ({vertice_x}, {vertice_y})\n"
            )

            # Identificar concavidad
            if a > 0:
                resultado += "Concavidad: Hacia arriba\n"
            else:
                resultado += "Concavidad: Hacia abajo\n"

        # Mostrar resultados en pantalla
        texto_resultados.config(state="normal")
        texto_resultados.delete("1.0", tk.END)
        texto_resultados.insert(tk.END, resultado)
        texto_resultados.config(state="disabled")

        # Generar grafico
        graficar(funcion)

    except Exception:

        messagebox.showerror(
            "Entrada no válida",
            "Solo podemos ingresar expresiones "
            "matemáticas válidas.\n\n"
            "Ejemplos:\n"
            "2x + 3\n"
            "x^2 + 2x - 3\n"
            "3x^3 + 2x + 1\n"
            "polinomicas hasta grado 3"
        )

# ==========================================
# FUNCION PARA GRAFICAR
# ==========================================

def graficar(funcion):

    figura.clear()

    eje = figura.add_subplot(111)

    # Generar valores para el eje X
    valores_x = np.linspace(-10, 10, 300)

    # Convertir expresion matematica a funcion numerica
    funcion_numerica = sp.lambdify(
        x,
        funcion,
        modules=["numpy"]
    )

    valores_y = funcion_numerica(valores_x)
    valores_y = funcion_numerica(valores_x)

    # Si la función es constante, generar valores
    # para todos los puntos del eje X
    if np.isscalar(valores_y):
        valores_y = np.full_like(
            valores_x,
            valores_y,
            dtype=float
        )

    # Dibujar funcion
    eje.plot(
        valores_x,
        valores_y,
        label=str(funcion),
        color="blue"
    )

    # Dibujar ejes
    eje.axhline(0, color="black", linewidth=0.8)
    eje.axvline(0, color="black", linewidth=0.8)

    eje.set_title("Gráfico de la función")
    eje.set_xlabel("Eje X")
    eje.set_ylabel("Eje Y")

    eje.grid(True)
    eje.legend()

    figura.tight_layout()

    canvas.draw()

# ==========================================
# FUNCION PARA LIMPIAR
# ==========================================

def limpiar():

    entrada.delete(0, tk.END)

    texto_resultados.config(state="normal")
    texto_resultados.delete("1.0", tk.END)
    texto_resultados.config(state="disabled")

    figura.clear()
    canvas.draw()

# ==========================================
# VENTANA PRINCIPAL
# ==========================================

ventana = tk.Tk()

ventana.title("PyMathInspector")

ventana.geometry("900x650")

ventana.minsize(750, 550)


# ==========================================
# TITULO
# ==========================================

titulo = tk.Label(
    ventana,
    text="PyMathInspector",
    font=("Arial", 24, "bold")
)

titulo.pack(pady=10)


subtitulo = tk.Label(
    ventana,
    text="Analizador interactivo de funciones matemáticas",
    font=("Arial", 11)
)

subtitulo.pack()


# ==========================================
# CAMPO DE INGRESO
# ==========================================

tk.Label(
    ventana,
    text="Ingresa una función matemática:",
    font=("Arial", 12, "bold")
).pack(pady=(20, 5))


entrada = ttk.Entry(
    ventana,
    font=("Arial", 14),
    width=40
)

entrada.pack()

# Ejemplo inicial
entrada.insert(0, "2x^2 + 2x + 1")


# ==========================================
# BOTONES
# ==========================================

marco_botones = tk.Frame(ventana)

marco_botones.pack(pady=15)


boton_analizar = ttk.Button(
    marco_botones,
    text="Analizar función",
    command=analizar
)

boton_analizar.pack(side="left", padx=5)


boton_limpiar = ttk.Button(
    marco_botones,
    text="Limpiar",
    command=limpiar
)

boton_limpiar.pack(side="left", padx=5)


# ==========================================
# AREA DE RESULTADOS
# ==========================================

marco_resultados = tk.LabelFrame(
    ventana,
    text="Resultados del análisis",
    font=("Arial", 11, "bold")
)

marco_resultados.pack(
    fill="x",
    padx=20,
    pady=10
)


texto_resultados = tk.Text(
    marco_resultados,
    height=8,
    font=("Consolas", 11),
    state="disabled"
)

texto_resultados.pack(
    fill="x",
    padx=10,
    pady=10
)


# ==========================================
# AREA DEL GRAFICO
# ==========================================

marco_grafico = tk.LabelFrame(
    ventana,
    text="Visualización gráfica"
)

marco_grafico.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=10
)


figura = plt.Figure(
    figsize=(6, 3),
    dpi=90
)


canvas = FigureCanvasTkAgg(
    figura,
    master=marco_grafico
)


canvas.get_tk_widget().pack(
    fill="both",
    expand=True
)


# ==========================================
# EJECUTAR PROGRAMA
# ==========================================

ventana.mainloop()