# Preguntas frecuentes

[English](FAQ.md) | [Inicio en español](README.es.md)

Estas respuestas distinguen lo comunicado por otras personas de lo registrado
en el proyecto. No se han hecho pruebas nuevas para esta traducción. Las guías
detalladas enlazadas siguen en inglés.

## ¿Los televisores VIDAA muestran anuncios?

Hay informes de recomendaciones, promociones, vistas previas automáticas y
canales VIDAA Free. Algunos propietarios también comunican anuncios de vídeo
al encender o cambiar de entrada. Lo que aparece depende del modelo, la
región y el firmware; no todas las pantallas se comportan igual.

## ¿Se pueden quitar?

No hay un interruptor que lo elimine todo.

- La [ruta de ajustes](docs/01-on-device-settings.md) documenta opciones de
  personalización, consentimiento y reconocimiento de contenido. Sus efectos
  todavía requieren comprobación en cada televisor.
- El [filtrado DNS](docs/02-dns-filtering.md) puede reducir promociones y
  tráfico. Un propietario de un Hisense 65A67H comunicó un inicio más limpio
  con YouTube y Netflix funcionando. No demuestra que desaparezca toda la
  publicidad ni que funcione igual en Toshiba.
- Para anuncios al encender o cambiar de entrada, primero
  [observa las peticiones](docs/03-observing-dns.md). No bloquees dominios
  por su nombre sin comprobar qué cambia.

## ¿Hace falta una cuenta VIDAA?

Las rutas de ajustes y DNS de este proyecto no necesitan una cuenta VIDAA.
Los requisitos de cada aplicación, tienda o servicio son distintos y pueden
cambiar; consulta lo que pida tu modelo y el servicio que quieras usar.

## ¿Qué datos recoge el televisor?

La [política de VIDAA](https://www.vidaa.com/os-privacy-policy/) describe datos
de dispositivo y de uso. La guía de ajustes explica las opciones documentadas
de consentimiento y personalización. Para saber qué dominios consulta tu
televisor, usa la ruta de observación. Un registro DNS no permite leer por sí
solo todo el contenido que transmite ni demuestra que haya dejado de recoger datos.

## ¿Puedo usar ADB, root o cambiar el launcher?

No con este proyecto. Aquí solo cubrimos ajustes normales y filtrado DNS.
Hay Hisense con Android y proyectos separados de cambios nativos en VIDAA,
pero eso no los convierte en métodos admitidos aquí. Identifica primero el
sistema y la función en la [guía de compatibilidad](docs/07-compatibility.md).

## ¿Puede dejar de funcionar YouTube, Netflix o Prime Video?

Sí, bloquear un dominio compartido puede romper funciones necesarias.
YouTube y Netflix constan como funcionando en un informe DNS del 65A67H,
no como garantía para cualquier firmware o lista futura.

La lista original mantiene activas seis reglas de recomendaciones con un
problema comunicado de miniaturas y partes de la interfaz de Prime Video.
El autor documenta ese compromiso y una variante de Owen3H que las desactiva.
Consulta la [tabla por aplicación](docs/08-app-compatibility.md) y el
[procedimiento de recuperación](TROUBLESHOOTING.md#an-app-stopped-loading-after-enabling-the-blocklist).
No desactives toda la lista ni permitas dominios a ciegas si puedes aislar la causa.

## ¿Qué televisores están cubiertos?

Las guías se dirigen a VIDAA no Android. Hisense es la familia más documentada;
solo hay una sesión DNS comunicada por un propietario. El Toshiba 50UV1553DB
sigue pendiente de su primera prueba registrada. Consulta las
[fichas por modelo](docs/tv/README.md), no solo la marca o el nombre comercial.

## ¿Puedo usar solo una lista en Pi-hole o AdGuard Home?

Sí, la [guía DNS](docs/02-dns-filtering.md) explica cómo suscribirse y limitar
el filtro al televisor. Comprueba el formato admitido por tu filtro. Las listas
no tienen todas las mismas reglas ni excepciones; no añadas varias para tener
un número mayor de bloqueos. Observa primero el resultado de una lista.

## ¿Por qué hay páginas en inglés?

Esta primera versión española cubre la entrada y las preguntas frecuentes.
Las guías técnicas y los informes siguen en inglés. Esta página se revisó
frente a FAQ.md de `46ec5d1`, 14 de noviembre de 2026. Las actualizaciones de
pasos, riesgos y pruebas deben revisar ambas versiones; una traducción no
convierte una afirmación pendiente en un resultado probado.
