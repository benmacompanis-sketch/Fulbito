# ==========================================
# pagina.py - El programa de la página web
# ==========================================
# Cada botón de index.html llama a una función de este archivo. Por ejemplo:
#     <button py-click="al_tocar_guardar_jugador">Guardar jugador</button>
# llama a la función al_tocar_guardar_jugador cuando alguien toca ese botón.
#
# Todas las funciones de botones se llaman "al_tocar_" + el texto del botón.
# Reciben "evento" (lo que pasó), pero no hace falta usarlo.
#
# Las cuentas (medias, armar equipos, fixture, tabla) están en logica.py.

import json
from pyscript import document, window
import logica

# Acá está todo lo que carga el usuario: jugadores, equipos y torneo.
# OJO: no cambiar estos nombres ("combinacionesVistas", "formatoActual", etc.)
# porque así quedan guardados en el navegador. Si se cambian, se pierden los datos.
todos_los_datos = {
    "jugadores": [],            # todos los jugadores cargados
    "equipos": [],              # los equipos armados
    "partidos": [],             # los partidos del torneo
    "combinacionesVistas": [],  # combinaciones de equipos que ya salieron (para no repetirlas)
    "formatoActual": 5,         # jugadores por equipo: 5, 8 u 11
}


# ---------- LEER Y ESCRIBIR EN LA PÁGINA ----------
# Cada casilla y cada lugar de la página tiene un "id" (su nombre) en index.html.
# Por ejemplo: <input type="text" id="nombre_del_jugador">

# Devuelve lo que está escrito en una casilla
def leer_casilla(id_de_la_casilla):
    return document.getElementById(id_de_la_casilla).value


# Escribe un texto en una casilla
def escribir_en_casilla(id_de_la_casilla, texto):
    document.getElementById(id_de_la_casilla).value = texto


# Devuelve True si la casilla para tildar está tildada
def casilla_esta_tildada(id_de_la_casilla):
    return document.getElementById(id_de_la_casilla).checked


# Tilda (True) o destilda (False) una casilla para tildar
def tildar_casilla(id_de_la_casilla, tildada):
    document.getElementById(id_de_la_casilla).checked = tildada


# Pone HTML adentro de un lugar de la página
def mostrar_html(id_del_lugar, html):
    document.getElementById(id_del_lugar).innerHTML = html


# Muestra un mensaje normal
def mostrar_mensaje(id_del_mensaje, texto):
    mostrar_html(id_del_mensaje, texto)


# Muestra un mensaje de error, en negrita
def mostrar_error(id_del_mensaje, texto):
    mostrar_html(id_del_mensaje, "<b>Error: " + texto + "</b>")


# Para que un nombre con < o > no rompa la página.
# Ejemplo: "<Juan>" se cambia por "&lt;Juan&gt;", que en la página se ve igual.
def texto_seguro(texto):
    texto = texto.replace("<", "&lt;")
    texto = texto.replace(">", "&gt;")
    return texto


# ---------- GUARDAR EN EL NAVEGADOR ----------
# Los datos se guardan en el navegador con el nombre "fulbito",
# así no se pierden al cerrar la página.

def guardar_en_el_navegador():
    texto_para_guardar = json.dumps(todos_los_datos)  # pasa los datos a texto
    window.localStorage.setItem("fulbito", texto_para_guardar)


def cargar_del_navegador():
    texto_guardado = window.localStorage.getItem("fulbito")
    if not texto_guardado:
        return  # todavía no había nada guardado

    datos_leidos = json.loads(texto_guardado)  # pasa el texto a datos
    logica.completar_datos_viejos(datos_leidos)
    todos_los_datos["jugadores"] = datos_leidos["jugadores"]
    todos_los_datos["equipos"] = datos_leidos["equipos"]
    todos_los_datos["partidos"] = datos_leidos["partidos"]
    todos_los_datos["combinacionesVistas"] = datos_leidos["combinacionesVistas"]
    todos_los_datos["formatoActual"] = datos_leidos["formatoActual"]


# ---------- 1. JUGADORES ----------

