import ctypes
import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from src.analizador import analizar_expresion
from src.graficador import graficar, limpiar_grafico


class PyMathInspectorApp:
    def __init__(self, ventana):
        self.ventana = ventana
        self.ruta = Path(__file__).resolve().parent.parent / "assets"

        self.configurar_ventana()
        self.crear_interfaz()

    def configurar_ventana(self):
        if sys.platform == "win32":
            resultado_app_id = (
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                    "don-python.PyMathInspector"
                )
            )
            if resultado_app_id != 0:
                raise OSError(
                    "No se pudo configurar el identificador de la aplicación."
                )

        self.ventana.title("PyMathInspector")
        self.ventana.geometry("900x650")
        self.ventana.minsize(750, 550)

        # Los iconos son opcionales: la aplicación abre aunque no estén presentes.
        png = self.ruta / "icono_pymathinspector.png"
        ico = self.ruta / "icono_pymathinspector.ico"

        if png.exists():
            self.icono = tk.PhotoImage(file=str(png))
            self.ventana.iconphoto(True, self.icono)

        if sys.platform == "win32" and ico.exists():
            self.ventana.iconbitmap(str(ico))

    def crear_interfaz(self):
        tk.Label(
            self.ventana,
            text="PyMathInspector",
            font=("Arial", 24, "bold"),
        ).pack(pady=10)

        tk.Label(
            self.ventana,
            text="Analizador interactivo de funciones matemáticas",
            font=("Arial", 11),
        ).pack()

        tk.Label(
            self.ventana,
            text=(
                "Ingresa una función polinómica, exponencial "
                "o logarítmica:"
            ),
            font=("Arial", 12, "bold"),
        ).pack(pady=(20, 5))

        self.entrada = ttk.Entry(
            self.ventana,
            font=("Arial", 14),
            width=40,
        )
        self.entrada.pack()
        self.entrada.insert(0, "2x^2 + 2x + 1")

        marco_botones = tk.Frame(self.ventana)
        marco_botones.pack(pady=15)

        ttk.Button(
            marco_botones,
            text="Analizar función",
            command=self.analizar,
        ).pack(side="left", padx=5)

        ttk.Button(
            marco_botones,
            text="Limpiar",
            command=self.limpiar,
        ).pack(side="left", padx=5)

        marco_resultados = tk.LabelFrame(
            self.ventana,
            text="Resultados del análisis",
            font=("Arial", 11, "bold"),
        )
        marco_resultados.pack(fill="x", padx=20, pady=10)

        self.texto_resultados = tk.Text(
            marco_resultados,
            height=8,
            font=("Consolas", 11),
            state="disabled",
        )
        self.texto_resultados.pack(fill="x", padx=10, pady=10)

        marco_grafico = tk.LabelFrame(
            self.ventana,
            text="Visualización gráfica",
        )
        marco_grafico.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10,
        )

        self.figura = plt.Figure(figsize=(6, 3), dpi=90)
        self.canvas = FigureCanvasTkAgg(
            self.figura,
            master=marco_grafico,
        )
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def mostrar_resultado(self, texto):
        self.texto_resultados.config(state="normal")
        self.texto_resultados.delete("1.0", tk.END)
        self.texto_resultados.insert(tk.END, texto)
        self.texto_resultados.config(state="disabled")

    def analizar(self):
        expresion = self.entrada.get().strip()

        if not expresion:
            messagebox.showwarning(
                "Aviso",
                "Debes ingresar una función matemática.",
            )
            return

        try:
            analisis = analizar_expresion(expresion)
            graficar(
                analisis["funcion"],
                self.figura,
                self.canvas,
            )
            self.mostrar_resultado(analisis["resultado"])

        except Exception as error:
            self.mostrar_resultado("")
            limpiar_grafico(self.figura, self.canvas)
            messagebox.showerror(
                "Entrada no válida",
                "Ingresa una función admitida.\n\n"
                "Polinómicas: grado 0, 1, 2 y 3.\n"
                "Exponenciales: 2^x o exp(x).\n"
                "Logarítmicas: log(x) o ln(x).\n\n"
                f"Detalle: {error}",
            )

    def limpiar(self):
        self.entrada.delete(0, tk.END)
        self.mostrar_resultado("")
        limpiar_grafico(self.figura, self.canvas)


def iniciar_aplicacion():
    ventana = tk.Tk()
    PyMathInspectorApp(ventana)
    ventana.mainloop()
