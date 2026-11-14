# Comprueba la compatibilidad por función, no por marca

[English](07-compatibility.md) | Español | [Inicio en español](../README.es.md)

Que un televisor lleve la marca Hisense o Toshiba no basta para elegir un
método de limpieza. Aunque dos modelos usen VIDAA, un resultado DNS en uno
no verifica los menús de ajustes, el control remoto local ni una modificación
de software en el otro.

## Identifica el televisor antes de cambiar nada

1. Lee el modelo exacto, la región y la cadena completa de firmware o
   compilación en el menú normal de información. Los nombres cambian entre
   modelos. No entres en un menú de servicio.
2. Comprueba el sistema operativo en el manual del modelo o en la página de
   soporte del fabricante. Una aplicación con marca VIDAA o el nombre de un
   paquete no demuestran cuál es el sistema. El
   [directorio Hisense de Clean Your TV](https://cleanyourtv.wiki/tv/hisense/)
   distingue los VIDAA no Android de los Hisense basados en Android,
   incluidos modelos para China con marca VIDAA.
3. Elige la función de la tabla. Si aún no puedes identificar el equipo,
   déjalo sin cambios y reúne primero la información que falta. El
   [soporte oficial de VIDAA](https://www.vidaa.com/support/) remite las
   consultas sobre el hardware al fabricante del televisor.

## Qué cubre la evidencia actual

| Función | Evidencia disponible | Qué no demuestra |
|---|---|---|
| Ajustes de privacidad del televisor | Rutas de menú con fuentes en la [ruta 1](01-on-device-settings.es.md) | No hay ninguna sesión completa de ajustes registrada aquí. Que el firmware tenga un nombre parecido no verifica la ruta ni su efecto. |
| Filtrado DNS | [Aportación de OliverS45](https://github.com/HALCONDEORO/vidaa-clean-tv/pull/31), recogida en [TESTING.md](../TESTING.md): sesión comunicada por el propietario de un Hisense 65A67H, V0000.09.09G.P0930, el 8 de noviembre de 2026 | No se registró la región. No se analizó una exportación del registro DNS original. No es una prueba en Toshiba, de los ajustes ni de todas las aplicaciones de vídeo. |
| Reglas DNS del proyecto original | [Lista de ipanalytics](https://github.com/ipanalytics/Hisense-VIDAA-DNS-Clean-TV-Blocklist): observaciones en Hisense y candidatos inferidos identificados como tales | La presencia o el nombre de un dominio no demuestran por sí solos su finalidad. Otras regiones o versiones de firmware pueden usar otros dominios. Bloquear uno compartido puede romper funciones necesarias. |
| Mando local por MQTT | [warrenrees/ha_vidaatv](https://github.com/warrenrees/ha_vidaatv) describe el emparejamiento por PIN y soporte para Hisense/VIDAA con MQTT y algunos Toshiba | No se ha probado aquí en el Toshiba 50UV1553DB. Enviar teclas de mando no demuestra que se puedan gestionar paquetes ni autoriza cambios de software. Consulta la [nota de investigación](04-local-control-mqtt.md), en inglés. |
| Limpieza de paquetes por ADB | Clean Your TV documenta por separado los modelos Android y los VIDAA no Android | No apliques la lista de paquetes de un modelo Android a un VIDAA no Android. Este proyecto no ofrece un procedimiento ADB. |

Son tipos de evidencia distintos, no una lista de equipos certificados.
Las [fichas por modelo](tv/README.md) siguen en inglés. Una actualización de
firmware es motivo para volver a comprobar los pasos afectados, no para
copiar los resultados de otro modelo.

## Proyectos de Home nativo o launcher

[nineodernein/hisense-vidaa-clean-home](https://github.com/nineodernein/hisense-vidaa-clean-home)
comunica una integración nativa de Home en un equipo MTK9602 / VIDAA U9 /
P0930. Su README distingue esa prueba original de su paquete público
generalizado, que, según indica, no se ha instalado como nueva compilación
en el televisor de referencia. Son afirmaciones de su autor, no pruebas de
este proyecto.

Es una vía distinta de modificación de software. Este proyecto no la
importa, instala ni recomienda como paso de limpieza; tampoco está cubierta
por sus instrucciones para volver al estado anterior. Compartir el nombre
VIDAA, la etiqueta U9 o el sufijo P0930 no basta para demostrar compatibilidad.
Aquí nos limitamos a ajustes normales y filtrado DNS: sin cambios de firmware,
de Home nativo ni de menús de servicio.

## Informa de una función cada vez

Usa la [guía para informar de un modelo](../CONTRIBUTING.md#reporting-a-new-model),
en inglés, y el [protocolo de primera sesión](05-first-hardware-session.es.md).
Incluye modelo, región, cadena completa de firmware, paso exacto, resultado
esperado, resultado observado y cambios revertidos. Indica también qué
funciones no se probaron. Un informe del propietario es útil sin presentarlo
como una prueba física independiente.

La página inglesa indica una revisión de fuentes del 14 de noviembre de
2026. Esta traducción no supone una nueva revisión externa ni nuevas pruebas
en un televisor. Redacción original del proyecto: no se han copiado código,
listas de bloqueo ni archivos de dispositivos de terceros.
