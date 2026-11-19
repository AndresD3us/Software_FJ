"""Simulación de operaciones de Software FJ con registro de eventos en un log.

Autor: Andres Felipe Benavides Gil
Curso: Programación 213023 - Fase 4 - UNAD

Ejecución: python main.py
"""

from decimal import Decimal
import logging
from pathlib import Path

from gestion import Gestion
from modelos import Asesoria, Cliente, Equipo, ErrorSistema, Sala

IVA = Decimal("0.19")


def crear_casos(sistema: Gestion) -> list:
    """Devuelve la lista de casos: (nombre, ¿se espera error?, operación)."""
    cliente = sistema.registrar_cliente
    servicio = sistema.registrar_servicio
    reservar = sistema.reservar
    return [
        ("Cliente válido", False,
         lambda: cliente(Cliente("C1", "Ana Ruiz", "ana@example.com", "3001234567")).describir()),
        ("Correo inválido", True,
         lambda: cliente(Cliente("C2", "Luis Díaz", "incorrecto", "3001234567"))),
        ("Nombre vacío (parámetro faltante)", True,
         lambda: cliente(Cliente("C3", "   ", "vacio@example.com", "3001234567"))),
        ("Nombre con números", True,
         lambda: cliente(Cliente("C4", "Pedro 123", "pedro@example.com", "3001234567"))),
        ("Teléfono inválido", True,
         lambda: cliente(Cliente("C5", "Marta Gil", "marta@example.com", "12ab"))),
        ("Cliente duplicado", True,
         lambda: cliente(Cliente("C1", "Ana Ruiz", "ana@example.com", "3001234567"))),
        ("Segundo cliente válido", False,
         lambda: cliente(Cliente("C2", "Luis Díaz", "luis@example.com", "3109876543")).describir()),
        ("Sala válida", False, lambda: servicio(Sala("S1", 50000)).describir()),
        ("Tarifa no numérica", True, lambda: servicio(Sala("S2", "abc"))),
        ("Tarifa negativa", True, lambda: servicio(Asesoria("A9", -5000))),
        ("Equipo válido", False, lambda: servicio(Equipo("E1", 35000)).describir()),
        ("Asesoría válida", False, lambda: servicio(Asesoria("A1", 90000)).describir()),
        ("Registro de servicio inactivo", False,
         lambda: servicio(Equipo("E2", 35000, disponible=False)).describir()),
        ("Reserva de servicio inactivo", True, lambda: reservar("R1", "C1", "E2", 2)),
        ("Duración inválida", True, lambda: reservar("R1", "C1", "E1", 1)),
        ("Servicio inexistente", True, lambda: reservar("R1", "C1", "X9", 2)),
        ("Reserva de sala (variante 1: solo horas)", False,
         lambda: reservar("R1", "C1", "S1", 2)),
        ("Reserva de equipo (variante 2: con IVA)", False,
         lambda: reservar("R2", "C2", "E1", 3, IVA)),
        ("Descuento fuera de rango", True,
         lambda: reservar("R3", "C1", "A1", 2, IVA, Decimal("1.1"))),
        ("Reserva de asesoría (variante 3: IVA y descuento)", False,
         lambda: reservar("R3", "C1", "A1", 2, IVA, Decimal("0.10"))),
        ("Reserva con código repetido", True, lambda: reservar("R3", "C2", "S1", 1)),
        ("Cancelación válida", False, lambda: sistema.cancelar("R1")),
        ("Cancelación repetida", True, lambda: sistema.cancelar("R1")),
        ("Cliente inexistente", True, lambda: reservar("R4", "C9", "S1", 1)),
        ("Reserva después de los errores", False, lambda: reservar("R4", "C2", "S1", 1)),
    ]


def ejecutar(registro: logging.Logger) -> int:
    """Ejecuta todos los casos y devuelve 0 si todo salió como se esperaba."""
    sistema = Gestion()
    casos = crear_casos(sistema)
    desviaciones = 0
    registro.info("Inicio de la simulación con %d casos", len(casos))
    for indice, (nombre, espera_error, operacion) in enumerate(casos, start=1):
        try:
            resultado = operacion()
        except ErrorSistema as error:
            registro.exception("Caso %02d | %s | %s", indice, nombre, error)
            etiqueta = "ERROR CONTROLADO" if espera_error else "FALLO DE SIMULACIÓN"
            desviaciones += int(not espera_error)
            print(f"{indice:02d}. {nombre} | {etiqueta} | {error}")
        except Exception:
            registro.exception("Caso %02d | Error inesperado en %s", indice, nombre)
            desviaciones += 1
            print(f"{indice:02d}. {nombre} | ERROR INESPERADO")
        else:
            registro.info("Caso %02d | %s | %s", indice, nombre, resultado)
            desviaciones += int(espera_error)
            etiqueta = "FALLO DE SIMULACIÓN" if espera_error else "CORRECTO"
            print(f"{indice:02d}. {nombre} | {etiqueta} | {resultado}")
        finally:
            registro.info("Caso %02d finalizado", indice)

    resumen = sistema.resumen()
    registro.info("Fin de la simulación | %s | Desviaciones: %d", resumen, desviaciones)
    print(f"\nCasos completados: {len(casos)}. Desviaciones: {desviaciones}.")
    print(resumen)
    return int(desviaciones > 0)


def main() -> int:
    """Configura el archivo de log, ejecuta la simulación y lo cierra."""
    registro = logging.getLogger("software_fj")
    registro.setLevel(logging.INFO)
    ruta = Path(__file__).with_name("software_fj.log")
    try:
        archivo = logging.FileHandler(ruta, encoding="utf-8")
    except OSError as error:
        print(f"No se pudo abrir {ruta.name}: {error}")
        return 1

    archivo.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    registro.addHandler(archivo)
    try:
        return ejecutar(registro)
    finally:
        registro.removeHandler(archivo)
        archivo.close()


if __name__ == "__main__":
    raise SystemExit(main())
