"""Gestión en memoria de clientes, servicios y reservas (sin base de datos).

Autor: Andres Felipe Benavides Gil
Curso: Programación 213023 - Fase 4 - UNAD
"""

from typing import TypeVar

from modelos import (
    Cliente, Entidad, ErrorSistema, OperacionInvalida, Reserva, Servicio, texto,
)

T = TypeVar("T", bound=Entidad)


class Gestion:
    """Centraliza el registro, la búsqueda y las reservas en listas internas."""

    def __init__(self):
        self._clientes: list[Cliente] = []
        self._servicios: list[Servicio] = []
        self._reservas: list[Reserva] = []

    @staticmethod
    def _buscar(lista: list[T], codigo: str) -> T:
        """Busca una entidad por código o lanza un error si no existe."""
        codigo = texto(codigo, "El código")
        for entidad in lista:
            if entidad.codigo == codigo:
                return entidad
        raise OperacionInvalida(f"El código {codigo} no está registrado.")

    @staticmethod
    def _registrar(lista: list[T], entidad: T) -> T:
        """Agrega una entidad a la lista si su código no está repetido."""
        if any(actual.codigo == entidad.codigo for actual in lista):
            raise OperacionInvalida(f"El código {entidad.codigo} ya está registrado.")
        lista.append(entidad)
        return entidad

    def registrar_cliente(self, cliente: Cliente) -> Cliente:
        return self._registrar(self._clientes, cliente)

    def registrar_servicio(self, servicio: Servicio) -> Servicio:
        return self._registrar(self._servicios, servicio)

    def reservar(self, codigo: str, cliente: str, servicio: str, horas: int,
                 impuesto=None, descuento=None) -> str:
        """Crea, confirma y registra una reserva."""
        cliente_registrado = self._buscar(self._clientes, cliente)
        servicio_registrado = self._buscar(self._servicios, servicio)
        if any(r.codigo == codigo for r in self._reservas):
            raise OperacionInvalida(f"La reserva {codigo} ya existe.")
        reserva = Reserva(codigo, cliente_registrado, servicio_registrado, horas)
        try:
            total = reserva.confirmar(impuesto, descuento)
        except ErrorSistema as causa:
            raise OperacionInvalida(
                f"No se pudo confirmar la reserva {codigo}: {causa}"
            ) from causa
        else:
            self._registrar(self._reservas, reserva)
        return f"{reserva.describir()} por COP {total:,.2f}"

    def cancelar(self, codigo: str) -> str:
        """Cancela una reserva registrada."""
        reserva = self._buscar(self._reservas, codigo)
        reserva.cancelar()
        return reserva.describir()

    def resumen(self) -> str:
        """Devuelve el conteo de objetos guardados en memoria."""
        confirmadas = sum(1 for r in self._reservas if r.estado.value == "confirmada")
        return (
            f"Clientes: {len(self._clientes)} | Servicios: {len(self._servicios)}"
            f" | Reservas: {len(self._reservas)} (confirmadas: {confirmadas})"
        )
