# Comparte tus resultados: el paquete de sesión

Has seguido [docs/03-observing-dns.md](03-observing-dns.md) y tienes un
registro DNS local. Esta página muestra cómo convertir uno o dos registros
en un único archivo HTML que puedes publicar en un foro, adjuntar a una
incidencia o enviar a un amigo, sin publicar la navegación de tu casa.

El paquete de sesión se genera **sin conexión** con
`scripts/build_session_pack.py` (Python 3.10+, sin dependencias, sin
peticiones de red). Los registros nunca salen de tu equipo.

## Qué contiene el informe - y qué no contiene nunca

La privacidad es la opción por defecto, no un ajuste; no hay opción para
relajarla:

- **Ningún dominio se nombra** salvo que lo indiques tú, una decisión
  deliberada por dominio, con `--name-domain`. Coincidir con una blocklist
  nunca es suficiente: una lista que aportes puede contener cualquier cosa,
  así que una coincidencia no prueba que un dominio sea público ni inocuo.
- **Contados, nunca nombrados:** todo lo demás aparece solo como agregado
  («N dominios únicos más, M consultas»), incluidas las coincidencias con la
  blocklist.
- **Nunca en el informe:** direcciones de clientes, marcas de tiempo,
  respuestas DNS y nombres de archivo.

Los recuentos agregados aún describen tu volumen de uso. Comparte el informe
solo donde eso sea aceptable y revísalo antes de publicarlo.

## Generar uno

```sh
python3 scripts/build_session_pack.py queries.json \
    --blocklist Blocked_Domains_AdGuard.txt \
    -o session-pack.html
```

- `queries.json` es cualquier registro que el clasificador lee: una
  exportación JSON de AdGuard Home, una copia nativa JSONL
  (`--format adguard-jsonl`), una copia de la base FTL de Pi-hole, o texto
  de dnsmasq/plano. En [docs/06-offline-example.md](06-offline-example.md)
  hay una entrada sintética para probar sin televisor.
- `--blocklist` (repetible) solo alimenta el recuento agregado de
  «coincidencias con la blocklist», para informar de cuánto tráfico cubren
  esas listas.
- `--name-domain ads.example.com` (repetible) es la única vía para que un
  dominio aparezca nombrado. Úsala para nombres públicos de
  publicidad/telemetría que quieras comentar; es tu decisión de
  divulgación, dominio a dominio.
- Añade `--before registro-antiguo.json` para una comparación antes/después,
  por ejemplo al activar el filtrado DNS. Los dos registros no son un
  experimento controlado: las diferencias pueden venir de qué se vio, de la
  caché del resolvedor o de la hora del día. La comparación no mide el
  efecto de la tele, del filtro ni de ningún ajuste, y el informe lo dice.
- El comando se niega a sobrescribir cualquier entrada (ambos registros y
  todas las listas) y escribe el informe de forma atómica.

## Compartirlo

Publica el HTML (o una captura) donde hables del proyecto, o adjúntalo al
abrir una incidencia de seguimiento como describe
[docs/05-first-hardware-session.md](05-first-hardware-session.md). Los
recuentos agregados dicen a otros dueños de VIDAA cuánto cubre una lista;
los dominios nombrados son temas de conversación que tú elegiste, con
evidencia de tu propio registro.

Si alguien pide el registro original, prefiere la exportación seudonimizada
de `scripts/redact_dns_log.py` antes que el archivo en crudo, y lee primero
sus avisos. Ninguna de las dos salidas es dato anónimo ni evidencia de
hardware; son ayudas para la conversación.

## Límites

- Las conclusiones cubren solo las consultas visibles en los registros; una
  tele apagada, o un nombre servido desde caché, no dejan rastro.
- Un recuento de coincidencias dice algo de las listas, no demuestra que
  ningún dominio sirviera anuncios en tu tele.
- No presentes el paquete como resultado de una sesión de ajustes: observa
  solo DNS.
