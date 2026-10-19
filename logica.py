# ==========================================
# logica.py - Las cuentas de Fulbito
# ==========================================
# Acá están las cuentas: medias, armar equipos, fixture y tabla.
# Lo usan los dos programas:
#   main.py   = el programa de consola
#   pagina.py = la página web

import random

ATRIBUTOS = ["ritmo", "pase", "regate", "defensa"]
NOMBRES_ATRIBUTOS = {"ritmo": "Ritmo", "pase": "Pase", "regate": "Regate", "defensa": "Defensa"}

POSICIONES = ["ARQ", "DEF", "MED", "DEL"]
NOMBRES_POSICIONES = {"ARQ": "Arquero", "DEF": "Defensor", "MED": "Mediocampista", "DEL": "Delantero"}


# ---------- COSAS CHICAS ----------

# Pasa un texto a número entero. Si no es un número entero, devuelve None.
def convertir_numero(texto):
    texto = texto.strip()
    if texto.isdecimal():
        return int(texto)
    return None


# Compara dos nombres sin importar mayúsculas
def mismo_nombre(nombre1, nombre2):
    return nombre1.strip().lower() == nombre2.strip().lower()


def buscar_jugador(jugadores, nombre):
    for jugador in jugadores:
        if mismo_nombre(jugador["nombre"], nombre):
            return jugador
    return None


# Completa lo que falte en los datos guardados por versiones viejas del programa
def arreglar_datos(datos):
    # La primera versión guardaba los jugadores en inglés
    if "players" in datos:
        datos["jugadores"] = []
        for viejo in datos["players"]:
            nuevo = {}
            nuevo["nombre"] = viejo["name"]
            nuevo["ritmo"] = viejo["pace"]
            nuevo["pase"] = viejo["passing"]
            nuevo["regate"] = viejo["dribbling"]
            nuevo["defensa"] = viejo["defending"]
            datos["jugadores"].append(nuevo)

    if "jugadores" not in datos:
        datos["jugadores"] = []
    if "equipos" not in datos:
        datos["equipos"] = []
    if "partidos" not in datos:
        datos["partidos"] = []
    if "combinacionesVistas" not in datos:
        datos["combinacionesVistas"] = []
    if "formatoActual" not in datos:
        datos["formatoActual"] = 5

    for jugador in datos["jugadores"]:
        if "posicion" not in jugador:
            jugador["posicion"] = ""
        if "secundarias" not in jugador:
            jugador["secundarias"] = []
        if "juega" not in jugador:
            jugador["juega"] = True


# ---------- JUGADORES ----------

# Revisa los datos antes de guardar un jugador.
# Devuelve el error, o "" si está todo bien.
def revisar_jugador(nombre, numeros, posicion):
    if nombre.strip() == "":
        return "Poné un nombre."
    if posicion == "":
        return "Elegí la posición principal."
    for atributo in ATRIBUTOS:
        numero = numeros[atributo]
        if numero == None or numero < 1 or numero > 99:
            return NOMBRES_ATRIBUTOS[atributo] + " tiene que ser un número del 1 al 99."
    return ""


# Guarda un jugador. Si ya había uno con ese nombre, le cambia los datos.
# Devuelve True si es nuevo y False si ya existía.
def guardar_jugador(jugadores, nombre, numeros, posicion, secundarias):
    jugador = buscar_jugador(jugadores, nombre)
    es_nuevo = False
    if jugador == None:
        jugador = {"nombre": nombre.strip(), "juega": True}
        jugadores.append(jugador)
        es_nuevo = True

    for atributo in ATRIBUTOS:
        jugador[atributo] = numeros[atributo]
    jugador["posicion"] = posicion

    # Las secundarias no repiten la principal ni se repiten entre ellas
    jugador["secundarias"] = []
    for otra in secundarias:
        if otra != posicion and otra not in jugador["secundarias"]:
            jugador["secundarias"].append(otra)
    return es_nuevo


def esta_en_un_equipo(equipos, nombre):
    for equipo in equipos:
        for otro in equipo["jugadores"]:
            if mismo_nombre(otro, nombre):
                return True
    return False


