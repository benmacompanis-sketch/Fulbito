# ==========================================
# logica.py - Las cuentas de Fulbito
# ==========================================
# Acá están todas las cuentas: medias, armar equipos parejos,
# puestos, fixture y tabla de posiciones.
# Este archivo no muestra nada en pantalla. Eso lo hacen:
#   main.py   -> la versión de consola
#   pagina.py -> la página web

import random

ATRIBUTOS = ["ritmo", "pase", "regate", "defensa"]
NOMBRES_ATRIBUTOS = {"ritmo": "Ritmo", "pase": "Pase", "regate": "Regate", "defensa": "Defensa"}

POSICIONES = ["ARQ", "DEF", "MED", "DEL"]
NOMBRES_POSICIONES = {"ARQ": "Arquero", "DEF": "Defensor", "MED": "Mediocampista", "DEL": "Delantero"}

# Cuánto importa que las posiciones queden parejas, comparado con la media.
# Con 1, tener un delantero de más que otro equipo pesa igual que un punto de media.
PESO_POSICIONES = 1


# ---------- COSAS CHICAS QUE SE USAN EN TODOS LADOS ----------

# Convierte un texto en número entero.
# Si el texto no es un número entero (por ejemplo "hola" o "7.5"), devuelve None.
def convertir_numero(texto):
    texto = texto.strip()
    if texto.isdecimal():
        return int(texto)
    return None


# Redondea a un decimal y lo devuelve como texto. Ejemplo: 66.666 -> "66.7"
def redondear(numero):
    return str(round(numero, 1))


# Compara dos nombres sin importar mayúsculas ni espacios de más
def mismo_nombre(nombre1, nombre2):
    return nombre1.strip().lower() == nombre2.strip().lower()


def buscar_jugador(jugadores, nombre):
    for jugador in jugadores:
        if mismo_nombre(jugador["nombre"], nombre):
            return jugador
    return None


# ---------- DATOS GUARDADOS ----------

# Se asegura de que los datos leídos tengan todo lo que hace falta.
# Sirve para los datos guardados por versiones anteriores del programa.
def arreglar_datos(datos):
    # La primera versión de consola guardaba los jugadores en inglés
    if "players" in datos:
        jugadores = []
        for viejo in datos["players"]:
            nuevo = {
                "nombre": viejo["name"],
                "ritmo": viejo["pace"],
                "pase": viejo["passing"],
                "regate": viejo["dribbling"],
                "defensa": viejo["defending"],
            }
            jugadores.append(nuevo)
        datos["jugadores"] = jugadores

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

    # Los jugadores cargados antes de que existieran las posiciones quedan sin posición
    for jugador in datos["jugadores"]:
        if "posicion" not in jugador:
            jugador["posicion"] = ""
        if "secundarias" not in jugador:
            jugador["secundarias"] = []
        if "juega" not in jugador:
            jugador["juega"] = True


# ---------- JUGADORES ----------

# Revisa los datos de un jugador antes de guardarlo.
# "numeros" es un diccionario con ritmo, pase, regate y defensa (o None si no eran números).
# Devuelve el texto del error, o "" si está todo bien.
def revisar_jugador(nombre, numeros, posicion):
    if nombre.strip() == "":
        return "Poné un nombre."
    if posicion == "":
        return "Elegí la posición principal."
    for atributo in ATRIBUTOS:
        numero = numeros[atributo]
        if numero == None or numero < 1 or numero > 99:
            return NOMBRES_ATRIBUTOS[atributo] + " tiene que ser un número entero del 1 al 99."
    return ""


