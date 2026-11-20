import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor,
)

x = sp.symbols("x")

TRANSFORMACIONES = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)


def analizar_expresion(expresion):
    """Interpreta y analiza una función admitida por PyMathInspector."""

    if not expresion.strip():
        raise ValueError("Debes ingresar una función matemática.")

    funcion = parse_expr(
        expresion,
        local_dict={
            "x": x,
            "log": sp.log,
            "ln": sp.log,
            "exp": sp.exp,
            "e": sp.E,
        },
        transformations=TRANSFORMACIONES,
    )

    if funcion.free_symbols - {x}:
        raise ValueError("Solo se permite utilizar la variable x.")

    polinomio = None
    grado = None

    try:
        polinomio = sp.Poly(funcion, x)
        grado = polinomio.degree()

        nombres = {
            0: "Función constante",
            1: "Función lineal (primer grado)",
            2: "Función cuadrática (segundo grado)",
            3: "Función cúbica (tercer grado)",
        }

        if grado not in nombres:
            raise ValueError(
                "Solo se permiten polinomios de grado 0, 1, 2 y 3."
            )

        tipo = nombres[grado]
        familia = "Polinómica"

    except sp.PolynomialError:
        if funcion.has(sp.log) and not funcion.has(sp.exp):
            logaritmos = funcion.atoms(sp.log)
            sin_logaritmos = funcion.xreplace({
                termino: sp.Symbol(f"_log{i}")
                for i, termino in enumerate(logaritmos)
            })

            if sin_logaritmos.has(x):
                raise ValueError(
                    "Por ahora se permiten funciones donde x aparezca "
                    "dentro del logaritmo."
                )

            tipo = "Función logarítmica"
            familia = "Logarítmica"

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

            sin_exponenciales = funcion.xreplace({
                termino: sp.Symbol(f"_exp{i}")
                for i, termino in enumerate(exponenciales)
            })

            if sin_exponenciales.has(x):
                raise ValueError(
                    "Por ahora se permiten funciones donde x aparezca "
                    "en el exponente."
                )

            tipo = "Función exponencial"
            familia = "Exponencial"

        else:
            raise ValueError(
                "La expresión no corresponde a una función admitida."
            )

    valor_y = sp.simplify(funcion.subs(x, 0))
    if (
        valor_y.has(sp.zoo, sp.oo, -sp.oo, sp.nan)
        or valor_y.is_finite is False
    ):
        interseccion_y = (
            "No existe (la función no está definida en x = 0)"
        )
    else:
        interseccion_y = f"(0, {valor_y})"

    lineas = [
        f"Función: {sp.sstr(funcion)}",
        f"Tipo: {tipo}",
        f"Familia: {familia}",
    ]

    if grado is not None:
        lineas.append(f"Grado: {grado}")

    lineas.append(f"Intersección con eje Y: {interseccion_y}")

    if grado == 2:
        a, b, _ = polinomio.all_coeffs()
        vertice_x = -b / (2 * a)
        vertice_y = sp.simplify(funcion.subs(x, vertice_x))
        lineas.append(f"Vértice: ({vertice_x}, {vertice_y})")
        lineas.append(
            "Concavidad: Hacia arriba" if a > 0
            else "Concavidad: Hacia abajo"
        )

    return {
        "funcion": funcion,
        "familia": familia,
        "tipo": tipo,
        "grado": grado,
        "resultado": "\n".join(lineas),
    }
