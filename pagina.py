# ==========================================
# pagina.py - Fulbito en la página web
# ==========================================
# Este archivo hace funcionar la página (index.html).
# Corre dentro del navegador gracias a PyScript.
# Las cuentas están en logica.py.
#
# En index.html cada botón dice qué función de acá llama. Por ejemplo:
#     <button py-click="tocar_armar">
# llama a la función tocar_armar cuando lo tocan.
# Esas funciones reciben el "evento": ahí dice qué botón se tocó.

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


# ---------- GUARDAR Y CARGAR ----------
# Los datos se guardan en el navegador (en "localStorage") con el nombre "fulbito".

def guardar_datos():
    window.localStorage.setItem("fulbito", json.dumps(datos))


def cargar_datos():
    texto = window.localStorage.getItem("fulbito")
    # Si no había nada guardado, no hay texto
    if not texto:
        return
    leidos = json.loads(texto)
    logica.arreglar_datos(leidos)
    datos["jugadores"] = leidos["jugadores"]
    datos["equipos"] = leidos["equipos"]
    datos["partidos"] = leidos["partidos"]
    datos["combinacionesVistas"] = leidos["combinacionesVistas"]
    datos["formatoActual"] = leidos["formatoActual"]


# ---------- COSAS CHICAS ----------

# Cambia los símbolos especiales para que un nombre como "<b>Juan</b>"
# se vea tal cual y no rompa la página
def escapar(texto):
    texto = str(texto)
    texto = texto.replace("&", "&amp;")
    texto = texto.replace("<", "&lt;")
    texto = texto.replace(">", "&gt;")
    texto = texto.replace('"', "&quot;")
    texto = texto.replace("'", "&#39;")
    return texto


# Muestra un mensaje. "tipo" es "ok" (verde), "error" (rojo) o "" (normal).
def mostrar_mensaje(id_mensaje, texto, tipo):
    mensaje = document.getElementById(id_mensaje)
    mensaje.textContent = texto
    mensaje.className = "mensaje " + tipo


# ---------- JUGADORES ----------

def leer_secundarias():
    secundarias = []
    for casilla in document.querySelectorAll('input[name="secundaria"]'):
        if casilla.checked:
            secundarias.append(casilla.value)
    return secundarias


# La posición principal no puede ser también secundaria: la destildamos y la bloqueamos
def actualizar_secundarias():
    principal = document.getElementById("posicion").value
    for casilla in document.querySelectorAll('input[name="secundaria"]'):
        if casilla.value == principal:
            casilla.checked = False
            casilla.disabled = True
        else:
            casilla.disabled = False


def tocar_posicion(evento):
    actualizar_secundarias()


def tocar_guardar_jugador(evento):
    nombre = document.getElementById("nombre").value.strip()
    numeros = {}
    for atributo in logica.ATRIBUTOS:
        numeros[atributo] = logica.convertir_numero(document.getElementById(atributo).value)
    posicion = document.getElementById("posicion").value
    secundarias = leer_secundarias()

    error = logica.revisar_jugador(nombre, numeros, posicion)
    if error != "":
        mostrar_mensaje("mensajeJugador", error, "error")
        return

    es_nuevo = logica.guardar_jugador(datos["jugadores"], nombre, numeros, posicion, secundarias)
    jugador = logica.buscar_jugador(datos["jugadores"], nombre)
    media = logica.redondear(logica.media_jugador(jugador))
    if es_nuevo:
        mostrar_mensaje("mensajeJugador", "Listo: " + jugador["nombre"] + ", media " + media + ".", "ok")
    else:
        mostrar_mensaje("mensajeJugador", "Actualizado: " + jugador["nombre"] + ", media " + media + ".", "ok")

    # Dejamos el formulario vacío para cargar otro
    document.getElementById("formJugador").reset()
    actualizar_secundarias()
    document.getElementById("nombre").focus()
    guardar_datos()
    mostrar_todo()


