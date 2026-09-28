import random
import unittest

from futbol import balance
from futbol.models import Player, Team, ValidationError, average_gap


def make_players(n: int, seed: int = 1) -> list[Player]:
    rng = random.Random(seed)
    return [
        Player(f"Jugador {i}", rng.randint(40, 95), rng.randint(40, 95), rng.randint(40, 95), rng.randint(40, 95))
        for i in range(n)
    ]


class PlayerTest(unittest.TestCase):
    def test_overall_is_mean_of_attributes(self):
        self.assertEqual(Player("Ana", 80, 70, 60, 50).overall, 65)

    def test_rejects_out_of_range_and_non_integers(self):
        with self.assertRaises(ValidationError):
            Player("Ana", 100, 70, 60, 50)
        with self.assertRaises(ValidationError):
            Player("Ana", 0, 70, 60, 50)
        with self.assertRaises(ValidationError):
            Player("Ana", 70.5, 70, 60, 50)
        with self.assertRaises(ValidationError):
            Player("   ", 70, 70, 60, 50)


class BalanceTest(unittest.TestCase):
    def test_every_player_in_exactly_one_team(self):
        players = make_players(16)
        groups = balance.balance_teams(players, 2, 8, random.Random(0))
        keys = [p.key for g in groups for p in g]
        self.assertEqual(sorted(keys), sorted(p.key for p in players))
        self.assertEqual([len(g) for g in groups], [8, 8])

    def test_teams_are_level(self):
        for seed in range(5):
            players = make_players(22, seed)
            groups = balance.balance_teams(players, 2, 11, random.Random(seed))
            self.assertLess(balance.spread_of(groups), 0.5)

    def test_beats_naive_split(self):
        # Ordenados de mejor a peor, partir por la mitad deja todo desparejo.
        players = sorted(make_players(10, 3), key=lambda p: -p.overall)
        naive = [players[:5], players[5:]]
        groups = balance.balance_teams(players, 2, 5, random.Random(0))
        self.assertLess(balance.spread_of(groups), balance.spread_of(naive))

    def test_more_than_two_teams_and_leftovers_as_substitutes(self):
        players = make_players(17)
        groups = balance.balance_teams(players, 3, 5, random.Random(0))
        self.assertEqual(sorted(len(g) for g in groups), [5, 6, 6])
        self.assertLess(balance.spread_of(groups), 1.5)

    def test_does_not_invent_players(self):
        with self.assertRaises(balance.NotEnoughPlayersError) as ctx:
            balance.balance_teams(make_players(9), 2, 5)
        self.assertEqual(ctx.exception.missing, 1)

    def test_rejects_duplicate_players(self):
        players = make_players(10)
        players[1] = Player(players[0].name.upper(), 50, 50, 50, 50)
        with self.assertRaises(ValidationError):
            balance.balance_teams(players, 2, 5)

    def test_other_combination_is_not_repeated(self):
        players = make_players(10)
        rng = random.Random(0)
        seen = set()
        for _ in range(5):
            groups = balance.balance_teams(players, 2, 5, rng, exclude=seen)
            key = balance.partition_key(groups)
            self.assertNotIn(key, seen)
            seen.add(key)

    def test_raises_when_no_new_combination_left(self):
        players = make_players(4)
        # 4 jugadores en 2 equipos de 2: sólo hay 3 repartos posibles.
        seen = set()
        rng = random.Random(0)
        for _ in range(3):
            seen.add(balance.partition_key(balance.balance_teams(players, 2, 2, rng, exclude=seen, restarts=200)))
        with self.assertRaises(balance.NoNewCombinationError):
            balance.balance_teams(players, 2, 2, rng, exclude=seen, restarts=200)

    def test_deterministic_with_same_seed(self):
        players = make_players(16)
        a = balance.balance_teams(players, 2, 8, random.Random(7))
        b = balance.balance_teams(players, 2, 8, random.Random(7))
        self.assertEqual(balance.partition_key(a), balance.partition_key(b))


class ManualEditTest(unittest.TestCase):
    def setUp(self):
        self.a, self.b, self.c, self.d = (Player(n, v, v, v, v) for n, v in [("A", 90), ("B", 60), ("C", 80), ("D", 70)])
        self.teams = [Team("Uno", [self.a, self.b]), Team("Dos", [self.c, self.d])]

    def test_swap_updates_averages(self):
        self.assertEqual(average_gap(self.teams), 0)
        balance.swap_players(self.teams, self.a.key, self.d.key)
        self.assertEqual([p.name for p in self.teams[0].players], ["D", "B"])
        self.assertEqual([p.name for p in self.teams[1].players], ["C", "A"])
        self.assertEqual(average_gap(self.teams), 20)

    def test_move(self):
        balance.move_player(self.teams, self.b.key, 1)
        self.assertEqual(len(self.teams[0].players), 1)
        self.assertEqual(len(self.teams[1].players), 3)

    def test_cannot_empty_a_team_or_swap_within_team(self):
        balance.move_player(self.teams, self.b.key, 1)
        with self.assertRaises(ValidationError):
            balance.move_player(self.teams, self.a.key, 1)
        with self.assertRaises(ValidationError):
            balance.swap_players(self.teams, self.c.key, self.d.key)


if __name__ == "__main__":
    unittest.main()