def al_tocar_guardar_jugador(evento):
    # Leemos lo que escribió el usuario
    nombre = leer_casilla("nombre_del_jugador").strip()

    valores_de_atributos = {}
    for atributo in logica.ATRIBUTOS:
        # La casilla de cada atributo se llama igual que el atributo: "ritmo", "pase", etc.
        valores_de_atributos[atributo] = logica.convertir_texto_a_numero(leer_casilla(atributo))

    posicion_principal = leer_casilla("posicion_principal")

    posiciones_secundarias = []
    for posicion in logica.POSICIONES:
        if casilla_esta_tildada("secundaria_" + posicion):
            posiciones_secundarias.append(posicion)

    # Revisamos que esté todo bien
    error = logica.buscar_error_en_jugador(nombre, valores_de_atributos, posicion_principal)
    if error != "":
        mostrar_error("mensaje_jugador", error)
        return

    # Guardamos al jugador
    jugador_es_nuevo = logica.agregar_o_actualizar_jugador(todos_los_datos["jugadores"], nombre, valores_de_atributos, posicion_principal, posiciones_secundarias)
    if jugador_es_nuevo:
        mostrar_mensaje("mensaje_jugador", "Listo, se guardó a " + texto_seguro(nombre) + ".")
    else:
        mostrar_mensaje("mensaje_jugador", "Se actualizaron los datos de " + texto_seguro(nombre) + ".")

    vaciar_formulario_de_jugador()
    guardar_en_el_navegador()
    actualizar_toda_la_pagina()


# Deja el formulario del jugador en blanco, para cargar otro
def vaciar_formulario_de_jugador():
    escribir_en_casilla("nombre_del_jugador", "")
    for atributo in logica.ATRIBUTOS:
        escribir_en_casilla(atributo, "")
    escribir_en_casilla("posicion_principal", "")
    for posicion in logica.POSICIONES:
        tildar_casilla("secundaria_" + posicion, False)


# Lee el número de jugador escrito en una casilla y devuelve ese jugador.
# Si el número está mal, muestra un error y devuelve None.
def buscar_jugador_por_numero(id_de_la_casilla, id_del_mensaje):
    numero_de_jugador = logica.convertir_texto_a_numero(leer_casilla(id_de_la_casilla))
    cantidad_de_jugadores = len(todos_los_datos["jugadores"])

    if numero_de_jugador == None or numero_de_jugador < 1 or numero_de_jugador > cantidad_de_jugadores:
        mostrar_error(id_del_mensaje, "Poné un número de jugador de la tabla.")
        return None

    # Restamos 1 porque en la tabla se cuenta desde 1, pero las listas de Python empiezan en 0
    return todos_los_datos["jugadores"][numero_de_jugador - 1]


# Pone los datos del jugador en el formulario de arriba para cambiarlos
def al_tocar_editar(evento):
    jugador = buscar_jugador_por_numero("numero_de_jugador", "mensaje_jugador")
    if jugador == None:
        return

    escribir_en_casilla("nombre_del_jugador", jugador["nombre"])
    for atributo in logica.ATRIBUTOS:
        escribir_en_casilla(atributo, str(jugador[atributo]))
    escribir_en_casilla("posicion_principal", jugador["posicion"])
    for posicion in logica.POSICIONES:
        puede_jugar_de_esto = posicion in jugador["secundarias"]
        tildar_casilla("secundaria_" + posicion, puede_jugar_de_esto)

    mostrar_mensaje("mensaje_jugador", "Cambiá lo que quieras arriba y tocá Guardar jugador.")


def al_tocar_juega_no_juega(evento):
    jugador = buscar_jugador_por_numero("numero_de_jugador", "mensaje_jugador")
    if jugador == None:
        return

    if jugador["juega"]:
        jugador["juega"] = False
        mostrar_mensaje("mensaje_jugador", texto_seguro(jugador["nombre"]) + " no juega.")
    else:
        jugador["juega"] = True
        mostrar_mensaje("mensaje_jugador", texto_seguro(jugador["nombre"]) + " juega.")

    guardar_en_el_navegador()
    actualizar_toda_la_pagina()


def al_tocar_borrar(evento):
    jugador = buscar_jugador_por_numero("numero_de_jugador", "mensaje_jugador")
    if jugador == None:
        return

    if logica.jugador_esta_en_algun_equipo(todos_los_datos["equipos"], jugador["nombre"]):
        mostrar_error("mensaje_jugador", texto_seguro(jugador["nombre"]) + " está en un equipo. Armá equipos nuevos antes de borrarlo.")
        return

    quiere_borrarlo = window.confirm("¿Borrar a " + jugador["nombre"] + "?")
    if not quiere_borrarlo:
        return

    todos_los_datos["jugadores"].remove(jugador)
    mostrar_mensaje("mensaje_jugador", "Jugador borrado.")
    guardar_en_el_navegador()
    actualizar_toda_la_pagina()


