# ==========================================
# main.py - Fulbito en la consola
# ==========================================
# Para usarlo, en una terminal dentro de esta carpeta:
#     python main.py
# Todo se guarda en el archivo datos.json, en la misma carpeta.
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
        return
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

# Pide un número entre "minimo" y "maximo". Insiste hasta que pongan uno válido.
def pedir_numero(mensaje, minimo, maximo):
    while True:
        numero = logica.convertir_numero(input(mensaje))
        if numero != None and numero >= minimo and numero <= maximo:
            return numero
        print("  Tiene que ser un número entero entre " + str(minimo) + " y " + str(maximo) + ".")


# Pregunta algo que se contesta con sí o no. Devuelve True si contestan "s".
def preguntar_si_no(mensaje):
    respuesta = input(mensaje + " (s/n): ")
    return respuesta.strip().lower() == "s"


def mostrar_lista_de_posiciones():
    for i in range(len(logica.POSICIONES)):
        codigo = logica.POSICIONES[i]
        print("  " + str(i + 1) + ". " + logica.NOMBRES_POSICIONES[codigo])


def pedir_posicion():
    print("Posición principal:")
    mostrar_lista_de_posiciones()
    numero = pedir_numero("Elegí un número: ", 1, 4)
    return logica.POSICIONES[numero - 1]


def pedir_secundarias(principal):
    print("¿En qué otras posiciones puede jugar?")
    mostrar_lista_de_posiciones()
    print("Poné los números separados por coma (por ejemplo 2,3) o apretá Enter si en ninguna.")
    texto = input("Otras posiciones: ")

    secundarias = []
    for parte in texto.split(","):
        numero = logica.convertir_numero(parte)
        if numero != None and numero >= 1 and numero <= 4:
            codigo = logica.POSICIONES[numero - 1]
            if codigo != principal:
                secundarias.append(codigo)
    return secundarias


# ---------- JUGADORES ----------

def ver_jugadores():
    if len(datos["jugadores"]) == 0:
        print("Todavía no cargaste jugadores.")
        return

    print("")
    print("  #  Juega  Nombre                Posición          RIT  PAS  REG  DEF  MEDIA")
    for i in range(len(datos["jugadores"])):
        jugador = datos["jugadores"][i]
        juega = "no"
        if jugador["juega"]:
            juega = "sí"
        linea = str(i + 1).rjust(3) + "  "
        linea = linea + juega.ljust(5) + "  "
        linea = linea + jugador["nombre"].ljust(20) + "  "
        linea = linea + logica.texto_posiciones(jugador).ljust(16)
        for atributo in logica.ATRIBUTOS:
            linea = linea + str(jugador[atributo]).rjust(5)
        linea = linea + logica.redondear(logica.media_jugador(jugador)).rjust(7)
        print(linea)


def cargar_jugador():
    print("")
    print("Cargar jugador. Si el nombre ya existe, se cambian sus datos.")
    nombre = input("Nombre (Enter para volver): ").strip()
    if nombre == "":
        return

    existente = logica.buscar_jugador(datos["jugadores"], nombre)
    if existente != None:
        print("Ya existe " + existente["nombre"] + ": vas a cambiar sus datos.")

    numeros = {}
    for atributo in logica.ATRIBUTOS:
        numeros[atributo] = pedir_numero(logica.NOMBRES_ATRIBUTOS[atributo] + " (1 a 99): ", 1, 99)
    posicion = pedir_posicion()
    secundarias = pedir_secundarias(posicion)

    error = logica.revisar_jugador(nombre, numeros, posicion)
    if error != "":
        print(error)
        return

    es_nuevo = logica.guardar_jugador(datos["jugadores"], nombre, numeros, posicion, secundarias)
    guardar_datos()

    jugador = logica.buscar_jugador(datos["jugadores"], nombre)
    media = logica.redondear(logica.media_jugador(jugador))
    if es_nuevo:
        print("Listo: " + jugador["nombre"] + ", media " + media + ".")
    else:
        print("Actualizado: " + jugador["nombre"] + ", media " + media + ".")


def borrar_jugador():
    ver_jugadores()
    if len(datos["jugadores"]) == 0:
        return

    numero = pedir_numero("Número del jugador a borrar (0 para volver): ", 0, len(datos["jugadores"]))
    if numero == 0:
        return

    jugador = datos["jugadores"][numero - 1]
    if logica.esta_en_un_equipo(datos["equipos"], jugador["nombre"]):
        print(jugador["nombre"] + " está en un equipo. Armá equipos nuevos antes de borrarlo.")
        return

    if preguntar_si_no("¿Borrar a " + jugador["nombre"] + "?"):
        datos["jugadores"].pop(numero - 1)
        guardar_datos()
        print("Borrado.")


