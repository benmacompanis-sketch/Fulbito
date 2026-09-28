"""Menú de consola. Todo lo que ve el usuario está acá, en español."""

from __future__ import annotations

import random
from pathlib import Path
from typing import Callable

from . import balance
from .models import (
    ATTRIBUTE_LABELS,
    ATTRIBUTES,
    FORMATS,
    MAX_RATING,
    MIN_RATING,
    Player,
    Team,
    ValidationError,
    average_gap,
    league_average,
    normalize_name,
)
from .storage import AppState, save_state
from .tournament import record_result, round_robin, standings

SHORT_LABELS = {"pace": "RIT", "passing": "PAS", "dribbling": "REG", "defending": "DEF"}


class Cancelled(Exception):
    """El usuario dejó un dato vacío para volver al menú."""


def parse_selection(text: str, count: int) -> list[int]:
    """Convierte "1,3,5-8" en índices base 0. "todos" selecciona a todos."""
    text = text.strip().casefold()
    if text in ("todos", "t", "*"):
        return list(range(count))
    chosen: list[int] = []
    for part in text.replace(" ", "").split(","):
        if not part:
            continue
        if "-" in part:
            start_s, end_s = part.split("-", 1)
            start, end = int(start_s), int(end_s)
            if start > end:
                start, end = end, start
            numbers = range(start, end + 1)
        else:
            numbers = [int(part)]
        for n in numbers:
            if not 1 <= n <= count:
                raise ValidationError(f"No hay jugador número {n}.")
            if n - 1 not in chosen:
                chosen.append(n - 1)
    return chosen


