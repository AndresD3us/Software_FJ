# Software FJ: sistema de gestión de clientes, servicios y reservas

Proyecto de **Programación 213023, Fase 4: Prácticas simuladas**, Universidad Nacional Abierta y a Distancia (UNAD).

**Autor:** Andres Felipe Benavides Gil (trabajo individual)

Aplicación de consola en Python orientada a objetos. Gestiona clientes, servicios (salas, alquiler de equipos y asesorías) y reservas **sin base de datos**: todo se guarda en objetos y listas en memoria. El único archivo que escribe el programa es el log de eventos y errores.

## Ejecución

Requiere Python 3.10 o superior y no usa librerías externas.

```sh
python main.py
```

La consola muestra 25 casos y termina con `Desviaciones: 0`. Cada ejecución agrega sus eventos a `software_fj.log`, en la misma carpeta. El archivo `software_fj_ejemplo.log` es una copia de una ejecución completa, para revisarla sin correr el programa.

## Estructura

| Archivo | Contenido |
|---|---|
| `modelos.py` | Excepciones propias, clase abstracta `Entidad`, `Cliente`, clase abstracta `Servicio`, servicios `Sala`, `Equipo` y `Asesoria`, y `Reserva` con sus estados. |
| `gestion.py` | Clase `Gestion`: listas internas, registro, búsqueda, reservas y cancelaciones. |
| `main.py` | Simulación de 25 operaciones y configuración del log. |

## Cómo se cumple cada requisito

| Requisito | Dónde está |
|---|---|
| Clase abstracta general | `Entidad` (con `ABC` y `@abstractmethod describir`) |
| Cliente con validaciones y encapsulación | `Cliente`: atributos privados `__nombre`, `__correo` y `__telefono`, que solo se leen mediante propiedades. Valida nombre, correo y teléfono. |
| Servicio abstracto y tres servicios | `Servicio` → `Sala`, `Equipo`, `Asesoria`. Cada uno sobrescribe `describir`, `validar_duracion` y `costo_base`. |
| Polimorfismo | `calcular_costo` llama a `costo_base` y `validar_duracion`, que cambian según el servicio. |
| Método sobrecargado | `Servicio.calcular_costo` tiene tres firmas declaradas con `@overload`: `(horas)`, `(horas, impuesto)` y `(horas, impuesto, descuento)`. |
| Reserva | `Reserva`: `procesar`, `confirmar` y `cancelar`, con estados `PENDIENTE`, `CONFIRMADA` y `CANCELADA`. |
| Excepciones personalizadas | `ErrorSistema`, `DatosInvalidos`, `ParametroFaltante`, `OperacionInvalida`, `ServicioNoDisponible` |
| `try/except` | `numero()`, `Servicio.calcular_costo`, `main.ejecutar` |
| `try/except/else` | `Gestion.reservar`, `main.ejecutar` |
| `try/except/finally` y `try/finally` | `main.ejecutar` (bucle de casos) y `main.main` (cierre del log) |
| Encadenamiento (`raise ... from`) | `numero()`, `Servicio.calcular_costo`, `Gestion.reservar` |
| Log de eventos y errores | `software_fj.log`, con la traza completa de cada error |
| Al menos 10 operaciones | 25 casos: 11 válidos y 14 errores controlados |

## Reglas de la simulación

- **Sala:** de 1 a 8 horas; se cobra la tarifa por cada hora.
- **Equipo:** de 2 a 24 horas; tarifa por hora más un cargo de entrega de COP 10.000.
- **Asesoría:** de 1 a 4 horas; la primera hora completa y desde la segunda el 80 % de la tarifa.
- El descuento se aplica antes del impuesto. Ambos se expresan como fracciones de 0 a 1 (el IVA del 19 % es `0.19`).
