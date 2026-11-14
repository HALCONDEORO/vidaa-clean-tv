# Empieza aquí: de "tengo un televisor VIDAA" a una primera acción

[English](00-start-here.md) | Español | [Inicio en español](../README.es.md)

Esta página te ayuda a elegir entre las guías. Dedica unos diez minutos a
leer y después elige una acción concreta que puedas revertir. No necesitas
root, ADB, cambiar el firmware ni comprar nada.

## Paso 1: identifica el equipo exacto, unos 5 minutos en el televisor

Abre el menú normal de información y anota tres datos:

- **Modelo**: la cadena completa, no solo "Hisense" o "Toshiba".
- **Región**: el país para el que está configurado el televisor.
- **Firmware**: la cadena completa de compilación.

Los nombres de los menús cambian entre modelos. No entres en un menú de
servicio. La marca no identifica el sistema operativo: algunos equipos con
marca VIDAA usan Android, y su procedimiento de limpieza es distinto al de
este proyecto. Si no sabes con seguridad qué tienes, lee
[Compatibilidad por función, no por marca](07-compatibility.es.md) antes de
cambiar nada.

## Paso 2: elige una ruta

Cada ruta es independiente. Empieza por la ruta 1 y añade las demás cuando
estés preparado. "Reversible" significa que puedes recuperar el ajuste
anterior desde el mismo menú. **No incluye borrar datos de usuario: ese
borrado no se puede deshacer y no es necesario para la primera sesión.**

| Ruta | Qué hace | Qué necesitas | Tiempo orientativo |
|---|---|---|---|
| [1: ajustes del televisor](01-on-device-settings.es.md) | Desactivar el reconocimiento de contenido, la personalización de anuncios y los consentimientos que no quieras mantener | Solo el mando | Unos 5 minutos; cambios de ajustes reversibles |
| [2: filtrado DNS](02-dns-filtering.md), en inglés | Bloquear la resolución de los dominios incluidos en el filtro de publicidad y telemetría | Un ordenador siempre encendido, una Raspberry Pi o acceso al router | Unos 30 minutos |
| [3: observar primero el DNS](03-observing-dns.md), en inglés | Ver qué dominios consulta el televisor para basar las reglas en observaciones | El mismo equipo que para la ruta 2 | Una tarde o noche de uso |
| [4: control local por MQTT](04-local-control-mqtt.md), en inglés | Notas preparatorias sobre control remoto local | Nada por ahora: **sin probar en los equipos cubiertos aquí** | Solo lectura |

La ruta 4 es preparación, no una función verificada: ningún modelo cubierto
por el proyecto tiene todavía una sesión MQTT comprobada. No es un paso que
debas ejecutar para completar esta guía.

## Paso 3: sigue una ruta y registra lo que ocurre

Sigue la página de la ruta que hayas elegido. Mientras trabajas, mantén
abierta una copia de la
[plantilla del registro de sesión](https://github.com/HALCONDEORO/vidaa-clean-tv/blob/main/docs/templates/session-log.md)
y rellénala con lo que ocurrió: qué esperabas, qué viste y qué devolviste a
su estado anterior. El [protocolo de primera sesión](05-first-hardware-session.es.md)
explica por qué importa tanto el registro: tus menús y tu firmware son la
evidencia que necesitan otros propietarios del mismo modelo.

El registro cumplimentado se puede convertir en filas para
[TESTING.md](../TESTING.md), ejecutando el conversor sin `--json`, o en un
informe que puedas revisar antes de compartir. Para generar y validar el
informe JSON, usa estos dos comandos sin conexión desde la raíz del repositorio:

```sh
python3 scripts/session_to_testing.py your-log.md --json > your-report.json
python3 scripts/validate_model_report.py your-report.json
```

`your-log.md` es tu copia cumplimentada de la plantilla; `your-report.json`
es el archivo de salida que eliges. Los comandos no añaden por sí solos el
resultado al registro público del proyecto.

El validador rechaza patrones comunes de identificadores en el informe JSON
que inspecciona: direcciones IP y MAC, correos, nombres de equipo locales,
horas exactas y cadenas hexadecimales largas. **Detectar patrones no es
anonimizar.** No cubre todos los datos personales y no examina el texto que
rodea al bloque JSON. Revisa tú mismo todos los textos y fotos antes de
compartirlos.

## Paso 4: comprueba tus reglas antes de usarlas

Si mantienes tu propia lista de bloqueo o un suplemento, valídalo antes de
suscribir el filtro del televisor a esa lista:

```sh
python3 scripts/validate_blocklist.py your-list.txt
```

`your-list.txt` es el archivo local que quieres comprobar. El validador
rechaza reglas mal formadas, duplicados y reglas ya cubiertas por un dominio
superior. La opción `--upstream` permite contrastarlo con una copia local de
la [lista a la que se suscribe el proyecto](02-dns-filtering.md), para detectar
reglas ya cubiertas por ella.

La validación comprueba la sintaxis, no que la lista bloquee lo que buscas
ni que sea segura para todas las aplicaciones. Eso exige observar tu propio
televisor y sus funciones, como explica la ruta 3. Si la red es compartida,
no cambies su DNS sin el acuerdo de las personas que puedan verse afectadas.

## Qué no te pedirá esta web

- No necesitas cuenta ni iniciar sesión en esta web. Es documentación
  estática alojada en GitHub Pages; el proyecto no añade analítica ni scripts
  de seguimiento.
- No necesitas menús de servicio, root, ADB ni cambiar el firmware.
- No necesitas compras ni suscripciones de pago. Las herramientas son
  programas Python que funcionan sin conexión.
- No se pide confianza a ciegas. Comprueba qué está verificado, por quién y
  en qué modelo, y qué sigue siendo desconocido. Si una página no lo
  demuestra, no lo des por verificado.

También puedes consultar el [inicio en español](../README.es.md) y las
[preguntas frecuentes](../FAQ.es.md). Los ajustes, la primera sesión y la
compatibilidad por función tienen guía en español; otras guías técnicas e
informes siguen en inglés.

Adaptación de la fuente inglesa de `114b8ef`, con la aclaración de salida
Markdown de `0f0a9d3`, 14 de noviembre de 2026. No añade nuevas pruebas en un
televisor ni una revisión externa de las fuentes.
