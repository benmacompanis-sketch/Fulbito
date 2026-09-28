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

1. Reparte a los jugadores al azar, de a uno por equipo.
2. Prueba cambiar jugadores de a dos entre equipos. Si con el cambio quedan más
   parejos, lo deja; si no, lo vuelve atrás. Repite hasta que ningún cambio mejore.
3. Hace todo eso varias veces y se queda con el resultado más parejo.

"Más parejo" quiere decir que la diferencia de media entre el mejor y el peor
equipo sea lo más chica posible. Con "emparejar también por posiciones", además
busca que cada equipo tenga parecida la cantidad de arqueros, defensores,
mediocampistas y delanteros: la posición principal cuenta 1 y cada secundaria,
medio.

Dentro de cada equipo, si falta un puesto (primero el arco), lo ocupa alguien
que lo tenga de secundaria, y los jugadores se muestran en orden de arquero,
defensores, mediocampistas y delanteros.

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
