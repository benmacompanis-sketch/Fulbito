# ===============================
# Fulbito - Organizador de equipos
# Versión web en Python (corre en el navegador con PyScript)
# ===============================

import html
import json
import random

from pyscript import document, when, window


# ---------- DATOS ----------

# Cada jugador es un diccionario:
# {"nombre", "ritmo", "pase", "regate", "defensa", "posicion", "secundarias", "juega"}
# "posicion" es la principal ("ARQ", "DEF", "MED" o "DEL") y "secundarias" es una lista.
jugadores = []

# Cada equipo: {"nombre": ..., "jugadores": [nombres de los jugadores]}
equipos = []

# Cada partido: {"fecha", "local", "visitante", "golesLocal", "golesVisitante"}
# (las claves quedan como estaban para no perder lo que ya estaba guardado)
partidos = []

# Combinaciones de equipos que ya se mostraron, para no repetirlas
combinaciones_vistas = []

formato_actual = 5

ATRIBUTOS = ["ritmo", "pase", "regate", "defensa"]
NOMBRES_ATRIBUTOS = {"ritmo": "Ritmo", "pase": "Pase", "regate": "Regate", "defensa": "Defensa"}

POSICIONES = ["ARQ", "DEF", "MED", "DEL"]

# Cuánto pesa que las posiciones queden desparejas, comparado con la media.
# Con 1, tener un delantero de más que otro equipo pesa igual que un punto de media.
PESO_POSICIONES = 1

# Si se tiene en cuenta la posición al armar equipos (lo cambia la casilla de la página)
usar_posiciones = True


# ---------- GUARDAR Y CARGAR (en el navegador) ----------

def guardar():
    datos = {
        "jugadores": jugadores,
        "equipos": equipos,
        "partidos": partidos,
        "combinacionesVistas": combinaciones_vistas,
        "formatoActual": formato_actual,
    }
    try:
        window.localStorage.setItem("fulbito", json.dumps(datos))
    except Exception:
        # Si el navegador no deja guardar, la página sigue andando igual
        pass


def cargar():
    global jugadores, equipos, partidos, combinaciones_vistas, formato_actual
    try:
        texto = window.localStorage.getItem("fulbito")
        if texto:
            datos = json.loads(texto)
            jugadores = datos.get("jugadores", [])
            # Los jugadores cargados antes de que existieran las posiciones quedan sin posición
            for jugador in jugadores:
                if not jugador.get("posicion"):
                    jugador["posicion"] = ""
                if not isinstance(jugador.get("secundarias"), list):
                    jugador["secundarias"] = []
            equipos = datos.get("equipos", [])
            partidos = datos.get("partidos", [])
            combinaciones_vistas = datos.get("combinacionesVistas", [])
            formato_actual = datos.get("formatoActual", 5)
    except Exception:
        # Si no se puede leer, arrancamos vacío
        pass


# ---------- UTILIDADES ----------

# Evita que un nombre con símbolos raros rompa la página
def escapar(texto):
    return html.escape(str(texto), quote=True)


def mismo_nombre(a, b):
    return a.strip().lower() == b.strip().lower()


def buscar_jugador(nombre):
    for jugador in jugadores:
        if mismo_nombre(jugador["nombre"], nombre):
            return jugador
    return None


def redondear(numero):
    return f"{numero:.1f}"


# Convierte un texto en número entero. Si no es un entero, devuelve None.
def leer_entero(texto):
    try:
        return int(texto.strip())
    except ValueError:
        return None


def mostrar_mensaje(id_elemento, texto, tipo=""):
    elemento = document.getElementById(id_elemento)
    elemento.textContent = texto
    elemento.className = "mensaje " + tipo


# ---------- MEDIAS ----------

# Media de un jugador: promedio de sus 4 atributos
def media_jugador(jugador):
    return (jugador["ritmo"] + jugador["pase"] + jugador["regate"] + jugador["defensa"]) / 4


# Media de un grupo de nombres. Sin atributo: media general
def media_grupo(nombres, atributo=None):
    if len(nombres) == 0:
        return 0
    suma = 0
    for nombre in nombres:
        jugador = buscar_jugador(nombre)
        if atributo:
            suma += jugador[atributo]
        else:
            suma += media_jugador(jugador)
    return suma / len(nombres)


