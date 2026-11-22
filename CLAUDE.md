# Ticket Rush · The Office IT — guía para Claude

Juego pixel personal, en vivo en **https://ticketrush.online**. Este archivo resume cómo se trabaja el
proyecto para poder seguirlo desde cualquier PC. Detalles técnicos en `README.md`; backlog en `PENDIENTES.md`
(léelo cuando pregunten "qué sigue" y marca ahí lo que se termine).

## Reglas de trabajo (acordadas con la dueña del proyecto)

- **Simple y divertido.** Nada de saltos ni botones extra.
- **La dificultad aprobada no se toca sin preguntar**: `CURVE`, velocidades, SLA, spawn, vidas, hitboxes.
  Después de cada cambio, revisa en el diff que esas líneas no cambiaron
  (grep: `CURVE|range|bossSp|sla|spawn|maxT|keep|BASE|HITBOX|MAX_LIVES|solids.push`).
- Si dice **"solo revisemos"**, se conversa primero, no se programa.
- **Probar siempre en celular vertical, celular horizontal y PC** antes de publicar.
- **Publicar después de probar; preguntar antes de commit + push** ("súbelo a git" = commit + push).
  Siempre `git fetch` antes de hacer commit (se trabaja desde varios PCs).
- `sprites/avatar_afro_pixel*.png` son pruebas: **nunca** se suben al repo. `promo/` tampoco, salvo que lo pida.
- Juega de forma anónima en la tabla: **nunca digas cuál registro es suyo**.

## Personajes

- **Protagonista**: la jugadora (afro, gafas, camisa cobalto, halo rosa).
- **Dani**: la compañera que le ayuda enamorando al jefe (lo distrae con corazones). No es la protagonista.
- **Jefe** (calvo, traje azul) → en Jefe de TI aparece el **Gerente** (cambio de color).
- **Señora del aseo** (desconecta cables → genera tickets), **sapo / chismosa** (desde Analista, le cuenta al
  jefe), **pasante del SENA** (se compra en la tienda en Jefe de TI; arregla tickets solo). Los tres van a color;
  el pasante es provisional (el jefe rejuvenecido, cara alegre, camiseta verde) hasta que Manuel haga su hoja.
- En Halloween (23 oct – 1 nov) usan los disfraces de `sprites/halloween/` (en gris: "son fantasmas").

## Construir

- Se edita `src/game_template.html` (y `src/sprites.config.json`, `src/sprite-*.js`). **Nunca** `ticket_rush.html`:
  se genera con `cd scripts && python construir_juego.py`.
- Sprites con Pillow, en este orden: `python preparar_chibi.py` → `python crear_provisionales.py` →
  `python crear_oficina_rangos.py` (este solo si cambian los muebles).
- Pruebas: `node tests/sprite-runtime.cjs`, `node tests/design-motion.cjs`, `node tests/octubre.cjs`.
- Sprite Studio de Manuel (solo local, no se publica): `python scripts/servidor_diseno.py` →
  http://127.0.0.1:8766/tools/sprites/ (ajusta recortes y animaciones, no colores).
- Para probar con la tabla: `STATS_STATIC=. STATS_DB=<base de prueba> python stats/stats_server.py`
  y abrir http://localhost:8095/ticket_rush.html. Para controlar el juego desde la consola, crea una copia
  `_prueba.html` que exponga `window.__g` y **bórrala al terminar**.

## Publicar en la VPS (Contabo, 66.94.101.47)

- Usuario `nelly`, con `sudo -n`. La llave SSH **no está en el repo**: cada PC usa su propia llave autorizada.
  El firewall limita intentos seguidos: si falla, esperar ~20 s y reintentar.
- Juego: `scp ticket_rush.html` a `/tmp` y `sudo -n install -m 644 /tmp/ticket_rush.html /var/www/juego/index.html`.
  Si cambia `intro/`, copiarla a `/var/www/juego/intro/`.
- Estadísticas: servicio `juego-stats` (Python + SQLite) en `/home/nelly/juego-stats/`, 127.0.0.1:8095.
  **Respaldar `stats.db` antes** (`sqlite3` `.backup` desde Python) y luego `sudo -n systemctl restart juego-stats`.
  Nueva temporada: `curl -X POST -d "" http://127.0.0.1:8095/stats/season` (en la VPS, después del respaldo).
- Caddy (`/etc/caddy/Caddyfile`, respaldar antes de editar, `caddy validate` y `systemctl reload caddy`):
  `ticketrush.online` sirve juego, `/api/*` y `/stats` (con clave); `www` redirige; la dirección vieja
  `juego.66.94.101.47.sslip.io` muestra `stats/mudanza.html` (copiado en `/var/www/juego-mudanza/index.html`)
  en `/` y redirige lo demás.
- El dominio se compró en GoDaddy el 29 oct 2026 por un año (vence el 29 oct 2027).

## Equipo

- **Manuel** (`valentinovergara`): arte y diseño, trabaja en ramas + PR. Pedidos abiertos en el issue #2.
- **Alex**: música 8 bits en su propia rama (ver PENDIENTES, sección 5). Falta su usuario de GitHub.
- Los PR se revisan antes del merge, buscando cambios en la dificultad.