# Pone los datos de un jugador en el formulario para cambiarlos
def tocar_editar(evento):
    indice = int(evento.target.getAttribute("data-indice"))
    jugador = datos["jugadores"][indice]

    document.getElementById("nombre").value = jugador["nombre"]
    for atributo in logica.ATRIBUTOS:
        document.getElementById(atributo).value = str(jugador[atributo])
    document.getElementById("posicion").value = jugador["posicion"]
    for casilla in document.querySelectorAll('input[name="secundaria"]'):
        casilla.checked = casilla.value in jugador["secundarias"]
    actualizar_secundarias()

    mostrar_mensaje("mensajeJugador", "Cambiá lo que quieras y tocá Guardar jugador.", "")
    document.getElementById("ritmo").focus()


def tocar_borrar(evento):
    indice = int(evento.target.getAttribute("data-indice"))
    jugador = datos["jugadores"][indice]

    if logica.esta_en_un_equipo(datos["equipos"], jugador["nombre"]):
        mostrar_mensaje("mensajeJugador", jugador["nombre"] + " está en un equipo. Armá equipos nuevos antes de borrarlo.", "error")
        return
    if not window.confirm("¿Borrar a " + jugador["nombre"] + "?"):
        return

    datos["jugadores"].pop(indice)
    guardar_datos()
    mostrar_todo()


# Tildar o destildar "Juega"
def tocar_juega(evento):
    indice = int(evento.target.getAttribute("data-indice"))
    datos["jugadores"][indice]["juega"] = evento.target.checked
    guardar_datos()


def mostrar_jugadores():
    tabla = document.getElementById("tablaJugadores")
    if len(datos["jugadores"]) == 0:
        tabla.innerHTML = '<tr><td colspan="9">Todavía no cargaste jugadores.</td></tr>'
        return

    filas = ""
    for i in range(len(datos["jugadores"])):
        jugador = datos["jugadores"][i]
        tildado = ""
        if jugador["juega"]:
            tildado = "checked"

        filas = filas + "<tr>"
        filas = filas + '<td><input type="checkbox" ' + tildado + ' py-change="tocar_juega" data-indice="' + str(i) + '"></td>'
        filas = filas + '<td class="nombre">' + escapar(jugador["nombre"]) + "</td>"
        filas = filas + '<td class="posicion">' + logica.texto_posiciones(jugador) + "</td>"
        for atributo in logica.ATRIBUTOS:
            filas = filas + "<td>" + str(jugador[atributo]) + "</td>"
        filas = filas + "<td><b>" + logica.redondear(logica.media_jugador(jugador)) + "</b></td>"
        filas = filas + "<td>"
        filas = filas + '<button class="chico secundario" py-click="tocar_editar" data-indice="' + str(i) + '">Editar</button> '
        filas = filas + '<button class="chico peligro" py-click="tocar_borrar" data-indice="' + str(i) + '">Borrar</button>'
        filas = filas + "</td>"
        filas = filas + "</tr>"
    tabla.innerHTML = filas


# ---------- EQUIPOS ----------

def tocar_armar(evento):
    armar(False)


def tocar_otra(evento):
    armar(True)


