# Ruta 1: ajustes del televisor

[English](01-on-device-settings.md) | Español | [Inicio en español](../README.es.md)

Tiempo orientativo: unos 5 minutos con el mando. Los cambios de ajustes se
pueden revertir desde el mismo menú. **Borrar datos es una excepción: no se
puede deshacer.** No es necesario borrar datos para seguir esta guía.

Los nombres de los menús cambian entre versiones de VIDAA y marcas. Si no
coinciden, abre la sección de privacidad y busca opciones sobre información
de visionado, datos de uso, reconocimiento de contenido o publicidad.
Conservamos a continuación los nombres en inglés de las fuentes: no son
traducciones oficiales de los menús de tu televisor.

## 1. Desactivar el reconocimiento de contenido (ACR) y los datos de uso

VIDAA llama **Enhanced Viewing Service** al servicio de reconocimiento:
es optativo durante la configuración y reconoce lo que aparece en pantalla a
partir del audio. Los manuales oficiales de Hisense VIDAA U5, U6 y U9 lo sitúan aquí:

- **Settings → Advanced settings → Enhanced viewing settings → Enable
  Automatic Content Recognition → Off**. Confirma los dos avisos: "No, thank
  you" y "Yes, Decline". En VIDAA U5, el mismo ajuste está en
  **Settings → System → Advanced settings**.
- Otras guías lo sitúan en **Settings → System → Advanced settings →
  Privacy**. Los nombres dependen de la versión, la marca y el país. Si no
  encuentras Enhanced Viewing, puede que tu modelo no lo ofrezca.

En la misma zona, desactiva las opciones que existan para:

- **Device usage data**: datos de uso del dispositivo.
- **App usage data collection**: recogida de datos de uso de aplicaciones.

En VIDAA U9, Enhanced Viewing también incluye **Enable Personalized Ads**,
**Enable Content Recommendation** y **Enable Automatic Picture and Audio
Quality**. Los manuales muestran cómo desactivarlas ahí. En U5 se desactivan
junto con Automatic Content Recognition.

Qué hace: desactiva las opciones documentadas de reconocimiento de contenido
y datos de uso. El fabricante describe el reconocimiento como aplicable al
contenido de aplicaciones, HDMI y televisión. Su alcance y efecto exactos en
el televisor objetivo siguen sin verificar hasta que se registren en
[TESTING.md](../TESTING.md).

Fuentes: la [política de privacidad de VIDAA OS](https://www.vidaa.com/os-privacy-policy/)
describe cómo rechazar Enhanced Viewing Service / ACR desde los ajustes del
dispositivo; la [guía de VIDAA de justatv.eu](https://justatv.eu/en/guides/cleaning-up-a-hisense-television-with-vidaa)
y la [guía de ACR de velmo.one](https://velmo.one/guides/turn-off-acr-hisense-tv/)
aportan rutas de menú; y la [guía de Clean Your TV para sistemas no Android](https://cleanyour.tv/not-android)
recoge las rutas y los nombres exactos de los manuales oficiales de Hisense
VIDAA U5/U6/U9. La guía inglesa indica que se comprobó esa fuente por última
vez el 26 de octubre de 2026. Los modelos europeos pueden usar nombres distintos
a los de los manuales estadounidenses.

## 2. Desactivar la publicidad personalizada y restablecer el identificador

El manual de VIDAA U9 indica **Settings → System → Advanced settings →
Personalised Ads → Off**, y **Reset Ads ID** en el mismo menú. Puede que los
menús más antiguos no incluyan estas opciones.

Seguirán pudiendo aparecer anuncios. La opción de personalización documentada
controla si se eligen a partir de un perfil sobre ti, no cuántos aparecen.
Su efecto no se ha verificado en el televisor objetivo.

## 3. Retirar los consentimientos que no quieras mantener

Los manuales sitúan estas opciones en **Settings → Support → Disclaimer and
Privacy** y después **Data Sharing, Privacy and EULA** (VIDAA U9), **EULA and
Other Policy and Services** (U6), o directamente en ese menú sin submenú (U5).
Rechaza los consentimientos que no quieras mantener. Puedes aceptarlos de
nuevo desde el mismo menú.

Ten en cuenta dos efectos distintos:

- Desmarcar el consentimiento de **VIDAA Account** cierra la sesión de la cuenta.
- **Remove User Data**, en ese mismo menú, borra los datos de uso guardados en
  el televisor y en la nube. **Ese borrado no se puede deshacer.** Lee el aviso
  antes de confirmar; no lo confundas con un interruptor reversible.

## 4. Voz sin pulsar el mando (opcional)

Si el televisor escucha "Hey VIDAA" o "Alexa", los manuales indican
**Settings → System → Voice Service → VIDAA Voice or Amazon Alexa → Hands-Free
Off** en U9, o **Amazon Alexa → Built-in Microphone Off** en U5.

Los televisores con reconocimiento de voz a distancia también tienen un
interruptor físico de micrófono. El manual impreso indica dónde está.
El botón de micrófono del mando sigue funcionando en ambos casos.

## 5. Cuenta VIDAA

La guía inglesa indica que el televisor funciona sin cuenta VIDAA y que esta
se necesita para instalar aplicaciones desde la tienda VIDAA. Si no usas la
tienda, cerrar la sesión elimina un identificador asociado a lo que ves.
Comprueba qué funciones de tu modelo dependen de la cuenta antes de cerrarla.

## 6. Aplicaciones de la pantalla de inicio

Selecciona una aplicación en la pantalla de inicio. Si el sistema ofrece un
icono de papelera, permite quitar esa aplicación. La guía inglesa distingue
estas aplicaciones de las del sistema o incluidas por acuerdos comerciales,
que no se pueden quitar desde ese procedimiento.

Las aplicaciones se pueden reordenar: lleva al final las que no uses.
Esto no es una instrucción para instalar otro launcher ni modificar el sistema.

## 7. Después de cada actualización

Algunas actualizaciones de VIDAA restablecen opciones de privacidad o vuelven
a pedir consentimiento. Aceptar deprisa con el mando puede activarlas de
nuevo. Después de una actualización, dedica unos 30 segundos a revisar la
sección de privacidad.

## Estado en el Toshiba 50UV1553DB

Los nombres exactos de los menús no están verificados en este modelo hasta
que se registre la primera sesión física en [TESTING.md](../TESTING.md).
Una ruta documentada no demuestra que aparezca o tenga el mismo efecto en tu
televisor. Para registrar una comprobación, sigue el
[protocolo de primera sesión](05-first-hardware-session.es.md).

Adaptación en español de la guía inglesa en `dc87d39`, 14 de noviembre de
2026. No añade nuevas pruebas en un televisor ni una revisión externa de las fuentes.
