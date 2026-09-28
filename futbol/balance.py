"""Reparto de jugadores en equipos parejos.

Lógica pura: no lee ni escribe archivos ni pide datos. El azar entra sólo por el
`random.Random` que recibe, así los tests son reproducibles.

El criterio es minimizar la diferencia de media general entre el mejor y el peor
equipo; como desempate, también se emparejan las medias de cada atributo (así no
queda un equipo con todos los rápidos y otro con todos los defensores).
"""

from __future__ import annotations

import random
from typing import Iterable

from .models import ATTRIBUTES, Player, Team, ValidationError

# Peso de la diferencia por atributo frente a la diferencia de media general.
ATTRIBUTE_WEIGHT = 0.1
# Reintentos desde repartos al azar: muchos con grupos chicos, menos con grupos
# grandes (cada búsqueda local cuesta más y el resultado ya sale parejo).
MAX_RESTARTS = 40
MIN_RESTARTS = 10
_EPS = 1e-9

Partition = frozenset  # frozenset[frozenset[str]]: claves de jugadores por equipo


class NotEnoughPlayersError(ValidationError):
    def __init__(self, missing: int, needed: int):
        self.missing = missing
        self.needed = needed
        super().__init__(
            f"Faltan {missing} jugador(es): se necesitan al menos {needed}. "
            "No se inventan jugadores; cargá más o armá menos equipos."
        )


class NoNewCombinationError(ValidationError):
    def __init__(self) -> None:
        super().__init__("No encontré otra combinación de equipos que no se haya armado antes.")


def team_sizes(num_players: int, num_teams: int) -> list[int]:
    """Tamaños de equipo lo más parejos posible (difieren a lo sumo en 1)."""
    base, extra = divmod(num_players, num_teams)
    return [base + 1 if i < extra else base for i in range(num_teams)]


def check_players(players: list[Player], num_teams: int, players_per_team: int) -> None:
    if num_teams < 2:
        raise ValidationError("Hacen falta al menos 2 equipos.")
    keys = [p.key for p in players]
    if len(set(keys)) != len(keys):
        raise ValidationError("Hay jugadores repetidos: un jugador no puede estar en dos equipos.")
    needed = num_teams * players_per_team
    if len(players) < needed:
        raise NotEnoughPlayersError(needed - len(players), needed)


def partition_key(groups: Iterable[Iterable[Player]]) -> Partition:
    """Identifica un reparto sin importar el orden de los equipos ni de los jugadores."""
    return frozenset(frozenset(p.key for p in group) for group in groups)


def _vector(player: Player) -> list[float]:
    return [player.overall, *(float(getattr(player, a)) for a in ATTRIBUTES)]


def _cost(sums: list[list[float]], sizes: list[int]) -> float:
    total = 0.0
    for dim in range(len(sums[0])):
        means = [s[dim] / sizes[t] for t, s in enumerate(sums)]
        gap = max(means) - min(means)
        total += gap if dim == 0 else ATTRIBUTE_WEIGHT * gap
    return total


def _local_search(groups: list[list[Player]]) -> None:
    """Mejora el reparto in situ con intercambios y pases hasta que no haya mejora."""
    vectors = {id(p): _vector(p) for g in groups for p in g}
    dims = len(next(iter(vectors.values())))
    sums = [[sum(vectors[id(p)][d] for p in g) for d in range(dims)] for g in groups]
    sizes = [len(g) for g in groups]
    current = _cost(sums, sizes)

    def apply(t: int, vec: list[float], sign: int) -> None:
        for d in range(dims):
            sums[t][d] += sign * vec[d]

    improved = True
    while improved:
        improved = False
        for i in range(len(groups)):
            for j in range(len(groups)):
                if i == j:
                    continue
                # Intercambio de un jugador de i por uno de j (se prueba una vez por par).
                if i < j:
                    for a in range(len(groups[i])):
                        for b in range(len(groups[j])):
                            va, vb = vectors[id(groups[i][a])], vectors[id(groups[j][b])]
                            apply(i, va, -1); apply(i, vb, 1)
                            apply(j, vb, -1); apply(j, va, 1)
                            cost = _cost(sums, sizes)
                            if cost < current - _EPS:
                                groups[i][a], groups[j][b] = groups[j][b], groups[i][a]
                                current = cost
                                improved = True
                            else:
                                apply(i, vb, -1); apply(i, va, 1)
                                apply(j, va, -1); apply(j, vb, 1)
                # Pase de un jugador del equipo más largo al más corto (los tamaños siguen parejos).
                if sizes[i] == sizes[j] + 1:
                    for a in range(len(groups[i])):
                        va = vectors[id(groups[i][a])]
                        apply(i, va, -1); apply(j, va, 1)
                        sizes[i] -= 1; sizes[j] += 1
                        cost = _cost(sums, sizes)
                        if cost < current - _EPS:
                            groups[j].append(groups[i].pop(a))
                            current = cost
                            improved = True
                            break
                        apply(i, va, 1); apply(j, va, -1)
                        sizes[i] += 1; sizes[j] -= 1


