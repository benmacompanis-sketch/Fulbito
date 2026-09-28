# ==========================================
# pruebas.py - Revisa que las cuentas de logica.py den bien
# ==========================================
# Para correrlo, en una terminal dentro de esta carpeta:
#     python pruebas.py
# Si algo está mal, se frena y muestra en qué línea.
# Si todo está bien, al final dice "Todas las pruebas pasaron".

import random
import logica

# Así el azar sale siempre igual y las pruebas dan lo mismo cada vez
random.seed(1)


def nuevo_jugador(nombre, media, posicion, secundarias):
    return {
        "nombre": nombre,
        "ritmo": media,
        "pase": media,
        "regate": media,
        "defensa": media,
        "posicion": posicion,
        "secundarias": secundarias,
        "juega": True,
    }


def prueba_media():
    jugador = {"nombre": "Ana", "ritmo": 80, "pase": 70, "regate": 60, "defensa": 50}
    assert logica.media_jugador(jugador) == 65
    assert logica.redondear(66.666) == "66.7"
    print("OK: media de un jugador")


def prueba_convertir_numero():
    assert logica.convertir_numero("7") == 7
    assert logica.convertir_numero(" 12 ") == 12
    assert logica.convertir_numero("hola") == None
    assert logica.convertir_numero("7.5") == None
    assert logica.convertir_numero("-1") == None
    assert logica.convertir_numero("") == None
    print("OK: convertir texto en número")


def prueba_revisar_jugador():
    bien = {"ritmo": 80, "pase": 70, "regate": 60, "defensa": 50}
    assert logica.revisar_jugador("Ana", bien, "DEF") == ""
    assert logica.revisar_jugador("", bien, "DEF") == "Poné un nombre."
    assert logica.revisar_jugador("Ana", bien, "") == "Elegí la posición principal."

    fuera_de_rango = {"ritmo": 150, "pase": 70, "regate": 60, "defensa": 50}
    assert logica.revisar_jugador("Ana", fuera_de_rango, "DEF") != ""

    no_es_numero = {"ritmo": None, "pase": 70, "regate": 60, "defensa": 50}
    assert logica.revisar_jugador("Ana", no_es_numero, "DEF") != ""
    print("OK: revisar los datos de un jugador")


def prueba_guardar_jugador():
    jugadores = []
    numeros = {"ritmo": 80, "pase": 70, "regate": 60, "defensa": 50}
    assert logica.guardar_jugador(jugadores, "Pepe", numeros, "ARQ", ["DEF", "ARQ"]) == True
    # La principal no queda repetida como secundaria
    assert jugadores[0]["secundarias"] == ["DEF"]

    # Mismo nombre con otras mayúsculas: se actualiza, no se repite
    otros = {"ritmo": 90, "pase": 90, "regate": 90, "defensa": 90}
    assert logica.guardar_jugador(jugadores, "PEPE", otros, "DEF", []) == False
    assert len(jugadores) == 1
    assert jugadores[0]["ritmo"] == 90
    print("OK: guardar y actualizar jugadores")


def prueba_equipos_parejos():
    # Con estas medias se puede armar dos equipos con media exactamente igual
    # (por ejemplo 90, 80, 70, 55, 40 contra 85, 75, 65, 60, 50)
    medias = [90, 85, 80, 75, 70, 65, 60, 55, 50, 40]
    jugadores = []
    for i in range(len(medias)):
        jugadores.append(nuevo_jugador("J" + str(i), medias[i], "MED", []))

    equipos = logica.armar_equipos(jugadores, 2, False, [])

    # Están todos, y cada uno una sola vez (no se inventa ni se repite nadie)
    todos = []
    for equipo in equipos:
        for nombre in equipo["jugadores"]:
            todos.append(nombre)
    assert len(todos) == 10
    for jugador in jugadores:
        assert todos.count(jugador["nombre"]) == 1

    # Quedan parejos
    assert logica.diferencia_entre_equipos(jugadores, equipos) < 0.5
    print("OK: equipos parejos por media")


