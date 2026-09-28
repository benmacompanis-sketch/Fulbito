# Organizador de equipos y torneos de fútbol

Hay dos versiones que hacen lo mismo:

- **Versión web, hecha en Python** (`index.html`, `style.css`, `pagina.py`): se abre
  en el navegador, también desde el celular. Publicada en
  https://benmacompanis-sketch.github.io/Fulbito/
  Toda la lógica está en `pagina.py`, que corre dentro del navegador gracias a
  [PyScript](https://pyscript.net). La primera vez que se abre tarda unos segundos
  en cargar Python; después queda en caché.
  Los datos quedan guardados en ese navegador.
  Además de los atributos, cada jugador tiene una posición principal (Arquero,
  Defensor, Mediocampista o Delantero) y las secundarias que quieras. Al armar
  equipos se emparejan la media y la cantidad de jugadores por posición (la
  principal cuenta 1 y cada secundaria medio), y avisa si un equipo queda sin
  nadie que ataje. Se puede destildar "Emparejar también por posiciones".
  Dentro de cada equipo, si falta un puesto (primero el arco) lo cubre alguien
  que lo tenga de secundaria, y los jugadores se muestran en orden de arquero,
  defensores, mediocampistas y delanteros según el puesto en que juegan.
- **Versión de consola en Python** (`main.py` y la carpeta `futbol/`), explicada abajo.

### Probar la versión web en tu compu

Con doble clic en `index.html` no anda: el navegador no deja que la página lea
`pagina.py` desde un archivo suelto. Hay que abrirla con un servidor local, que
ya viene con Python. En una terminal, dentro de la carpeta del proyecto:

```bash
python -m http.server
```

y abrí http://localhost:8000 en el navegador. Hace falta internet para bajar
PyScript. Para cortar el servidor, `Ctrl + C` en la terminal.

## Versión de consola (Python)

Programa de consola en Python para armar equipos parejos y torneos a partir de las
estadísticas que vos cargás de cada jugador. No usa dependencias externas: sólo la
biblioteca estándar (Python 3.10 o más nuevo).

## Cómo se usa

```bash
python3 main.py              # guarda todo en datos.json, al lado de main.py
python3 main.py otro.json    # o en el archivo que le indiques
```

Menú:

| Opción | Qué hace |
| --- | --- |
| 1 · Ver jugadores | Lista con Ritmo, Pase, Regate, Defensa y la media de cada uno. |
| 2 · Cargar jugador | Nombre y los cuatro atributos (1 a 99). No se pueden repetir nombres. |
| 3 · Editar atributos | Cambia los números de un jugador; las medias de su equipo se actualizan solas. |
| 4 · Borrar jugador | Sólo si no está en un equipo armado. |
| 5 · Armar equipos parejos | Elegís formato (F5, F8, F11), cantidad de equipos y quiénes juegan. Te propone un reparto; podés aceptarlo o pedir **otra combinación**, que nunca repite una ya vista. |
| 6 · Ver equipos y medias | Media general y por atributo de cada equipo, promedio entre equipos y diferencia entre el más fuerte y el más débil. |
| 7 · Modificar equipos a mano | Mover un jugador a otro equipo, intercambiar dos o renombrar un equipo. Muestra cómo quedan las medias después de cada cambio. |
| 8 · Armar torneo | Con los equipos actuales o armando nuevos: fixture todos contra todos (ida, o ida y vuelta), sin cruces repetidos. Con cantidad impar, uno queda libre por fecha. |
| 9 · Fixture y resultados | Cargás los resultados como `3-1`. |
| 10 · Tabla de posiciones | PJ, G, E, P, GF, GC, DG y puntos (3 por victoria, 1 por empate). |

En cualquier pregunta, Enter vacío vuelve al menú.

## Cómo se calculan las medias

- **Media del jugador:** promedio simple de sus cuatro atributos.
- **Media del equipo:** promedio de las medias de sus jugadores (y lo mismo por atributo).
- **Promedio del torneo:** promedio de las medias de los equipos.

## Cómo reparte

1. Arranca con un reparto "tipo draft": el mejor al equipo 1, el siguiente al 2, y
   así en zigzag.
2. Lo mejora probando todos los intercambios de a dos jugadores (y pases de un
   jugador cuando los equipos tienen distinto tamaño) mientras la diferencia de
   media baje.
3. Repite desde varios repartos al azar y se queda con el mejor.

Lo que minimiza es la diferencia de media general entre el mejor y el peor equipo.
Como desempate, con menos peso, también empareja cada atributo, para que no quede
un equipo con todos los rápidos y otro con todos los defensores.

Si hay más jugadores que los que pide el formato, **juegan todos**: los que sobran
quedan como suplentes, repartidos de a uno. Si faltan, avisa cuántos faltan.

## Qué hace y qué no

Hace: calificar jugadores según sus atributos, organizar equipos parejos, permitir
modificarlos a tu gusto, organizar torneos parejos, promediar medias de equipos y
armar para F5, F8 y F11.

No hace, a propósito:

- **Inventar jugadores.** Si faltan para el formato, lo dice y no completa con nadie.
- **Repetir equipos.** Un jugador no puede estar en dos equipos, dos equipos no
  pueden llamarse igual, cada cruce del torneo se juega una vez (o dos con ida y
  vuelta), y "otra combinación" no repite repartos ya armados.
- **Conseguir gente, conseguir o recomendar cancha.**
- **Poner atributos automáticamente.** Todos los números los cargás vos.

## Estructura

```
main.py              entrada del programa
futbol/models.py     jugador, equipo, formatos y medias
futbol/balance.py    reparto parejo y cambios manuales (lógica pura)
futbol/tournament.py fixture, resultados y tabla (lógica pura)
futbol/storage.py    estado y guardado en JSON
futbol/cli.py        menú de consola (todo el texto en español)
tests/               tests con unittest
```

## Tests

```bash
python3 -m unittest discover -s tests -t .
```