def _snake_draft(players: list[Player], sizes: list[int]) -> list[list[Player]]:
    ordered = sorted(players, key=lambda p: (-p.overall, p.key))
    groups: list[list[Player]] = [[] for _ in sizes]
    order = list(range(len(sizes)))
    while ordered:
        for t in order:
            if ordered and len(groups[t]) < sizes[t]:
                groups[t].append(ordered.pop(0))
        order.reverse()
    return groups


def _groups_cost(groups: list[list[Player]]) -> float:
    sums = [[sum(v) for v in zip(*(_vector(p) for p in g))] for g in groups]
    return _cost(sums, [len(g) for g in groups])


def _neighbors(groups: list[list[Player]]) -> Iterable[list[list[Player]]]:
    """Repartos a un intercambio o un pase de distancia (manteniendo tamaños parejos)."""
    for i in range(len(groups)):
        for j in range(len(groups)):
            if i < j:
                for a in range(len(groups[i])):
                    for b in range(len(groups[j])):
                        new = [g[:] for g in groups]
                        new[i][a], new[j][b] = new[j][b], new[i][a]
                        yield new
            if i != j and len(groups[i]) == len(groups[j]) + 1:
                for a in range(len(groups[i])):
                    new = [g[:] for g in groups]
                    new[j].append(new[i].pop(a))
                    yield new


def spread_of(groups: list[list[Player]]) -> float:
    means = [sum(p.overall for p in g) / len(g) for g in groups]
    return max(means) - min(means)


def balance_teams(
    players: list[Player],
    num_teams: int,
    players_per_team: int,
    rng: random.Random | None = None,
    exclude: set[Partition] | frozenset[Partition] = frozenset(),
    restarts: int | None = None,
) -> list[list[Player]]:
    """Reparte a todos los jugadores en `num_teams` equipos con medias lo más parejas posible.

    Todos juegan: si sobran jugadores respecto del formato, quedan como suplentes
    repartidos de a uno. `exclude` son repartos ya armados que no se deben repetir.
    """
    check_players(players, num_teams, players_per_team)
    rng = rng or random.Random()
    sizes = team_sizes(len(players), num_teams)
    if restarts is None:
        restarts = max(MIN_RESTARTS, min(MAX_RESTARTS, 1200 // len(players)))

    best: list[list[Player]] | None = None
    best_cost = float("inf")
    explored: set[Partition] = set()
    for attempt in range(restarts):
        if attempt == 0:
            groups = _snake_draft(players, sizes)
        else:
            shuffled = players[:]
            rng.shuffle(shuffled)
            groups, start = [], 0
            for size in sizes:
                groups.append(shuffled[start:start + size])
                start += size
        _local_search(groups)
        key = partition_key(groups)
        if key in explored:
            continue
        explored.add(key)
        # Si el mejor reparto encontrado ya se armó antes, buscamos el mejor de al lado.
        candidates = _neighbors(groups) if key in exclude else [groups]
        for candidate in candidates:
            if partition_key(candidate) in exclude:
                continue
            cost = _groups_cost(candidate)
            if cost < best_cost - _EPS:
                best, best_cost = candidate, cost

    if best is None:
        raise NoNewCombinationError()
    # El equipo con mejor media primero, jugadores de mayor a menor media.
    for g in best:
        g.sort(key=lambda p: (-p.overall, p.key))
    best.sort(key=lambda g: -sum(p.overall for p in g) / len(g))
    return best


def default_team_names(count: int) -> list[str]:
    return [f"Equipo {i + 1}" for i in range(count)]


def build_teams(groups: list[list[Player]], names: list[str] | None = None) -> list[Team]:
    names = names or default_team_names(len(groups))
    return [Team(name, list(g)) for name, g in zip(names, groups)]


def move_player(teams: list[Team], player_key: str, target_index: int) -> None:
    """Pasa un jugador a otro equipo (modificación manual)."""
    source = find_team_index(teams, player_key)
    if not 0 <= target_index < len(teams):
        raise ValidationError("Ese equipo no existe.")
    if source == target_index:
        raise ValidationError("El jugador ya está en ese equipo.")
    if len(teams[source].players) == 1:
        raise ValidationError("No podés dejar un equipo sin jugadores.")
    player = next(p for p in teams[source].players if p.key == player_key)
    teams[source].players.remove(player)
    teams[target_index].players.append(player)


def swap_players(teams: list[Team], key_a: str, key_b: str) -> None:
    """Intercambia dos jugadores de equipos distintos (modificación manual)."""
    ta, tb = find_team_index(teams, key_a), find_team_index(teams, key_b)
    if ta == tb:
        raise ValidationError("Los dos jugadores están en el mismo equipo.")
    pa = next(p for p in teams[ta].players if p.key == key_a)
    pb = next(p for p in teams[tb].players if p.key == key_b)
    ia, ib = teams[ta].players.index(pa), teams[tb].players.index(pb)
    teams[ta].players[ia], teams[tb].players[ib] = pb, pa


def find_team_index(teams: list[Team], player_key: str) -> int:
    for i, team in enumerate(teams):
        if any(p.key == player_key for p in team.players):
            return i
    raise ValidationError("Ese jugador no está en ningún equipo.")
