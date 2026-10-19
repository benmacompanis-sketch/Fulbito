# ==========================================
# pruebas.py - Revisa que las cuentas de logica.py den bien
# ==========================================
# Para correrlo:  python pruebas.py
# Si algo está mal, se frena y muestra en qué línea.

import random
import logica

# Así el azar sale siempre igual y las pruebas dan lo mismo cada vez
random.seed(1)


def nuevo_jugador(nombre, media, posicion, secundarias):
    jugador = {}
    jugador["nombre"] = nombre
    jugador["ritmo"] = media
    jugador["pase"] = media
    jugador["regate"] = media
    jugador["defensa"] = media
    jugador["posicion"] = posicion
    jugador["secundarias"] = secundarias
    jugador["juega"] = True
    return jugador


# ---- Media ----
jugador = {"nombre": "Ana", "ritmo": 80, "pase": 70, "regate": 60, "defensa": 50}
assert logica.media_jugador(jugador) == 65
print("OK: media de un jugador")


# ---- Convertir texto en número ----
assert logica.convertir_numero("7") == 7
assert logica.convertir_numero(" 12 ") == 12
assert logica.convertir_numero("hola") == None
assert logica.convertir_numero("7.5") == None
assert logica.convertir_numero("") == None
print("OK: convertir texto en número")


# ---- Revisar y guardar jugadores ----
bien = {"ritmo": 80, "pase": 70, "regate": 60, "defensa": 50}
mal = {"ritmo": 150, "pase": 70, "regate": 60, "defensa": 50}
assert logica.revisar_jugador("Ana", bien, "DEF") == ""
assert logica.revisar_jugador("", bien, "DEF") != ""
assert logica.revisar_jugador("Ana", bien, "") != ""
assert logica.revisar_jugador("Ana", mal, "DEF") != ""

jugadores = []
assert logica.guardar_jugador(jugadores, "Pepe", bien, "ARQ", ["DEF", "ARQ", "DEF"]) == True
assert jugadores[0]["secundarias"] == ["DEF"]
assert logica.guardar_jugador(jugadores, "PEPE", mal, "DEF", []) == False
assert len(jugadores) == 1
print("OK: revisar y guardar jugadores")


# ---- Equipos parejos ----
# Con estas medias se pueden armar dos equipos con media exactamente igual
medias = [90, 85, 80, 75, 70, 65, 60, 55, 50, 40]
jugadores = []
for i in range(len(medias)):
    jugadores.append(nuevo_jugador("J" + str(i), medias[i], "MED", []))
equipos = logica.armar_equipos(jugadores, 2, False, [])

todos = []
for equipo in equipos:
    for nombre in equipo["jugadores"]:
        todos.append(nombre)
assert len(todos) == 10
for jugador in jugadores:
    assert todos.count(jugador["nombre"]) == 1  # nadie repetido ni inventado
assert logica.diferencia_entre_equipos(jugadores, equipos) < 0.5
print("OK: equipos parejos por media")


# ---- Equipos parejos por posición ----
jugadores = [
    nuevo_jugador("Arq1", 60, "ARQ", []),
    nuevo_jugador("Def1", 62, "DEF", ["ARQ"]),
    nuevo_jugador("Del1", 85, "DEL", []),
    nuevo_jugador("Del2", 84, "DEL", []),
    nuevo_jugador("Del3", 83, "DEL", []),
    nuevo_jugador("Del4", 86, "DEL", []),
    nuevo_jugador("Def2", 65, "DEF", []),
    nuevo_jugador("Def3", 64, "DEF", []),
    nuevo_jugador("Med1", 70, "MED", []),
    nuevo_jugador("Med2", 71, "MED", []),
]
equipos = logica.armar_equipos(jugadores, 2, True, [])
for equipo in equipos:
    lista = logica.jugadores_del_equipo(jugadores, equipo)
    cuenta = logica.contar_puestos(logica.puestos_del_equipo(lista))
    assert cuenta["ARQ"] == 1  # el arquero y el defensor que ataja quedan separados
    assert cuenta["DEL"] == 2
print("OK: equipos parejos por posición")


# ---- Otra combinación no repite ----
jugadores = []
for i in range(10):
    jugadores.append(nuevo_jugador("J" + str(i), 50 + i * 4, "MED", []))
vistas = []
for vez in range(5):
    equipos = logica.armar_equipos(jugadores, 2, False, vistas)
    clave = logica.clave_de_equipos(equipos)
    assert clave not in vistas
    vistas.append(clave)
print("OK: otra combinación no repite")


# ---- Quién ataja ----
equipo = [
    nuevo_jugador("bufalo", 93, "DEF", []),
    nuevo_jugador("chichi", 30, "DEF", []),
    nuevo_jugador("fausti", 60, "MED", ["ARQ"]),
    nuevo_jugador("tanque", 60, "MED", []),
    nuevo_jugador("Papo", 86, "DEL", ["MED"]),
]
puestos = logica.puestos_del_equipo(equipo)
assert puestos["fausti"] == "ARQ"
ordenados = logica.ordenar_para_mostrar(equipo, puestos)
assert ordenados[0]["nombre"] == "fausti"
assert ordenados[4]["nombre"] == "Papo"
print("OK: el que ataja aparece primero")


# ---- Fixture ----
for cantidad in range(2, 9):
    nombres = []
    for i in range(cantidad):
        nombres.append("E" + str(i))
    partidos = logica.crear_fixture(nombres, False)

    cruces = []
    for partido in partidos:
        par = [partido["local"], partido["visitante"]]
        par.sort()
        cruces.append(par[0] + "-" + par[1])
    assert len(cruces) == cantidad * (cantidad - 1) // 2
    for cruce in cruces:
        assert cruces.count(cruce) == 1  # cada cruce una sola vez

    assert len(logica.crear_fixture(nombres, True)) == 2 * len(partidos)
print("OK: fixture todos contra todos")


# ---- Tabla ----
partidos = [
    {"fecha": 1, "local": "A", "visitante": "B", "golesLocal": 2, "golesVisitante": 0},
    {"fecha": 2, "local": "A", "visitante": "C", "golesLocal": 1, "golesVisitante": 1},
    {"fecha": 3, "local": "B", "visitante": "C", "golesLocal": 3, "golesVisitante": 1},
]
filas = logica.calcular_tabla(["A", "B", "C"], partidos)
assert filas[0]["equipo"] == "A" and filas[0]["pts"] == 4
assert filas[1]["equipo"] == "B" and filas[1]["pts"] == 3
assert filas[2]["equipo"] == "C" and filas[2]["pts"] == 1
print("OK: tabla de posiciones")


# ---- Mover y renombrar ----
equipos = [{"nombre": "Rojo", "jugadores": ["A", "B"]}, {"nombre": "Azul", "jugadores": ["C"]}]
assert logica.mover_jugador(equipos, "B", 1) == True
assert logica.mover_jugador(equipos, "A", 1) == False  # Rojo quedaría vacío
assert logica.renombrar_equipo(equipos, [], 0, "Verde") == True
assert logica.renombrar_equipo(equipos, [], 0, "azul") == False
print("OK: mover y renombrar")


# ---- Datos viejos ----
viejos = {"players": [{"name": "Ana", "pace": 80, "passing": 70, "dribbling": 60, "defending": 50}]}
logica.arreglar_datos(viejos)
assert viejos["jugadores"][0]["nombre"] == "Ana"
assert viejos["jugadores"][0]["posicion"] == ""
print("OK: datos de versiones viejas")

print("")
print("Todas las pruebas pasaron.")
