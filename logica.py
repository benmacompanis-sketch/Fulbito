# ==========================================
# logica.py - Las cuentas de Fulbito
# ==========================================
# Acá están las cuentas: medias, armar equipos, fixture y tabla de posiciones.
# Este archivo no toca la página: recibe datos, hace cuentas y devuelve resultados.
# Lo usa pagina.py, que es el programa de la página web.
#
# Cómo es cada cosa (son diccionarios):
#
#   Un jugador:
#     {"nombre": "Juan", "juega": True,
#      "ritmo": 80, "pase": 70, "regate": 60, "defensa": 50,
#      "posicion": "DEF", "secundarias": ["MED"]}
#
#   Un equipo (guarda solo los nombres de sus jugadores):
#     {"nombre": "Equipo 1", "jugadores": ["Juan", "Pedro", "Ana"]}
#
#   Un partido del torneo (None quiere decir que todavía no se jugó):
#     {"fecha": 1, "local": "Equipo 1", "visitante": "Equipo 2",
#      "golesLocal": None, "golesVisitante": None}
#
# OJO: esos nombres ("golesLocal", "secundarias", etc.) son los que quedan
# guardados en el navegador. Si se cambian, se pierden los datos que ya había.

import random

# Los 4 atributos de cada jugador. Cada uno es un número del 1 al 99.
ATRIBUTOS = ["ritmo", "pase", "regate", "defensa"]

# Cómo se escribe cada atributo para mostrarlo en la página
NOMBRE_DE_CADA_ATRIBUTO = {"ritmo": "Ritmo", "pase": "Pase", "regate": "Regate", "defensa": "Defensa"}

# Las posiciones: ARQ = Arquero, DEF = Defensor, MED = Mediocampista, DEL = Delantero
POSICIONES = ["ARQ", "DEF", "MED", "DEL"]


# ---------- AYUDAS CHIQUITAS ----------

# Pasa un texto a número entero. Ejemplo: "25" -> 25
# Si el texto no es un número entero (por ejemplo "", "hola" o "-3"), devuelve None.
def convertir_texto_a_numero(texto):
    texto_sin_espacios = texto.strip()
    if texto_sin_espacios.isdecimal():
        return int(texto_sin_espacios)
    return None


# Dice si dos nombres son iguales sin importar mayúsculas ni espacios en los costados.
# Ejemplo: "Juan" y " juan " son el mismo nombre.
def son_el_mismo_nombre(primer_nombre, segundo_nombre):
    return primer_nombre.strip().lower() == segundo_nombre.strip().lower()


# Busca en la lista al jugador que tiene ese nombre. Si no está, devuelve None.
def buscar_jugador_por_nombre(lista_de_jugadores, nombre_buscado):
    for jugador in lista_de_jugadores:
        if son_el_mismo_nombre(jugador["nombre"], nombre_buscado):
            return jugador
    return None


# Completa lo que falte en los datos guardados por versiones viejas de la página
def completar_datos_viejos(datos):
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

# Revisa que los datos de un jugador estén bien antes de guardarlo.
# "valores_de_atributos" es un diccionario. Ejemplo: {"ritmo": 80, "pase": 70, ...}
# Devuelve el texto del error, o "" (texto vacío) si está todo bien.
def buscar_error_en_jugador(nombre, valores_de_atributos, posicion_principal):
    if nombre.strip() == "":
        return "Poné un nombre."
    if posicion_principal == "":
        return "Elegí la posición principal."
    for atributo in ATRIBUTOS:
        valor = valores_de_atributos[atributo]
        if valor == None or valor < 1 or valor > 99:
            return NOMBRE_DE_CADA_ATRIBUTO[atributo] + " tiene que ser un número del 1 al 99."
    return ""