def prueba_posiciones_parejas():
    jugadores = [
        nuevo_jugador("Arq1", 60, "ARQ", []),
        nuevo_jugador("Arq2", 62, "ARQ", []),
        nuevo_jugador("Del1", 85, "DEL", []),
        nuevo_jugador("Del2", 84, "DEL", []),
        nuevo_jugador("Del3", 83, "DEL", []),
        nuevo_jugador("Del4", 86, "DEL", []),
        nuevo_jugador("Def1", 65, "DEF", []),
        nuevo_jugador("Def2", 64, "DEF", []),
        nuevo_jugador("Med1", 70, "MED", []),
        nuevo_jugador("Med2", 71, "MED", []),
    ]
    equipos = logica.armar_equipos(jugadores, 2, True, [])

    # Cada equipo tiene un arquero, dos delanteros, un defensor y un medio
    for equipo in equipos:
        lista = logica.jugadores_del_equipo(jugadores, equipo)
        cuenta = logica.contar_puestos(logica.asignar_puestos(lista))
        assert cuenta["ARQ"] == 1
        assert cuenta["DEL"] == 2
        assert cuenta["DEF"] == 1
        assert cuenta["MED"] == 1
    print("OK: equipos parejos por posición")


def prueba_otra_combinacion():
    jugadores = []
    for i in range(10):
        jugadores.append(nuevo_jugador("J" + str(i), 50 + i * 4, "MED", []))

    vistas = []
    for vez in range(5):
        equipos = logica.armar_equipos(jugadores, 2, False, vistas)
        clave = logica.clave_de_equipos(equipos)
        assert clave not in vistas
        vistas.append(clave)

    # Con 4 jugadores en 2 equipos de 2 hay solo 3 combinaciones posibles
    cuatro = []
    for i in range(4):
        cuatro.append(nuevo_jugador("K" + str(i), 50 + i * 10, "MED", []))
    vistas = []
    for vez in range(3):
        equipos = logica.armar_equipos(cuatro, 2, False, vistas)
        vistas.append(logica.clave_de_equipos(equipos))
    assert logica.armar_equipos(cuatro, 2, False, vistas) == None
    print("OK: otra combinación no repite")


def prueba_puestos():
    # El caso de la captura: fausti y liberman atajan aunque su principal sea otra
    jugadores = [
        nuevo_jugador("bufalo", 93, "DEF", []),
        nuevo_jugador("chichi", 30, "DEF", []),
        nuevo_jugador("fausti", 60, "MED", ["ARQ"]),
        nuevo_jugador("tanque", 60, "MED", []),
        nuevo_jugador("Papo", 86, "DEL", ["MED"]),
    ]
    puestos = logica.asignar_puestos(jugadores)
    assert puestos["fausti"] == "ARQ"
    assert puestos["Papo"] == "DEL"

    ordenados = logica.ordenar_para_mostrar(jugadores, puestos)
    assert ordenados[0]["nombre"] == "fausti"
    assert ordenados[4]["nombre"] == "Papo"

    # Si el único defensor puede atajar y no hay arquero, va al arco igual
    jugadores = [
        nuevo_jugador("A", 60, "DEF", ["ARQ"]),
        nuevo_jugador("B", 60, "MED", []),
        nuevo_jugador("C", 60, "DEL", []),
    ]
    assert logica.asignar_puestos(jugadores)["A"] == "ARQ"

    # Pero el único mediocampista no deja el medio vacío para ser defensor
    jugadores = [
        nuevo_jugador("G", 60, "ARQ", []),
        nuevo_jugador("M", 60, "MED", ["DEF"]),
        nuevo_jugador("F", 60, "DEL", []),
    ]
    assert logica.asignar_puestos(jugadores)["M"] == "MED"
    print("OK: puestos dentro de cada equipo")


