# Estudio de sprites de Ticket Rush

Abre **http://127.0.0.1:8766/tools/sprites/** después de iniciar:

```sh
python3 scripts/servidor_diseno.py
```

El servidor sirve el proyecto completo y permite guardar los ajustes desde el visor.
No requiere instalar dependencias. Para solo consultar o exportar JSON también funciona con
un servidor estático, por ejemplo el del puerto 8765.

## Flujo de trabajo

1. Elige el slot del personaje o mueble. El nombre del PNG activo aparece arriba.
2. Elige la animación; reproduce, pausa o avanza fotograma a fotograma.
3. Haz clic en una celda para inspeccionarla aislada. Activa «Cuadro anterior» para comparar la alineación.
4. Ajusta columnas, filas y tamaño de celda. Los índices empiezan en **0**, recorriendo la hoja por filas.
5. Modifica tamaño de dibujo, ancla y desplazamiento. Arrastra en el visor para desplazar el sprite.
6. «Recortar este fotograma» permite excluir restos de celdas vecinas con un recorte individual del PNG. Corrige saltos con «Alinear este fotograma». Estos ajustes afectan el cuadro seleccionado en todas las secuencias que lo usan.
7. «Probar borrador en el juego» abre el juego usando estos ajustes, sin escribir archivos.
8. «Guardar en proyecto» valida los PNG y los fotogramas, escribe `src/sprites.config.json` y regenera `ticket_rush.html`. Recarga la pestaña del juego.

El borrador queda en el almacenamiento de este navegador y **este origen** (el puerto es parte
del origen). Úsalo desde el mismo servidor que el juego. El juego normal ignora los borradores;
solo los aplica con `?sprites=preview`. Si la pestaña del juego ya estaba abierta, recárgala.
«Descartar borrador completo» vuelve a la última configuración guardada; no borra archivos.
«Restablecer» reinicia solo el slot seleccionado. Exportar e importar permiten compartir ajustes.

Puedes seleccionar otro PNG existente o subir uno: se guarda con nombre nuevo en `sprites/custom_*.png`,
sin sobrescribir arte existente. Revisa la cuadrícula después de cambiar de archivo. Las hojas de
personajes nuevas pueden conservar el formato de 4 columnas × 3 filas; las tiras heredadas de 12 × 1
y los atlas de muebles también se soportan explícitamente.

## Por qué había diferencias

La protagonista usa tres PNG diferentes: movimiento direccional nuevo, tecleo anterior y acciones
anteriores. Cada uno tiene su slot. Elegir un PNG diferente en el visor solo modifica ese slot;
las otras acciones no cambian automáticamente. El original de `design-proposals/` es una referencia:
los scripts lo recortan, escalan, alinean y reducen de paleta para crear el PNG de `sprites/`.

**El visor y el juego comparten `src/sprite-runtime.js`**, que aplica el mismo recorte, tamaño,
ancla, reflejo y desplazamiento por cuadro. La configuración compartida es `src/sprites.config.json`.
El generador incrusta ambos y los PNG activos en el HTML, conservando el juego autocontenido.

Los efectos del juego (estrellas, sudor incorporado en la hoja, sombrero provisional del pasante,
bocadillos, sombras, disfraces de Halloween) y los monitores dibujados encima de los escritorios
son capas adicionales. El estudio muestra el sprite base; «Probar borrador» permite revisar
el resultado con esas capas. Las colisiones y posiciones del mapa no se alteran desde el estudio.

Las animaciones de caminar/correr avanzan por distancia en el juego: controla su cadencia con
«Distancia por paso». FPS controla las acciones y la reproducción del visor. El estado del juego
sigue eligiendo cuándo caminar, trabajar o celebrar; cambiar una secuencia no altera esa lógica.

## Archivos

- `src/sprites.config.json`: archivo editable de configuración.
- `src/sprite-runtime.js`: renderizado compartido.
- `tools/sprites/`: interfaz del estudio.
- `scripts/sprite_config.py`: validación de configuración y dimensiones reales de PNG.
- `scripts/servidor_diseno.py`: servidor local con guardado y carga de PNG.
- `scripts/construir_juego.py`: generación del HTML con ajustes guardados.

No subas el HTML generado a la rama; sigue el flujo del README principal del proyecto.
