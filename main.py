# ==========================================
# main.py - Fulbito en la consola
# ==========================================
# Para usarlo, en una terminal dentro de esta carpeta:
#     python main.py
# Todo se guarda en el archivo datos.json.
# Las cuentas están en logica.py.

import json
import os
import logica

ARCHIVO = "datos.json"

# Acá está todo: jugadores, equipos y torneo
datos = {
    "jugadores": [],
    "equipos": [],
    "partidos": [],
    "combinacionesVistas": [],
    "formatoActual": 5,
}


# ---------- GUARDAR Y CARGAR ----------

def cargar_datos():
    if not os.path.exists(ARCHIVO):
        return  # todavía no hay nada guardado
    archivo = open(ARCHIVO, "r", encoding="utf-8")
    leidos = json.load(archivo)
    archivo.close()

    logica.arreglar_datos(leidos)
    datos["jugadores"] = leidos["jugadores"]
    datos["equipos"] = leidos["equipos"]
    datos["partidos"] = leidos["partidos"]
    datos["combinacionesVistas"] = leidos["combinacionesVistas"]
    datos["formatoActual"] = leidos["formatoActual"]


def guardar_datos():
    archivo = open(ARCHIVO, "w", encoding="utf-8")
    json.dump(datos, archivo, ensure_ascii=False, indent=2)
    archivo.close()


# ---------- PREGUNTAS ----------

# Pide un número entre minimo y maximo. Pregunta de nuevo hasta que esté bien.
def pedir_numero(mensaje, minimo, maximo):
    while True:
        numero = logica.convertir_numero(input(mensaje))
        if numero != None and numero >= minimo and numero <= maximo:
            return numero
        print("Tiene que ser un número entre " + str(minimo) + " y " + str(maximo) + ".")


# Pregunta algo de sí o no. Devuelve True si contestan "s".
def preguntar_si_no(mensaje):
    respuesta = input(mensaje + " (s/n): ")
    return respuesta.strip().lower() == "s"


def mostrar_posiciones():
    print("  1. Arquero")
    print("  2. Defensor")
    print("  3. Mediocampista")
    print("  4. Delantero")


# ---------- JUGADORES ----------

def ver_jugadores():
    if len(datos["jugadores"]) == 0:
        print("Todavía no cargaste jugadores.")
        return

    print("")
    print("N° | Juega | Nombre | Posición | Ritmo Pase Regate Defensa | Media")
    numero = 1
    for jugador in datos["jugadores"]:
        juega = "no"
        if jugador["juega"]:
            juega = "sí"
        numeros = str(jugador["ritmo"]) + " " + str(jugador["pase"]) + " " + str(jugador["regate"]) + " " + str(jugador["defensa"])
        media = str(round(logica.media_jugador(jugador), 1))
        print(str(numero) + " | " + juega + " | " + jugador["nombre"] + " | " + logica.texto_posiciones(jugador) + " | " + numeros + " | " + media)
        numero = numero + 1


def cargar_jugador():
    print("")
    print("Cargar jugador. Si el nombre ya existe, se cambian sus datos.")
    nombre = input("Nombre (Enter para volver): ").strip()
    if nombre == "":
        return

    numeros = {}
    numeros["ritmo"] = pedir_numero("Ritmo (1 a 99): ", 1, 99)
    numeros["pase"] = pedir_numero("Pase (1 a 99): ", 1, 99)
    numeros["regate"] = pedir_numero("Regate (1 a 99): ", 1, 99)
    numeros["defensa"] = pedir_numero("Defensa (1 a 99): ", 1, 99)

    print("Posición principal:")
    mostrar_posiciones()
    numero = pedir_numero("Elegí un número: ", 1, 4)
    posicion = logica.POSICIONES[numero - 1]

    print("¿En qué otras posiciones puede jugar?")
    mostrar_posiciones()
    secundarias = []
    while True:
        numero = pedir_numero("Número de otra posición (0 para terminar): ", 0, 4)
        if numero == 0:
            break
        secundarias.append(logica.POSICIONES[numero - 1])

    es_nuevo = logica.guardar_jugador(datos["jugadores"], nombre, numeros, posicion, secundarias)
    guardar_datos()
    if es_nuevo:
        print("Listo, se guardó a " + nombre + ".")
    else:
        print("Se actualizaron los datos de " + nombre + ".")


# Pide el número de un jugador. Devuelve el jugador, o None si ponen 0.
def elegir_jugador(mensaje):
    ver_jugadores()
    if len(datos["jugadores"]) == 0:
        return None
    numero = pedir_numero(mensaje + " (0 para volver): ", 0, len(datos["jugadores"]))
    if numero == 0:
        return None
    return datos["jugadores"][numero - 1]


def borrar_jugador():
    jugador = elegir_jugador("Número del jugador a borrar")
    if jugador == None:
        return
    if logica.esta_en_un_equipo(datos["equipos"], jugador["nombre"]):
        print(jugador["nombre"] + " está en un equipo. Armá equipos nuevos antes de borrarlo.")
        return
    if preguntar_si_no("¿Borrar a " + jugador["nombre"] + "?"):
        datos["jugadores"].remove(jugador)
        guardar_datos()
        print("Borrado.")