# Guarda un jugador en la lista. Si ya había uno con ese nombre, le cambia los datos.
# Devuelve True si el jugador es nuevo, y False si ya existía.
def agregar_o_actualizar_jugador(lista_de_jugadores, nombre, valores_de_atributos, posicion_principal, posiciones_secundarias):
    jugador = buscar_jugador_por_nombre(lista_de_jugadores, nombre)
    if jugador == None:
        jugador_es_nuevo = True
        jugador = {"nombre": nombre.strip(), "juega": True}
        lista_de_jugadores.append(jugador)
    else:
        jugador_es_nuevo = False

    for atributo in ATRIBUTOS:
        jugador[atributo] = valores_de_atributos[atributo]
    jugador["posicion"] = posicion_principal

    # Las secundarias no repiten la principal ni se repiten entre ellas
    jugador["secundarias"] = []
    for posicion in posiciones_secundarias:
        if posicion != posicion_principal and posicion not in jugador["secundarias"]:
            jugador["secundarias"].append(posicion)

    return jugador_es_nuevo


# Dice si el jugador con ese nombre está en alguno de los equipos
def jugador_esta_en_algun_equipo(lista_de_equipos, nombre_del_jugador):
    for equipo in lista_de_equipos:
        for nombre_en_el_equipo in equipo["jugadores"]:
            if son_el_mismo_nombre(nombre_en_el_equipo, nombre_del_jugador):
                return True
    return False


# Texto para mostrar las posiciones de un jugador. Ejemplo: "ARQ (DEF, MED)"
def texto_de_posiciones(jugador):
    if jugador["posicion"] == "":
        return "Sin posición"
    texto = jugador["posicion"]
    if len(jugador["secundarias"]) > 0:
        # ", ".join(lista) junta los textos de la lista separados por coma
        texto = texto + " (" + ", ".join(jugador["secundarias"]) + ")"
    return texto


# ---------- MEDIAS ----------

# La media de un jugador es el promedio de sus 4 atributos
def media_del_jugador(jugador):
    suma = jugador["ritmo"] + jugador["pase"] + jugador["regate"] + jugador["defensa"]
    return suma / 4


# Media general de una lista de jugadores: el promedio de las medias de todos.
# Si la lista está vacía, devuelve 0.
def media_general(lista_de_jugadores):
    if len(lista_de_jugadores) == 0:
        return 0
    suma = 0
    for jugador in lista_de_jugadores:
        suma = suma + media_del_jugador(jugador)
    return suma / len(lista_de_jugadores)


# Promedio de un solo atributo en una lista de jugadores. Ejemplo: el ritmo promedio.
# Si la lista está vacía, devuelve 0.
def media_de_un_atributo(lista_de_jugadores, atributo):
    if len(lista_de_jugadores) == 0:
        return 0
    suma = 0
    for jugador in lista_de_jugadores:
        suma = suma + jugador[atributo]
    return suma / len(lista_de_jugadores)


# Un equipo guarda solo los nombres de sus jugadores.
# Esto devuelve la lista con los jugadores completos (con sus atributos).
def buscar_jugadores_del_equipo(todos_los_jugadores, equipo):
    jugadores_del_equipo = []
    for nombre in equipo["jugadores"]:
        jugadores_del_equipo.append(buscar_jugador_por_nombre(todos_los_jugadores, nombre))
    return jugadores_del_equipo


# Diferencia de media entre el equipo más fuerte y el más débil
def diferencia_entre_equipos(todos_los_jugadores, equipos):
    medias_de_los_equipos = []
    for equipo in equipos:
        jugadores_del_equipo = buscar_jugadores_del_equipo(todos_los_jugadores, equipo)
        medias_de_los_equipos.append(media_general(jugadores_del_equipo))
    # max() da el número más grande de la lista y min() el más chico
    return max(medias_de_los_equipos) - min(medias_de_los_equipos)


# Promedio de las medias de todos los equipos
def promedio_de_los_equipos(todos_los_jugadores, equipos):
    suma = 0
    for equipo in equipos:
        jugadores_del_equipo = buscar_jugadores_del_equipo(todos_los_jugadores, equipo)
        suma = suma + media_general(jugadores_del_equipo)
    return suma / len(equipos)


# ---------- PUESTOS DENTRO DE UN EQUIPO ----------