# Texto para mostrar las posiciones. Ejemplo: "ARQ (DEF)"
def texto_posiciones(jugador):
    if jugador["posicion"] == "":
        return "Sin posición"
    texto = jugador["posicion"]
    if len(jugador["secundarias"]) > 0:
        texto = texto + " (" + ", ".join(jugador["secundarias"]) + ")"
    return texto


# ---------- MEDIAS ----------

# Media de un jugador: el promedio de sus 4 atributos
def media_jugador(jugador):
    suma = jugador["ritmo"] + jugador["pase"] + jugador["regate"] + jugador["defensa"]
    return suma / 4


# Media de una lista de jugadores.
# Si atributo es "" es la media general. Si no, la de ese atributo.
def media_de_lista(lista, atributo):
    if len(lista) == 0:
        return 0
    suma = 0
    for jugador in lista:
        if atributo == "":
            suma = suma + media_jugador(jugador)
        else:
            suma = suma + jugador[atributo]
    return suma / len(lista)


# Un equipo guarda los nombres. Esto devuelve los jugadores de verdad.
def jugadores_del_equipo(jugadores, equipo):
    lista = []
    for nombre in equipo["jugadores"]:
        lista.append(buscar_jugador(jugadores, nombre))
    return lista


# Diferencia de media entre el mejor y el peor equipo
def diferencia_entre_equipos(jugadores, equipos):
    medias = []
    for equipo in equipos:
        medias.append(media_de_lista(jugadores_del_equipo(jugadores, equipo), ""))
    return max(medias) - min(medias)


# Promedio de las medias de los equipos
def promedio_de_equipos(jugadores, equipos):
    suma = 0
    for equipo in equipos:
        suma = suma + media_de_lista(jugadores_del_equipo(jugadores, equipo), "")
    return suma / len(equipos)


# ---------- PUESTOS DENTRO DE UN EQUIPO ----------

# Dice de qué juega cada uno en su equipo. Cada uno juega de su posición principal,
# pero si el equipo no tiene arquero, ataja el primero que tenga "arquero" de secundaria.
def puestos_del_equipo(lista):
    puestos = {}
    hay_arquero = False
    for jugador in lista:
        puestos[jugador["nombre"]] = jugador["posicion"]
        if jugador["posicion"] == "ARQ":
            hay_arquero = True

    if hay_arquero == False:
        for jugador in lista:
            if "ARQ" in jugador["secundarias"]:
                puestos[jugador["nombre"]] = "ARQ"
                break

    return puestos


# Cuántos jugadores hay en cada puesto
def contar_puestos(puestos):
    cuenta = {"ARQ": 0, "DEF": 0, "MED": 0, "DEL": 0}
    for nombre in puestos:
        puesto = puestos[nombre]
        if puesto != "":
            cuenta[puesto] = cuenta[puesto] + 1
    return cuenta


# Número de cada puesto para ordenar: ARQ=0, DEF=1, MED=2, DEL=3, sin puesto=4
def numero_de_puesto(puesto):
    if puesto == "":
        return 4
    return POSICIONES.index(puesto)


# Ordena el equipo para mostrarlo: arquero, defensores, medios y delanteros.
# Usa el método burbuja: compara de a dos y los da vuelta si están mal.
def ordenar_para_mostrar(lista, puestos):
    ordenada = []
    for jugador in lista:
        ordenada.append(jugador)

    for vuelta in range(len(ordenada)):
        for i in range(len(ordenada) - 1):
            a = ordenada[i]
            b = ordenada[i + 1]
            numero_a = numero_de_puesto(puestos[a["nombre"]])
            numero_b = numero_de_puesto(puestos[b["nombre"]])
            if numero_b < numero_a or (numero_b == numero_a and media_jugador(b) > media_jugador(a)):
                ordenada[i] = b
                ordenada[i + 1] = a
    return ordenada


# ---------- ARMAR EQUIPOS PAREJOS ----------

# Para repartir, el que puede atajar (de principal o secundaria) cuenta como arquero.
# Así los que atajan quedan en equipos distintos.
def grupo_para_repartir(jugador):
    if jugador["posicion"] == "ARQ" or "ARQ" in jugador["secundarias"]:
        return "ARQ"
    return jugador["posicion"]