def prueba_fixture():
    for cantidad in range(2, 9):
        nombres = []
        for i in range(cantidad):
            nombres.append("E" + str(i))
        partidos = logica.crear_fixture(nombres, False)

        # Cada par de equipos se cruza una sola vez
        cruces = []
        for partido in partidos:
            par = [partido["local"], partido["visitante"]]
            par.sort()
            cruces.append(par[0] + "-" + par[1])
        assert len(cruces) == cantidad * (cantidad - 1) // 2
        for cruce in cruces:
            assert cruces.count(cruce) == 1

        # Nadie juega dos veces en la misma fecha
        for fecha in range(1, logica.ultima_fecha(partidos) + 1):
            juegan = []
            for partido in partidos:
                if partido["fecha"] == fecha:
                    juegan.append(partido["local"])
                    juegan.append(partido["visitante"])
            for nombre in juegan:
                assert juegan.count(nombre) == 1

        # Ida y vuelta: el doble de partidos
        assert len(logica.crear_fixture(nombres, True)) == 2 * len(partidos)
    print("OK: fixture todos contra todos")


def prueba_tabla():
    partidos = logica.crear_fixture(["A", "B", "C"], False)
    for partido in partidos:
        cruce = [partido["local"], partido["visitante"]]
        cruce.sort()
        # A le gana 2-0 a B, A empata 1-1 con C, B le gana 3-1 a C
        if cruce == ["A", "B"]:
            goles = {"A": 2, "B": 0}
        elif cruce == ["A", "C"]:
            goles = {"A": 1, "C": 1}
        else:
            goles = {"B": 3, "C": 1}
        partido["golesLocal"] = goles[partido["local"]]
        partido["golesVisitante"] = goles[partido["visitante"]]

    filas = logica.calcular_tabla(["A", "B", "C"], partidos)
    assert filas[0]["equipo"] == "A" and filas[0]["pts"] == 4 and filas[0]["dg"] == 2
    assert filas[1]["equipo"] == "B" and filas[1]["pts"] == 3 and filas[1]["dg"] == 0
    assert filas[2]["equipo"] == "C" and filas[2]["pts"] == 1 and filas[2]["dg"] == -2
    print("OK: tabla de posiciones")


def prueba_mover_y_renombrar():
    equipos = [
        {"nombre": "Rojo", "jugadores": ["A", "B"]},
        {"nombre": "Azul", "jugadores": ["C"]},
    ]
    assert logica.mover_jugador(equipos, "B", 1) == True
    assert equipos[1]["jugadores"] == ["C", "B"]
    # No se puede dejar un equipo vacío
    assert logica.mover_jugador(equipos, "A", 1) == False

    partidos = logica.crear_fixture(["Rojo", "Azul"], False)
    assert logica.renombrar_equipo(equipos, partidos, 0, "Verde") == True
    assert equipos[0]["nombre"] == "Verde"
    assert partidos[0]["local"] == "Verde" or partidos[0]["visitante"] == "Verde"
    # No puede haber dos equipos con el mismo nombre
    assert logica.renombrar_equipo(equipos, partidos, 0, "azul") == False
    print("OK: mover jugadores y renombrar equipos")


def prueba_datos_viejos():
    # Datos de la primera versión de consola (en inglés)
    viejos = {"players": [{"name": "Ana", "pace": 80, "passing": 70, "dribbling": 60, "defending": 50}]}
    logica.arreglar_datos(viejos)
    assert viejos["jugadores"][0]["nombre"] == "Ana"
    assert viejos["jugadores"][0]["pase"] == 70
    assert viejos["jugadores"][0]["posicion"] == ""
    assert viejos["equipos"] == []

    # Jugador de antes de que existieran las posiciones
    sin_posicion = {"jugadores": [{"nombre": "Beto", "ritmo": 70, "pase": 70, "regate": 70, "defensa": 70}]}
    logica.arreglar_datos(sin_posicion)
    assert logica.texto_posiciones(sin_posicion["jugadores"][0]) == "Sin posición"
    print("OK: datos guardados por versiones anteriores")


prueba_media()
prueba_convertir_numero()
prueba_revisar_jugador()
prueba_guardar_jugador()
prueba_equipos_parejos()
prueba_posiciones_parejas()
prueba_otra_combinacion()
prueba_puestos()
prueba_fixture()
prueba_tabla()
prueba_mover_y_renombrar()
prueba_datos_viejos()
print("")
print("Todas las pruebas pasaron.")
