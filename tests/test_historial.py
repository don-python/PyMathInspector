from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.historial import guardar_historial


class GuardarHistorialTests(unittest.TestCase):
    def test_append_entry_to_existing_history_file(self):
        with TemporaryDirectory() as directorio:
            ruta_historial = Path(directorio) / "historial.txt"
            ruta_historial.write_text("Entrada anterior\n", encoding="utf-8")

            guardar_historial(
                "2x^2 + 1",
                "Tipo: Función cuadrática",
                ruta_historial,
            )

            contenido = ruta_historial.read_text(encoding="utf-8")

        self.assertTrue(contenido.startswith("Entrada anterior\n"))
        self.assertRegex(
            contenido,
            r"Fecha y hora: \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\n",
        )
        self.assertIn("Expresión ingresada: 2x^2 + 1\n", contenido)
        self.assertTrue(
            contenido.endswith(
                "Tipo: Función cuadrática\n"
                "----------------------------------------\n"
            )
        )


if __name__ == "__main__":
    unittest.main()