# Guarda un jugador nuevo, o actualiza sus datos si ya existía uno con ese nombre.
# Devuelve True si era nuevo y False si se actualizó.
def guardar_jugador(jugadores, nombre, numeros, posicion, secundarias):
    # Las secundarias van siempre en el mismo orden y sin repetir la principal
    secundarias_ordenadas = []
    for otra in POSICIONES:
        if otra in secundarias and otra != posicion:
            secundarias_ordenadas.append(otra)

    jugador = buscar_jugador(jugadores, nombre)
    es_nuevo = False
    if jugador == None:
        jugador = {"nombre": nombre.strip(), "juega": True}
        jugadores.append(jugador)
        es_nuevo = True

    for atributo in ATRIBUTOS:
        jugador[atributo] = numeros[atributo]
    jugador["posicion"] = posicion
    jugador["secundarias"] = secundarias_ordenadas
    return es_nuevo


def esta_en_un_equipo(equipos, nombre):
    for equipo in equipos:
        for otro in equipo["jugadores"]:
            if mismo_nombre(otro, nombre):
                return True
    return False


# ---------- MEDIAS ----------

# Media de un jugador: el promedio de sus 4 atributos
def media_jugador(jugador):
    suma = jugador["ritmo"] + jugador["pase"] + jugador["regate"] + jugador["defensa"]
    return suma / 4


# Media de una lista de jugadores.
# Si "atributo" es "", es la media general; si no, la de ese atributo.
def media_de_lista(lista_jugadores, atributo):
    if len(lista_jugadores) == 0:
        return 0
    suma = 0
    for jugador in lista_jugadores:
        if atributo == "":
            suma = suma + media_jugador(jugador)
        else:
            suma = suma + jugador[atributo]
    return suma / len(lista_jugadores)


# Pasa de la lista de nombres de un equipo a la lista de jugadores
def jugadores_del_equipo(jugadores, equipo):
    lista = []
    for nombre in equipo["jugadores"]:
        lista.append(buscar_jugador(jugadores, nombre))
    return lista


# Diferencia entre el equipo con mejor media y el de peor media
def diferencia_entre_equipos(jugadores, equipos):
    medias = []
    for equipo in equipos:
        medias.append(media_de_lista(jugadores_del_equipo(jugadores, equipo), ""))
    return max(medias) - min(medias)


# Promedio de las medias de todos los equipos
def promedio_de_equipos(jugadores, equipos):
    suma = 0
    for equipo in equipos:
        suma = suma + media_de_lista(jugadores_del_equipo(jugadores, equipo), "")
    return suma / len(equipos)


# ---------- POSICIONES ----------

# Texto corto para mostrar. Ejemplo: "ARQ (DEF, MED)"
def texto_posiciones(jugador):
    if jugador["posicion"] == "":
        return "Sin posición"
    texto = jugador["posicion"]
    if len(jugador["secundarias"]) > 0:
        texto = texto + " (" + ", ".join(jugador["secundarias"]) + ")"
    return texto


# Decide en qué puesto juega cada jugador dentro de su equipo.
# Devuelve un diccionario, por ejemplo {"Pepe": "ARQ", "Tito": "DEF"}.
#
# 1. Todos arrancan en su posición principal.
# 2. Si al equipo le falta un puesto (primero el arco, después defensa,
#    medio y delantera), lo ocupa alguien que lo tenga de secundaria.
#    Sale de su puesto el que deja menos hueco: el que tiene más
#    compañeros en su posición. Si empatan, el de menor media.
#    Para el arco se acepta dejar otro puesto vacío; para los demás, no.
def asignar_puestos(lista_jugadores):
    puestos = {}
    cuenta = {"ARQ": 0, "DEF": 0, "MED": 0, "DEL": 0}

    # 1. Todos en su posición principal
    for jugador in lista_jugadores:
        puestos[jugador["nombre"]] = jugador["posicion"]
        if jugador["posicion"] != "":
            cuenta[jugador["posicion"]] = cuenta[jugador["posicion"]] + 1

    # 2. Llenamos los puestos vacíos
    for puesto in POSICIONES:
        if cuenta[puesto] > 0:
            continue

        elegido = None
        for jugador in lista_jugadores:
            actual = puestos[jugador["nombre"]]
            if puesto not in jugador["secundarias"]:
                continue
            if actual == "":
                continue
            if puesto != "ARQ" and cuenta[actual] < 2:
                continue

            if elegido == None:
                elegido = jugador
            else:
                companeros_nuevo = cuenta[actual]
                companeros_elegido = cuenta[puestos[elegido["nombre"]]]
                if companeros_nuevo > companeros_elegido:
                    elegido = jugador
                elif companeros_nuevo == companeros_elegido:
                    if media_jugador(jugador) < media_jugador(elegido):
                        elegido = jugador

        if elegido != None:
            anterior = puestos[elegido["nombre"]]
            cuenta[anterior] = cuenta[anterior] - 1
            puestos[elegido["nombre"]] = puesto
            cuenta[puesto] = cuenta[puesto] + 1

    return puestos