# Diferencia entre el equipo con mejor media y el de peor media
def diferencia_de_medias(grupos):
    medias = [media_grupo(grupo) for grupo in grupos]
    return max(medias) - min(medias)


# ---------- POSICIONES ----------

# Texto corto para mostrar: "ARQ (DEF, MED)"
def texto_posiciones(jugador):
    if not jugador["posicion"]:
        return "Sin posición"
    texto = jugador["posicion"]
    if len(jugador["secundarias"]) > 0:
        texto += " (" + ", ".join(jugador["secundarias"]) + ")"
    return texto


# Cuánto aporta un jugador a cada posición: 1 la principal y 0,5 cada secundaria
def aporte_por_posicion(jugador):
    aporte = {"ARQ": 0, "DEF": 0, "MED": 0, "DEL": 0}
    if jugador["posicion"]:
        aporte[jugador["posicion"]] = 1
    for posicion in jugador["secundarias"]:
        if posicion != jugador["posicion"]:
            aporte[posicion] = 0.5
    return aporte


# Decide en qué puesto juega cada jugador dentro de su equipo.
# Devuelve algo como {"Pepe": "ARQ", "Tito": "DEF", ...}.
#
# 1. Todos arrancan en su posición principal.
# 2. Si al equipo le falta un puesto (primero el arco, después defensa,
#    medio y delantera), lo ocupa alguien que lo tenga de secundaria.
#    Sale de su puesto el que deja menos hueco: el que tiene más
#    compañeros en su posición; si empatan, el de menor media.
#    Para el arco se acepta dejar otro puesto vacío; para los demás, no.
def asignar_puestos(nombres):
    puestos = {}
    cuenta = {"ARQ": 0, "DEF": 0, "MED": 0, "DEL": 0}

    for nombre in nombres:
        jugador = buscar_jugador(nombre)
        puestos[nombre] = jugador["posicion"]
        if jugador["posicion"]:
            cuenta[jugador["posicion"]] += 1

    for puesto in POSICIONES:
        if cuenta[puesto] > 0:
            continue

        elegido = None
        for nombre in nombres:
            jugador = buscar_jugador(nombre)
            actual = puestos[nombre]
            if puesto not in jugador["secundarias"]:
                continue
            if not actual:
                continue
            if puesto != "ARQ" and cuenta[actual] < 2:
                continue

            if elegido is None:
                elegido = nombre
            else:
                companeros_nuevo = cuenta[actual]
                companeros_elegido = cuenta[puestos[elegido]]
                media_nuevo = media_jugador(jugador)
                media_elegido = media_jugador(buscar_jugador(elegido))
                if companeros_nuevo > companeros_elegido or (
                    companeros_nuevo == companeros_elegido and media_nuevo < media_elegido
                ):
                    elegido = nombre

        if elegido is not None:
            cuenta[puestos[elegido]] -= 1
            puestos[elegido] = puesto
            cuenta[puesto] += 1

    return puestos


# Cuántos jugadores hay en cada puesto, según asignar_puestos
def contar_puestos(puestos):
    cuenta = {"ARQ": 0, "DEF": 0, "MED": 0, "DEL": 0}
    for puesto in puestos.values():
        if puesto:
            cuenta[puesto] += 1
    return cuenta


# ---------- QUÉ TAN PAREJOS SON UNOS EQUIPOS ----------

# Cuanto más bajo, más parejos. Suma:
#  - la diferencia de media entre el mejor y el peor equipo
#  - por cada posición, la diferencia entre el equipo que más tiene y el que menos
#
# No recibe los equipos sino las sumas de cada equipo, que se van actualizando
# a medida que se prueban cambios. Así no hay que recalcular todo cada vez.
def calcular_costo(suma_medias, suma_posiciones, tamanios):
    medias = [suma_medias[t] / tamanios[t] for t in range(len(tamanios))]
    costo = max(medias) - min(medias)
    if usar_posiciones:
        for posicion in POSICIONES:
            valores = [suma_posiciones[t][posicion] for t in range(len(tamanios))]
            costo += PESO_POSICIONES * (max(valores) - min(valores))
    return costo


def calcular_sumas(grupos, medias, aportes):
    suma_medias = [sum(medias[n] for n in grupo) for grupo in grupos]
    suma_posiciones = []
    for grupo in grupos:
        suma = {"ARQ": 0, "DEF": 0, "MED": 0, "DEL": 0}
        for nombre in grupo:
            for posicion in POSICIONES:
                suma[posicion] += aportes[nombre][posicion]
        suma_posiciones.append(suma)
    tamanios = [len(grupo) for grupo in grupos]
    return suma_medias, suma_posiciones, tamanios


