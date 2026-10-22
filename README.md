# Ticket Rush · The Office IT

Juego de oficina en pixel art: eres la nueva de TI y tienes que resolver los tickets de todo el mundo antes de que se venza el SLA, mientras esquivas al jefe y su "cosita rápida".

**Jugar:** https://juego.66.94.101.47.sslip.io (funciona en computador y celular; en celular se ve mejor horizontal).

---

## Cómo se juega

| | Computador | Celular |
|---|---|---|
| Moverse | Flechas o WASD | Flechas en pantalla |
| Arreglar / resolver / aprobar | Mantener ESPACIO o E | Mantener el botón redondo |

- Cada **!** amarillo es un ticket. Quédate al lado y mantén el botón hasta que se llene la barra morada. La barra de abajo es el tiempo que queda antes de que se venza el **SLA**.
- Si se vence un SLA o **el jefe te alcanza**, pierdes una vida (empiezas con 3, máximo 5).
- **☕ La cafetera** (pared del fondo) da turbo por 6 s: caminas y arreglas más rápido. Cuando tiene vapor y luz verde está lista.
- **♥ Dani**, la compañera, pasea por la oficina. Si el jefe pasa cerca de ella, se queda embobado unos segundos con corazones y deja de perseguirte. Truco: llévale el jefe.
- **🆘 Ayuda:** el botón AYUDA abre la Guía del turno (y pausa la partida). La primera vez que alguien entra, la guía se abre sola.
- **Combos:** resolver tickets seguidos (menos de 5 s entre uno y otro) da más puntos.

### Rangos

Empiezas de practicante ("DÍA 1") y asciendes resolviendo tickets. Cada ascenso pasa el tiempo ("1 AÑO DESPUÉS", "5 AÑOS DESPUÉS", con la partida en pausa mientras se ve el cartel), da una vida y cambia lo que haces:

| Rango | Desde | Botón | Te persigue | Ejemplo de ticket |
|---|---|---|---|---|
| Practicante | 0 tickets | ARREGLAR | El jefe | "Olvidé mi clave (otra vez)" |
| Analista | 10 tickets | RESOLVER | El jefe | "El antivirus bloqueó la nómina" |
| Jefe de TI | 25 tickets | APROBAR | **El Gerente** | "Explicar por qué se pidió otra RAM" |

La dificultad sube poco a poco, ticket a ticket, y se estabiliza a los 45 tickets (tabla `CURVE` en `src/game_template.html`):

| Tickets | El jefe te ve a | Velocidad del jefe* | Tiempo de los tickets | Nuevo ticket cada | Máx. abiertos | Avance que conservas si te alcanza |
|---|---|---|---|---|---|---|
| 0 | 120 px | 50 | ×1,40 | 8 s | 3 | 100 % |
| 10 | 160 px | 60 | ×1,15 | 7 s | 4 | 50 % |
| 25 | 196 px | 67 | ×1,00 | 6 s | 5 | 0 % |
| 45+ | 230 px | 95 | ×0,75 | 3,5 s | 7 | 0 % |

\* Tú caminas a 125, así que el jefe nunca es más rápido que tú.

### Competencia

- Al jugar por primera vez se pide un **apodo opcional** (se puede jugar como anónimo).
- **🏆 Tabla de líderes** con dos pestañas: **esta semana** (se reinicia el lunes, hora Colombia) e **histórico**. Una línea por persona con su mejor puntaje.
- El #1 de la semana es el **🏅 Empleado de la semana** y su nombre aparece en un cuadro en la pared de la oficina. El #1 histórico es la **🏆 Leyenda de TI**.
- Al perder: récord personal, "¡Le ganaste a …!" y tu puesto de la semana.

---

## Cómo está hecho

Sin frameworks ni dependencias en el navegador: un solo archivo HTML con un `<canvas>` de 768×480 (casillas de 48 px), CSS y JavaScript a mano. Las fuentes son Press Start 2P y VT323 (Google Fonts).

```
 Navegador                          VPS
 ┌─────────────────────┐           ┌──────────────────────────────────────┐
 │ ticket_rush.html    │  HTTPS    │ Caddy                                │
 │  canvas + JS        │──────────▶│  /          → /var/www/juego (HTML)  │
 │  sprites en base64  │           │  /api/*     → juego-stats :8095      │
 │                     │           │  /stats     → juego-stats (con clave)│
 └─────────────────────┘           │                                      │
                                   │ juego-stats (systemd)                │
                                   │  Python estándar + SQLite            │
                                   └──────────────────────────────────────┘
```

### El juego (`src/game_template.html`)

Todo el juego está en este archivo. Las partes principales, en orden:

- **Mundo y colisiones:** escritorios, servidor, impresora, cafetera y materas. Cada objeto tiene una caja de choque ajustada a lo que se ve (solo su base), y hay **ayuda en las esquinas**: si rozas un borde por pocos píxeles, el personaje se desliza solo.
- **Dificultad:** `RANKS` (rangos) y `CURVE` (curva de dificultad), interpolada con `diff()`.
- **Textos:** `TEXTS` (tickets por rango) y `BOSSES` (frases del jefe y del Gerente).
- **Actualización y dibujo:** `update()` mueve todo; `render()` dibuja ordenando por profundidad (el que está más abajo se dibuja encima).
- **Estadísticas y tabla:** `track()` manda visitas y partidas al servidor con un id anónimo por navegador; si el servidor no responde, el juego sigue normal. Si abres el HTML como archivo local, no manda nada.

