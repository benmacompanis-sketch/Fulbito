"""Estado de la aplicación y su guardado en un archivo JSON."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

from .models import Player, Team, ValidationError
from .tournament import Match


@dataclass
class AppState:
    players: list[Player] = field(default_factory=list)
    game_format: str | None = None
    team_names: list[str] = field(default_factory=list)
    # Plantel de cada equipo guardado por clave de jugador, así editar atributos
    # actualiza las medias sin rearmar nada.
    rosters: list[list[str]] = field(default_factory=list)
    matches: list[Match] = field(default_factory=list)
    # Repartos ya armados, para no repetir equipos al pedir otra combinación.
    history: list[list[list[str]]] = field(default_factory=list)

    def player_by_key(self, key: str) -> Player:
        for p in self.players:
            if p.key == key:
                return p
        raise ValidationError("Ese jugador no existe.")

    def add_player(self, player: Player) -> None:
        if any(p.key == player.key for p in self.players):
            raise ValidationError(f"Ya hay un jugador llamado {player.name}.")
        self.players.append(player)

    def replace_player(self, player: Player) -> None:
        for i, p in enumerate(self.players):
            if p.key == player.key:
                self.players[i] = player
                return
        raise ValidationError("Ese jugador no existe.")

    def remove_player(self, key: str) -> None:
        if any(key in roster for roster in self.rosters):
            raise ValidationError("Ese jugador está en un equipo: sacalo del equipo primero o borrá los equipos.")
        self.players = [p for p in self.players if p.key != key]

    def teams(self) -> list[Team]:
        return [
            Team(name, [self.player_by_key(k) for k in roster])
            for name, roster in zip(self.team_names, self.rosters)
        ]

    def set_teams(self, teams: list[Team]) -> None:
        self.team_names = [t.name for t in teams]
        self.rosters = [[p.key for p in t.players] for t in teams]

    def clear_teams(self) -> None:
        self.team_names, self.rosters, self.matches = [], [], []
        self.game_format = None

    def to_dict(self) -> dict:
        return {
            "players": [p.to_dict() for p in self.players],
            "format": self.game_format,
            "team_names": self.team_names,
            "rosters": self.rosters,
            "matches": [m.to_dict() for m in self.matches],
            "history": self.history,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AppState":
        return cls(
            players=[Player.from_dict(p) for p in data.get("players", [])],
            game_format=data.get("format"),
            team_names=data.get("team_names", []),
            rosters=data.get("rosters", []),
            matches=[Match.from_dict(m) for m in data.get("matches", [])],
            history=data.get("history", []),
        )


def load_state(path: Path) -> AppState:
    if not path.exists():
        return AppState()
    with path.open(encoding="utf-8") as f:
        return AppState.from_dict(json.load(f))


def save_state(state: AppState, path: Path) -> None:
    # Se escribe a un temporal y se renombra, para no dejar el archivo por la mitad.
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(state.to_dict(), f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)