def costo_de(grupos, medias, aportes):
    return calcular_costo(*calcular_sumas(grupos, medias, aportes))


# ---------- ARMAR EQUIPOS PAREJOS ----------

# Reparte los nombres en grupos, de a uno por equipo (como cuando se "pisa")
def repartir_al_azar(nombres, cantidad):
    mezclados = list(nombres)
    random.shuffle(mezclados)
    grupos = [[] for _ in range(cantidad)]
    for i, nombre in enumerate(mezclados):
        grupos[i % cantidad].append(nombre)
    return grupos


# Intercambia a "x" (del equipo a) con "y" (del equipo b) en las sumas
def pasar_en_sumas(suma_medias, suma_posiciones, a, b, x, y, medias, aportes):
    suma_medias[a] += medias[y] - medias[x]
    suma_medias[b] += medias[x] - medias[y]
    for posicion in POSICIONES:
        suma_posiciones[a][posicion] += aportes[y][posicion] - aportes[x][posicion]
        suma_posiciones[b][posicion] += aportes[x][posicion] - aportes[y][posicion]


# Prueba cambiar jugadores de a dos entre equipos mientras queden más parejos
def mejorar_con_intercambios(grupos, medias, aportes):
    suma_medias, suma_posiciones, tamanios = calcular_sumas(grupos, medias, aportes)
    actual = calcular_costo(suma_medias, suma_posiciones, tamanios)

    hubo_mejora = True
    while hubo_mejora:
        hubo_mejora = False
        for a in range(len(grupos)):
            for b in range(a + 1, len(grupos)):
                for i in range(len(grupos[a])):
                    for j in range(len(grupos[b])):
                        x = grupos[a][i]
                        y = grupos[b][j]
                        # Probamos el cambio
                        pasar_en_sumas(suma_medias, suma_posiciones, a, b, x, y, medias, aportes)
                        nuevo = calcular_costo(suma_medias, suma_posiciones, tamanios)
                        if nuevo < actual - 0.0001:
                            grupos[a][i], grupos[b][j] = y, x
                            actual = nuevo
                            hubo_mejora = True
                        else:
                            # No mejoró: lo volvemos atrás
                            pasar_en_sumas(suma_medias, suma_posiciones, a, b, y, x, medias, aportes)


# Cambia dos jugadores al azar de dos equipos distintos
def intercambio_al_azar(grupos):
    a, b = random.sample(range(len(grupos)), 2)
    i = random.randrange(len(grupos[a]))
    j = random.randrange(len(grupos[b]))
    grupos[a][i], grupos[b][j] = grupos[b][j], grupos[a][i]


# Texto que identifica una combinación sin importar el orden
def clave_de(grupos):
    partes = [",".join(sorted(n.lower() for n in grupo)) for grupo in grupos]
    return " | ".join(sorted(partes))


# Busca la combinación más pareja que todavía no se haya mostrado
def buscar_equipos_parejos(nombres, cantidad):
    medias = {}
    aportes = {}
    for nombre in nombres:
        jugador = buscar_jugador(nombre)
        medias[nombre] = media_jugador(jugador)
        aportes[nombre] = aporte_por_posicion(jugador)

    mejor = None
    mejor_costo = float("inf")
    intentos = 15 if len(nombres) > 30 else 40

    for _ in range(intentos):
        grupos = repartir_al_azar(nombres, cantidad)
        mejorar_con_intercambios(grupos, medias, aportes)

        # Si esta ya salió antes, la movemos un poco hasta encontrar una nueva
        vueltas = 0
        while clave_de(grupos) in combinaciones_vistas and vueltas < 50:
            intercambio_al_azar(grupos)
            vueltas += 1
        if clave_de(grupos) in combinaciones_vistas:
            continue

        costo = costo_de(grupos, medias, aportes)
        if costo < mejor_costo:
            mejor = grupos
            mejor_costo = costo

    return mejor