# Dice de qué juega cada jugador en su equipo.
# Devuelve un diccionario "nombre del jugador -> puesto". Ejemplo: {"Juan": "ARQ", "Pedro": "DEF"}
# Cada uno juega de su posición principal. Pero si el equipo no tiene arquero,
# ataja el primero que tenga "arquero" como posición secundaria.
def calcular_puesto_de_cada_jugador(jugadores_del_equipo):
    puesto_de_cada_jugador = {}
    el_equipo_tiene_arquero = False
    for jugador in jugadores_del_equipo:
        puesto_de_cada_jugador[jugador["nombre"]] = jugador["posicion"]
        if jugador["posicion"] == "ARQ":
            el_equipo_tiene_arquero = True

    if el_equipo_tiene_arquero == False:
        for jugador in jugadores_del_equipo:
            if "ARQ" in jugador["secundarias"]:
                puesto_de_cada_jugador[jugador["nombre"]] = "ARQ"
                break  # con un arquero alcanza: dejamos de buscar

    return puesto_de_cada_jugador


# Cuenta cuántos jugadores hay en cada puesto. Ejemplo: {"ARQ": 1, "DEF": 2, "MED": 1, "DEL": 1}
def contar_jugadores_por_puesto(puesto_de_cada_jugador):
    cantidad_por_puesto = {"ARQ": 0, "DEF": 0, "MED": 0, "DEL": 0}
    for nombre in puesto_de_cada_jugador:
        puesto = puesto_de_cada_jugador[nombre]
        if puesto != "":
            cantidad_por_puesto[puesto] = cantidad_por_puesto[puesto] + 1
    return cantidad_por_puesto


# Número de orden de cada puesto, para ordenar: ARQ=0, DEF=1, MED=2, DEL=3 y sin puesto=4
def numero_de_orden_del_puesto(puesto):
    if puesto == "ARQ":
        return 0
    if puesto == "DEF":
        return 1
    if puesto == "MED":
        return 2
    if puesto == "DEL":
        return 3
    return 4


# Dice si jugador_1 tiene que aparecer antes que jugador_2 en la lista del equipo
def va_antes_al_mostrar(jugador_1, jugador_2, puesto_de_cada_jugador):
    orden_del_1 = numero_de_orden_del_puesto(puesto_de_cada_jugador[jugador_1["nombre"]])
    orden_del_2 = numero_de_orden_del_puesto(puesto_de_cada_jugador[jugador_2["nombre"]])
    if orden_del_1 < orden_del_2:
        return True  # juega en un puesto que va más arriba
    if orden_del_1 == orden_del_2 and media_del_jugador(jugador_1) > media_del_jugador(jugador_2):
        return True  # juegan en el mismo puesto, pero tiene mejor media
    return False


# Ordena a los jugadores de un equipo para mostrarlos:
# primero el arquero, después defensores, mediocampistas y delanteros.
# Si dos juegan en el mismo puesto, va primero el de mejor media.
#
# Usa el "método burbuja": recorre la lista comparando cada jugador con el de al lado,
# y si están en el orden equivocado los da vuelta. Lo repite hasta que queda ordenada.
def ordenar_jugadores_para_mostrar(jugadores_del_equipo, puesto_de_cada_jugador):
    # Hacemos una copia para no desordenar la lista original
    jugadores_ordenados = []
    for jugador in jugadores_del_equipo:
        jugadores_ordenados.append(jugador)

    for numero_de_vuelta in range(len(jugadores_ordenados)):
        for lugar in range(len(jugadores_ordenados) - 1):
            jugador_actual = jugadores_ordenados[lugar]
            jugador_siguiente = jugadores_ordenados[lugar + 1]
            if va_antes_al_mostrar(jugador_siguiente, jugador_actual, puesto_de_cada_jugador):
                jugadores_ordenados[lugar] = jugador_siguiente
                jugadores_ordenados[lugar + 1] = jugador_actual

    return jugadores_ordenados


# ---------- ARMAR EQUIPOS PAREJOS ----------
# Mientras se arman, cada equipo es un "grupo": una lista con los jugadores completos.
# Al final cada grupo se pasa a un equipo con nombre ("Equipo 1", "Equipo 2", ...).

