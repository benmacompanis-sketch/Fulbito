"""Torneos todos contra todos: fixture, resultados y tabla de posiciones. Lógica pura."""

from __future__ import annotations

from dataclasses import dataclass

from .models import ValidationError

POINTS_WIN = 3
POINTS_DRAW = 1


@dataclass
class Match:
    round: int
    home: str
    away: str
    home_goals: int | None = None
    away_goals: int | None = None

    @property
    def played(self) -> bool:
        return self.home_goals is not None and self.away_goals is not None

    def to_dict(self) -> dict:
        return {
            "round": self.round,
            "home": self.home,
            "away": self.away,
            "home_goals": self.home_goals,
            "away_goals": self.away_goals,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Match":
        return cls(**data)


@dataclass
class StandingRow:
    team: str
    played: int = 0
    won: int = 0
    drawn: int = 0
    lost: int = 0
    goals_for: int = 0
    goals_against: int = 0

    @property
    def goal_diff(self) -> int:
        return self.goals_for - self.goals_against

    @property
    def points(self) -> int:
        return self.won * POINTS_WIN + self.drawn * POINTS_DRAW


def round_robin(team_names: list[str], double: bool = False) -> list[Match]:
    """Fixture por el método del círculo: cada par de equipos se cruza una sola vez
    (o dos, ida y vuelta, con `double`). Con cantidad impar, uno descansa por fecha."""
    if len(team_names) < 2:
        raise ValidationError("Un torneo necesita al menos 2 equipos.")
    if len(set(team_names)) != len(team_names):
        raise ValidationError("Hay equipos con el mismo nombre.")

    slots: list[str | None] = list(team_names)
    if len(slots) % 2:
        slots.append(None)  # fecha libre
    n = len(slots)
    matches: list[Match] = []
    for rnd in range(n - 1):
        for k in range(n // 2):
            home, away = slots[k], slots[n - 1 - k]
            if home is None or away is None:
                continue
            # Alternamos localía para que nadie sea siempre local.
            if rnd % 2 and k == 0:
                home, away = away, home
            matches.append(Match(rnd + 1, home, away))
        slots = [slots[0], slots[-1], *slots[1:-1]]

    if double:
        first_leg_rounds = n - 1
        matches += [Match(m.round + first_leg_rounds, m.away, m.home) for m in list(matches)]
    return matches


def record_result(match: Match, home_goals: int, away_goals: int) -> None:
    for goals in (home_goals, away_goals):
        if isinstance(goals, bool) or not isinstance(goals, int) or goals < 0:
            raise ValidationError("Los goles tienen que ser un entero mayor o igual a 0.")
    match.home_goals = home_goals
    match.away_goals = away_goals


def standings(team_names: list[str], matches: list[Match]) -> list[StandingRow]:
    """Tabla ordenada por puntos, diferencia de gol, goles a favor y nombre."""
    rows = {name: StandingRow(name) for name in team_names}
    for m in matches:
        if not m.played:
            continue
        home, away = rows[m.home], rows[m.away]
        home.played += 1
        away.played += 1
        home.goals_for += m.home_goals
        home.goals_against += m.away_goals
        away.goals_for += m.away_goals
        away.goals_against += m.home_goals
        if m.home_goals > m.away_goals:
            home.won += 1
            away.lost += 1
        elif m.home_goals < m.away_goals:
            away.won += 1
            home.lost += 1
        else:
            home.drawn += 1
            away.drawn += 1
    return sorted(
        rows.values(),
        key=lambda r: (-r.points, -r.goal_diff, -r.goals_for, r.team.casefold()),
    )
