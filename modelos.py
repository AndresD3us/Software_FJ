"""Entidades, reglas de negocio y excepciones propias de Software FJ.

Autor: Andres Felipe Benavides Gil
Curso: Programación 213023 - Fase 4 - UNAD
"""

from abc import ABC, abstractmethod
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from enum import Enum
import re
from typing import overload


class ErrorSistema(Exception):
    """Excepción base para todos los errores esperados del sistema."""


class DatosInvalidos(ErrorSistema):
    """Se lanza cuando un dato no cumple las reglas del sistema."""


class ParametroFaltante(DatosInvalidos):
    """Se lanza cuando un campo obligatorio llega vacío o no se envía."""


class OperacionInvalida(ErrorSistema):
    """Se lanza cuando la operación no está permitida en el estado actual."""


class ServicioNoDisponible(OperacionInvalida):
    """Se lanza cuando se intenta reservar un servicio inactivo."""


def texto(valor: str, campo: str) -> str:
    """Valida que un campo obligatorio sea un texto con contenido."""
    if not isinstance(valor, str) or not valor.strip():
        raise ParametroFaltante(f"{campo} es obligatorio.")
    return valor.strip()


def numero(valor: int | str | Decimal, campo: str) -> Decimal:
    """Convierte un valor a Decimal y conserva la causa original si falla."""
    try:
        resultado = Decimal(str(valor))
    except (InvalidOperation, ValueError) as causa:
        raise DatosInvalidos(f"{campo} debe contener un número.") from causa
    if not resultado.is_finite():
        raise DatosInvalidos(f"{campo} debe ser un número finito.")
    return resultado


class Entidad(ABC):
    """Clase abstracta base para todas las entidades identificables."""

    def __init__(self, codigo: str):
        self._codigo = texto(codigo, "El código")

    @property
    def codigo(self) -> str:
        return self._codigo

    @abstractmethod
    def describir(self) -> str:
        """Cada entidad concreta debe devolver su propia descripción."""


class Cliente(Entidad):
    """Cliente con datos personales encapsulados y validados."""

    PATRON_CORREO = r"[^@\s]+@[^@\s]+\.[A-Za-z]{2,}"
    PATRON_NOMBRE = r"[A-Za-zÁÉÍÓÚáéíóúÑñÜü ]+"
    PATRON_TELEFONO = r"\d{10}"

    def __init__(self, codigo: str, nombre: str, correo: str, telefono: str):
        super().__init__(codigo)
        self.__nombre = self._validar_nombre(nombre)
        self.__correo = self._validar_correo(correo)
        self.__telefono = self._validar_telefono(telefono)

    @classmethod
    def _validar_nombre(cls, nombre: str) -> str:
        nombre = texto(nombre, "El nombre")
        if not 3 <= len(nombre) <= 80:
            raise DatosInvalidos("El nombre debe tener entre 3 y 80 caracteres.")
        if not re.fullmatch(cls.PATRON_NOMBRE, nombre):
            raise DatosInvalidos("El nombre solo puede contener letras y espacios.")
        return nombre

    @classmethod
    def _validar_correo(cls, correo: str) -> str:
        correo = texto(correo, "El correo")
        if not re.fullmatch(cls.PATRON_CORREO, correo):
            raise DatosInvalidos("El correo tiene un formato inválido.")
        return correo.lower()

    @classmethod
    def _validar_telefono(cls, telefono: str) -> str:
        telefono = texto(telefono, "El teléfono")
        if not re.fullmatch(cls.PATRON_TELEFONO, telefono):
            raise DatosInvalidos("El teléfono debe tener 10 dígitos.")
        return telefono

    @property
    def nombre(self) -> str:
        return self.__nombre

    @property
    def correo(self) -> str:
        return self.__correo

    @property
    def telefono(self) -> str:
        return "******" + self.__telefono[-4:]

    def describir(self) -> str:
        return f"Cliente {self.codigo} ({self.nombre})"