def mostrar_tabla_de_jugadores():
    jugadores = todos_los_datos["jugadores"]
    if len(jugadores) == 0:
        mostrar_html("tabla_de_jugadores", '<tr><td colspan="9">Todavía no cargaste jugadores.</td></tr>')
        return

    html = ""
    numero_de_jugador = 1
    for jugador in jugadores:
        if jugador["juega"]:
            texto_juega = "Sí"
        else:
            texto_juega = "No"
        media = round(logica.media_del_jugador(jugador), 1)  # redondeada a 1 decimal

        html = html + "<tr>"
        html = html + "<td>" + str(numero_de_jugador) + "</td>"
        html = html + "<td>" + texto_juega + "</td>"
        html = html + "<td>" + texto_seguro(jugador["nombre"]) + "</td>"
        html = html + "<td>" + logica.texto_de_posiciones(jugador) + "</td>"
        html = html + "<td>" + str(jugador["ritmo"]) + "</td>"
        html = html + "<td>" + str(jugador["pase"]) + "</td>"
        html = html + "<td>" + str(jugador["regate"]) + "</td>"
        html = html + "<td>" + str(jugador["defensa"]) + "</td>"
        html = html + "<td><b>" + str(media) + "</b></td>"
        html = html + "</tr>"
        numero_de_jugador = numero_de_jugador + 1

    mostrar_html("tabla_de_jugadores", html)


# ---------- 2. EQUIPOS ----------

def al_tocar_armar_equipos_parejos(evento):
    armar_equipos(False)


def al_tocar_otra_combinacion(evento):
    armar_equipos(True)


# Arma los equipos.
# Si pedir_otra_combinacion es True, no repite las combinaciones que ya salieron.
def armar_equipos(pedir_otra_combinacion):
    jugadores_por_equipo = logica.convertir_texto_a_numero(leer_casilla("formato"))  # 5, 8 u 11
    cantidad_de_equipos = logica.convertir_texto_a_numero(leer_casilla("cantidad_de_equipos"))
    usar_posiciones = casilla_esta_tildada("usar_posiciones")

    if cantidad_de_equipos == None or cantidad_de_equipos < 2:
        mostrar_error("mensaje_equipos", "Tienen que ser al menos 2 equipos.")
        return

    # Solo cuentan los jugadores que juegan
    jugadores_que_juegan = []
    for jugador in todos_los_datos["jugadores"]:
        if jugador["juega"]:
            jugadores_que_juegan.append(jugador)

    jugadores_necesarios = jugadores_por_equipo * cantidad_de_equipos
    if len(jugadores_que_juegan) < jugadores_necesarios:
        jugadores_que_faltan = jugadores_necesarios - len(jugadores_que_juegan)
        texto = "Faltan " + str(jugadores_que_faltan) + " jugadores: se necesitan " + str(jugadores_necesarios)
        texto = texto + " y juegan " + str(len(jugadores_que_juegan)) + ". No inventamos jugadores."
        mostrar_error("mensaje_equipos", texto)
        return

    if len(todos_los_datos["partidos"]) > 0:
        quiere_seguir = window.confirm("Hay un torneo armado. Si cambiás los equipos se borra. ¿Seguir?")
        if not quiere_seguir:
            return

    # "Armar equipos parejos" empieza de cero.
    # "Otra combinación" se acuerda de las que ya salieron, para no repetirlas.
    if pedir_otra_combinacion and len(todos_los_datos["equipos"]) > 0:
        combinacion_actual = logica.texto_de_la_combinacion(todos_los_datos["equipos"])
        todos_los_datos["combinacionesVistas"].append(combinacion_actual)
    else:
        todos_los_datos["combinacionesVistas"] = []

    equipos_nuevos = logica.armar_equipos_parejos(jugadores_que_juegan, cantidad_de_equipos, usar_posiciones, todos_los_datos["combinacionesVistas"])
    if equipos_nuevos == None:
        mostrar_error("mensaje_equipos", "No encontré otra combinación distinta.")
        return

    todos_los_datos["equipos"] = equipos_nuevos
    todos_los_datos["formatoActual"] = jugadores_por_equipo
    todos_los_datos["partidos"] = []  # cambiaron los equipos: el torneo viejo se borra

    texto = "¡Equipos armados!"
    jugadores_que_sobran = len(jugadores_que_juegan) - jugadores_necesarios
    if jugadores_que_sobran > 0:
        texto = texto + " Sobran " + str(jugadores_que_sobran) + " jugadores: quedan de suplentes."
    mostrar_mensaje("mensaje_equipos", texto)
    mostrar_mensaje("mensaje_torneo", "")
    guardar_en_el_navegador()
    actualizar_toda_la_pagina()