# Para repartir, el que puede atajar (de principal o de secundaria) cuenta como arquero.
# Así los que pueden atajar quedan en equipos distintos.
def posicion_para_repartir(jugador):
    if jugador["posicion"] == "ARQ" or "ARQ" in jugador["secundarias"]:
        return "ARQ"
    return jugador["posicion"]


# Ordena a los jugadores así: primero los arqueros, después defensores,
# mediocampistas, delanteros y al final los que no tienen posición.
def ordenar_por_posicion(jugadores):
    jugadores_ordenados = []
    for posicion in ["ARQ", "DEF", "MED", "DEL", ""]:
        for jugador in jugadores:
            if posicion_para_repartir(jugador) == posicion:
                jugadores_ordenados.append(jugador)
    return jugadores_ordenados


# Diferencia de media entre el grupo más fuerte y el más débil
def diferencia_entre_grupos(grupos):
    medias_de_los_grupos = []
    for grupo in grupos:
        medias_de_los_grupos.append(media_general(grupo))
    return max(medias_de_los_grupos) - min(medias_de_los_grupos)


# Prueba cambiar cada jugador del primer grupo con cada jugador del segundo grupo.
# Si con un cambio la diferencia de media baja, lo deja. Si no, lo deshace.
# Devuelve True si dejó por lo menos un cambio.
def probar_cambios_entre_dos_grupos(grupos, primer_grupo, segundo_grupo, usar_posiciones):
    dejo_algun_cambio = False

    for lugar_en_el_primero in range(len(primer_grupo)):
        for lugar_en_el_segundo in range(len(segundo_grupo)):
            jugador_del_primero = primer_grupo[lugar_en_el_primero]
            jugador_del_segundo = segundo_grupo[lugar_en_el_segundo]

            # Si se usan posiciones, solo se cambian jugadores de la misma posición
            if usar_posiciones and posicion_para_repartir(jugador_del_primero) != posicion_para_repartir(jugador_del_segundo):
                continue  # este par no se puede cambiar: pasamos al siguiente

            diferencia_antes = diferencia_entre_grupos(grupos)

            # Hacemos el cambio
            primer_grupo[lugar_en_el_primero] = jugador_del_segundo
            segundo_grupo[lugar_en_el_segundo] = jugador_del_primero

            diferencia_despues = diferencia_entre_grupos(grupos)

            # Si mejoró (por lo menos un poquito: 0.001) lo dejamos. Si no, lo deshacemos.
            if diferencia_despues < diferencia_antes - 0.001:
                dejo_algun_cambio = True
            else:
                primer_grupo[lugar_en_el_primero] = jugador_del_primero
                segundo_grupo[lugar_en_el_segundo] = jugador_del_segundo

    return dejo_algun_cambio


# Prueba cambios de jugadores entre todos los pares de grupos
# (el 1 con el 2, el 1 con el 3, el 2 con el 3...) para que las medias queden parejas.
# Repite todo hasta que ningún cambio sirva más.
def emparejar_grupos(grupos, usar_posiciones):
    hubo_alguna_mejora = True
    while hubo_alguna_mejora:
        hubo_alguna_mejora = False
        for numero_del_primero in range(len(grupos)):
            for numero_del_segundo in range(numero_del_primero + 1, len(grupos)):
                primer_grupo = grupos[numero_del_primero]
                segundo_grupo = grupos[numero_del_segundo]
                if probar_cambios_entre_dos_grupos(grupos, primer_grupo, segundo_grupo, usar_posiciones):
                    hubo_alguna_mejora = True


# Arma un texto que describe una combinación de equipos, para saber si ya salió antes.
# No importa el orden de los equipos ni de los jugadores: la misma gente da el mismo texto.
# Ejemplo: "ana,juan | luis,pedro"
def texto_de_la_combinacion(equipos):
    textos_de_los_equipos = []
    for equipo in equipos:
        nombres_en_minuscula = []
        for nombre in equipo["jugadores"]:
            nombres_en_minuscula.append(nombre.lower())
        nombres_en_minuscula.sort()  # sort() ordena la lista alfabéticamente
        textos_de_los_equipos.append(",".join(nombres_en_minuscula))
    textos_de_los_equipos.sort()
    return " | ".join(textos_de_los_equipos)