# Arma equipos parejos. Si "es_otra" es True, no repite las combinaciones que ya salieron.
def armar(es_otra):
    formato = int(document.getElementById("formato").value)
    cantidad = logica.convertir_numero(document.getElementById("cantidadEquipos").value)
    usar_posiciones = document.getElementById("usarPosiciones").checked

    if cantidad == None or cantidad < 2:
        mostrar_mensaje("mensajeEquipos", "Tienen que ser al menos 2 equipos.", "error")
        return

    juegan = []
    for jugador in datos["jugadores"]:
        if jugador["juega"]:
            juegan.append(jugador)

    necesarios = formato * cantidad
    if len(juegan) < necesarios:
        faltan = necesarios - len(juegan)
        texto = "Faltan " + str(faltan) + " jugador(es): para " + str(cantidad) + " equipos de F" + str(formato)
        texto = texto + " se necesitan " + str(necesarios) + " y juegan " + str(len(juegan)) + ". No inventamos jugadores."
        mostrar_mensaje("mensajeEquipos", texto, "error")
        return

    if len(datos["partidos"]) > 0:
        if not window.confirm("Hay un torneo armado. Si cambiás los equipos se borra el torneo. ¿Seguir?"):
            return

    # "Armar" empieza de cero. "Otra combinación" agrega la actual a las ya vistas.
    if es_otra and len(datos["equipos"]) > 0:
        datos["combinacionesVistas"].append(logica.clave_de_equipos(datos["equipos"]))
    else:
        datos["combinacionesVistas"] = []

    equipos = logica.armar_equipos(juegan, cantidad, usar_posiciones, datos["combinacionesVistas"])
    if equipos == None:
        mostrar_mensaje("mensajeEquipos", "No hay otra combinación distinta de las que ya viste.", "error")
        return

    datos["equipos"] = equipos
    datos["formatoActual"] = formato
    datos["partidos"] = []

    texto = "¡Equipos armados!"
    sobran = len(juegan) - necesarios
    if sobran > 0:
        texto = texto + " Sobran " + str(sobran) + " jugador(es) para F" + str(formato) + ": quedan como suplentes."
    mostrar_mensaje("mensajeEquipos", texto, "ok")
    mostrar_mensaje("mensajeTorneo", "", "")
    guardar_datos()
    mostrar_todo()


# Cuando eligen otro equipo en la lista que está al lado de cada jugador
def tocar_mover(evento):
    nombre = evento.target.getAttribute("data-nombre")
    destino = int(evento.target.value)

    if logica.mover_jugador(datos["equipos"], nombre, destino):
        mostrar_mensaje("mensajeEquipos", nombre + " pasó a " + datos["equipos"][destino]["nombre"] + ".", "ok")
        guardar_datos()
    else:
        mostrar_mensaje("mensajeEquipos", "No podés dejar un equipo sin jugadores.", "error")
    mostrar_todo()


def tocar_renombrar(evento):
    indice = int(evento.target.getAttribute("data-equipo"))
    viejo = datos["equipos"][indice]["nombre"]
    nuevo = window.prompt("Nombre nuevo para " + viejo + ":", viejo)

    # Si tocan "Cancelar" o lo dejan vacío, no hacemos nada
    if not nuevo:
        return
    if nuevo.strip() == "":
        return

    if logica.renombrar_equipo(datos["equipos"], datos["partidos"], indice, nuevo):
        guardar_datos()
        mostrar_todo()
    else:
        mostrar_mensaje("mensajeEquipos", "Ya hay un equipo con ese nombre.", "error")