def armar_equipos(es_otra_combinacion):
    global equipos, partidos, combinaciones_vistas, formato_actual, usar_posiciones

    formato = int(document.getElementById("formato").value)
    cantidad = leer_entero(document.getElementById("cantidadEquipos").value)
    nombres = [j["nombre"] for j in jugadores if j["juega"]]

    if cantidad is None or cantidad < 2:
        mostrar_mensaje("mensajeEquipos", "Tienen que ser al menos 2 equipos.", "error")
        return

    necesarios = formato * cantidad
    if len(nombres) < necesarios:
        faltan = necesarios - len(nombres)
        mostrar_mensaje(
            "mensajeEquipos",
            f"Faltan {faltan} jugador(es): para {cantidad} equipos de F{formato} "
            f"se necesitan {necesarios} y juegan {len(nombres)}. No inventamos jugadores.",
            "error",
        )
        return

    if len(partidos) > 0 and not window.confirm(
        "Hay un torneo armado. Si cambiás los equipos se borra el torneo. ¿Seguir?"
    ):
        return

    # "Armar" empieza de cero; "Otra combinación" no repite las ya mostradas
    if not es_otra_combinacion or len(equipos) == 0:
        combinaciones_vistas = []
    else:
        combinaciones_vistas.append(clave_de([e["jugadores"] for e in equipos]))

    usar_posiciones = document.getElementById("usarPosiciones").checked
    grupos = buscar_equipos_parejos(nombres, cantidad)
    if grupos is None:
        mostrar_mensaje("mensajeEquipos", "No hay otra combinación distinta de las que ya viste.", "error")
        return

    equipos = [{"nombre": f"Equipo {i + 1}", "jugadores": grupo} for i, grupo in enumerate(grupos)]
    formato_actual = formato
    partidos = []

    sobran = len(nombres) - necesarios
    texto = "¡Equipos armados!"
    if sobran > 0:
        texto += f" Sobran {sobran} jugador(es) para F{formato}: quedan como suplentes."
    mostrar_mensaje("mensajeEquipos", texto, "ok")
    mostrar_mensaje("mensajeTorneo", "")

    guardar()
    mostrar_todo()


# ---------- JUGADORES ----------

# Devuelve las posiciones secundarias tildadas en el formulario
def leer_secundarias():
    tildadas = document.querySelectorAll('input[name="secundaria"]:checked')
    return [casilla.value for casilla in tildadas]


# La posición principal no puede ser también secundaria: la destildamos y la bloqueamos
def actualizar_secundarias():
    principal = document.getElementById("posicion").value
    for casilla in document.querySelectorAll('input[name="secundaria"]'):
        if casilla.value == principal:
            casilla.checked = False
            casilla.disabled = True
        else:
            casilla.disabled = False


def guardar_jugador():
    nombre = document.getElementById("nombre").value.strip()
    valores = {}
    for atributo in ATRIBUTOS:
        valores[atributo] = leer_entero(document.getElementById(atributo).value)

    posicion = document.getElementById("posicion").value
    marcadas = leer_secundarias()
    # Guardamos las secundarias siempre en el mismo orden y sin repetir la principal
    secundarias = [p for p in POSICIONES if p in marcadas and p != posicion]

    if nombre == "":
        mostrar_mensaje("mensajeJugador", "Poné un nombre.", "error")
        return
    if posicion == "":
        mostrar_mensaje("mensajeJugador", "Elegí la posición principal.", "error")
        return
    for atributo in ATRIBUTOS:
        valor = valores[atributo]
        if valor is None or valor < 1 or valor > 99:
            mostrar_mensaje(
                "mensajeJugador",
                NOMBRES_ATRIBUTOS[atributo] + " tiene que ser un número entero del 1 al 99.",
                "error",
            )
            return

    existente = buscar_jugador(nombre)
    if existente:
        # Si ya existe, actualizamos sus datos
        for atributo in ATRIBUTOS:
            existente[atributo] = valores[atributo]
        existente["posicion"] = posicion
        existente["secundarias"] = secundarias
        mostrar_mensaje(
            "mensajeJugador",
            f"Actualizado: {existente['nombre']}, media {redondear(media_jugador(existente))}.",
            "ok",
        )
    else:
        nuevo = {"nombre": nombre, "posicion": posicion, "secundarias": secundarias, "juega": True}
        for atributo in ATRIBUTOS:
            nuevo[atributo] = valores[atributo]
        jugadores.append(nuevo)
        mostrar_mensaje("mensajeJugador", f"Listo: {nombre}, media {redondear(media_jugador(nuevo))}.", "ok")

    document.getElementById("formJugador").reset()
    actualizar_secundarias()
    document.getElementById("nombre").focus()
    guardar()
    mostrar_todo()