# Arma los equipos más parejos que encuentre, sin repetir las combinaciones ya vistas.
# Hace 20 intentos distintos y se queda con el más parejo.
# Devuelve la lista de equipos, o None si no encontró ninguna combinación nueva.
def armar_equipos_parejos(jugadores_que_juegan, cantidad_de_equipos, usar_posiciones, combinaciones_ya_vistas):
    mejores_equipos = None
    diferencia_de_los_mejores = 0

    for numero_de_intento in range(20):
        # 1. Mezclamos a los jugadores al azar
        jugadores_mezclados = []
        for jugador in jugadores_que_juegan:
            jugadores_mezclados.append(jugador)
        random.shuffle(jugadores_mezclados)

        # 2. Si se usan posiciones, los ordenamos por posición (los arqueros primero)
        if usar_posiciones:
            jugadores_mezclados = ordenar_por_posicion(jugadores_mezclados)

        # 3. Los repartimos de a uno por equipo, como cuando se "pisa":
        #    uno al primer equipo, otro al segundo... y al llegar al último se vuelve al primero.
        grupos = []
        while len(grupos) < cantidad_de_equipos:
            grupos.append([])  # cada equipo empieza vacío

        numero_del_equipo_que_recibe = 0  # el primero es 0, porque las listas empiezan en 0
        for jugador in jugadores_mezclados:
            grupos[numero_del_equipo_que_recibe].append(jugador)
            numero_del_equipo_que_recibe = numero_del_equipo_que_recibe + 1
            if numero_del_equipo_que_recibe == cantidad_de_equipos:
                numero_del_equipo_que_recibe = 0

        # 4. Probamos cambios para que las medias queden parejas
        emparejar_grupos(grupos, usar_posiciones)

        # 5. Pasamos cada grupo a un equipo con nombre: "Equipo 1", "Equipo 2", ...
        equipos = []
        for grupo in grupos:
            nombres_de_los_jugadores = []
            for jugador in grupo:
                nombres_de_los_jugadores.append(jugador["nombre"])
            numero_del_equipo = len(equipos) + 1
            equipos.append({"nombre": "Equipo " + str(numero_del_equipo), "jugadores": nombres_de_los_jugadores})

        # 6. Si esta combinación ya salió antes, no la usamos.
        #    Si es nueva, nos quedamos con la más pareja de todos los intentos.
        ya_salio_antes = texto_de_la_combinacion(equipos) in combinaciones_ya_vistas
        if ya_salio_antes == False:
            diferencia = diferencia_entre_grupos(grupos)
            if mejores_equipos == None or diferencia < diferencia_de_los_mejores:
                mejores_equipos = equipos
                diferencia_de_los_mejores = diferencia

    return mejores_equipos


# ---------- CAMBIOS A MANO ----------

# Pasa a un jugador a otro equipo.
# "indice_del_equipo_nuevo" es el lugar del equipo en la lista (el primero es 0).
# Devuelve False si no se puede: si no está en ningún equipo, o si su equipo quedaría vacío.
def pasar_jugador_a_otro_equipo(equipos, nombre_del_jugador, indice_del_equipo_nuevo):
    for equipo in equipos:
        for nombre_en_el_equipo in equipo["jugadores"]:
            if son_el_mismo_nombre(nombre_en_el_equipo, nombre_del_jugador):
                if len(equipo["jugadores"]) == 1:
                    return False  # es el único del equipo: quedaría vacío
                equipo["jugadores"].remove(nombre_en_el_equipo)
                equipos[indice_del_equipo_nuevo]["jugadores"].append(nombre_en_el_equipo)
                return True
    return False


