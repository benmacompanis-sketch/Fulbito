# ==========================================
# pagina.py - El programa de la página web
# ==========================================
# Cada botón de index.html llama a una función de acá. Por ejemplo:
#     <button py-click="guardar_jugador">
# llama a la función guardar_jugador.
# Esas funciones reciben "evento" (lo que pasó), pero no hace falta usarlo.
#
# Las cuentas están en logica.py.

import json
from pyscript import document, window
import logica

# Acá está todo: jugadores, equipos y torneo
datos = {
    "jugadores": [],
    "equipos": [],
    "partidos": [],
    "combinacionesVistas": [],
    "formatoActual": 5,
}


# ---------- LEER Y ESCRIBIR EN LA PÁGINA ----------

# Devuelve lo que está escrito en una casilla
def leer(id_casilla):
    return document.getElementById(id_casilla).value


# Escribe algo en una casilla
def poner(id_casilla, texto):
    document.getElementById(id_casilla).value = texto


# Devuelve True si la casilla está tildada
def tildado(id_casilla):
    return document.getElementById(id_casilla).checked


# Pone HTML adentro de un elemento de la página
def mostrar_html(id_elemento, html):
    document.getElementById(id_elemento).innerHTML = html


# Muestra un mensaje. tipo puede ser "ok" (verde) o "error" (rojo).
def mostrar_mensaje(id_mensaje, texto, tipo):
    mensaje = document.getElementById(id_mensaje)
    mensaje.innerHTML = texto
    mensaje.className = "mensaje " + tipo


# Para que un nombre con < o > no rompa la página
def limpiar(texto):
    texto = texto.replace("<", "&lt;")
    texto = texto.replace(">", "&gt;")
    return texto


# ---------- GUARDAR EN EL NAVEGADOR ----------
# Los datos se guardan en el navegador con el nombre "fulbito"

def guardar_datos():
    window.localStorage.setItem("fulbito", json.dumps(datos))


def cargar_datos():
    texto = window.localStorage.getItem("fulbito")
    if not texto:
        return  # todavía no había nada guardado
    leidos = json.loads(texto)
    logica.arreglar_datos(leidos)
    datos["jugadores"] = leidos["jugadores"]
    datos["equipos"] = leidos["equipos"]
    datos["partidos"] = leidos["partidos"]
    datos["combinacionesVistas"] = leidos["combinacionesVistas"]
    datos["formatoActual"] = leidos["formatoActual"]


# ---------- 1. JUGADORES ----------

def guardar_jugador(evento):
    nombre = leer("nombre").strip()
    numeros = {}
    for atributo in logica.ATRIBUTOS:
        numeros[atributo] = logica.convertir_numero(leer(atributo))
    posicion = leer("posicion")

    secundarias = []
    for otra in logica.POSICIONES:
        if tildado("secundaria_" + otra):
            secundarias.append(otra)

    error = logica.revisar_jugador(nombre, numeros, posicion)
    if error != "":
        mostrar_mensaje("mensaje_jugador", error, "error")
        return

    es_nuevo = logica.guardar_jugador(datos["jugadores"], nombre, numeros, posicion, secundarias)
    if es_nuevo:
        mostrar_mensaje("mensaje_jugador", "Listo, se guardó a " + limpiar(nombre) + ".", "ok")
    else:
        mostrar_mensaje("mensaje_jugador", "Se actualizaron los datos de " + limpiar(nombre) + ".", "ok")

    # Vaciamos el formulario para cargar otro
    poner("nombre", "")
    for atributo in logica.ATRIBUTOS:
        poner(atributo, "")
    poner("posicion", "")
    for otra in logica.POSICIONES:
        document.getElementById("secundaria_" + otra).checked = False

    guardar_datos()
    mostrar_todo()


# Devuelve el jugador del número escrito en la casilla, o None si el número está mal
def jugador_elegido(id_casilla, id_mensaje):
    numero = logica.convertir_numero(leer(id_casilla))
    if numero == None or numero < 1 or numero > len(datos["jugadores"]):
        mostrar_mensaje(id_mensaje, "Poné un número de jugador de la tabla.", "error")
        return None
    return datos["jugadores"][numero - 1]


# Pone los datos del jugador en el formulario para cambiarlos
def editar_jugador(evento):
    jugador = jugador_elegido("numero_jugador", "mensaje_jugador")
    if jugador == None:
        return

    poner("nombre", jugador["nombre"])
    for atributo in logica.ATRIBUTOS:
        poner(atributo, str(jugador[atributo]))
    poner("posicion", jugador["posicion"])
    for otra in logica.POSICIONES:
        casilla = document.getElementById("secundaria_" + otra)
        casilla.checked = otra in jugador["secundarias"]
    mostrar_mensaje("mensaje_jugador", "Cambiá lo que quieras arriba y tocá Guardar jugador.", "")


