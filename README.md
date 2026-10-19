# Fulbito - Organizador de equipos y torneos de fútbol

Arma equipos parejos a partir de los atributos que vos cargás de cada jugador
(Ritmo, Pase, Regate y Defensa) y de sus posiciones, y organiza torneos todos
contra todos. Para F5, F8 y F11.

Está hecho en **Python básico**: funciones, `if`, `for`, `while`, listas y
diccionarios. Hay dos formas de usarlo, que hacen lo mismo:

- **Página web** (`index.html` + `pagina.py`): se usa desde el navegador,
  también en el celular. Publicada en https://benmacompanis-sketch.github.io/Fulbito/
- **Consola** (`main.py`): se usa desde la terminal.

## Archivos

| Archivo | Qué tiene |
| --- | --- |
| `logica.py` | Todas las cuentas: medias, armar equipos parejos, puestos, fixture y tabla. Lo usan las dos versiones. |
| `main.py` | La versión de consola (menú con `input` y `print`). Guarda en `datos.json`. |
| `pagina.py` | Lo que hace funcionar la página web. |
| `index.html` | La estructura de la página. Cada botón dice qué función de `pagina.py` llama (`py-click="..."`). |
| `style.css` | Los colores y el diseño de la página. |
| `pruebas.py` | Pruebas que revisan que las cuentas den bien. |

## Cómo se usa

**Consola:**

```bash
python main.py
```

**Página web en tu compu:** con doble clic en `index.html` no anda, porque el
navegador no deja leer los archivos `.py` sueltos. Abrí una terminal en esta
carpeta y escribí:

```bash
python -m http.server
```

Después entrá a http://localhost:8000. Hace falta internet, porque la página
baja [PyScript](https://pyscript.net), que es lo que permite correr Python
dentro del navegador. La primera vez tarda unos segundos en cargar.
Para cortar el servidor, `Ctrl + C`.

**Pruebas:**

```bash
python pruebas.py
```

## Cómo arma los equipos

1. Mezcla a los jugadores.
2. Si se emparejan por posición, los pone en orden: primero los que pueden atajar,
   después defensores, mediocampistas y delanteros.
3. Los reparte de a uno por equipo, como cuando se "pisa".
4. Prueba cambiar jugadores de a dos entre equipos (de la misma posición, si se
   usan posiciones). Si la diferencia de media baja, deja el cambio.
5. Hace todo eso 20 veces y se queda con los equipos más parejos.

En cada equipo cada uno juega de su posición principal, pero si el equipo no
tiene arquero, ataja el que tenga "arquero" de secundaria.

En la página, para editar, borrar o mover a un jugador escribís su **número**
(el N° de la tabla de jugadores) y tocás el botón.

## Qué hace y qué no

Hace: calificar jugadores por sus atributos, armar equipos parejos, dejarte
cambiarlos a mano, organizar torneos, promediar las medias de los equipos y
armar para F5, F8 y F11.

No hace, a propósito:

- **Inventar jugadores:** si faltan, te dice cuántos.
- **Repetir equipos:** un jugador no puede estar en dos equipos y "otra
  combinación" nunca repite una que ya viste.
- **Conseguir gente ni recomendar cancha.**
- **Poner atributos solo:** todos los números los cargás vos.