# Pone los datos de un jugador en el formulario para cambiarlos
def editar_jugador(indice):
    jugador = jugadores[indice]
    document.getElementById("nombre").value = jugador["nombre"]
    for atributo in ATRIBUTOS:
        document.getElementById(atributo).value = str(jugador[atributo])
    document.getElementById("posicion").value = jugador["posicion"]
    for casilla in document.querySelectorAll('input[name="secundaria"]'):
        casilla.checked = casilla.value in jugador["secundarias"]
    actualizar_secundarias()
    mostrar_mensaje("mensajeJugador", "Cambiá lo que quieras y tocá Guardar jugador.")
    document.getElementById("ritmo").focus()


def borrar_jugador(indice):
    jugador = jugadores[indice]
    esta_en_un_equipo = any(
        mismo_nombre(nombre, jugador["nombre"]) for equipo in equipos for nombre in equipo["jugadores"]
    )
    if esta_en_un_equipo:
        mostrar_mensaje(
            "mensajeJugador",
            jugador["nombre"] + " está en un equipo. Sacalo del equipo o armá equipos nuevos antes de borrarlo.",
            "error",
        )
        return
    if not window.confirm("¿Borrar a " + jugador["nombre"] + "?"):
        return
    jugadores.pop(indice)
    guardar()
    mostrar_todo()


def cambiar_juega(indice, valor):
    jugadores[indice]["juega"] = valor
    guardar()


def mostrar_jugadores():
    tabla = document.getElementById("tablaJugadores")

    if len(jugadores) == 0:
        tabla.innerHTML = '<tr><td colspan="9">Todavía no cargaste jugadores.</td></tr>'
        return

    filas = ""
    for i, jugador in enumerate(jugadores):
        tildado = "checked" if jugador["juega"] else ""
        filas += f"""
          <tr>
            <td><input type="checkbox" {tildado} data-accion="juega" data-indice="{i}"></td>
            <td class="nombre">{escapar(jugador["nombre"])}</td>
            <td class="posicion">{texto_posiciones(jugador)}</td>
            <td>{jugador["ritmo"]}</td>
            <td>{jugador["pase"]}</td>
            <td>{jugador["regate"]}</td>
            <td>{jugador["defensa"]}</td>
            <td><b>{redondear(media_jugador(jugador))}</b></td>
            <td>
              <button class="chico secundario" data-accion="editar" data-indice="{i}">Editar</button>
              <button class="chico peligro" data-accion="borrar" data-indice="{i}">Borrar</button>
            </td>
          </tr>"""
    tabla.innerHTML = filas


# ---------- MODIFICAR EQUIPOS A MANO ----------

def mover_jugador(equipo_origen, lugar, equipo_destino):
    if equipo_destino == equipo_origen:
        return

    if len(equipos[equipo_origen]["jugadores"]) == 1:
        mostrar_mensaje("mensajeEquipos", "No podés dejar un equipo sin jugadores.", "error")
        mostrar_equipos()
        return

    nombre = equipos[equipo_origen]["jugadores"].pop(lugar)
    equipos[equipo_destino]["jugadores"].append(nombre)
    mostrar_mensaje("mensajeEquipos", f"{nombre} pasó a {equipos[equipo_destino]['nombre']}.", "ok")
    guardar()
    mostrar_todo()


def renombrar_equipo(indice):
    viejo = equipos[indice]["nombre"]
    nuevo = window.prompt("Nombre nuevo para " + viejo + ":", viejo)
    if not nuevo or nuevo.strip() == "":
        return
    nuevo = nuevo.strip()

    repetido = any(i != indice and mismo_nombre(e["nombre"], nuevo) for i, e in enumerate(equipos))
    if repetido:
        mostrar_mensaje("mensajeEquipos", "Ya hay un equipo con ese nombre.", "error")
        return

    equipos[indice]["nombre"] = nuevo
    # También lo cambiamos en el fixture
    for partido in partidos:
        if partido["local"] == viejo:
            partido["local"] = nuevo
        if partido["visitante"] == viejo:
            partido["visitante"] = nuevo
    guardar()
    mostrar_todo()


