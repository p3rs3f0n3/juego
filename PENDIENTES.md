# Pendientes de Ticket Rush

Ideas y requerimientos para no olvidar. Salieron del chat con los amigos que juegan (22 oct 2026).
Cuando algo se termine, se marca con `[x]` y se anota el Pull Request o commit.

**Orden sugerido:** 1 → 2 → 3 → 4. Lo de arriba mejora la experiencia de todos y es rápido; lo de abajo cambia la jugabilidad y hay que probarlo con calma para no romper la dificultad.

---

## 1. Primero (rápido y para todos)

- [ ] **Cerrar el PR #1 de Manuel (rama `design`)**: achicar el logo a 304×152 px y dejar solo íconos en SONIDO/AYUDA en celular horizontal. Luego merge a `main`, regenerar `ticket_rush.html` y publicar en la VPS.
- [ ] **La ayuda se abre sola la primera vez** que alguien entra (y se recuerda en el navegador para que no vuelva a salir). Varios no vieron la cafetera ni leyeron instrucciones. *(Carlos, Manuel)*
- [ ] **Reiniciar la tabla de líderes** cuando salga la actualización, para que todos arranquen parejo. Guardar el histórico viejo antes. *(Daniela)*
- [ ] **Revisar el puntaje #1** con los datos (tickets y tiempo) para aclarar si es real: hay sospechas de "hacker criollo". *(Carlos, Daniela)*
- [ ] **La compañera se llama "Dani"** (en frases y en la ayuda). *(Carlos)*
- [ ] **Frases nuevas:**
  - Jefe: "Uy, venga le digo" *(Daniela)*, "Hoy te tienes que quedar conmigo hasta las 8 para terminar un informe" *(Daniela)*.
  - Contra los de TI (jefe o chismosa): "Usted es solo reiniciar el PC" *(Jesús)*, "Tanto que le pagan solo por reiniciar", "Los de TI no hacen nada", "La de TI entró por palanca" *(Daniela)*.
  - Chismosa al jefe: "Jefe, los de TI están jugando Minecraft" *(Daniela)*.
- [ ] **Preguntarle a Daniela** qué quería "más grande" (mandó una imagen que no quedó en el chat).

## 2. Después: animaciones de Manuel

- [ ] **Integrar los spritesheets chibi** (`spritesheets-chibi-v2.zip`): caminar, correr con turbo y acción especial (jugadora celebra al ascender, jefe se enoja al alcanzarte, compañera enamorada al distraer al jefe). Son generados con IA: hay que limpiarlos (bordes nítidos, sin transparencias, paleta reducida) y reducirlos a 48 px. Faltan las direcciones arriba/abajo (izquierda = reflejar).
- [ ] **Decidir: ¿Gerente sí o no?** En la propuesta de Manuel la chismosa reemplaza al Gerente (que hoy aparece al llegar a Jefe de TI). Opciones: quedarse con el Gerente, reemplazarlo, o tener los dos.
- [ ] **Decidir el vestido de Dani** (la propuesta nueva es un vestido rosado strapless; la actual es blusa y falda de oficina).

## 3. Personajes nuevos (cambian la jugabilidad)

- [ ] **Compañera chismosa / coordinadora / "sapo lambón"** que perjudica a la de TI. Aparecería **en un rango alto**. Manuel ya hizo su sprite. *(Jesús, Daniela, Carlos)*
  - Decidir qué hace: le cuenta al jefe dónde estás y él va directo · le da turbo al jefe · te distrae con frases · o es "bipolar" (un día ayuda y otro perjudica).
- [ ] **Pasante del SENA / auxiliar** que ayuda a la de TI. *(Daniela, Carlos)*
  - Decidir qué hace: te da turbo · resuelve tickets solo · otra cosa. Ya existe un sprite sin usar (`scripts/crear_companero.py`).
- [ ] *(Opcional)* **Variedad de jefes**: que no siempre sea calvo (más gordo, más joven…). *(Esposito, Carlos)*

## 4. Ambientación

- [ ] **Temporadas**: Halloween en octubre (brujas, calabazas) y Navidad en diciembre (decoración, gorros). Para Halloween el tiempo está justo; quizás apuntarle a Navidad. *(Jesús)*
- [ ] **Puertas con letreros chistosos** en la oficina (Il Palazzo, Condoricosas, cuarto de las escobas). *(Manuel)*

## Decisiones pendientes

- [ ] **Ko-fi**: a qué cuenta debe apuntar el enlace de donaciones (hoy va a la página principal de Ko-fi). Se queda en el PR mientras se define.

## Ya decidido

- **El turbo sigue siendo café** (se habló de Coca-Cola, pero ganó el café colombiano y así se evitan problemas de marca registrada).
- **La dificultad aprobada no se cambia sin hablarlo** (ver README).
