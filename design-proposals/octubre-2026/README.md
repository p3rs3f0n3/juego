# Update de octubre de 2026

Fuentes de personaje: PNG transparente, 4 columnas × 3 filas.

- `jugadora-caminar.png`: filas hacia abajo, hacia arriba y derecha; izquierda reflejada.
- `jugadora-acciones.png`: filas tecleando, celebrando y en reposo.

Camisa cobalto en todos los estados, afro y lentes turquesa conservados.
`node scripts/preparar_octubre.cjs` genera las hojas de juego y nueve variantes Halloween.
Los PNG de Halloween son 256 × 216 px (celdas 64 × 72), con margen para accesorios; las hojas
base son 224 × 168 px (celdas 56 × 56). El ancla de pies mantiene la misma escala en el juego.
El halo y las decoraciones no alteran colisiones, velocidad, tickets ni dificultad.
