# Guía de contenido (obligatoria para todos los vídeos)

Sale de los datos de los primeros días: los Shorts que mejor funcionan son los que tienen **una cifra concreta y sorprendente** y cuentan **un suceso real casi increíble** (por ejemplo, la epidemia de risa que cerró 14 escuelas, o Petra, una ciudad en el desierto sin ríos).

## PASO OBLIGATORIO: copia lo que funciona
Antes de elegir tema, ejecuta `python youtube_api.py [--canal civ] ranking`. Coge los **3 Shorts con más visitas** del canal como modelo y el nuevo vídeo tiene que parecerse a ellos en:
1. **El tipo de tema.** Busca un hecho real del mismo estilo, nunca el mismo hecho.
2. **La fórmula del título.** Copia su estructura (cifra, palabra en mayúsculas, emoji) con otro contenido.
3. **El gancho:** la primera frase tiene la misma forma, una cifra o un dato imposible dicho de golpe.

Mira también los 2 que **peor** funcionan y evita su tipo de tema y de título.

### Lo que ya sabemos (datos del 25 al 27 de noviembre)
**Archivos Malditos TV**, de más a menos visitas:

| Vídeo | Visitas | Me gusta |
|---|---|---|
| La epidemia de RISA que cerró 14 escuelas | 1.386 | 46 |
| El barco de guerra que se HUNDIÓ en 20 minutos | 656 | 10 |
| La EXPLOSIÓN sin cráter que arrasó Siberia en 1908 | 653 | 22 |
| El PAPA MUERTO que fue juzgado en un tribunal | 403 | 19 |

Fracaso: "El GRAN HEDOR que paralizó Londres" (4 visitas). Era un tema de ciudad e higiene, sin víctima concreta ni nada imposible.

**Escribas del Tiempo:**

| Vídeo | Visitas | Me gusta |
|---|---|---|
| La CIUDAD que dominó el DESIERTO sin ríos (Petra) | 591 | 17 |
| La CIUDAD SUBTERRÁNEA donde vivían 20.000 personas | 277 | 11 |
| El ORDENADOR de la Antigua Grecia que nadie entendía | 141 | 4 |

Lo que tienen en común los que funcionan:
- **Una paradoja o algo imposible en el título:** una risa que cierra escuelas, una explosión sin cráter, un papa muerto juzgado, un barco hundido en minutos, una ciudad sin ríos en el desierto.
- **Una cifra o fecha concreta**: 14 escuelas, 20 minutos, 1908, 20.000 personas.
- **Un protagonista claro**, sea una persona, un barco o una ciudad, al que le pasa algo extremo.
- **Lugares y civilizaciones "mágicos"** (Petra, Derinkuyu) en Escribas del Tiempo. Funcionan peor los temas técnicos o abstractos.

Lo que no funciona:
- Temas sin protagonista ni giro (higiene urbana, procesos lentos).
- Títulos que describen en vez de sorprender.

## Temas
- Prioriza los sucesos reales que parecen imposibles: epidemias raras, fenómenos colectivos, inventos adelantados a su época, ciudades perdidas, desapariciones y desastres absurdos.
- Siempre que puedas, encaja el tema en una **serie** reconocible y ponla en `playlist` (ver abajo). Si el tema da para más, termina con "En el próximo te cuento…".

## Gancho (Shorts y vídeos largos)
- La **primera frase** tiene un máximo de 10 palabras y lleva el dato más chocante, con una cifra si la hay. Sin saludos ni presentaciones.
  - Bien: "En 1962, una risa contagiosa cerró 14 escuelas."
  - Mal: "Hoy os voy a contar una historia increíble sobre…"
- **Shorts:** añade `"hook_text"`, un texto fijo que se ve arriba durante todo el Short. Es una pregunta o frase de choque de 3 a 7 palabras, distinta del título. Ejemplo: "¿Una ciudad bailando hasta morir?".

## Cierre
- El último segmento termina con **una pregunta concreta** que invite a comentar, por ejemplo "¿Tú te habrías quedado encerrado en Eyam?". No vale un genérico "¿qué opinas?".
- **Shorts:** justo antes de la pregunta, una frase corta que invite al canal, como "En el canal tienes la historia completa de casos como este".

## Títulos
- Una cifra o un dato concreto, una palabra en MAYÚSCULAS como mucho y un emoji. En los Shorts, menos de 60 caracteres antes de los hashtags.

## Listas de reproducción (`playlist`)
Cada episodio lleva `"playlist"` con UNA de estas listas. Usa siempre el nombre exacto para no crear duplicados:
- **Archivos Malditos TV:** "Epidemias y locuras colectivas", "Misterios sin resolver", "Desastres absurdos", "Crímenes y castigos de la historia", "Barcos y lugares fantasma".
- **Escribas del Tiempo:** "Ciudades perdidas", "Ingenios de la Antigüedad", "Imperios que cayeron", "Templos y construcciones imposibles", "Vida cotidiana en la Antigüedad".

Si ninguna encaja de verdad, puedes crear una nueva con un nombre de 2 a 5 palabras del mismo estilo.
