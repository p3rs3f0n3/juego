# Pendientes de Ticket Rush

Ideas y requerimientos para no olvidar. Salieron del chat con los amigos que juegan (22 oct 2026).
Cuando algo se termine, se marca con `[x]` y se anota el Pull Request o commit.

**Orden sugerido:** 1 → 2 → 3 → 4. Lo de arriba mejora la experiencia de todos y es rápido; lo de abajo cambia la jugabilidad y hay que probarlo con calma para no romper la dificultad.

---

## 1. Primero (rápido y para todos)

- [x] **Cerrar el PR #1 de Manuel (rama `design`)**: logo a 304×152 px e íconos en celular horizontal. Unido a `main` y publicado el 22 oct 2026 (merge `cf70b9d`).
- [x] **La ayuda se abre sola la primera vez** que alguien entra (y se recuerda en el navegador para que no vuelva a salir). Varios no vieron la cafetera ni leyeron instrucciones. *(Carlos, Manuel)*
- [x] **Reiniciar la tabla de líderes** *(Daniela)*: se hizo con **temporadas** (22 oct 2026). La Temporada 2 arrancó de cero; la Temporada 1 queda en la base y en un respaldo, y su campeón (AYES, 4174) sale en el salón de la fama. Para abrir otra temporada: botón en `/stats`.
- [x] **Revisar el puntaje #1** *(Carlos, Daniela)*: 4174 pts con 227 tickets en 15 min (~4 s por ticket y ~18 pts por ticket con combos). Más rápido que el resto (5,5–6,6 s) pero posible; el servidor ya limita los puntajes imposibles.
- [x] **La compañera se llama "Dani"** (en frases, tips y en la ayuda). *(Carlos)*
- [x] **Frases nuevas** (excepto la de la chismosa, que espera a que exista el personaje):
  - Jefe: "Uy, venga le digo" *(Daniela)*, "Hoy te tienes que quedar conmigo hasta las 8 para terminar un informe" *(Daniela)*.
  - Contra los de TI (jefe o chismosa): "Usted es solo reiniciar el PC" *(Jesús)*, "Tanto que le pagan solo por reiniciar", "Los de TI no hacen nada", "La de TI entró por palanca" *(Daniela)*.
  - Chismosa al jefe: "Jefe, los de TI están jugando Minecraft" *(Daniela)*.
- [ ] **Preguntarle a Daniela** qué quería "más grande" (mandó una imagen que no quedó en el chat).

## 2. Después: animaciones de Manuel

- [x] **Integrar los spritesheets chibi** (22 oct 2026): caminar, correr con turbo y acciones especiales (jugadora celebra al ascender, jefe/Gerente se enoja al alcanzarte, Dani enamorada al distraer al jefe). Limpieza con `scripts/preparar_chibi.py`; izquierda = reflejo. Pendiente opcional: cuadros caminando hacia arriba/abajo si Manuel los hace.
- [x] **Decidir: ¿Gerente sí o no?** Decidido (22 oct 2026): **el Gerente se queda** (aparece al llegar a Jefe de TI). El sprite de la chismosa de Manuel es para el **compañero sapo** (sección 3), no reemplaza al Gerente. Para las animaciones, el Gerente puede salir como variante de colores del jefe chibi.
- [x] **Decidir el vestido de Dani**: se probó el vestido rosado de Manuel (22 oct 2026).

## 2b. Nuevas ideas (22 oct 2026, segunda ronda del chat)

Orden sugerido: frases + días → intro cómic → señora del aseo → comodines.

- [x] **Frases nuevas del jefe:** "Renunció Pepito y borró las BD", "No hay documentación".
- [x] **Los rangos son "días" con transición tipo película** (22 oct 2026: cartel a pantalla completa, pausa la partida, se salta con una tecla o un toque): "Día 1" como practicante → cartel *"1 año después"* al pasar a Analista → *"5 años después"* al llegar a Jefe de TI ("cada día trae su afán", Alex). Reemplaza o acompaña el cartel de "¡ASCENSO!". No cambia la dificultad.
- [x] **Intro tipo cómic** (22 oct 2026, viñetas de Manuel en `arte/intro/comic.jpg`, recortadas con `scripts/preparar_intro.py`): 4 ilustraciones con slider (deslizar/flechas), botón "Saltar", se ve una sola vez (recordado en el navegador) y se puede volver a ver desde AYUDA. **Necesita las 4 ilustraciones de Manuel.** Cargarlas como archivos aparte (no dentro del HTML) para no hacer pesado el juego.
- [ ] **Señora del aseo** 🧹: pasea por la oficina y "desconecta cosas"; los tickets aparecen en el puesto por donde ella pasó. Si los tickets salen con la misma frecuencia (solo cambia dónde), no toca la dificultad. **Necesita sprite de Manuel.**
- [ ] **Comodines / excusas para defenderse del jefe:** "Tengo cita médica", "Voy por el boletín escolar", "Voy al baño", "Le dije que había que hacer un DRP", "Yo pedí otro servidor", "El proveedor de internet se cayó".
  - Propuesta: se **compran con puntos** en la transición entre días (mini tienda en el cartel de "1 año después").
  - Propuesta para no agregar botones: si tienes un comodín y el jefe te alcanza, **se usa solo**: la jugadora dice la excusa, el jefe se va y no pierdes la vida.
  - **Ojo: cambia la dificultad** (hace más fácil al jefe). Probarlo y aprobarlo antes, como la curva.

## 3. Personajes nuevos (cambian la jugabilidad)

- [ ] **Compañera chismosa / coordinadora / "sapo lambón"** que perjudica a la de TI. Aparecería **en un rango alto**. Su sprite es la "compañera chismosa" de `spritesheets-chibi-v2.zip` (moño, gafas, cárdigan lila; acción especial: chismear). *(Jesús, Daniela, Carlos)*
  - Decidir qué hace: le cuenta al jefe dónde estás y él va directo · le da turbo al jefe · te distrae con frases · o es "bipolar" (un día ayuda y otro perjudica).
- [ ] **Pasante del SENA / auxiliar** que ayuda a la de TI. *(Daniela, Carlos)*
  - Decidir qué hace: te da turbo · resuelve tickets solo · otra cosa. Ya existe un sprite sin usar (`scripts/crear_companero.py`).
- [ ] *(Opcional)* **Variedad de jefes**: que no siempre sea calvo (más gordo, más joven…). *(Esposito, Carlos)*

## 4. Ambientación

- [ ] **Temporadas**: Halloween en octubre (brujas, calabazas) y Navidad en diciembre (decoración, gorros). Para Halloween el tiempo está justo; quizás apuntarle a Navidad. *(Jesús)*
- [ ] **Puertas con letreros chistosos** en la oficina (Il Palazzo, Condoricosas, cuarto de las escobas). *(Manuel)*

## Decisiones pendientes

- [ ] **Ko-fi**: a qué cuenta debe apuntar el enlace de donaciones. Manuel lo quitó al ajustar el PR #1; hoy el juego no tiene enlace. Cuando se defina la cuenta, se vuelve a agregar.

## Detalles menores

- [ ] El color de la chaqueta de la jugadora cambia un poco al empezar a arreglar (las hojas de Manuel tienen tonos distintos). Igualar en el script o pedir a Manuel el mismo tono.
- [ ] Animaciones caminando hacia arriba/abajo, si Manuel las hace.

## Ya decidido

- **El turbo sigue siendo café** (se habló de Coca-Cola, pero ganó el café colombiano y así se evitan problemas de marca registrada).
- **La dificultad aprobada no se cambia sin hablarlo** (ver README).