def elegir_quien_juega():
    while True:
        ver_jugadores()
        if len(datos["jugadores"]) == 0:
            return

        numero = pedir_numero("Número del jugador para cambiar si juega o no (0 para volver): ", 0, len(datos["jugadores"]))
        if numero == 0:
            return

        jugador = datos["jugadores"][numero - 1]
        jugador["juega"] = not jugador["juega"]
        guardar_datos()


# ---------- EQUIPOS ----------

def nombres_de_equipos():
    nombres = []
    for equipo in datos["equipos"]:
        nombres.append(equipo["nombre"])
    return nombres


def mostrar_equipos(equipos, formato):
    # Solo avisamos de arqueros si hay jugadores con posición cargada
    hay_posiciones = False
    for jugador in datos["jugadores"]:
        if jugador["posicion"] != "":
            hay_posiciones = True

    for equipo in equipos:
        lista = logica.jugadores_del_equipo(datos["jugadores"], equipo)
        puestos = logica.asignar_puestos(lista)
        cuenta = logica.contar_puestos(puestos)

        print("")
        print(equipo["nombre"] + " - media " + logica.redondear(logica.media_de_lista(lista, "")))

        texto = "  "
        for atributo in logica.ATRIBUTOS:
            texto = texto + logica.NOMBRES_ATRIBUTOS[atributo] + " "
            texto = texto + logica.redondear(logica.media_de_lista(lista, atributo)) + "   "
        print(texto)

        texto = "  Posiciones: "
        for posicion in logica.POSICIONES:
            texto = texto + str(cuenta[posicion]) + " " + posicion + "   "
        print(texto)

        if len(lista) < formato:
            print("  Ojo: tiene " + str(len(lista)) + " jugadores y F" + str(formato) + " pide " + str(formato) + ".")
        if hay_posiciones and cuenta["ARQ"] == 0:
            print("  Ojo: nadie de este equipo juega de arquero.")

        for jugador in logica.ordenar_para_mostrar(lista, puestos):
            puesto = puestos[jugador["nombre"]]
            aclaracion = ""
            if puesto != "" and puesto != jugador["posicion"]:
                aclaracion = " (juega de secundaria)"
            if puesto == "":
                puesto = "---"
            linea = "  [" + puesto + "] " + jugador["nombre"] + aclaracion
            linea = linea + " - " + logica.texto_posiciones(jugador)
            linea = linea + " - media " + logica.redondear(logica.media_jugador(jugador))
            print(linea)

    promedio = logica.promedio_de_equipos(datos["jugadores"], equipos)
    diferencia = logica.diferencia_entre_equipos(datos["jugadores"], equipos)
    print("")
    print("Promedio de las medias: " + logica.redondear(promedio))
    print("Diferencia entre el más fuerte y el más débil: " + str(round(diferencia, 2)))


def ver_equipos():
    if len(datos["equipos"]) == 0:
        print("Todavía no armaste equipos.")
        return
    mostrar_equipos(datos["equipos"], datos["formatoActual"])


def armar_equipos():
    if len(datos["partidos"]) > 0:
        if not preguntar_si_no("Hay un torneo armado. Si guardás equipos nuevos se borra. ¿Seguir?"):
            return

    print("Formato:")
    print("  1. F5 (5 por equipo)")
    print("  2. F8 (8 por equipo)")
    print("  3. F11 (11 por equipo)")
    opcion = pedir_numero("Elegí un número: ", 1, 3)
    formato = 5
    if opcion == 2:
        formato = 8
    if opcion == 3:
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
        print("Faltan " + str(faltan) + " jugador(es): se necesitan " + str(necesarios) + " y juegan " + str(len(juegan)) + ".")
        print("No inventamos jugadores: cargá más o armá menos equipos.")
        return

    vistas = []
    while True:
        print("Buscando equipos parejos...")
        equipos = logica.armar_equipos(juegan, cantidad, usar_posiciones, vistas)
        if equipos == None:
            print("No hay otra combinación distinta de las que ya viste.")
            return

        mostrar_equipos(equipos, formato)
        sobran = len(juegan) - necesarios
        if sobran > 0:
            print("Sobran " + str(sobran) + " jugador(es) para F" + str(formato) + ": quedan como suplentes.")

        respuesta = input("¿Te sirven? (s = sí, o = otra combinación, n = cancelar): ").strip().lower()
        if respuesta == "o":
            vistas.append(logica.clave_de_equipos(equipos))
        elif respuesta == "s":
            datos["equipos"] = equipos
            datos["partidos"] = []
            datos["formatoActual"] = formato
            datos["combinacionesVistas"] = vistas
            guardar_datos()
            print("Equipos guardados.")
            return
        else:
            print("No se guardó nada.")
            return