# Le cambia el nombre a un equipo. También lo cambia en los partidos del torneo.
# "indice_del_equipo" es el lugar del equipo en la lista (el primero es 0).
# Devuelve False si ya hay otro equipo con ese nombre.
def cambiar_nombre_de_equipo(equipos, partidos, indice_del_equipo, nombre_nuevo):
    nombre_nuevo = nombre_nuevo.strip()
    for indice_de_otro_equipo in range(len(equipos)):
        nombre_del_otro_equipo = equipos[indice_de_otro_equipo]["nombre"]
        if indice_de_otro_equipo != indice_del_equipo and son_el_mismo_nombre(nombre_del_otro_equipo, nombre_nuevo):
            return False

    nombre_viejo = equipos[indice_del_equipo]["nombre"]
    equipos[indice_del_equipo]["nombre"] = nombre_nuevo
    for partido in partidos:
        if partido["local"] == nombre_viejo:
            partido["local"] = nombre_nuevo
        if partido["visitante"] == nombre_viejo:
            partido["visitante"] = nombre_nuevo
    return True


# ---------- TORNEO ----------

def crear_partido_sin_jugar(numero_de_fecha, equipo_local, equipo_visitante):
    return {"fecha": numero_de_fecha, "local": equipo_local, "visitante": equipo_visitante, "golesLocal": None, "golesVisitante": None}


# Arma el fixture "todos contra todos": cada par de equipos juega una vez
# (dos veces si es ida y vuelta). Si la cantidad de equipos es impar,
# en cada fecha un equipo queda libre.
#
# Cómo funciona:
#   - Ponemos a los equipos en una fila.
#   - En cada fecha juega el 1° con el último, el 2° con el anteúltimo, y así.
#   - Para la fecha siguiente, el último pasa al 2° lugar (el 1° no se mueve nunca).
#   Así, al terminar, todos jugaron contra todos.
def crear_fixture(nombres_de_equipos, ida_y_vuelta):
    fila_de_equipos = []
    for nombre in nombres_de_equipos:
        fila_de_equipos.append(nombre)

    # Si son impares, agregamos un None: el que "juega" contra None queda libre esa fecha.
    # (% 2 da el resto de dividir por 2: si da 1, el número es impar)
    if len(fila_de_equipos) % 2 == 1:
        fila_de_equipos.append(None)

    cantidad_en_la_fila = len(fila_de_equipos)
    cantidad_de_fechas = cantidad_en_la_fila - 1
    partidos_por_fecha = cantidad_en_la_fila // 2  # // divide sin decimales

    partidos = []
    for numero_de_fecha in range(1, cantidad_de_fechas + 1):
        # El 1° juega con el último, el 2° con el anteúltimo, y así
        for lugar in range(partidos_por_fecha):
            equipo_local = fila_de_equipos[lugar]
            equipo_visitante = fila_de_equipos[cantidad_en_la_fila - 1 - lugar]
            if equipo_local != None and equipo_visitante != None:
                partidos.append(crear_partido_sin_jugar(numero_de_fecha, equipo_local, equipo_visitante))

        # Para la fecha siguiente: sacamos al último de la fila (pop)
        # y lo metemos en el 2° lugar (insert en el lugar 1, porque se cuenta desde 0)
        ultimo_equipo = fila_de_equipos.pop()
        fila_de_equipos.insert(1, ultimo_equipo)

    if ida_y_vuelta:
        # La vuelta: los mismos partidos, con local y visitante al revés, en las fechas que siguen
        partidos_de_vuelta = []
        for partido_de_ida in partidos:
            fecha_de_vuelta = partido_de_ida["fecha"] + cantidad_de_fechas
            partidos_de_vuelta.append(crear_partido_sin_jugar(fecha_de_vuelta, partido_de_ida["visitante"], partido_de_ida["local"]))
        partidos = partidos + partidos_de_vuelta

    return partidos


def numero_de_la_ultima_fecha(partidos):
    ultima_fecha = 0
    for partido in partidos:
        if partido["fecha"] > ultima_fecha:
            ultima_fecha = partido["fecha"]
    return ultima_fecha


