# La primera sesión en el televisor

[English](05-first-hardware-session.md) | Español | [Inicio en español](../README.es.md)

Protocolo para la primera sesión real de ajustes en el televisor objetivo:
Toshiba 50UV1553DB, VIDAA. Hasta completarla y registrarla, nada de este
repositorio se considera verificado en ese modelo. Necesitas el mando,
estar delante del televisor y unos 15 minutos.

## Antes

- Lee la [guía de compatibilidad](07-compatibility.es.md) y confirma modelo,
  región y sistema operativo antes de tomar pasos de otro televisor.
  Limita la sesión a la función que vayas a comprobar.
- Anota la versión de firmware. Los manuales oficiales de VIDAA indican
  **Settings → Support → About**, o **Settings → Support → System Info →
  Version** en modelos más antiguos. Conservamos los nombres ingleses de
  las fuentes; no son nombres oficiales en español. Apunta la versión en
  el registro de la sesión.
- Anota qué opciones de privacidad existen y su texto exacto. Los nombres
  varían; el registro necesita los de tu televisor, no los de la guía.

## Durante: solo ruta 1, ajustes del televisor

1. Sigue la [guía de ajustes](01-on-device-settings.es.md) paso a paso.
2. Después de cada cambio, anota el nombre de la opción, el valor elegido y
   cualquier resultado inesperado. Conserva el valor anterior para poder
   recuperarlo.
3. Haz una foto de las pantallas cuyo texto sea distinto al de la guía.
   Esas fotos sirven para corregir la documentación. Antes de compartirlas,
   revisa que no muestren cuentas, identificadores u otros datos privados.

Esta sesión comprueba cambios reversibles de ajustes. No borres datos de
usuario: la opción **Remove User Data** descrita en la guía es irreversible.

## Después

- Confirma que el televisor sigue funcionando con normalidad: carga la
  pantalla de inicio, abre una aplicación, por ejemplo YouTube, y comprueba
  una entrada HDMI.
- Completa el registro de sesión de [TESTING.md](../TESTING.md): fecha,
  firmware, cada paso, resultado esperado, resultado observado y si se
  revirtió el cambio (sí/no).
- Solo entonces pueden dejar de figurar como "sin verificar" las
  afirmaciones concretas comprobadas en ese modelo. La sesión no valida
  funciones que no hayas probado.

## Volver al estado anterior

Los cambios de ajustes de esta sesión se revierten desde el mismo menú.
Si algo se comporta de forma extraña, revierte primero ese cambio y anótalo
en el registro.

## Qué queda fuera de esta sesión

No incluye filtrado DNS, cambios en el router ni experimentos de
emparejamiento MQTT. Son decisiones separadas y necesitan su propia sesión
y sus propias entradas en el registro.

Adaptación en español de la guía inglesa en `dc87d39`, 14 de noviembre de
2026. No añade nuevas pruebas en un televisor ni una revisión externa de las fuentes.
