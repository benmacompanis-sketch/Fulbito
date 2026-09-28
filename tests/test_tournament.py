import itertools
import unittest

from futbol.models import ValidationError
from futbol.tournament import record_result, round_robin, standings


class RoundRobinTest(unittest.TestCase):
    def check_each_pair_once(self, n: int):
        names = [f"E{i}" for i in range(n)]
        matches = round_robin(names)
        pairs = [frozenset((m.home, m.away)) for m in matches]
        self.assertEqual(len(pairs), len(set(pairs)))
        self.assertEqual(set(pairs), {frozenset(p) for p in itertools.combinations(names, 2)})
        # Nadie juega dos veces en la misma fecha.
        for rnd in {m.round for m in matches}:
            teams = [t for m in matches if m.round == rnd for t in (m.home, m.away)]
            self.assertEqual(len(teams), len(set(teams)))

    def test_even_and_odd(self):
        for n in range(2, 9):
            self.check_each_pair_once(n)

    def test_double_round(self):
        matches = round_robin(["A", "B", "C", "D"], double=True)
        self.assertEqual(len(matches), 12)
        legs = [(m.home, m.away) for m in matches]
        self.assertEqual(len(legs), len(set(legs)))

    def test_rejects_repeated_teams(self):
        with self.assertRaises(ValidationError):
            round_robin(["A", "A", "B"])


class StandingsTest(unittest.TestCase):
    def test_table(self):
        matches = round_robin(["A", "B", "C"])
        results = {frozenset(("A", "B")): {"A": 2, "B": 0}, frozenset(("A", "C")): {"A": 1, "C": 1},
                   frozenset(("B", "C")): {"B": 3, "C": 1}}
        for m in matches:
            r = results[frozenset((m.home, m.away))]
            record_result(m, r[m.home], r[m.away])
        table = standings(["A", "B", "C"], matches)
        self.assertEqual([(r.team, r.points, r.goal_diff) for r in table], [("A", 4, 2), ("B", 3, 0), ("C", 1, -2)])

    def test_unplayed_matches_do_not_count(self):
        table = standings(["A", "B"], round_robin(["A", "B"]))
        self.assertTrue(all(r.played == 0 for r in table))

    def test_rejects_negative_goals(self):
        with self.assertRaises(ValidationError):
            record_result(round_robin(["A", "B"])[0], -1, 0)


if __name__ == "__main__":
    unittest.main()