# Devuelve los equipos que no juegan en esa fecha
def equipos_libres_en_la_fecha(nombres_de_equipos, partidos, numero_de_fecha):
    equipos_que_juegan = []
    for partido in partidos:
        if partido["fecha"] == numero_de_fecha:
            equipos_que_juegan.append(partido["local"])
            equipos_que_juegan.append(partido["visitante"])

    equipos_libres = []
    for nombre in nombres_de_equipos:
        if nombre not in equipos_que_juegan:
            equipos_libres.append(nombre)
    return equipos_libres


# ---------- TABLA DE POSICIONES ----------

# Busca la fila de la tabla que corresponde a un equipo
def buscar_fila_del_equipo(filas, nombre_del_equipo):
    for fila in filas:
        if fila["equipo"] == nombre_del_equipo:
            return fila
    return None


# Dice si fila_1 tiene que ir más arriba que fila_2 en la tabla
def va_mas_arriba_en_la_tabla(fila_1, fila_2):
    if fila_1["puntos"] > fila_2["puntos"]:
        return True  # tiene más puntos
    if fila_1["puntos"] == fila_2["puntos"] and fila_1["diferencia_de_gol"] > fila_2["diferencia_de_gol"]:
        return True  # mismos puntos, pero mejor diferencia de gol
    return False


# Arma la tabla de posiciones: una fila por equipo.
# Ganar da 3 puntos, empatar da 1 y perder da 0.
# Queda ordenada: más puntos arriba. Si empatan en puntos, arriba el de mejor diferencia de gol.
def calcular_tabla_de_posiciones(nombres_de_equipos, partidos):
    filas = []
    for nombre in nombres_de_equipos:
        filas.append({
            "equipo": nombre,
            "partidos_jugados": 0,
            "ganados": 0,
            "empatados": 0,
            "perdidos": 0,
            "goles_a_favor": 0,
            "goles_en_contra": 0,
            "diferencia_de_gol": 0,
            "puntos": 0,
        })

    for partido in partidos:
        if partido["golesLocal"] == None:
            continue  # todavía no se jugó: no cuenta, pasamos al siguiente

        fila_del_local = buscar_fila_del_equipo(filas, partido["local"])
        fila_del_visitante = buscar_fila_del_equipo(filas, partido["visitante"])
        goles_del_local = partido["golesLocal"]
        goles_del_visitante = partido["golesVisitante"]

        fila_del_local["partidos_jugados"] = fila_del_local["partidos_jugados"] + 1
        fila_del_visitante["partidos_jugados"] = fila_del_visitante["partidos_jugados"] + 1

        fila_del_local["goles_a_favor"] = fila_del_local["goles_a_favor"] + goles_del_local
        fila_del_local["goles_en_contra"] = fila_del_local["goles_en_contra"] + goles_del_visitante
        fila_del_visitante["goles_a_favor"] = fila_del_visitante["goles_a_favor"] + goles_del_visitante
        fila_del_visitante["goles_en_contra"] = fila_del_visitante["goles_en_contra"] + goles_del_local

        if goles_del_local > goles_del_visitante:
            fila_del_local["ganados"] = fila_del_local["ganados"] + 1
            fila_del_visitante["perdidos"] = fila_del_visitante["perdidos"] + 1
        elif goles_del_local < goles_del_visitante:
            fila_del_visitante["ganados"] = fila_del_visitante["ganados"] + 1
            fila_del_local["perdidos"] = fila_del_local["perdidos"] + 1
        else:
            fila_del_local["empatados"] = fila_del_local["empatados"] + 1
            fila_del_visitante["empatados"] = fila_del_visitante["empatados"] + 1

    for fila in filas:
        fila["diferencia_de_gol"] = fila["goles_a_favor"] - fila["goles_en_contra"]
        fila["puntos"] = fila["ganados"] * 3 + fila["empatados"]

    # Ordenamos con el método burbuja (el mismo que se usa para ordenar los equipos)
    for numero_de_vuelta in range(len(filas)):
        for lugar in range(len(filas) - 1):
            fila_actual = filas[lugar]
            fila_siguiente = filas[lugar + 1]
            if va_mas_arriba_en_la_tabla(fila_siguiente, fila_actual):
                filas[lugar] = fila_siguiente
                filas[lugar + 1] = fila_actual

    return filas
