from datetime import datetime


def guardar_historial(expresion, resultado, ruta_historial):
    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with ruta_historial.open("a", encoding="utf-8") as archivo:
        archivo.write(
            f"Fecha y hora: {fecha_hora}\n"
            f"Expresión ingresada: {expresion}\n"
            f"{resultado}\n"
            "----------------------------------------\n"
        )