# Cuántos jugadores hay en cada puesto
def contar_puestos(puestos):
    cuenta = {"ARQ": 0, "DEF": 0, "MED": 0, "DEL": 0}
    for nombre in puestos:
        puesto = puestos[nombre]
        if puesto != "":
            cuenta[puesto] = cuenta[puesto] + 1
    return cuenta


# Número de orden de un puesto: ARQ=0, DEF=1, MED=2, DEL=3 y sin puesto=4
def numero_de_puesto(puesto):
    if puesto == "":
        return 4
    return POSICIONES.index(puesto)


# ¿El jugador "a" se muestra antes que el "b"? Primero por puesto y después por media.
def va_antes_en_equipo(a, b, puestos):
    numero_a = numero_de_puesto(puestos[a["nombre"]])
    numero_b = numero_de_puesto(puestos[b["nombre"]])
    if numero_a != numero_b:
        return numero_a < numero_b
    return media_jugador(a) > media_jugador(b)


# Ordena los jugadores de un equipo para mostrarlos:
# arquero, defensores, mediocampistas y delanteros (método burbuja).
def ordenar_para_mostrar(lista_jugadores, puestos):
    lista = []
    for jugador in lista_jugadores:
        lista.append(jugador)

    for vuelta in range(len(lista)):
        for i in range(len(lista) - 1):
            if va_antes_en_equipo(lista[i + 1], lista[i], puestos):
                guardado = lista[i]
                lista[i] = lista[i + 1]
                lista[i + 1] = guardado
    return lista


# ---------- ARMAR EQUIPOS PAREJOS ----------

# Una "ficha" tiene lo que hace falta para comparar equipos:
# el nombre, la media y cuánto aporta a cada posición
# (1 si es su posición principal, 0.5 si es secundaria, 0 si no la juega).
# Se calcula una sola vez para que después las cuentas vayan rápido.
def hacer_fichas(lista_jugadores):
    fichas = []
    for jugador in lista_jugadores:
        ficha = {"nombre": jugador["nombre"], "media": media_jugador(jugador)}
        for posicion in POSICIONES:
            if jugador["posicion"] == posicion:
                ficha[posicion] = 1
            elif posicion in jugador["secundarias"]:
                ficha[posicion] = 0.5
            else:
                ficha[posicion] = 0
        fichas.append(ficha)
    return fichas


# Qué tan desparejos son unos equipos. Cuanto más bajo, más parejos.
# Suma la diferencia de media entre el mejor y el peor equipo, y
# (si se usan posiciones) la diferencia en cada posición.
def desparejo(grupos, usar_posiciones):
    medias = []
    for grupo in grupos:
        suma = 0
        for ficha in grupo:
            suma = suma + ficha["media"]
        medias.append(suma / len(grupo))
    puntaje = max(medias) - min(medias)

    if usar_posiciones:
        for posicion in POSICIONES:
            cantidades = []
            for grupo in grupos:
                cantidad = 0
                for ficha in grupo:
                    cantidad = cantidad + ficha[posicion]
                cantidades.append(cantidad)
            puntaje = puntaje + PESO_POSICIONES * (max(cantidades) - min(cantidades))

    return puntaje


