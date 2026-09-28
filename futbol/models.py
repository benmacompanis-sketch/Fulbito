"""Modelos del dominio: jugadores, equipos y formatos de partido."""

from __future__ import annotations

from dataclasses import dataclass, field

# Orden fijo de los atributos. La interfaz los muestra con las etiquetas en español.
ATTRIBUTES = ("pace", "passing", "dribbling", "defending")
ATTRIBUTE_LABELS = {
    "pace": "Ritmo",
    "passing": "Pase",
    "dribbling": "Regate",
    "defending": "Defensa",
}
MIN_RATING = 1
MAX_RATING = 99

# Jugadores por equipo en cancha según el formato.
FORMATS = {"F5": 5, "F8": 8, "F11": 11}


class ValidationError(ValueError):
    """Dato cargado por el usuario que no cumple las reglas."""


def normalize_name(name: str) -> str:
    """Clave para comparar nombres sin importar mayúsculas ni espacios de más."""
    return " ".join(name.split()).casefold()


@dataclass(frozen=True)
class Player:
    name: str
    pace: int
    passing: int
    dribbling: int
    defending: int

    def __post_init__(self) -> None:
        clean = " ".join(str(self.name).split())
        if not clean:
            raise ValidationError("El jugador necesita un nombre.")
        object.__setattr__(self, "name", clean)
        for attr in ATTRIBUTES:
            value = getattr(self, attr)
            # bool es subclase de int: lo descartamos a propósito.
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValidationError(f"{ATTRIBUTE_LABELS[attr]} tiene que ser un número entero.")
            if not MIN_RATING <= value <= MAX_RATING:
                raise ValidationError(
                    f"{ATTRIBUTE_LABELS[attr]} tiene que estar entre {MIN_RATING} y {MAX_RATING}."
                )

    @property
    def key(self) -> str:
        return normalize_name(self.name)

    @property
    def overall(self) -> float:
        """Media del jugador: promedio simple de sus cuatro atributos."""
        return sum(getattr(self, attr) for attr in ATTRIBUTES) / len(ATTRIBUTES)

    def to_dict(self) -> dict:
        return {"name": self.name, **{attr: getattr(self, attr) for attr in ATTRIBUTES}}

    @classmethod
    def from_dict(cls, data: dict) -> "Player":
        return cls(name=data["name"], **{attr: data[attr] for attr in ATTRIBUTES})


@dataclass
class Team:
    name: str
    players: list[Player] = field(default_factory=list)

    def average(self, attr: str | None = None) -> float:
        """Media del equipo. Sin `attr`, la media general; con `attr`, la de ese atributo."""
        if not self.players:
            return 0.0
        if attr is None:
            return sum(p.overall for p in self.players) / len(self.players)
        return sum(getattr(p, attr) for p in self.players) / len(self.players)


def league_average(teams: list[Team]) -> float:
    """Promedio de las medias de los equipos."""
    if not teams:
        return 0.0
    return sum(t.average() for t in teams) / len(teams)


def average_gap(teams: list[Team], attr: str | None = None) -> float:
    """Diferencia entre el equipo de mayor media y el de menor media."""
    if not teams:
        return 0.0
    values = [t.average(attr) for t in teams]
    return max(values) - min(values)