def mostrar_equipos():
    contenedor = document.getElementById("equipos")
    resumen = document.getElementById("resumenEquipos")
    equipos = datos["equipos"]

    if len(equipos) == 0:
        contenedor.innerHTML = "<p>Todavía no armaste equipos.</p>"
        resumen.textContent = ""
        return

    # Solo avisamos de arqueros si hay jugadores con posición cargada
    hay_posiciones = False
    for jugador in datos["jugadores"]:
        if jugador["posicion"] != "":
            hay_posiciones = True

    texto = ""
    for e in range(len(equipos)):
        equipo = equipos[e]
        lista = logica.jugadores_del_equipo(datos["jugadores"], equipo)
        puestos = logica.asignar_puestos(lista)
        cuenta = logica.contar_puestos(puestos)
        media = logica.redondear(logica.media_de_lista(lista, ""))

        medias = ""
        for atributo in logica.ATRIBUTOS:
            if medias != "":
                medias = medias + " · "
            medias = medias + logica.NOMBRES_ATRIBUTOS[atributo] + " "
            medias = medias + logica.redondear(logica.media_de_lista(lista, atributo))

        posiciones = ""
        for posicion in logica.POSICIONES:
            if posiciones != "":
                posiciones = posiciones + " · "
            posiciones = posiciones + str(cuenta[posicion]) + " " + posicion

        texto = texto + '<div class="equipo">'
        texto = texto + "<h3><span>" + escapar(equipo["nombre"]) + " — " + media + "</span>"
        texto = texto + '<button class="chico secundario" py-click="tocar_renombrar" data-equipo="' + str(e) + '">Renombrar</button></h3>'
        texto = texto + '<div class="medias">' + medias + "</div>"
        texto = texto + '<div class="medias">Posiciones: ' + posiciones + "</div>"

        if len(lista) < datos["formatoActual"]:
            formato = str(datos["formatoActual"])
            texto = texto + '<p class="mensaje error">Tiene ' + str(len(lista)) + " y F" + formato + " pide " + formato + ".</p>"
        if hay_posiciones and cuenta["ARQ"] == 0:
            texto = texto + '<p class="mensaje error">Nadie de este equipo juega de arquero.</p>'

        texto = texto + "<ul>"
        for jugador in logica.ordenar_para_mostrar(lista, puestos):
            puesto = puestos[jugador["nombre"]]

            # El cartelito con el puesto: lleno si es su posición principal,
            # blanco si juega de una posición secundaria
            cartel = ""
            if puesto == jugador["posicion"]:
                cartel = '<span class="puesto">' + puesto + "</span>"
            elif puesto != "":
                cartel = '<span class="puesto cambiado" title="Juega de su posición secundaria">' + puesto + "</span>"

            # Lista para mover al jugador a otro equipo
            opciones = ""
            for o in range(len(equipos)):
                elegido = ""
                if o == e:
                    elegido = "selected"
                opciones = opciones + '<option value="' + str(o) + '" ' + elegido + ">" + escapar(equipos[o]["nombre"]) + "</option>"

            texto = texto + "<li><span>" + cartel + " " + escapar(jugador["nombre"])
            texto = texto + ' <span class="posicion">' + logica.texto_posiciones(jugador) + "</span>"
            texto = texto + " (" + logica.redondear(logica.media_jugador(jugador)) + ")</span>"
            texto = texto + '<select title="Mover a otro equipo" py-change="tocar_mover" data-nombre="' + escapar(jugador["nombre"]) + '">'
            texto = texto + opciones + "</select></li>"
        texto = texto + "</ul></div>"

    contenedor.innerHTML = texto

    promedio = logica.promedio_de_equipos(datos["jugadores"], equipos)
    diferencia = logica.diferencia_entre_equipos(datos["jugadores"], equipos)
    texto = "Promedio de las medias: " + logica.redondear(promedio)
    texto = texto + " · Diferencia entre el más fuerte y el más débil: " + str(round(diferencia, 2))
    resumen.textContent = texto


# ---------- TORNEO ----------

def nombres_de_equipos():
    nombres = []
    for equipo in datos["equipos"]:
        nombres.append(equipo["nombre"])
    return nombres


def tocar_torneo(evento):
    if len(datos["equipos"]) < 2:
        mostrar_mensaje("mensajeTorneo", "Primero armá al menos 2 equipos.", "error")
        return
    if len(datos["partidos"]) > 0:
        if not window.confirm("Ya hay un torneo. Si armás otro se borran los resultados. ¿Seguir?"):
            return

    ida_y_vuelta = document.getElementById("idaYVuelta").checked
    datos["partidos"] = logica.crear_fixture(nombres_de_equipos(), ida_y_vuelta)
    mostrar_mensaje("mensajeTorneo", "Torneo armado: " + str(len(datos["partidos"])) + " partidos.", "ok")
    guardar_datos()
    mostrar_todo()


def tocar_guardar_resultado(evento):
    indice = int(evento.target.getAttribute("data-partido"))
    partido = datos["partidos"][indice]
    texto_local = document.getElementById("local" + str(indice)).value.strip()
    texto_visitante = document.getElementById("visitante" + str(indice)).value.strip()

    # Si borran los dos, el partido vuelve a "sin jugar"
    if texto_local == "" and texto_visitante == "":
        partido["golesLocal"] = None
        partido["golesVisitante"] = None
    else:
        goles_local = logica.convertir_numero(texto_local)
        goles_visitante = logica.convertir_numero(texto_visitante)
        if goles_local == None or goles_visitante == None:
            mostrar_mensaje("mensajeTorneo", "Los goles tienen que ser números enteros desde 0.", "error")
            return
        partido["golesLocal"] = goles_local
        partido["golesVisitante"] = goles_visitante

    mostrar_mensaje("mensajeTorneo", "Resultado guardado.", "ok")
    guardar_datos()
    mostrar_todo()