# Mezcla las fichas y las reparte de a una por equipo (como cuando se "pisa")
def repartir_al_azar(fichas, cantidad_equipos):
    mezcladas = []
    for ficha in fichas:
        mezcladas.append(ficha)
    random.shuffle(mezcladas)

    grupos = []
    for i in range(cantidad_equipos):
        grupos.append([])
    for i in range(len(mezcladas)):
        grupos[i % cantidad_equipos].append(mezcladas[i])
    return grupos


# Cambia al jugador i del equipo a por el jugador j del equipo b
def intercambiar(grupos, a, i, b, j):
    guardado = grupos[a][i]
    grupos[a][i] = grupos[b][j]
    grupos[b][j] = guardado


# Prueba cambiar jugadores de a dos entre equipos.
# Si con el cambio quedan más parejos, lo deja. Si no, lo vuelve atrás.
# Repite hasta que ningún cambio mejore.
def mejorar(grupos, usar_posiciones):
    actual = desparejo(grupos, usar_posiciones)
    hubo_mejora = True
    while hubo_mejora:
        hubo_mejora = False
        for a in range(len(grupos)):
            for b in range(a + 1, len(grupos)):
                for i in range(len(grupos[a])):
                    for j in range(len(grupos[b])):
                        intercambiar(grupos, a, i, b, j)
                        nuevo = desparejo(grupos, usar_posiciones)
                        if nuevo < actual - 0.0001:
                            actual = nuevo
                            hubo_mejora = True
                        else:
                            intercambiar(grupos, a, i, b, j)


# Cambia dos jugadores al azar de dos equipos distintos
def cambio_al_azar(grupos):
    a = random.randint(0, len(grupos) - 1)
    b = random.randint(0, len(grupos) - 1)
    while b == a:
        b = random.randint(0, len(grupos) - 1)
    i = random.randint(0, len(grupos[a]) - 1)
    j = random.randint(0, len(grupos[b]) - 1)
    intercambiar(grupos, a, i, b, j)


# Texto que identifica una combinación de equipos sin importar el orden.
# Sirve para no mostrar dos veces la misma combinación.
def armar_clave(listas_de_nombres):
    partes = []
    for nombres in listas_de_nombres:
        copia = []
        for nombre in nombres:
            copia.append(nombre.lower())
        copia.sort()
        partes.append(",".join(copia))
    partes.sort()
    return " | ".join(partes)


def clave_de_equipos(equipos):
    listas = []
    for equipo in equipos:
        listas.append(equipo["jugadores"])
    return armar_clave(listas)


def clave_de_grupos(grupos):
    listas = []
    for grupo in grupos:
        nombres = []
        for ficha in grupo:
            nombres.append(ficha["nombre"])
        listas.append(nombres)
    return armar_clave(listas)


# Arma los equipos más parejos que encuentre y que no estén en "vistas".
# Devuelve la lista de equipos, o None si no encontró ninguna combinación nueva.
def armar_equipos(lista_jugadores, cantidad_equipos, usar_posiciones, vistas):
    fichas = hacer_fichas(lista_jugadores)

    # Con muchos jugadores cada intento tarda más, así que hacemos menos
    intentos = 20
    if len(fichas) > 30:
        intentos = 8

    mejor = None
    mejor_puntaje = 0
    for intento in range(intentos):
        grupos = repartir_al_azar(fichas, cantidad_equipos)
        mejorar(grupos, usar_posiciones)

        # Si esta combinación ya salió antes, la movemos un poco hasta que sea nueva
        vueltas = 0
        while clave_de_grupos(grupos) in vistas and vueltas < 50:
            cambio_al_azar(grupos)
            vueltas = vueltas + 1
        if clave_de_grupos(grupos) in vistas:
            continue

        puntaje = desparejo(grupos, usar_posiciones)
        if mejor == None or puntaje < mejor_puntaje:
            mejor = grupos
            mejor_puntaje = puntaje

    if mejor == None:
        return None

    # Pasamos de fichas a equipos con nombres
    equipos = []
    for i in range(len(mejor)):
        nombres = []
        for ficha in mejor[i]:
            nombres.append(ficha["nombre"])
        equipos.append({"nombre": "Equipo " + str(i + 1), "jugadores": nombres})
    return equipos