class App:
    def __init__(
        self,
        state: AppState,
        path: Path | None,
        input_fn: Callable[[str], str] = input,
        output_fn: Callable[[str], None] = print,
        rng: random.Random | None = None,
    ):
        self.state = state
        self.path = path
        self.input = input_fn
        self.out = output_fn
        self.rng = rng or random.Random()

    # ---------- utilidades de entrada ----------

    def ask(self, prompt: str, allow_empty: bool = False) -> str:
        answer = self.input(prompt).strip()
        if not answer and not allow_empty:
            raise Cancelled()
        return answer

    def ask_int(self, prompt: str, low: int, high: int, default: int | None = None) -> int:
        while True:
            answer = self.input(prompt).strip()
            if not answer:
                if default is not None:
                    return default
                raise Cancelled()
            try:
                value = int(answer)
            except ValueError:
                self.out("  Poné un número entero.")
                continue
            if low <= value <= high:
                return value
            self.out(f"  Tiene que estar entre {low} y {high}.")

    def ask_yes_no(self, prompt: str, default: bool) -> bool:
        hint = "S/n" if default else "s/N"
        answer = self.input(f"{prompt} ({hint}): ").strip().casefold()
        if not answer:
            return default
        return answer in ("s", "si", "sí", "y")

    def ask_player(self, prompt: str) -> Player:
        self.show_players()
        number = self.ask_int(prompt, 1, len(self.state.players))
        return self.state.players[number - 1]

    def save(self) -> None:
        if self.path is not None:
            save_state(self.state, self.path)

    # ---------- jugadores ----------

    def show_players(self) -> None:
        if not self.state.players:
            self.out("Todavía no cargaste jugadores.")
            return
        header = "     " + f"{'Jugador':<22}" + " ".join(f"{SHORT_LABELS[a]:>4}" for a in ATTRIBUTES) + "  MEDIA"
        self.out(header)
        for i, p in enumerate(self.state.players, 1):
            attrs = " ".join(f"{getattr(p, a):>4}" for a in ATTRIBUTES)
            self.out(f"{i:>3}. {p.name:<22}{attrs}  {p.overall:5.1f}")

    def ask_attributes(self, current: Player | None = None) -> dict[str, int]:
        values = {}
        for attr in ATTRIBUTES:
            default = getattr(current, attr) if current else None
            suffix = f" [{default}]" if default is not None else ""
            values[attr] = self.ask_int(
                f"  {ATTRIBUTE_LABELS[attr]} ({MIN_RATING}-{MAX_RATING}){suffix}: ",
                MIN_RATING,
                MAX_RATING,
                default,
            )
        return values

    def add_player(self) -> None:
        self.out("Cargá el jugador (Enter vacío para volver).")
        name = self.ask("  Nombre: ")
        if any(p.key == normalize_name(name) for p in self.state.players):
            self.out(f"Ya hay un jugador llamado {name}.")
            return
        player = Player(name=name, **self.ask_attributes())
        self.state.add_player(player)
        self.save()
        self.out(f"Listo: {player.name}, media {player.overall:.1f}.")

    def edit_player(self) -> None:
        if not self.state.players:
            self.out("Todavía no cargaste jugadores.")
            return
        current = self.ask_player("Número del jugador a editar: ")
        self.out(f"Editando a {current.name} (Enter deja el valor actual).")
        updated = Player(name=current.name, **self.ask_attributes(current))
        self.state.replace_player(updated)
        self.save()
        self.out(f"Listo: {updated.name}, media {updated.overall:.1f}.")

    def remove_player(self) -> None:
        if not self.state.players:
            self.out("Todavía no cargaste jugadores.")
            return
        player = self.ask_player("Número del jugador a borrar: ")
        if not self.ask_yes_no(f"¿Borrar a {player.name}?", False):
            return
        self.state.remove_player(player.key)
        self.save()
        self.out(f"{player.name} borrado.")

    # ---------- equipos ----------

    def show_teams(self, teams: list[Team] | None = None, fmt: str | None = None) -> None:
        teams = teams if teams is not None else self.state.teams()
        fmt = fmt or self.state.game_format
        if not teams:
            self.out("Todavía no armaste equipos.")
            return
        number = 1
        for team in teams:
            attrs = " · ".join(f"{ATTRIBUTE_LABELS[a]} {team.average(a):.1f}" for a in ATTRIBUTES)
            self.out(f"\n{team.name} — media {team.average():.1f}  ({attrs})")
            for p in team.players:
                self.out(f"  {number:>3}. {p.name:<22} media {p.overall:5.1f}")
                number += 1
        self.out(f"\nPromedio de las medias de los equipos: {league_average(teams):.1f}")
        self.out(f"Diferencia entre el más fuerte y el más débil: {average_gap(teams):.2f}")
        self.warn_short_teams(teams, fmt)

    def warn_short_teams(self, teams: list[Team], fmt: str | None) -> None:
        if fmt not in FORMATS:
            return
        for team in teams:
            if len(team.players) < FORMATS[fmt]:
                self.out(f"Ojo: {team.name} tiene {len(team.players)} jugadores y {fmt} pide {FORMATS[fmt]}.")

    def ask_format(self) -> str:
        options = " / ".join(FORMATS)
        while True:
            answer = self.ask(f"Formato ({options}): ").upper().replace(" ", "")
            if not answer.startswith("F"):
                answer = "F" + answer
            if answer in FORMATS:
                return answer
            self.out(f"  Elegí uno de: {options}.")

    def generate_teams(self, min_teams: int = 2) -> tuple[list[Team], str] | None:
        """Pide formato, cantidad de equipos y jugadores; devuelve los equipos parejos
        que el usuario aceptó y el formato, o None si canceló."""
        if len(self.state.players) < 2:
            self.out("Necesitás cargar jugadores primero.")
            return None
        fmt = self.ask_format()
        per_team = FORMATS[fmt]
        max_teams = max(min_teams, len(self.state.players) // per_team)
        num_teams = self.ask_int(
            f"¿Cuántos equipos? ({min_teams}-{max_teams}) [{min_teams}]: ", min_teams, max_teams, min_teams
        )

        self.show_players()
        while True:
            try:
                selection = parse_selection(
                    self.ask("¿Quiénes juegan? (ej: 1,2,5-9 o 'todos'): "), len(self.state.players)
                )
                break
            except ValueError as err:
                self.out(f"  {err}" if isinstance(err, ValidationError) else "  No entendí la lista.")
        players = [self.state.players[i] for i in selection]

        exclude: set = set()
        if self.state.history and self.ask_yes_no("¿Evitar repetir equipos que ya se armaron antes?", True):
            exclude = {frozenset(frozenset(g) for g in past) for past in self.state.history}

        try:
            while True:
                groups = balance.balance_teams(players, num_teams, per_team, self.rng, exclude)
                teams = balance.build_teams(groups)
                self.show_teams(teams, fmt)
                extra = len(players) - num_teams * per_team
                if extra:
                    self.out(f"Sobran {extra} jugador(es) para {fmt}: quedan como suplentes repartidos.")
                answer = self.ask("\n[a]ceptar · [o]tra combinación · [c]ancelar: ", allow_empty=True).casefold()
                if answer.startswith("a"):
                    return teams, fmt
                if answer.startswith("o"):
                    exclude.add(balance.partition_key(groups))
                    continue
                return None
        except ValidationError as err:
            self.out(str(err))
            return None

    def accept_teams(self, teams: list[Team], fmt: str) -> None:
        names = [t.name for t in teams]
        if self.ask_yes_no("¿Querés ponerles nombre a los equipos?", False):
            names = []
            for t in teams:
                while True:
                    name = self.ask(f"  Nombre para {t.name} [{t.name}]: ", allow_empty=True) or t.name
                    if normalize_name(name) in {normalize_name(n) for n in names}:
                        self.out("  Ya hay un equipo con ese nombre.")
                        continue
                    names.append(name)
                    break
            for t, name in zip(teams, names):
                t.name = name
        self.state.set_teams(teams)
        self.state.game_format = fmt
        self.state.matches = []
        self.state.history.append([sorted(roster) for roster in self.state.rosters])
        self.save()
        self.out("Equipos guardados.")

    def build_teams_menu(self) -> None:
        if self.state.matches and not self.ask_yes_no(
            "Hay un torneo armado; armar equipos nuevos lo borra. ¿Seguir?", False
        ):
            return
        result = self.generate_teams()
        if result is not None:
            self.accept_teams(*result)

    def modify_teams(self) -> None:
        teams = self.state.teams()
        if not teams:
            self.out("Todavía no armaste equipos.")
            return
        while True:
            self.show_teams(teams)
            answer = self.ask(
                "\n[m]over jugador · [i]ntercambiar dos · [r]enombrar equipo · [v]olver: ", allow_empty=True
            ).casefold()
            flat = [p for t in teams for p in t.players]
            try:
                if answer.startswith("m"):
                    player = flat[self.ask_int("Número del jugador: ", 1, len(flat)) - 1]
                    for i, t in enumerate(teams, 1):
                        self.out(f"  {i}. {t.name}")
                    target = self.ask_int("¿A qué equipo? ", 1, len(teams)) - 1
                    balance.move_player(teams, player.key, target)
                elif answer.startswith("i"):
                    a = flat[self.ask_int("Número del primer jugador: ", 1, len(flat)) - 1]
                    b = flat[self.ask_int("Número del segundo jugador: ", 1, len(flat)) - 1]
                    balance.swap_players(teams, a.key, b.key)
                elif answer.startswith("r"):
                    for i, t in enumerate(teams, 1):
                        self.out(f"  {i}. {t.name}")
                    index = self.ask_int("¿Qué equipo? ", 1, len(teams)) - 1
                    new_name = self.ask("Nombre nuevo: ")
                    if any(normalize_name(t.name) == normalize_name(new_name) for j, t in enumerate(teams) if j != index):
                        raise ValidationError("Ya hay un equipo con ese nombre.")
                    old_name = teams[index].name
                    teams[index].name = new_name
                    for m in self.state.matches:
                        if m.home == old_name:
                            m.home = new_name
                        if m.away == old_name:
                            m.away = new_name
                else:
                    return
            except ValidationError as err:
                self.out(str(err))
                continue
            except Cancelled:
                continue
            self.state.set_teams(teams)
            self.save()

    # ---------- torneo ----------

    def build_tournament(self) -> None:
        if self.state.matches and not self.ask_yes_no("Ya hay un torneo; armar otro borra sus resultados. ¿Seguir?", False):
            return
        teams = self.state.teams()
        if not (len(teams) >= 2 and self.ask_yes_no(f"¿Usar los {len(teams)} equipos actuales?", True)):
            self.out("Armemos equipos parejos para el torneo.")
            result = self.generate_teams()
            if result is None:
                return
            self.accept_teams(*result)
            teams = self.state.teams()
        double = self.ask_yes_no("¿Ida y vuelta?", False)
        self.state.matches = round_robin([t.name for t in teams], double)
        self.save()
        self.out(f"Torneo armado: {len(self.state.matches)} partidos. Todos contra todos, sin cruces repetidos.")
        self.show_fixture()

    def show_fixture(self) -> None:
        if not self.state.matches:
            self.out("Todavía no armaste un torneo.")
            return
        numbered = list(enumerate(self.state.matches, 1))
        for rnd in sorted({m.round for m in self.state.matches}):
            self.out(f"\nFecha {rnd}")
            in_round = [(i, m) for i, m in numbered if m.round == rnd]
            for i, m in in_round:
                result = f"{m.home_goals} - {m.away_goals}" if m.played else "sin jugar"
                self.out(f"  {i:>3}. {m.home} vs {m.away}: {result}")
            playing = {t for _, m in in_round for t in (m.home, m.away)}
            free = [t for t in self.state.team_names if t not in playing]
            if free:
                self.out(f"       Libre: {', '.join(free)}")

    def results_menu(self) -> None:
        while True:
            self.show_fixture()
            if not self.state.matches:
                return
            try:
                number = self.ask_int("\nNúmero de partido para cargar el resultado (Enter para volver): ", 1, len(self.state.matches))
            except Cancelled:
                return
            match = self.state.matches[number - 1]
            text = self.ask(f"Resultado {match.home} vs {match.away} (ej: 3-1): ", allow_empty=True)
            try:
                home_s, away_s = text.replace(" ", "").split("-")
                record_result(match, int(home_s), int(away_s))
            except ValueError as err:
                self.out(str(err) if isinstance(err, ValidationError) else "Escribilo así: 3-1.")
                continue
            self.save()

    def show_standings(self) -> None:
        if not self.state.matches:
            self.out("Todavía no armaste un torneo.")
            return
        rows = standings(self.state.team_names, self.state.matches)
        self.out(f"\n{'#':>2}  {'Equipo':<20}{'PJ':>4}{'G':>4}{'E':>4}{'P':>4}{'GF':>4}{'GC':>4}{'DG':>5}{'PTS':>5}")
        for pos, r in enumerate(rows, 1):
            self.out(
                f"{pos:>2}  {r.team:<20}{r.played:>4}{r.won:>4}{r.drawn:>4}{r.lost:>4}"
                f"{r.goals_for:>4}{r.goals_against:>4}{r.goal_diff:>+5}{r.points:>5}"
            )

    # ---------- menú principal ----------

    def run(self) -> None:
        actions = {
            "1": ("Ver jugadores", self.show_players),
            "2": ("Cargar jugador", self.add_player),
            "3": ("Editar atributos de un jugador", self.edit_player),
            "4": ("Borrar jugador", self.remove_player),
            "5": ("Armar equipos parejos", self.build_teams_menu),
            "6": ("Ver equipos y medias", self.show_teams),
            "7": ("Modificar equipos a mano", self.modify_teams),
            "8": ("Armar torneo", self.build_tournament),
            "9": ("Fixture y resultados", self.results_menu),
            "10": ("Tabla de posiciones", self.show_standings),
        }
        while True:
            self.out("\n=== Organizador de fútbol ===")
            for key, (label, _) in actions.items():
                self.out(f"{key:>3}. {label}")
            self.out("  0. Salir")
            try:
                choice = self.input("> ").strip()
            except EOFError:
                return
            if choice == "0":
                return
            if not choice:
                continue
            if choice not in actions:
                self.out("Opción inválida.")
                continue
            try:
                actions[choice][1]()
            except Cancelled:
                self.out("Cancelado.")
            except ValidationError as err:
                self.out(str(err))
            except EOFError:
                return