# Lee el número de equipo escrito en una casilla.
# Si no es un equipo que exista, muestra un error y devuelve None.
def leer_numero_de_equipo(id_de_la_casilla):
    numero_del_equipo = logica.convertir_texto_a_numero(leer_casilla(id_de_la_casilla))
    cantidad_de_equipos = len(todos_los_datos["equipos"])

    if numero_del_equipo == None or numero_del_equipo < 1 or numero_del_equipo > cantidad_de_equipos:
        mostrar_error("mensaje_equipos", "Poné un número de equipo que exista.")
        return None
    return numero_del_equipo


def al_tocar_mover(evento):
    jugador = buscar_jugador_por_numero("numero_de_jugador_a_mover", "mensaje_equipos")
    if jugador == None:
        return

    numero_del_equipo_nuevo = leer_numero_de_equipo("numero_de_equipo_destino")
    if numero_del_equipo_nuevo == None:
        return

    # Restamos 1 porque las listas de Python empiezan en 0
    indice_del_equipo_nuevo = numero_del_equipo_nuevo - 1

    se_pudo_mover = logica.pasar_jugador_a_otro_equipo(todos_los_datos["equipos"], jugador["nombre"], indice_del_equipo_nuevo)
    if se_pudo_mover:
        equipo_nuevo = todos_los_datos["equipos"][indice_del_equipo_nuevo]
        mostrar_mensaje("mensaje_equipos", texto_seguro(jugador["nombre"]) + " pasó a " + texto_seguro(equipo_nuevo["nombre"]) + ".")
        guardar_en_el_navegador()
        actualizar_toda_la_pagina()
    else:
        mostrar_error("mensaje_equipos", "No se puede: no está en un equipo o su equipo quedaría vacío.")


def al_tocar_cambiar_nombre(evento):
    numero_del_equipo = leer_numero_de_equipo("numero_de_equipo_a_renombrar")
    if numero_del_equipo == None:
        return

    nombre_nuevo = leer_casilla("nombre_nuevo_del_equipo").strip()
    if nombre_nuevo == "":
        mostrar_error("mensaje_equipos", "Escribí el nombre nuevo.")
        return

    # Restamos 1 porque las listas de Python empiezan en 0
    indice_del_equipo = numero_del_equipo - 1

    se_pudo_cambiar = logica.cambiar_nombre_de_equipo(todos_los_datos["equipos"], todos_los_datos["partidos"], indice_del_equipo, nombre_nuevo)
    if se_pudo_cambiar:
        mostrar_mensaje("mensaje_equipos", "Listo, ahora se llama " + texto_seguro(nombre_nuevo) + ".")
        escribir_en_casilla("nombre_nuevo_del_equipo", "")
        guardar_en_el_navegador()
        actualizar_toda_la_pagina()
    else:
        mostrar_error("mensaje_equipos", "Ya hay un equipo con ese nombre.")


def mostrar_equipos():
    equipos = todos_los_datos["equipos"]
    if len(equipos) == 0:
        mostrar_html("lista_de_equipos", "<p>Todavía no armaste equipos.</p>")
        mostrar_html("resumen_de_equipos", "")
        return

    html = ""
    numero_del_equipo = 1
    for equipo in equipos:
        html = html + html_de_un_equipo(equipo, numero_del_equipo)
        numero_del_equipo = numero_del_equipo + 1
    mostrar_html("lista_de_equipos", html)

    promedio = round(logica.promedio_de_los_equipos(todos_los_datos["jugadores"], equipos), 1)
    diferencia = round(logica.diferencia_entre_equipos(todos_los_datos["jugadores"], equipos), 2)
    texto = "Promedio de las medias: " + str(promedio)
    texto = texto + " - Diferencia entre el más fuerte y el más débil: " + str(diferencia)
    mostrar_html("resumen_de_equipos", texto)