def mover_jugador():
    if len(datos["equipos"]) == 0:
        print("Todavía no armaste equipos.")
        return

    # Mostramos a todos los jugadores de los equipos con un número
    todos = []
    for equipo in datos["equipos"]:
        print(equipo["nombre"] + ":")
        for nombre in equipo["jugadores"]:
            todos.append(nombre)
            print("  " + str(len(todos)) + ". " + nombre)

    numero = pedir_numero("Número del jugador a mover (0 para volver): ", 0, len(todos))
    if numero == 0:
        return
    nombre = todos[numero - 1]

    print("¿A qué equipo?")
    for i in range(len(datos["equipos"])):
        print("  " + str(i + 1) + ". " + datos["equipos"][i]["nombre"])
    destino = pedir_numero("Número de equipo: ", 1, len(datos["equipos"]))

    if logica.mover_jugador(datos["equipos"], nombre, destino - 1):
        guardar_datos()
        print(nombre + " pasó a " + datos["equipos"][destino - 1]["nombre"] + ".")
        ver_equipos()
    else:
        print("No podés dejar un equipo sin jugadores.")


def renombrar_equipo():
    if len(datos["equipos"]) == 0:
        print("Todavía no armaste equipos.")
        return

    for i in range(len(datos["equipos"])):
        print("  " + str(i + 1) + ". " + datos["equipos"][i]["nombre"])
    numero = pedir_numero("Número de equipo (0 para volver): ", 0, len(datos["equipos"]))
    if numero == 0:
        return

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
    nombres = nombres_de_equipos()
    for fecha in range(1, logica.ultima_fecha(datos["partidos"]) + 1):
        print("")
        print("Fecha " + str(fecha))
        for n in range(len(datos["partidos"])):
            partido = datos["partidos"][n]
            if partido["fecha"] == fecha:
                if partido["golesLocal"] == None:
                    resultado = "sin jugar"
                else:
                    resultado = str(partido["golesLocal"]) + " - " + str(partido["golesVisitante"])
                print("  " + str(n + 1) + ". " + partido["local"] + " vs " + partido["visitante"] + ": " + resultado)
        libres = logica.libres_en_fecha(nombres, datos["partidos"], fecha)
        if len(libres) > 0:
            print("     Libre: " + ", ".join(libres))


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
    print("Torneo armado: " + str(len(datos["partidos"])) + " partidos. Todos contra todos.")
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
    print(" #  Equipo                 PJ   G   E   P  GF  GC   DG  PTS")
    for i in range(len(filas)):
        fila = filas[i]
        diferencia = str(fila["dg"])
        if fila["dg"] > 0:
            diferencia = "+" + diferencia
        linea = str(i + 1).rjust(2) + "  " + fila["equipo"].ljust(20)
        linea = linea + str(fila["pj"]).rjust(4) + str(fila["g"]).rjust(4)
        linea = linea + str(fila["e"]).rjust(4) + str(fila["p"]).rjust(4)
        linea = linea + str(fila["gf"]).rjust(4) + str(fila["gc"]).rjust(4)
        linea = linea + diferencia.rjust(5) + str(fila["pts"]).rjust(5)
        print(linea)


# ---------- MENÚ ----------

def menu():
    cargar_datos()
    while True:
        print("")
        print("=== Fulbito ===")
        print(" 1. Ver jugadores")
        print(" 2. Cargar o editar un jugador")
        print(" 3. Borrar un jugador")
        print(" 4. Elegir quién juega")
        print(" 5. Armar equipos parejos")
        print(" 6. Ver equipos")
        print(" 7. Mover un jugador a otro equipo")
        print(" 8. Cambiar el nombre de un equipo")
        print(" 9. Armar torneo")
        print("10. Cargar un resultado")
        print("11. Ver fixture y tabla de posiciones")
        print(" 0. Salir")
        opcion = input("> ").strip()

        if opcion == "1":
            ver_jugadores()
        elif opcion == "2":
            cargar_jugador()
        elif opcion == "3":
            borrar_jugador()
        elif opcion == "4":
            elegir_quien_juega()
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
            print("Opción inválida.")


menu()