def mostrar_fixture():
    contenedor = document.getElementById("fixture")
    partidos = datos["partidos"]
    if len(partidos) == 0:
        contenedor.innerHTML = "<p>Todavía no armaste un torneo.</p>"
        return

    texto = ""
    for fecha in range(1, logica.ultima_fecha(partidos) + 1):
        texto = texto + '<div class="fecha"><h4>Fecha ' + str(fecha) + "</h4>"
        for i in range(len(partidos)):
            partido = partidos[i]
            if partido["fecha"] != fecha:
                continue

            goles_local = ""
            goles_visitante = ""
            if partido["golesLocal"] != None:
                goles_local = str(partido["golesLocal"])
                goles_visitante = str(partido["golesVisitante"])

            texto = texto + '<div class="partido">'
            texto = texto + "<span>" + escapar(partido["local"]) + "</span>"
            texto = texto + '<input type="number" min="0" id="local' + str(i) + '" value="' + goles_local + '">'
            texto = texto + "<span>-</span>"
            texto = texto + '<input type="number" min="0" id="visitante' + str(i) + '" value="' + goles_visitante + '">'
            texto = texto + "<span>" + escapar(partido["visitante"]) + "</span>"
            texto = texto + '<button class="chico" py-click="tocar_guardar_resultado" data-partido="' + str(i) + '">Guardar</button>'
            texto = texto + "</div>"

        libres = logica.libres_en_fecha(nombres_de_equipos(), partidos, fecha)
        if len(libres) > 0:
            texto = texto + '<p class="libre">Libre: ' + escapar(", ".join(libres)) + "</p>"
        texto = texto + "</div>"

    contenedor.innerHTML = texto


def mostrar_tabla_de_posiciones():
    tabla = document.getElementById("tablaPosiciones")
    if len(datos["partidos"]) == 0:
        tabla.innerHTML = ""
        return

    filas = logica.calcular_tabla(nombres_de_equipos(), datos["partidos"])
    texto = ""
    for i in range(len(filas)):
        fila = filas[i]
        diferencia = str(fila["dg"])
        if fila["dg"] > 0:
            diferencia = "+" + diferencia
        texto = texto + "<tr>"
        texto = texto + "<td>" + str(i + 1) + "</td>"
        texto = texto + '<td class="nombre">' + escapar(fila["equipo"]) + "</td>"
        texto = texto + "<td>" + str(fila["pj"]) + "</td>"
        texto = texto + "<td>" + str(fila["g"]) + "</td>"
        texto = texto + "<td>" + str(fila["e"]) + "</td>"
        texto = texto + "<td>" + str(fila["p"]) + "</td>"
        texto = texto + "<td>" + str(fila["gf"]) + "</td>"
        texto = texto + "<td>" + str(fila["gc"]) + "</td>"
        texto = texto + "<td>" + diferencia + "</td>"
        texto = texto + "<td><b>" + str(fila["pts"]) + "</b></td>"
        texto = texto + "</tr>"
    tabla.innerHTML = texto


# ---------- BORRAR TODO ----------

def tocar_borrar_todo(evento):
    if not window.confirm("¿Seguro? Se borran jugadores, equipos y torneo."):
        return
    datos["jugadores"] = []
    datos["equipos"] = []
    datos["partidos"] = []
    datos["combinacionesVistas"] = []
    guardar_datos()
    mostrar_todo()


# ---------- DIBUJAR TODO ----------

def mostrar_todo():
    mostrar_jugadores()
    mostrar_equipos()
    mostrar_fixture()
    mostrar_tabla_de_posiciones()


# ---------- ARRANQUE ----------

cargar_datos()
document.getElementById("formato").value = str(datos["formatoActual"])
mostrar_todo()

# Python ya cargó: sacamos el cartel de "Cargando" y mostramos la página
document.getElementById("cargando").hidden = True
document.getElementById("contenido").hidden = False