# Pone primero a los arqueros, después defensores, medios, delanteros y los sin posición
def ordenar_por_posicion(jugadores):
    resultado = []
    for grupo in ["ARQ", "DEF", "MED", "DEL", ""]:
        for jugador in jugadores:
            if grupo_para_repartir(jugador) == grupo:
                resultado.append(jugador)
    return resultado


# Diferencia de media entre el mejor y el peor grupo
def diferencia_de_grupos(grupos):
    medias = []
    for grupo in grupos:
        medias.append(media_de_lista(grupo, ""))
    return max(medias) - min(medias)


# Prueba cambiar jugadores de a dos entre equipos.
# Si la diferencia de media baja, deja el cambio. Si no, lo vuelve atrás.
# Si se usan posiciones, solo cambia jugadores del mismo grupo de posición.
def mejorar(grupos, usar_posiciones):
    hubo_cambio = True
    while hubo_cambio:
        hubo_cambio = False
        for a in range(len(grupos)):
            for b in range(a + 1, len(grupos)):
                for i in range(len(grupos[a])):
                    for j in range(len(grupos[b])):
                        jugador_a = grupos[a][i]
                        jugador_b = grupos[b][j]
                        if usar_posiciones and grupo_para_repartir(jugador_a) != grupo_para_repartir(jugador_b):
                            continue

                        antes = diferencia_de_grupos(grupos)
                        grupos[a][i] = jugador_b
                        grupos[b][j] = jugador_a
                        despues = diferencia_de_grupos(grupos)

                        if despues < antes - 0.001:
                            hubo_cambio = True
                        else:
                            grupos[a][i] = jugador_a
                            grupos[b][j] = jugador_b


# Texto que identifica una combinación de equipos, para no repetirla
def clave_de_equipos(equipos):
    partes = []
    for equipo in equipos:
        nombres = []
        for nombre in equipo["jugadores"]:
            nombres.append(nombre.lower())
        nombres.sort()
        partes.append(",".join(nombres))
    partes.sort()
    return " | ".join(partes)


# Arma los equipos más parejos que encuentre, sin repetir los de "vistas".
# Devuelve la lista de equipos, o None si no encontró ninguna combinación nueva.
def armar_equipos(jugadores, cantidad, usar_posiciones, vistas):
    mejor = None
    mejor_diferencia = 0

    for intento in range(20):
        # 1. Mezclamos a los jugadores
        mezclados = []
        for jugador in jugadores:
            mezclados.append(jugador)
        random.shuffle(mezclados)

        # 2. Si se usan posiciones, los ponemos en orden de posición
        if usar_posiciones:
            mezclados = ordenar_por_posicion(mezclados)

        # 3. Los repartimos de a uno por equipo, como cuando se "pisa"
        grupos = []
        for numero in range(cantidad):
            grupos.append([])
        for i in range(len(mezclados)):
            grupos[i % cantidad].append(mezclados[i])

        # 4. Probamos cambios para que las medias queden parejas
        mejorar(grupos, usar_posiciones)

        # 5. Pasamos a equipos con nombres
        equipos = []
        for numero in range(cantidad):
            nombres = []
            for jugador in grupos[numero]:
                nombres.append(jugador["nombre"])
            equipos.append({"nombre": "Equipo " + str(numero + 1), "jugadores": nombres})

        # 6. Si ya salió antes, la descartamos. Si no, nos quedamos con la más pareja.
        if clave_de_equipos(equipos) in vistas:
            continue
        diferencia = diferencia_de_grupos(grupos)
        if mejor == None or diferencia < mejor_diferencia:
            mejor = equipos
            mejor_diferencia = diferencia

    return mejor


# ---------- CAMBIOS A MANO ----------

# Pasa a un jugador al equipo número "destino" (empezando de 0).
# Devuelve False si no se puede (no está en ningún equipo o dejaría un equipo vacío).
def mover_jugador(equipos, nombre, destino):
    for equipo in equipos:
        for otro in equipo["jugadores"]:
            if mismo_nombre(otro, nombre):
                if len(equipo["jugadores"]) == 1:
                    return False
                equipo["jugadores"].remove(otro)
                equipos[destino]["jugadores"].append(otro)
                return True
    return False


