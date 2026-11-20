
import ctypes
from pathlib import Path
import sys

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

if sys.platform == "win32":
    resultado_app_id = ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
        "don-python.PyMathInspector"
    )
    if resultado_app_id != 0:
        raise OSError(
            f"No se pudo configurar el identificador de la aplicación "
            f"(HRESULT 0x{resultado_app_id & 0xFFFFFFFF:08X})."
        )

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
        # Interpretar la expresión ingresada.
        # Se aceptan x^2, 2x, log(x), ln(x), exp(x) y 2^x.
        funcion = parse_expr(
            expresion,
            local_dict={"x": x, "log": sp.log, "ln": sp.log, "exp": sp.exp, "e": sp.E},
            transformations=transformaciones
        )

        # Validar que no existan variables desconocidas.
        if funcion.free_symbols - {x}:
            raise ValueError("Variable no permitida")

        # Identificar la familia de la función.
        polinomio = None

        try:
            polinomio = sp.Poly(funcion, x)
            grado = polinomio.degree()

            if grado == 0:
                tipo = "Función constante"
            elif grado == 1:
                tipo = "Función lineal (primer grado)"
            elif grado == 2:
                tipo = "Función cuadrática (segundo grado)"
            elif grado == 3:
                tipo = "Función cúbica (tercer grado)"
            else:
                raise ValueError(
                    "Solo se permiten polinomios de grado 0, 1, 2 y 3."
                )

            familia = "Polinómica"

        except sp.PolynomialError:
            grado = None

            # Funciones logarítmicas: log(x), ln(x), log(x, 2), etc.
            if funcion.has(sp.log) and not funcion.has(sp.exp):
                logaritmos = funcion.atoms(sp.log)
                expresion_sin_logaritmos = funcion.xreplace({
                    termino: sp.Symbol(f"_log{i}")
                    for i, termino in enumerate(logaritmos)
                })

                # Evitar clasificar como logarítmica una expresión
                # que también tenga x fuera del logaritmo.
                if expresion_sin_logaritmos.has(x):
                    raise ValueError("Expresión logarítmica no permitida")

                tipo = "Función logarítmica"
                familia = "Logarítmica"

            # Funciones exponenciales: 2^x, e^x, exp(x), etc.
            elif funcion.has(sp.exp) or any(
                potencia.exp.has(x) and not potencia.base.has(x)
                for potencia in funcion.atoms(sp.Pow)
            ):
                exponenciales = set(funcion.atoms(sp.exp))
                exponenciales.update(
                    potencia
                    for potencia in funcion.atoms(sp.Pow)
                    if potencia.exp.has(x) and not potencia.base.has(x)
                )

                expresion_sin_exponenciales = funcion.xreplace({
                    termino: sp.Symbol(f"_exp{i}")
                    for i, termino in enumerate(exponenciales)
                })

                # Evitar clasificar como exponencial una expresión
                # que también tenga x fuera del exponente.
                if expresion_sin_exponenciales.has(x):
                    raise ValueError("Expresión exponencial no permitida")

                tipo = "Función exponencial"
                familia = "Exponencial"

            else:
                raise ValueError("Tipo de función no permitido")

        # Calcular intersección con el eje Y cuando exista.
        valor_y = sp.simplify(funcion.subs(x, 0))

        if valor_y.has(sp.zoo, sp.oo, -sp.oo, sp.nan) or valor_y.is_finite is False:
            interseccion = "No existe (la función no está definida en x = 0)"
        else:
            interseccion = f"(0, {valor_y})"

        # Preparar los resultados.
        resultado = (
            f"Función: {sp.sstr(funcion)}\n"
            f"Tipo: {tipo}\n"
            f"Familia: {familia}\n"
        )

        if grado is not None:
            resultado += f"Grado: {grado}\n"

        resultado += f"Intersección con eje Y: {interseccion}\n"

        # Calcular vértice y concavidad solo para cuadráticas.
        if grado == 2:
            a, b, c = polinomio.all_coeffs()

            vertice_x = -b / (2 * a)
            vertice_y = funcion.subs(x, vertice_x)

            resultado += (
                f"Vértice: ({vertice_x}, {vertice_y})\n"
            )

            if a > 0:
                resultado += "Concavidad: Hacia arriba\n"
            else:
                resultado += "Concavidad: Hacia abajo\n"

        # Mostrar resultados en pantalla.
        texto_resultados.config(state="normal")
        texto_resultados.delete("1.0", tk.END)
        texto_resultados.insert(tk.END, resultado)
        texto_resultados.config(state="disabled")

        # Generar gráfico.
        graficar(funcion)

    except Exception:
        # Limpiar resultados y gráfico para no dejar información anterior
        # cuando la entrada actual no sea válida.
        texto_resultados.config(state="normal")
        texto_resultados.delete("1.0", tk.END)
        texto_resultados.config(state="disabled")

        figura.clear()
        canvas.draw()
        messagebox.showerror(
            "Entrada no válida",
            "Ingresa una función polinómica de grado 0 a 3, "
            "exponencial o logarítmica.\n\n"
            "Ejemplos válidos:\n"
            "5\n"
            "2x + 3\n"
            "x^2 + 2x + 1\n"
            "x^3 - 2x + 5\n"
            "2^x o exp(x)\n"
            "log(x) o ln(x)"
        )


# ==========================================
# FUNCION PARA GRAFICAR
# ==========================================

def graficar(funcion):

    figura.clear()
    eje = figura.add_subplot(111)

    # crear valores para el eje X.
    valores_x = np.linspace(-10, 10, 500)

    # convertir la expresión simbolica a una función numérica.
    funcion_numerica = sp.lambdify(
        x,
        funcion,
        modules=["numpy"]
    )

    # evaluar la funcion. algunas funciones, como log(x),
    # no estan definidas para todos los valores de X.
    with np.errstate(all="ignore"):
        valores_y = funcion_numerica(valores_x)

    # Las funciones constantes entregan un solo valor.
    if np.isscalar(valores_y):
        valores_y = np.full_like(
            valores_x,
            valores_y,
            dtype=float
        )
    else:
        valores_y = np.asarray(valores_y)

    # Evitar errores al graficar valores no reales o infinitos.
    valores_y = np.real_if_close(valores_y)

    if np.iscomplexobj(valores_y):
        raise ValueError("La función no entrega valores reales en este intervalo.")

    valores_y = np.asarray(valores_y, dtype=float)
    valores_y[~np.isfinite(valores_y)] = np.nan

    # Dibujar la función.
    eje.plot(
        valores_x,
        valores_y,
        label=str(funcion),
        color="blue"
    )

    # Dibujar los ejes cartesianos.
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

ruta_iconos = Path(__file__).resolve().parent
icono = tk.PhotoImage(file=str(ruta_iconos / "icono_pymathinspector.png"))
ventana.iconphoto(True, icono)
ventana.iconbitmap(str(ruta_iconos / "icono_pymathinspector.ico"))

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
    text="Ingresa una función polinómica, exponencial o logarítmica:",
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