# Arma el HTML de un equipo: su nombre, sus medias, los avisos y sus jugadores
def html_de_un_equipo(equipo, numero_del_equipo):
    jugadores_del_equipo = logica.buscar_jugadores_del_equipo(todos_los_datos["jugadores"], equipo)
    puesto_de_cada_jugador = logica.calcular_puesto_de_cada_jugador(jugadores_del_equipo)
    cantidad_por_puesto = logica.contar_jugadores_por_puesto(puesto_de_cada_jugador)
    media_del_equipo = round(logica.media_general(jugadores_del_equipo), 1)

    html = "<hr>"
    html = html + "<h3>" + str(numero_del_equipo) + ". " + texto_seguro(equipo["nombre"]) + " (media " + str(media_del_equipo) + ")</h3>"

    # La media de cada atributo. Ejemplo: Ritmo 75.5  Pase 70.2 ...
    html = html + "<p><small>"
    for atributo in logica.ATRIBUTOS:
        media_del_atributo = round(logica.media_de_un_atributo(jugadores_del_equipo, atributo), 1)
        html = html + logica.NOMBRE_DE_CADA_ATRIBUTO[atributo] + " " + str(media_del_atributo) + " &nbsp; "
    html = html + "<br>"

    # Cuántos hay en cada puesto. Ejemplo: ARQ: 1  DEF: 2 ...
    for puesto in logica.POSICIONES:
        html = html + puesto + ": " + str(cantidad_por_puesto[puesto]) + " &nbsp; "
    html = html + "</small></p>"

    # Avisos
    if len(jugadores_del_equipo) < todos_los_datos["formatoActual"]:
        html = html + "<p><b>Ojo: tiene menos jugadores de los que pide el formato.</b></p>"
    if cantidad_por_puesto["ARQ"] == 0:
        html = html + "<p><b>Ojo: nadie de este equipo juega de arquero.</b></p>"

    # Los jugadores en orden: arquero, defensores, mediocampistas y delanteros
    html = html + "<ul>"
    jugadores_ordenados = logica.ordenar_jugadores_para_mostrar(jugadores_del_equipo, puesto_de_cada_jugador)
    for jugador in jugadores_ordenados:
        puesto = puesto_de_cada_jugador[jugador["nombre"]]
        if puesto == "":
            texto_del_puesto = "---"
        else:
            texto_del_puesto = puesto

        # Su número en la tabla de jugadores (se cuenta desde 1)
        numero_de_jugador = todos_los_datos["jugadores"].index(jugador) + 1
        media = round(logica.media_del_jugador(jugador), 1)

        html = html + "<li><b>" + texto_del_puesto + "</b> - N° " + str(numero_de_jugador) + " " + texto_seguro(jugador["nombre"])
        if puesto != jugador["posicion"]:
            html = html + " (juega de secundaria)"
        html = html + " <small>" + logica.texto_de_posiciones(jugador)
        html = html + " - media " + str(media) + "</small></li>"
    html = html + "</ul>"

    return html


# ---------- 3. TORNEO ----------

def nombres_de_los_equipos():
    nombres = []
    for equipo in todos_los_datos["equipos"]:
        nombres.append(equipo["nombre"])
    return nombres


def al_tocar_armar_torneo(evento):
    if len(todos_los_datos["equipos"]) < 2:
        mostrar_error("mensaje_torneo", "Primero armá al menos 2 equipos.")
        return

    if len(todos_los_datos["partidos"]) > 0:
        quiere_seguir = window.confirm("Ya hay un torneo. Si armás otro se borran los resultados. ¿Seguir?")
        if not quiere_seguir:
            return

    ida_y_vuelta = casilla_esta_tildada("ida_y_vuelta")
    todos_los_datos["partidos"] = logica.crear_fixture(nombres_de_los_equipos(), ida_y_vuelta)
    cantidad_de_partidos = len(todos_los_datos["partidos"])
    mostrar_mensaje("mensaje_torneo", "Torneo armado: " + str(cantidad_de_partidos) + " partidos.")
    guardar_en_el_navegador()
    actualizar_toda_la_pagina()


def al_tocar_guardar_resultado(evento):
    numero_de_partido = logica.convertir_texto_a_numero(leer_casilla("numero_de_partido"))
    goles_del_local = logica.convertir_texto_a_numero(leer_casilla("goles_del_local"))
    goles_del_visitante = logica.convertir_texto_a_numero(leer_casilla("goles_del_visitante"))
    cantidad_de_partidos = len(todos_los_datos["partidos"])

    if numero_de_partido == None or numero_de_partido < 1 or numero_de_partido > cantidad_de_partidos:
        mostrar_error("mensaje_torneo", "Poné un número de partido del fixture.")
        return
    if goles_del_local == None or goles_del_visitante == None:
        mostrar_error("mensaje_torneo", "Los goles tienen que ser números desde 0.")
        return

    # Restamos 1 porque las listas de Python empiezan en 0
    partido = todos_los_datos["partidos"][numero_de_partido - 1]
    partido["golesLocal"] = goles_del_local
    partido["golesVisitante"] = goles_del_visitante

    mostrar_mensaje("mensaje_torneo", "Resultado guardado.")
    escribir_en_casilla("numero_de_partido", "")
    escribir_en_casilla("goles_del_local", "")
    escribir_en_casilla("goles_del_visitante", "")
    guardar_en_el_navegador()
    actualizar_toda_la_pagina()