def cambiar_juega(evento):
    jugador = jugador_elegido("numero_jugador", "mensaje_jugador")
    if jugador == None:
        return

    if jugador["juega"]:
        jugador["juega"] = False
        mostrar_mensaje("mensaje_jugador", limpiar(jugador["nombre"]) + " no juega.", "ok")
    else:
        jugador["juega"] = True
        mostrar_mensaje("mensaje_jugador", limpiar(jugador["nombre"]) + " juega.", "ok")
    guardar_datos()
    mostrar_todo()


def borrar_jugador(evento):
    jugador = jugador_elegido("numero_jugador", "mensaje_jugador")
    if jugador == None:
        return

    if logica.esta_en_un_equipo(datos["equipos"], jugador["nombre"]):
        mostrar_mensaje("mensaje_jugador", limpiar(jugador["nombre"]) + " está en un equipo. Armá equipos nuevos antes de borrarlo.", "error")
        return
    if not window.confirm("¿Borrar a " + jugador["nombre"] + "?"):
        return

    datos["jugadores"].remove(jugador)
    mostrar_mensaje("mensaje_jugador", "Jugador borrado.", "ok")
    guardar_datos()
    mostrar_todo()


def mostrar_jugadores():
    if len(datos["jugadores"]) == 0:
        mostrar_html("tabla_jugadores", '<tr><td colspan="9">Todavía no cargaste jugadores.</td></tr>')
        return

    html = ""
    numero = 1
    for jugador in datos["jugadores"]:
        juega = "No"
        if jugador["juega"]:
            juega = "Sí"
        media = str(round(logica.media_jugador(jugador), 1))

        html = html + "<tr>"
        html = html + "<td>" + str(numero) + "</td>"
        html = html + "<td>" + juega + "</td>"
        html = html + "<td>" + limpiar(jugador["nombre"]) + "</td>"
        html = html + "<td>" + logica.texto_posiciones(jugador) + "</td>"
        html = html + "<td>" + str(jugador["ritmo"]) + "</td>"
        html = html + "<td>" + str(jugador["pase"]) + "</td>"
        html = html + "<td>" + str(jugador["regate"]) + "</td>"
        html = html + "<td>" + str(jugador["defensa"]) + "</td>"
        html = html + "<td><b>" + media + "</b></td>"
        html = html + "</tr>"
        numero = numero + 1

    mostrar_html("tabla_jugadores", html)


# ---------- 2. EQUIPOS ----------

def armar_equipos(evento):
    armar(False)


def otra_combinacion(evento):
    armar(True)


# Arma los equipos. Si es_otra es True, no repite las combinaciones que ya salieron.
def armar(es_otra):
    formato = logica.convertir_numero(leer("formato"))
    cantidad = logica.convertir_numero(leer("cantidad_equipos"))
    usar_posiciones = tildado("usar_posiciones")

    if cantidad == None or cantidad < 2:
        mostrar_mensaje("mensaje_equipos", "Tienen que ser al menos 2 equipos.", "error")
        return

    juegan = []
    for jugador in datos["jugadores"]:
        if jugador["juega"]:
            juegan.append(jugador)

    necesarios = formato * cantidad
    if len(juegan) < necesarios:
        faltan = necesarios - len(juegan)
        texto = "Faltan " + str(faltan) + " jugadores: se necesitan " + str(necesarios)
        texto = texto + " y juegan " + str(len(juegan)) + ". No inventamos jugadores."
        mostrar_mensaje("mensaje_equipos", texto, "error")
        return

    if len(datos["partidos"]) > 0:
        if not window.confirm("Hay un torneo armado. Si cambiás los equipos se borra. ¿Seguir?"):
            return

    # "Armar" empieza de cero. "Otra combinación" se acuerda de las que ya salieron.
    if es_otra and len(datos["equipos"]) > 0:
        datos["combinacionesVistas"].append(logica.clave_de_equipos(datos["equipos"]))
    else:
        datos["combinacionesVistas"] = []

    equipos = logica.armar_equipos(juegan, cantidad, usar_posiciones, datos["combinacionesVistas"])
    if equipos == None:
        mostrar_mensaje("mensaje_equipos", "No encontré otra combinación distinta.", "error")
        return

    datos["equipos"] = equipos
    datos["formatoActual"] = formato
    datos["partidos"] = []

    texto = "¡Equipos armados!"
    sobran = len(juegan) - necesarios
    if sobran > 0:
        texto = texto + " Sobran " + str(sobran) + " jugadores: quedan de suplentes."
    mostrar_mensaje("mensaje_equipos", texto, "ok")
    mostrar_mensaje("mensaje_torneo", "", "")
    guardar_datos()
    mostrar_todo()