# ---------- CAMBIOS A MANO ----------

# Devuelve en qué número de equipo está un jugador (o -1 si no está en ninguno)
def equipo_del_jugador(equipos, nombre):
    for i in range(len(equipos)):
        for otro in equipos[i]["jugadores"]:
            if mismo_nombre(otro, nombre):
                return i
    return -1


# Pasa un jugador al equipo número "destino".
# Devuelve False si no se puede: si no está en ningún equipo o si dejaría a su equipo vacío.
def mover_jugador(equipos, nombre, destino):
    origen = equipo_del_jugador(equipos, nombre)
    if origen == -1:
        return False
    if origen == destino:
        return True
    if len(equipos[origen]["jugadores"]) == 1:
        return False
    equipos[origen]["jugadores"].remove(nombre)
    equipos[destino]["jugadores"].append(nombre)
    return True


# Cambia el nombre de un equipo, también en el fixture.
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


# Fixture todos contra todos (método del círculo): cada par de equipos
# se cruza una sola vez, o dos si es ida y vuelta.
# Si la cantidad de equipos es impar, uno queda libre en cada fecha.
def crear_fixture(nombres_equipos, ida_y_vuelta):
    lista = []
    for nombre in nombres_equipos:
        lista.append(nombre)
    if len(lista) % 2 == 1:
        lista.append(None)  # None = fecha libre

    total = len(lista)
    partidos = []
    for fecha in range(1, total):
        for k in range(total // 2):
            local = lista[k]
            visitante = lista[total - 1 - k]
            if local != None and visitante != None:
                # Alternamos la localía del primer partido de cada fecha
                if fecha % 2 == 0 and k == 0:
                    guardado = local
                    local = visitante
                    visitante = guardado
                partidos.append(nuevo_partido(fecha, local, visitante))
        # Rotamos a todos menos al primero
        ultimo = lista.pop()
        lista.insert(1, ultimo)

    if ida_y_vuelta:
        cantidad_ida = len(partidos)
        for n in range(cantidad_ida):
            ida = partidos[n]
            partidos.append(nuevo_partido(ida["fecha"] + total - 1, ida["visitante"], ida["local"]))

    return partidos


# Equipos que no juegan en una fecha
def libres_en_fecha(nombres_equipos, partidos, fecha):
    juegan = []
    for partido in partidos:
        if partido["fecha"] == fecha:
            juegan.append(partido["local"])
            juegan.append(partido["visitante"])
    libres = []
    for nombre in nombres_equipos:
        if nombre not in juegan:
            libres.append(nombre)
    return libres


def ultima_fecha(partidos):
    ultima = 0
    for partido in partidos:
        if partido["fecha"] > ultima:
            ultima = partido["fecha"]
    return ultima


# ¿La fila "a" va arriba de la "b" en la tabla?
# Primero por puntos, después diferencia de gol, goles a favor y nombre.
def va_antes_en_tabla(a, b):
    if a["pts"] != b["pts"]:
        return a["pts"] > b["pts"]
    if a["dg"] != b["dg"]:
        return a["dg"] > b["dg"]
    if a["gf"] != b["gf"]:
        return a["gf"] > b["gf"]
    return a["equipo"].lower() < b["equipo"].lower()


# Tabla de posiciones: 3 puntos por partido ganado y 1 por empate
def calcular_tabla(nombres_equipos, partidos):
    filas = []
    for nombre in nombres_equipos:
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

    # Ordenamos con el método burbuja
    for vuelta in range(len(filas)):
        for i in range(len(filas) - 1):
            if va_antes_en_tabla(filas[i + 1], filas[i]):
                guardado = filas[i]
                filas[i] = filas[i + 1]
                filas[i + 1] = guardado

    return filas