class Servicio(Entidad):
    """Clase abstracta que define la interfaz común de los servicios."""

    def __init__(self, codigo: str, tarifa: int | str | Decimal,
                 disponible: bool = True):
        super().__init__(codigo)
        self._tarifa = numero(tarifa, "La tarifa")
        if self._tarifa <= 0:
            raise DatosInvalidos("La tarifa debe ser positiva.")
        if not isinstance(disponible, bool):
            raise DatosInvalidos("La disponibilidad debe ser booleana.")
        self._disponible = disponible

    @property
    def disponible(self) -> bool:
        return self._disponible

    @abstractmethod
    def validar_duracion(self, horas: int) -> None:
        """Cada servicio define su propio rango de horas permitido."""

    @abstractmethod
    def costo_base(self, horas: int) -> Decimal:
        """Cada servicio define su propia fórmula de costo."""

    @overload
    def calcular_costo(self, horas: int) -> Decimal: ...

    @overload
    def calcular_costo(self, horas: int, impuesto: Decimal) -> Decimal: ...

    @overload
    def calcular_costo(self, horas: int, impuesto: Decimal,
                       descuento: Decimal) -> Decimal: ...

    def calcular_costo(self, horas, impuesto=None, descuento=None):
        """Implementación única de las tres variantes del cálculo.

        El descuento se aplica primero y luego el impuesto. Ambos se
        expresan como fracciones entre 0 y 1 (0.19 equivale a 19 %).
        """
        self.validar_duracion(horas)
        impuesto = Decimal(0) if impuesto is None else numero(impuesto, "El impuesto")
        descuento = Decimal(0) if descuento is None else numero(descuento, "El descuento")
        if not 0 <= impuesto <= 1 or not 0 <= descuento <= 1:
            raise DatosInvalidos("El impuesto y el descuento deben estar entre 0 y 1.")
        try:
            total = self.costo_base(horas) * (1 - descuento) * (1 + impuesto)
            total = total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        except ArithmeticError as causa:
            raise DatosInvalidos("No se pudo calcular el costo.") from causa
        if total < 0:
            raise DatosInvalidos("El costo calculado es inconsistente.")
        return total

    @staticmethod
    def validar_rango(horas: int, minimo: int, maximo: int) -> None:
        """Comprueba que las horas sean enteras y estén en el rango."""
        if type(horas) is not int or not minimo <= horas <= maximo:
            raise DatosInvalidos(
                f"La duración exige horas enteras entre {minimo} y {maximo}."
            )


class Sala(Servicio):
    """Reserva de salas: se cobra la tarifa por cada hora."""

    def describir(self) -> str:
        return f"Sala {self.codigo}"

    def validar_duracion(self, horas: int) -> None:
        self.validar_rango(horas, 1, 8)

    def costo_base(self, horas: int) -> Decimal:
        return self._tarifa * horas


class Equipo(Servicio):
    """Alquiler de equipos: tarifa por hora más un cargo de entrega."""

    CARGO_ENTREGA = Decimal("10000")

    def describir(self) -> str:
        return f"Alquiler de equipo {self.codigo}"

    def validar_duracion(self, horas: int) -> None:
        self.validar_rango(horas, 2, 24)

    def costo_base(self, horas: int) -> Decimal:
        return self._tarifa * horas + self.CARGO_ENTREGA


class Asesoria(Servicio):
    """Asesoría especializada: desde la segunda hora hay 20 % de descuento."""

    def describir(self) -> str:
        return f"Asesoría {self.codigo}"

    def validar_duracion(self, horas: int) -> None:
        self.validar_rango(horas, 1, 4)

    def costo_base(self, horas: int) -> Decimal:
        return self._tarifa + (horas - 1) * self._tarifa * Decimal("0.8")


class Estado(Enum):
    """Estados posibles de una reserva."""

    PENDIENTE = "pendiente"
    CONFIRMADA = "confirmada"
    CANCELADA = "cancelada"


class Reserva(Entidad):
    """Integra cliente, servicio, duración y estado."""

    def __init__(self, codigo: str, cliente: Cliente, servicio: Servicio,
                 horas: int):
        super().__init__(codigo)
        if not isinstance(cliente, Cliente) or not isinstance(servicio, Servicio):
            raise DatosInvalidos("La reserva requiere un cliente y un servicio válidos.")
        servicio.validar_duracion(horas)
        self._cliente = cliente
        self._servicio = servicio
        self._horas = horas
        self._estado = Estado.PENDIENTE
        self._total = None

    @property
    def estado(self) -> Estado:
        return self._estado

    @property
    def total(self) -> Decimal | None:
        return self._total

    def describir(self) -> str:
        return f"Reserva {self.codigo} {self.estado.value}"

    def procesar(self, impuesto=None, descuento=None) -> Decimal:
        """Verifica que la reserva se pueda confirmar y calcula su costo."""
        if self.estado is not Estado.PENDIENTE:
            raise OperacionInvalida("Solo se puede procesar una reserva pendiente.")
        if not self._servicio.disponible:
            raise ServicioNoDisponible(
                f"El servicio {self._servicio.codigo} no está disponible."
            )
        return self._servicio.calcular_costo(self._horas, impuesto, descuento)

    def confirmar(self, impuesto=None, descuento=None) -> Decimal:
        """Confirma la reserva solo si el procesamiento termina sin errores."""
        total = self.procesar(impuesto, descuento)
        self._total = total
        self._estado = Estado.CONFIRMADA
        return total

    def cancelar(self) -> None:
        """Cancela la reserva si todavía no está cancelada."""
        if self.estado is Estado.CANCELADA:
            raise OperacionInvalida("La reserva ya está cancelada.")
        self._estado = Estado.CANCELADA