def cambiar_juega():
    jugador = elegir_jugador("Número del jugador")
    if jugador == None:
        return
    if jugador["juega"]:
        jugador["juega"] = False
        print(jugador["nombre"] + " no juega.")
    else:
        jugador["juega"] = True
        print(jugador["nombre"] + " juega.")
    guardar_datos()


# ---------- EQUIPOS ----------

def nombres_de_equipos():
    nombres = []
    for equipo in datos["equipos"]:
        nombres.append(equipo["nombre"])
    return nombres


def mostrar_equipos(equipos, formato):
    numero_equipo = 1
    for equipo in equipos:
        lista = logica.jugadores_del_equipo(datos["jugadores"], equipo)
        puestos = logica.puestos_del_equipo(lista)
        cuenta = logica.contar_puestos(puestos)
        media = str(round(logica.media_de_lista(lista, ""), 1))

        print("")
        print(str(numero_equipo) + ". " + equipo["nombre"] + " (media " + media + ")")
        print("   Ritmo " + str(round(logica.media_de_lista(lista, "ritmo"), 1))
              + " - Pase " + str(round(logica.media_de_lista(lista, "pase"), 1))
              + " - Regate " + str(round(logica.media_de_lista(lista, "regate"), 1))
              + " - Defensa " + str(round(logica.media_de_lista(lista, "defensa"), 1)))
        print("   ARQ: " + str(cuenta["ARQ"]) + "  DEF: " + str(cuenta["DEF"])
              + "  MED: " + str(cuenta["MED"]) + "  DEL: " + str(cuenta["DEL"]))

        if len(lista) < formato:
            print("   Ojo: tiene menos jugadores de los que pide el formato.")
        if cuenta["ARQ"] == 0:
            print("   Ojo: nadie de este equipo juega de arquero.")

        for jugador in logica.ordenar_para_mostrar(lista, puestos):
            puesto = puestos[jugador["nombre"]]
            if puesto == "":
                puesto = "---"
            linea = "   [" + puesto + "] " + jugador["nombre"]
            if puesto != jugador["posicion"] and puesto != "---":
                linea = linea + " (juega de secundaria)"
            linea = linea + " - media " + str(round(logica.media_jugador(jugador), 1))
            print(linea)
        numero_equipo = numero_equipo + 1

    promedio = round(logica.promedio_de_equipos(datos["jugadores"], equipos), 1)
    diferencia = round(logica.diferencia_entre_equipos(datos["jugadores"], equipos), 2)
    print("")
    print("Promedio de las medias: " + str(promedio))
    print("Diferencia entre el más fuerte y el más débil: " + str(diferencia))


def ver_equipos():
    if len(datos["equipos"]) == 0:
        print("Todavía no armaste equipos.")
        return
    mostrar_equipos(datos["equipos"], datos["formatoActual"])


def armar_equipos():
    if len(datos["partidos"]) > 0:
        if not preguntar_si_no("Hay un torneo armado. Si guardás equipos nuevos se borra. ¿Seguir?"):
            return

    print("Formato:  1. F5   2. F8   3. F11")
    opcion = pedir_numero("Elegí un número: ", 1, 3)
    if opcion == 1:
        formato = 5
    elif opcion == 2:
        formato = 8
    else:
        formato = 11

    cantidad = pedir_numero("¿Cuántos equipos? (2 a 10): ", 2, 10)
    usar_posiciones = preguntar_si_no("¿Emparejar también por posiciones?")

    juegan = []
    for jugador in datos["jugadores"]:
        if jugador["juega"]:
            juegan.append(jugador)

    necesarios = formato * cantidad
    if len(juegan) < necesarios:
        faltan = necesarios - len(juegan)
        print("Faltan " + str(faltan) + " jugadores: se necesitan " + str(necesarios) + " y juegan " + str(len(juegan)) + ".")
        print("No inventamos jugadores.")
        return

    vistas = []
    while True:
        equipos = logica.armar_equipos(juegan, cantidad, usar_posiciones, vistas)
        if equipos == None:
            print("No encontré otra combinación distinta.")
            return

        mostrar_equipos(equipos, formato)
        sobran = len(juegan) - necesarios
        if sobran > 0:
            print("Sobran " + str(sobran) + " jugadores: quedan de suplentes.")

        respuesta = input("¿Te sirven? (s = sí, o = otra combinación, n = cancelar): ").strip().lower()
        if respuesta == "o":
            vistas.append(logica.clave_de_equipos(equipos))
        elif respuesta == "s":
            datos["equipos"] = equipos
            datos["partidos"] = []
            datos["formatoActual"] = formato
            guardar_datos()
            print("Equipos guardados.")
            return
        else:
            print("No se guardó nada.")
            return


def elegir_equipo(mensaje):
    numero = 1
    for equipo in datos["equipos"]:
        print("  " + str(numero) + ". " + equipo["nombre"])
        numero = numero + 1
    return pedir_numero(mensaje, 1, len(datos["equipos"]))