# Le cambia el nombre a un equipo, también en el fixture.
# Devuelve False si ya hay otro equipo con ese nombre.
def renombrar_equipo(equipos, partidos, indice, nuevo):
    nuevo = nuevo.strip()
    for i in range(len(equipos)):
        if i != indice and mismo_nombre(equipos[i]["nombre"], nuevo):
            return False

    viejo = equipos[indice]["nombre"]
    equipos[indice]["nombre"] = nuevo
    for partido in partidos:
        if partido["local"] == viejo:
            partido["local"] = nuevo
        if partido["visitante"] == viejo:
            partido["visitante"] = nuevo
    return True


# ---------- TORNEO ----------

def nuevo_partido(fecha, local, visitante):
    return {"fecha": fecha, "local": local, "visitante": visitante, "golesLocal": None, "golesVisitante": None}


# Fixture todos contra todos: cada par de equipos juega una vez (dos si es ida y vuelta).
# Si son impares, en cada fecha uno queda libre.
def crear_fixture(nombres, ida_y_vuelta):
    lista = []
    for nombre in nombres:
        lista.append(nombre)
    if len(lista) % 2 == 1:
        lista.append(None)  # None quiere decir "fecha libre"

    total = len(lista)
    partidos = []
    for fecha in range(1, total):
        # El primero juega con el último, el segundo con el anteúltimo, y así
        for k in range(total // 2):
            local = lista[k]
            visitante = lista[total - 1 - k]
            if local != None and visitante != None:
                partidos.append(nuevo_partido(fecha, local, visitante))
        # Para la fecha siguiente, el último pasa al segundo lugar
        ultimo = lista.pop()
        lista.insert(1, ultimo)

    if ida_y_vuelta:
        cantidad_ida = len(partidos)
        for n in range(cantidad_ida):
            ida = partidos[n]
            partidos.append(nuevo_partido(ida["fecha"] + total - 1, ida["visitante"], ida["local"]))

    return partidos


def ultima_fecha(partidos):
    ultima = 0
    for partido in partidos:
        if partido["fecha"] > ultima:
            ultima = partido["fecha"]
    return ultima


# Equipos que no juegan en una fecha
def libres_en_fecha(nombres, partidos, fecha):
    juegan = []
    for partido in partidos:
        if partido["fecha"] == fecha:
            juegan.append(partido["local"])
            juegan.append(partido["visitante"])
    libres = []
    for nombre in nombres:
        if nombre not in juegan:
            libres.append(nombre)
    return libres


# Tabla de posiciones: 3 puntos por ganar y 1 por empatar
def calcular_tabla(nombres, partidos):
    filas = []
    for nombre in nombres:
        filas.append({"equipo": nombre, "pj": 0, "g": 0, "e": 0, "p": 0, "gf": 0, "gc": 0, "dg": 0, "pts": 0})

    for partido in partidos:
        if partido["golesLocal"] == None:
            continue  # todavía no se jugó

        for fila in filas:
            if fila["equipo"] == partido["local"]:
                local = fila
            if fila["equipo"] == partido["visitante"]:
                visitante = fila

        goles_local = partido["golesLocal"]
        goles_visitante = partido["golesVisitante"]
        local["pj"] = local["pj"] + 1
        visitante["pj"] = visitante["pj"] + 1
        local["gf"] = local["gf"] + goles_local
        local["gc"] = local["gc"] + goles_visitante
        visitante["gf"] = visitante["gf"] + goles_visitante
        visitante["gc"] = visitante["gc"] + goles_local

        if goles_local > goles_visitante:
            local["g"] = local["g"] + 1
            visitante["p"] = visitante["p"] + 1
        elif goles_local < goles_visitante:
            visitante["g"] = visitante["g"] + 1
            local["p"] = local["p"] + 1
        else:
            local["e"] = local["e"] + 1
            visitante["e"] = visitante["e"] + 1

    for fila in filas:
        fila["dg"] = fila["gf"] - fila["gc"]
        fila["pts"] = fila["g"] * 3 + fila["e"]

    # Ordenamos con el método burbuja: más puntos arriba, y si empatan, mejor diferencia de gol
    for vuelta in range(len(filas)):
        for i in range(len(filas) - 1):
            a = filas[i]
            b = filas[i + 1]
            if b["pts"] > a["pts"] or (b["pts"] == a["pts"] and b["dg"] > a["dg"]):
                filas[i] = b
                filas[i + 1] = a

    return filas