def mostrar_equipos():
    contenedor = document.getElementById("equipos")
    resumen = document.getElementById("resumenEquipos")

    if len(equipos) == 0:
        contenedor.innerHTML = "<p>Todavía no armaste equipos.</p>"
        resumen.textContent = ""
        return

    hay_posiciones_cargadas = any(j["posicion"] for j in jugadores)
    tarjetas = ""
    for e, equipo in enumerate(equipos):
        medias = " · ".join(
            NOMBRES_ATRIBUTOS[a] + " " + redondear(media_grupo(equipo["jugadores"], a)) for a in ATRIBUTOS
        )

        puestos = asignar_puestos(equipo["jugadores"])
        cuenta = contar_puestos(puestos)
        posiciones = " · ".join(f"{cuenta[p]} {p}" for p in POSICIONES)

        aviso = ""
        if len(equipo["jugadores"]) < formato_actual:
            aviso += (
                f'<p class="mensaje error">Tiene {len(equipo["jugadores"])} '
                f"y F{formato_actual} pide {formato_actual}.</p>"
            )
        if hay_posiciones_cargadas and cuenta["ARQ"] == 0:
            aviso += '<p class="mensaje error">Nadie de este equipo juega de arquero.</p>'

        tarjetas += f"""
          <div class="equipo">
            <h3>
              <span>{escapar(equipo["nombre"])} — {redondear(media_grupo(equipo["jugadores"]))}</span>
              <button class="chico secundario" data-accion="renombrar" data-equipo="{e}">Renombrar</button>
            </h3>
            <div class="medias">{medias}</div>
            <div class="medias">Posiciones: {posiciones}</div>
            {aviso}
            <ul>"""

        # Los mostramos por el puesto en que juegan (arquero, defensores, medios,
        # delanteros) y dentro de cada puesto de mejor a peor. Guardamos el lugar
        # original en la lista para poder moverlos a otro equipo.
        def orden_para_mostrar(par):
            lugar, nombre = par
            puesto = puestos[nombre]
            numero_de_puesto = POSICIONES.index(puesto) if puesto else len(POSICIONES)
            return (numero_de_puesto, -media_jugador(buscar_jugador(nombre)))

        orden = sorted(enumerate(equipo["jugadores"]), key=orden_para_mostrar)

        for lugar, nombre in orden:
            jugador = buscar_jugador(nombre)
            puesto = puestos[nombre]

            # Si juega de una posición secundaria, el cartelito se ve distinto
            cartel = ""
            if puesto == jugador["posicion"]:
                cartel = f'<span class="puesto">{puesto}</span>'
            elif puesto:
                cartel = f'<span class="puesto cambiado" title="Juega de su posición secundaria">{puesto}</span>'

            opciones = ""
            for o, otro in enumerate(equipos):
                elegido = "selected" if o == e else ""
                opciones += f'<option value="{o}" {elegido}>{escapar(otro["nombre"])}</option>'

            tarjetas += f"""
              <li>
                <span>{cartel} {escapar(nombre)} <span class="posicion">{texto_posiciones(jugador)}</span> ({redondear(media_jugador(jugador))})</span>
                <select title="Mover a otro equipo" data-accion="mover" data-equipo="{e}" data-lugar="{lugar}">{opciones}</select>
              </li>"""

        tarjetas += """
            </ul>
          </div>"""
    contenedor.innerHTML = tarjetas

    medias_equipos = [media_grupo(e["jugadores"]) for e in equipos]
    promedio = sum(medias_equipos) / len(medias_equipos)
    diferencia = diferencia_de_medias([e["jugadores"] for e in equipos])
    resumen.textContent = (
        f"Promedio de las medias: {redondear(promedio)} · "
        f"Diferencia entre el más fuerte y el más débil: {diferencia:.2f}"
    )


# ---------- TORNEO ----------