def mover_jugador():
    if len(datos["equipos"]) == 0:
        print("Todavía no armaste equipos.")
        return
    jugador = elegir_jugador("Número del jugador a mover")
    if jugador == None:
        return
    destino = elegir_equipo("¿A qué equipo? ")

    if logica.mover_jugador(datos["equipos"], jugador["nombre"], destino - 1):
        guardar_datos()
        print(jugador["nombre"] + " pasó a " + datos["equipos"][destino - 1]["nombre"] + ".")
    else:
        print("No se puede: no está en un equipo o su equipo quedaría vacío.")


def renombrar_equipo():
    if len(datos["equipos"]) == 0:
        print("Todavía no armaste equipos.")
        return
    numero = elegir_equipo("Número de equipo: ")
    nuevo = input("Nombre nuevo: ").strip()
    if nuevo == "":
        return
    if logica.renombrar_equipo(datos["equipos"], datos["partidos"], numero - 1, nuevo):
        guardar_datos()
        print("Listo.")
    else:
        print("Ya hay un equipo con ese nombre.")


# ---------- TORNEO ----------

def mostrar_fixture():
    for fecha in range(1, logica.ultima_fecha(datos["partidos"]) + 1):
        print("")
        print("Fecha " + str(fecha))
        numero = 1
        for partido in datos["partidos"]:
            if partido["fecha"] == fecha:
                if partido["golesLocal"] == None:
                    resultado = "sin jugar"
                else:
                    resultado = str(partido["golesLocal"]) + " a " + str(partido["golesVisitante"])
                print("  Partido " + str(numero) + ": " + partido["local"] + " vs " + partido["visitante"] + " - " + resultado)
            numero = numero + 1
        libres = logica.libres_en_fecha(nombres_de_equipos(), datos["partidos"], fecha)
        if len(libres) > 0:
            print("  Libre: " + ", ".join(libres))


def armar_torneo():
    if len(datos["equipos"]) < 2:
        print("Primero armá al menos 2 equipos.")
        return
    if len(datos["partidos"]) > 0:
        if not preguntar_si_no("Ya hay un torneo. Si armás otro se borran los resultados. ¿Seguir?"):
            return

    ida_y_vuelta = preguntar_si_no("¿Ida y vuelta?")
    datos["partidos"] = logica.crear_fixture(nombres_de_equipos(), ida_y_vuelta)
    guardar_datos()
    print("Torneo armado: " + str(len(datos["partidos"])) + " partidos.")
    mostrar_fixture()


def cargar_resultado():
    if len(datos["partidos"]) == 0:
        print("Todavía no armaste un torneo.")
        return
    mostrar_fixture()
    numero = pedir_numero("Número de partido (0 para volver): ", 0, len(datos["partidos"]))
    if numero == 0:
        return
    partido = datos["partidos"][numero - 1]
    partido["golesLocal"] = pedir_numero("Goles de " + partido["local"] + ": ", 0, 99)
    partido["golesVisitante"] = pedir_numero("Goles de " + partido["visitante"] + ": ", 0, 99)
    guardar_datos()
    print("Resultado guardado.")


def ver_tabla():
    if len(datos["partidos"]) == 0:
        print("Todavía no armaste un torneo.")
        return
    mostrar_fixture()
    filas = logica.calcular_tabla(nombres_de_equipos(), datos["partidos"])
    print("")
    print("# | Equipo | PJ G E P | GF GC DG | Puntos")
    posicion = 1
    for fila in filas:
        partidos = str(fila["pj"]) + " " + str(fila["g"]) + " " + str(fila["e"]) + " " + str(fila["p"])
        goles = str(fila["gf"]) + " " + str(fila["gc"]) + " " + str(fila["dg"])
        print(str(posicion) + " | " + fila["equipo"] + " | " + partidos + " | " + goles + " | " + str(fila["pts"]))
        posicion = posicion + 1


# ---------- MENÚ ----------

cargar_datos()

while True:
    print("")
    print("=== Fulbito ===")
    print("1. Ver jugadores")
    print("2. Cargar o editar un jugador")
    print("3. Borrar un jugador")
    print("4. Cambiar si un jugador juega o no")
    print("5. Armar equipos parejos")
    print("6. Ver equipos")
    print("7. Mover un jugador a otro equipo")
    print("8. Cambiar el nombre de un equipo")
    print("9. Armar torneo")
    print("10. Cargar un resultado")
    print("11. Ver fixture y tabla de posiciones")
    print("0. Salir")
    opcion = input("Elegí una opción: ").strip()

    if opcion == "1":
        ver_jugadores()
    elif opcion == "2":
        cargar_jugador()
    elif opcion == "3":
        borrar_jugador()
    elif opcion == "4":
        cambiar_juega()
    elif opcion == "5":
        armar_equipos()
    elif opcion == "6":
        ver_equipos()
    elif opcion == "7":
        mover_jugador()
    elif opcion == "8":
        renombrar_equipo()
    elif opcion == "9":
        armar_torneo()
    elif opcion == "10":
        cargar_resultado()
    elif opcion == "11":
        ver_tabla()
    elif opcion == "0":
        print("¡Nos vemos en la cancha!")
        break
    else:
        print("Esa opción no existe.")