### Los personajes (`scripts/` → `sprites/`)

Los sprites se **dibujan con código** (Python + Pillow), píxel por píxel, sin imágenes externas:

| Script | Genera | Notas |
|---|---|---|
| `crear_avatar.py` | `avatar_48.png` | La jugadora |
| `crear_jefe.py` | `boss_48.png` | El jefe |
| `crear_gerente.py` | `gerente_48.png` | **Variante de paleta del jefe**: no se redibuja, solo se cambian colores. Correr después de `crear_jefe.py` |
| `crear_companera.py` | `companera_48.png` | Sombras con matiz violeta y contorno de color |
| `crear_companero.py` | `partner_48.png` | Todavía no sale en el juego |
| `construir_juego.py` | `ticket_rush.html` | Mete los sprites (en base64) dentro del template |

Los `*_preview.png` son versiones grandes para ver el dibujo.

**Animaciones chibi (de Manuel).** Los personajes del juego hoy usan las hojas de `arte/chibi/` (generadas con IA por Manuel: 4 columnas × 3 filas, caminar, correr y acción especial). `scripts/preparar_chibi.py` las limpia (bordes nítidos, sin transparencias a medias, paleta reducida, pies alineados, misma escala para todos) y genera `sprites/chibi_<nombre>.png`: una tira de 12 cuadros de 56 px. El Gerente sale del jefe cambiando colores. Los sprites de 48 px de arriba quedan de respaldo por si las tiras no cargan.

| Personaje | Camina | Corre | Acción especial |
|---|---|---|---|
| Jugadora | al moverse | con turbo ☕ | celebra al ascender; nerviosa y sudando mientras arregla (hoja extra `jugadora_arreglando.webp`) |
| Jefe / Gerente | paseando | persiguiendo o huyendo | se enoja al alcanzarte |
| Dani | paseando | — | se enamora cuando distrae al jefe |
| Sapo | (preparado, todavía no sale en el juego) | | chismea |

Para actualizar las animaciones: reemplazar las hojas en `arte/chibi/`, correr `python preparar_chibi.py` y luego `python construir_juego.py` (desde `scripts/`).

### Estadísticas (`stats/`)

`stats_server.py` es un servicio pequeño con solo la librería estándar de Python y SQLite:

| Ruta | Para qué |
|---|---|
| `POST /api/visit`, `/api/start`, `/api/end` | El juego avisa visitas, inicios y finales (o abandonos) de partida |
| `POST /api/name` | Guardar el apodo (filtro de groserías; responde 422 si no se permite) |
| `GET /api/board` | Tabla de líderes pública |
| `GET /stats` | Página de estadísticas para quien administra el juego (con usuario y clave) |

**Privacidad:** no se guardan IPs ni nombres reales; cada navegador tiene un id al azar y el apodo es opcional. **Contra trampas:** el servidor limita los puntajes a lo que es posible (máx. un ticket cada 2 s y 80 puntos por ticket).

`juego-stats.service` es la unidad de systemd con la que corre en la VPS.

---

## Probarlo en tu computador

Necesitas Python 3 y, para los sprites, Pillow:

```bash
pip install pillow
```

**Solo el juego:** genera el HTML y ábrelo con doble clic (así no manda estadísticas):

```bash
cd scripts
python construir_juego.py
```

**El juego con tabla de líderes y estadísticas**, con una base de datos de prueba local (desde la carpeta del repo):

```bash
STATS_STATIC=. STATS_DB=stats-local.db python stats/stats_server.py
```

En PowerShell:

```powershell
$env:STATS_STATIC="."; $env:STATS_DB="stats-local.db"; python stats/stats_server.py
```

Abre http://127.0.0.1:8095 para jugar y http://127.0.0.1:8095/stats para ver las estadísticas (en local no pide clave). La base local (`*.db`) no se sube al repo.

---

## Cómo colaborar

1. **Trabaja en una rama**, una por idea: `git checkout -b nuevo-enemigo`. No subas cambios directo a `main`: `main` es lo que está publicado.
2. **Sube solo los archivos fuente** (`src/`, `scripts/`, `sprites/`, `stats/`). **No subas `ticket_rush.html` en tu rama**: se genera completo cada vez y siempre daría conflictos. Se regenera una sola vez, después de unir la rama a `main`.
3. **Nunca edites `ticket_rush.html` a mano**: `construir_juego.py` lo reescribe y se pierde el cambio.
4. **No cambies la dificultad (`CURVE`, `RANKS`, velocidades, tiempos) sin hablarlo antes**: hay una tabla de líderes semanal y cambiarla haría la competencia injusta.
5. **Pruébalo** en tu computador (sección anterior), en computador y en celular horizontal.
6. Abre un **Pull Request** hacia `main` contando qué cambiaste y por qué. Después de revisarlo se une, se regenera el HTML y se publica.

**Estilo:** el juego debe seguir siendo **simple y divertido**: nada de controles nuevos complicados. El humor es de oficina de TI. Código en el mismo estilo que el que ya existe (JavaScript sin librerías, comentarios cortos en español).

**Publicar** en la VPS lo hace quien administra el juego; las llaves y claves no están en el repositorio.