# Fixture todos contra todos (método del círculo)
def crear_fixture(nombres_equipos, ida_y_vuelta):
    lista = list(nombres_equipos)
    if len(lista) % 2 == 1:
        lista.append(None)  # None = fecha libre

    total = len(lista)
    resultado = []

    for fecha in range(total - 1):
        for k in range(total // 2):
            local = lista[k]
            visitante = lista[total - 1 - k]
            if local is None or visitante is None:
                continue
            # Alternamos la localía del primer partido
            if fecha % 2 == 1 and k == 0:
                local, visitante = visitante, local
            resultado.append(
                {"fecha": fecha + 1, "local": local, "visitante": visitante, "golesLocal": None, "golesVisitante": None}
            )
        # Rotamos todos menos el primero
        lista.insert(1, lista.pop())

    if ida_y_vuelta:
        fechas_ida = total - 1
        vuelta = []
        for p in resultado:
            vuelta.append({
                "fecha": p["fecha"] + fechas_ida,
                "local": p["visitante"],
                "visitante": p["local"],
                "golesLocal": None,
                "golesVisitante": None,
            })
        resultado += vuelta
    return resultado


def armar_torneo():
    global partidos
    if len(equipos) < 2:
        mostrar_mensaje("mensajeTorneo", "Primero armá al menos 2 equipos.", "error")
        return
    if len(partidos) > 0 and not window.confirm("Ya hay un torneo. Si armás otro se borran los resultados. ¿Seguir?"):
        return
    ida_y_vuelta = document.getElementById("idaYVuelta").checked
    partidos = crear_fixture([e["nombre"] for e in equipos], ida_y_vuelta)
    mostrar_mensaje("mensajeTorneo", f"Torneo armado: {len(partidos)} partidos.", "ok")
    guardar()
    mostrar_todo()


def guardar_resultado(indice):
    texto_local = document.getElementById(f"local{indice}").value.strip()
    texto_visitante = document.getElementById(f"visitante{indice}").value.strip()

    # Si borrás los dos, el partido vuelve a "sin jugar"
    if texto_local == "" and texto_visitante == "":
        partidos[indice]["golesLocal"] = None
        partidos[indice]["golesVisitante"] = None
    else:
        goles_local = leer_entero(texto_local)
        goles_visitante = leer_entero(texto_visitante)
        if goles_local is None or goles_visitante is None or goles_local < 0 or goles_visitante < 0:
            mostrar_mensaje("mensajeTorneo", "Los goles tienen que ser números enteros desde 0.", "error")
            return
        partidos[indice]["golesLocal"] = goles_local
        partidos[indice]["golesVisitante"] = goles_visitante

    mostrar_mensaje("mensajeTorneo", "Resultado guardado.", "ok")
    guardar()
    mostrar_todo()


def mostrar_fixture():
    contenedor = document.getElementById("fixture")
    if len(partidos) == 0:
        contenedor.innerHTML = "<p>Todavía no armaste un torneo.</p>"
        return

    ultima_fecha = max(p["fecha"] for p in partidos)
    texto = ""
    for fecha in range(1, ultima_fecha + 1):
        texto += f'<div class="fecha"><h4>Fecha {fecha}</h4>'
        juegan = []
        for i, p in enumerate(partidos):
            if p["fecha"] != fecha:
                continue
            juegan += [p["local"], p["visitante"]]
            gl = "" if p["golesLocal"] is None else p["golesLocal"]
            gv = "" if p["golesVisitante"] is None else p["golesVisitante"]
            texto += f"""
              <div class="partido">
                <span>{escapar(p["local"])}</span>
                <input type="number" min="0" id="local{i}" value="{gl}">
                <span>-</span>
                <input type="number" min="0" id="visitante{i}" value="{gv}">
                <span>{escapar(p["visitante"])}</span>
                <button class="chico" data-accion="resultado" data-partido="{i}">Guardar</button>
              </div>"""
        libres = [e["nombre"] for e in equipos if e["nombre"] not in juegan]
        if len(libres) > 0:
            texto += f'<p class="libre">Libre: {escapar(", ".join(libres))}</p>'
        texto += "</div>"
    contenedor.innerHTML = texto


def mostrar_tabla_de_posiciones():
    tabla = document.getElementById("tablaPosiciones")
    if len(partidos) == 0:
        tabla.innerHTML = ""
        return

    filas = {}
    for equipo in equipos:
        filas[equipo["nombre"]] = {"equipo": equipo["nombre"], "pj": 0, "g": 0, "e": 0, "p": 0, "gf": 0, "gc": 0}

    for partido in partidos:
        if partido["golesLocal"] is None:
            continue
        local = filas[partido["local"]]
        visitante = filas[partido["visitante"]]
        local["pj"] += 1
        visitante["pj"] += 1
        local["gf"] += partido["golesLocal"]
        local["gc"] += partido["golesVisitante"]
        visitante["gf"] += partido["golesVisitante"]
        visitante["gc"] += partido["golesLocal"]
        if partido["golesLocal"] > partido["golesVisitante"]:
            local["g"] += 1
            visitante["p"] += 1
        elif partido["golesLocal"] < partido["golesVisitante"]:
            visitante["g"] += 1
            local["p"] += 1
        else:
            local["e"] += 1
            visitante["e"] += 1

    lista = list(filas.values())
    for fila in lista:
        fila["dg"] = fila["gf"] - fila["gc"]
        fila["pts"] = fila["g"] * 3 + fila["e"]
    # Ordenamos por puntos, diferencia de gol y goles a favor
    lista.sort(key=lambda f: (-f["pts"], -f["dg"], -f["gf"], f["equipo"].lower()))

    texto = ""
    for i, fila in enumerate(lista):
        dg = f"+{fila['dg']}" if fila["dg"] > 0 else str(fila["dg"])
        texto += f"""
          <tr>
            <td>{i + 1}</td>
            <td class="nombre">{escapar(fila["equipo"])}</td>
            <td>{fila["pj"]}</td>
            <td>{fila["g"]}</td>
            <td>{fila["e"]}</td>
            <td>{fila["p"]}</td>
            <td>{fila["gf"]}</td>
            <td>{fila["gc"]}</td>
            <td>{dg}</td>
            <td><b>{fila["pts"]}</b></td>
          </tr>"""
    tabla.innerHTML = texto


# ---------- BORRAR TODO ----------

def borrar_todo():
    global jugadores, equipos, partidos, combinaciones_vistas
    if not window.confirm("¿Seguro? Se borran jugadores, equipos y torneo."):
        return
    jugadores = []
    equipos = []
    partidos = []
    combinaciones_vistas = []
    guardar()
    mostrar_todo()


def mostrar_todo():
    mostrar_jugadores()
    mostrar_equipos()
    mostrar_fixture()
    mostrar_tabla_de_posiciones()


# ---------- BOTONES Y EVENTOS ----------
# "@when" conecta una función con algo que pasa en la página.
# Para las tablas y los equipos, que se dibujan de nuevo cada vez, escuchamos
# en el contenedor y miramos el "data-accion" del botón que se tocó.

@when("submit", "#formJugador")
def al_enviar_formulario(evento):
    evento.preventDefault()
    guardar_jugador()


@when("change", "#posicion")
def al_cambiar_posicion(evento):
    actualizar_secundarias()


@when("click", "#tablaJugadores")
def al_tocar_en_jugadores(evento):
    boton = evento.target
    accion = boton.getAttribute("data-accion")
    if accion == "editar":
        editar_jugador(int(boton.getAttribute("data-indice")))
    elif accion == "borrar":
        borrar_jugador(int(boton.getAttribute("data-indice")))


@when("change", "#tablaJugadores")
def al_tildar_juega(evento):
    casilla = evento.target
    if casilla.getAttribute("data-accion") == "juega":
        cambiar_juega(int(casilla.getAttribute("data-indice")), casilla.checked)


@when("click", "#botonArmar")
def al_tocar_armar(evento):
    armar_equipos(False)


@when("click", "#botonOtra")
def al_tocar_otra(evento):
    armar_equipos(True)


@when("click", "#equipos")
def al_tocar_en_equipos(evento):
    boton = evento.target
    if boton.getAttribute("data-accion") == "renombrar":
        renombrar_equipo(int(boton.getAttribute("data-equipo")))


@when("change", "#equipos")
def al_mover_jugador(evento):
    lista = evento.target
    if lista.getAttribute("data-accion") == "mover":
        mover_jugador(
            int(lista.getAttribute("data-equipo")),
            int(lista.getAttribute("data-lugar")),
            int(lista.value),
        )


@when("click", "#botonTorneo")
def al_tocar_torneo(evento):
    armar_torneo()


@when("click", "#fixture")
def al_tocar_en_fixture(evento):
    boton = evento.target
    if boton.getAttribute("data-accion") == "resultado":
        guardar_resultado(int(boton.getAttribute("data-partido")))


@when("click", "#botonBorrarTodo")
def al_tocar_borrar_todo(evento):
    borrar_todo()


# ---------- ARRANQUE ----------

cargar()
document.getElementById("formato").value = str(formato_actual)
mostrar_todo()

# Python ya cargó: sacamos el cartel de "Cargando" y mostramos la página
document.getElementById("cargando").hidden = True
document.getElementById("contenido").hidden = False