def mover_jugador(evento):
    jugador = jugador_elegido("mover_jugador", "mensaje_equipos")
    if jugador == None:
        return

    numero_equipo = logica.convertir_numero(leer("mover_equipo"))
    if numero_equipo == None or numero_equipo < 1 or numero_equipo > len(datos["equipos"]):
        mostrar_mensaje("mensaje_equipos", "Poné un número de equipo que exista.", "error")
        return

    if logica.mover_jugador(datos["equipos"], jugador["nombre"], numero_equipo - 1):
        equipo = datos["equipos"][numero_equipo - 1]
        mostrar_mensaje("mensaje_equipos", limpiar(jugador["nombre"]) + " pasó a " + limpiar(equipo["nombre"]) + ".", "ok")
        guardar_datos()
        mostrar_todo()
    else:
        mostrar_mensaje("mensaje_equipos", "No se puede: no está en un equipo o su equipo quedaría vacío.", "error")


def renombrar_equipo(evento):
    numero_equipo = logica.convertir_numero(leer("renombrar_numero"))
    nuevo = leer("renombrar_nombre").strip()

    if numero_equipo == None or numero_equipo < 1 or numero_equipo > len(datos["equipos"]):
        mostrar_mensaje("mensaje_equipos", "Poné un número de equipo que exista.", "error")
        return
    if nuevo == "":
        mostrar_mensaje("mensaje_equipos", "Escribí el nombre nuevo.", "error")
        return

    if logica.renombrar_equipo(datos["equipos"], datos["partidos"], numero_equipo - 1, nuevo):
        mostrar_mensaje("mensaje_equipos", "Listo, ahora se llama " + limpiar(nuevo) + ".", "ok")
        poner("renombrar_nombre", "")
        guardar_datos()
        mostrar_todo()
    else:
        mostrar_mensaje("mensaje_equipos", "Ya hay un equipo con ese nombre.", "error")


def mostrar_equipos():
    equipos = datos["equipos"]
    if len(equipos) == 0:
        mostrar_html("equipos", "<p>Todavía no armaste equipos.</p>")
        mostrar_html("resumen_equipos", "")
        return

    html = ""
    numero_equipo = 1
    for equipo in equipos:
        lista = logica.jugadores_del_equipo(datos["jugadores"], equipo)
        puestos = logica.puestos_del_equipo(lista)
        cuenta = logica.contar_puestos(puestos)
        media = str(round(logica.media_de_lista(lista, ""), 1))

        html = html + '<div class="equipo">'
        html = html + "<h3>" + str(numero_equipo) + ". " + limpiar(equipo["nombre"]) + " (media " + media + ")</h3>"

        # Medias de cada atributo
        html = html + '<p class="gris">'
        for atributo in logica.ATRIBUTOS:
            html = html + logica.NOMBRES_ATRIBUTOS[atributo] + " " + str(round(logica.media_de_lista(lista, atributo), 1)) + " &nbsp; "
        html = html + "<br>"
        # Cuántos hay en cada puesto
        for puesto in logica.POSICIONES:
            html = html + puesto + ": " + str(cuenta[puesto]) + " &nbsp; "
        html = html + "</p>"

        # Avisos
        if len(lista) < datos["formatoActual"]:
            html = html + '<p class="error">Tiene menos jugadores de los que pide el formato.</p>'
        if cuenta["ARQ"] == 0:
            html = html + '<p class="error">Nadie de este equipo juega de arquero.</p>'

        # Jugadores en orden: arquero, defensores, medios y delanteros
        html = html + "<ul>"
        for jugador in logica.ordenar_para_mostrar(lista, puestos):
            puesto = puestos[jugador["nombre"]]
            texto_puesto = puesto
            if puesto == "":
                texto_puesto = "---"
            numero_jugador = datos["jugadores"].index(jugador) + 1
            html = html + "<li><b>" + texto_puesto + "</b> - N° " + str(numero_jugador) + " " + limpiar(jugador["nombre"])
            if puesto != jugador["posicion"]:
                html = html + " (juega de secundaria)"
            html = html + ' <span class="gris">' + logica.texto_posiciones(jugador)
            html = html + " - media " + str(round(logica.media_jugador(jugador), 1)) + "</span></li>"
        html = html + "</ul>"
        html = html + "</div>"
        numero_equipo = numero_equipo + 1

    mostrar_html("equipos", html)

    promedio = round(logica.promedio_de_equipos(datos["jugadores"], equipos), 1)
    diferencia = round(logica.diferencia_entre_equipos(datos["jugadores"], equipos), 2)
    texto = "Promedio de las medias: " + str(promedio)
    texto = texto + " - Diferencia entre el más fuerte y el más débil: " + str(diferencia)
    mostrar_html("resumen_equipos", texto)


# ---------- 3. TORNEO ----------