def mostrar_fixture():
    partidos = todos_los_datos["partidos"]
    if len(partidos) == 0:
        mostrar_html("fixture", "<p>Todavía no armaste un torneo.</p>")
        return

    html = ""
    ultima_fecha = logica.numero_de_la_ultima_fecha(partidos)
    for numero_de_fecha in range(1, ultima_fecha + 1):
        html = html + "<h4>Fecha " + str(numero_de_fecha) + "</h4><ul>"

        # Los partidos se numeran 1, 2, 3... en el orden de la lista.
        # Es el número que hay que escribir para cargar el resultado.
        numero_de_partido = 1
        for partido in partidos:
            if partido["fecha"] == numero_de_fecha:
                if partido["golesLocal"] == None:
                    texto_del_resultado = "sin jugar"
                else:
                    texto_del_resultado = str(partido["golesLocal"]) + " a " + str(partido["golesVisitante"])
                html = html + "<li>Partido " + str(numero_de_partido) + ": " + texto_seguro(partido["local"])
                html = html + " vs " + texto_seguro(partido["visitante"]) + " - <b>" + texto_del_resultado + "</b></li>"
            numero_de_partido = numero_de_partido + 1

        equipos_libres = logica.equipos_libres_en_la_fecha(nombres_de_los_equipos(), partidos, numero_de_fecha)
        if len(equipos_libres) > 0:
            html = html + "<li><i>Libre: " + texto_seguro(", ".join(equipos_libres)) + "</i></li>"
        html = html + "</ul>"

    mostrar_html("fixture", html)


def mostrar_tabla_de_posiciones():
    if len(todos_los_datos["partidos"]) == 0:
        mostrar_html("tabla_de_posiciones", "")
        return

    filas = logica.calcular_tabla_de_posiciones(nombres_de_los_equipos(), todos_los_datos["partidos"])
    html = ""
    lugar_en_la_tabla = 1
    for fila in filas:
        html = html + "<tr>"
        html = html + "<td>" + str(lugar_en_la_tabla) + "</td>"
        html = html + "<td>" + texto_seguro(fila["equipo"]) + "</td>"
        html = html + "<td>" + str(fila["partidos_jugados"]) + "</td>"
        html = html + "<td>" + str(fila["ganados"]) + "</td>"
        html = html + "<td>" + str(fila["empatados"]) + "</td>"
        html = html + "<td>" + str(fila["perdidos"]) + "</td>"
        html = html + "<td>" + str(fila["goles_a_favor"]) + "</td>"
        html = html + "<td>" + str(fila["goles_en_contra"]) + "</td>"
        html = html + "<td>" + str(fila["diferencia_de_gol"]) + "</td>"
        html = html + "<td><b>" + str(fila["puntos"]) + "</b></td>"
        html = html + "</tr>"
        lugar_en_la_tabla = lugar_en_la_tabla + 1

    mostrar_html("tabla_de_posiciones", html)


# ---------- BORRAR TODO ----------

def al_tocar_borrar_todos_los_datos(evento):
    quiere_borrar_todo = window.confirm("¿Seguro? Se borran jugadores, equipos y torneo.")
    if not quiere_borrar_todo:
        return

    todos_los_datos["jugadores"] = []
    todos_los_datos["equipos"] = []
    todos_los_datos["partidos"] = []
    todos_los_datos["combinacionesVistas"] = []
    guardar_en_el_navegador()
    actualizar_toda_la_pagina()


# ---------- ACTUALIZAR LA PÁGINA ----------
# Vuelve a dibujar todas las tablas y listas con los datos de ahora

def actualizar_toda_la_pagina():
    mostrar_tabla_de_jugadores()
    mostrar_equipos()
    mostrar_fixture()
    mostrar_tabla_de_posiciones()


# ---------- ARRANQUE ----------
# Esto se hace una sola vez, cuando se abre la página

cargar_del_navegador()
escribir_en_casilla("formato", str(todos_los_datos["formatoActual"]))
actualizar_toda_la_pagina()
mostrar_html("aviso_cargando", "")  # Python ya cargó: sacamos el aviso de "Cargando..."