def nombres_de_equipos():
    nombres = []
    for equipo in datos["equipos"]:
        nombres.append(equipo["nombre"])
    return nombres


def armar_torneo(evento):
    if len(datos["equipos"]) < 2:
        mostrar_mensaje("mensaje_torneo", "Primero armá al menos 2 equipos.", "error")
        return
    if len(datos["partidos"]) > 0:
        if not window.confirm("Ya hay un torneo. Si armás otro se borran los resultados. ¿Seguir?"):
            return

    datos["partidos"] = logica.crear_fixture(nombres_de_equipos(), tildado("ida_y_vuelta"))
    mostrar_mensaje("mensaje_torneo", "Torneo armado: " + str(len(datos["partidos"])) + " partidos.", "ok")
    guardar_datos()
    mostrar_todo()


def guardar_resultado(evento):
    numero = logica.convertir_numero(leer("numero_partido"))
    goles_local = logica.convertir_numero(leer("goles_local"))
    goles_visitante = logica.convertir_numero(leer("goles_visitante"))

    if numero == None or numero < 1 or numero > len(datos["partidos"]):
        mostrar_mensaje("mensaje_torneo", "Poné un número de partido del fixture.", "error")
        return
    if goles_local == None or goles_visitante == None:
        mostrar_mensaje("mensaje_torneo", "Los goles tienen que ser números desde 0.", "error")
        return

    partido = datos["partidos"][numero - 1]
    partido["golesLocal"] = goles_local
    partido["golesVisitante"] = goles_visitante
    mostrar_mensaje("mensaje_torneo", "Resultado guardado.", "ok")
    poner("numero_partido", "")
    poner("goles_local", "")
    poner("goles_visitante", "")
    guardar_datos()
    mostrar_todo()


def mostrar_fixture():
    partidos = datos["partidos"]
    if len(partidos) == 0:
        mostrar_html("fixture", "<p>Todavía no armaste un torneo.</p>")
        return

    html = ""
    for fecha in range(1, logica.ultima_fecha(partidos) + 1):
        html = html + "<h4>Fecha " + str(fecha) + "</h4><ul>"
        numero = 1
        for partido in partidos:
            if partido["fecha"] == fecha:
                if partido["golesLocal"] == None:
                    resultado = "sin jugar"
                else:
                    resultado = str(partido["golesLocal"]) + " a " + str(partido["golesVisitante"])
                html = html + "<li>Partido " + str(numero) + ": " + limpiar(partido["local"])
                html = html + " vs " + limpiar(partido["visitante"]) + " - <b>" + resultado + "</b></li>"
            numero = numero + 1
        libres = logica.libres_en_fecha(nombres_de_equipos(), partidos, fecha)
        if len(libres) > 0:
            html = html + '<li class="gris">Libre: ' + limpiar(", ".join(libres)) + "</li>"
        html = html + "</ul>"

    mostrar_html("fixture", html)


def mostrar_tabla_de_posiciones():
    if len(datos["partidos"]) == 0:
        mostrar_html("tabla_posiciones", "")
        return

    filas = logica.calcular_tabla(nombres_de_equipos(), datos["partidos"])
    html = ""
    posicion = 1
    for fila in filas:
        html = html + "<tr>"
        html = html + "<td>" + str(posicion) + "</td>"
        html = html + "<td>" + limpiar(fila["equipo"]) + "</td>"
        html = html + "<td>" + str(fila["pj"]) + "</td>"
        html = html + "<td>" + str(fila["g"]) + "</td>"
        html = html + "<td>" + str(fila["e"]) + "</td>"
        html = html + "<td>" + str(fila["p"]) + "</td>"
        html = html + "<td>" + str(fila["gf"]) + "</td>"
        html = html + "<td>" + str(fila["gc"]) + "</td>"
        html = html + "<td>" + str(fila["dg"]) + "</td>"
        html = html + "<td><b>" + str(fila["pts"]) + "</b></td>"
        html = html + "</tr>"
        posicion = posicion + 1

    mostrar_html("tabla_posiciones", html)


# ---------- BORRAR TODO ----------

def borrar_todo(evento):
    if not window.confirm("¿Seguro? Se borran jugadores, equipos y torneo."):
        return
    datos["jugadores"] = []
    datos["equipos"] = []
    datos["partidos"] = []
    datos["combinacionesVistas"] = []
    guardar_datos()
    mostrar_todo()


# ---------- MOSTRAR TODO ----------

def mostrar_todo():
    mostrar_jugadores()
    mostrar_equipos()
    mostrar_fixture()
    mostrar_tabla_de_posiciones()


# ---------- ARRANQUE ----------
# Esto se hace una sola vez, cuando abre la página

cargar_datos()
poner("formato", str(datos["formatoActual"]))
mostrar_todo()
mostrar_html("cargando", "")
