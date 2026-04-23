import unittest

from dice_model import FACES, Dice, RollResult

PROBS = [0.1, 0.2, 0.3, 0.1, 0.2, 0.1]


class TestDice(unittest.TestCase):
    def test_default_initialization(self):
        d = Dice()
        self.assertEqual(d.num_rolls, 1)
        self.assertEqual(len(d.probabilities), 6)
        self.assertAlmostEqual(sum(d.probabilities), 1.0)

    def test_custom_initialization(self):
        d = Dice(probabilities=PROBS, num_rolls=10)
        self.assertEqual(d.probabilities, PROBS)
        self.assertEqual(d.num_rolls, 10)

    def test_invalid_probabilities(self):
        with self.assertRaises((ValueError, TypeError)):
            Dice(probabilities=[0.5, 0.5])

    def test_invalid_num_rolls(self):
        with self.assertRaises(ValueError):
            Dice(num_rolls=0)

    def test_roll_returns_result(self):
        r = Dice(num_rolls=20).roll()
        self.assertIsInstance(r, RollResult)

    def test_roll_length(self):
        r = Dice(num_rolls=20).roll()
        self.assertEqual(len(r.results), 20)

    def test_faces_are_valid(self):
        r = Dice(num_rolls=50).roll()
        for f in r.results:
            self.assertIn(f, FACES)

    def test_counts_and_frequencies(self):
        r = Dice(num_rolls=100).roll()
        self.assertEqual(sum(r.counts.values()), 100)
        self.assertAlmostEqual(sum(r.frequencies.values()), 1.0, places=3)

    def test_setters(self):
        d = Dice()
        d.set_num_rolls(30)
        self.assertEqual(d.num_rolls, 30)
        d.set_probabilities([0.1, 0.1, 0.2, 0.2, 0.2, 0.2])
        self.assertEqual(d.probabilities, [0.1, 0.1, 0.2, 0.2, 0.2, 0.2])

    def test_weight_excced_one(self):
        d = Dice()
        d.set_num_rolls(10)
        with self.assertRaises(ValueError):
            d.set_probabilities([1, 1, 1, 1, 1, 1])


if __name__ == "__main__":
    unittest.main(verbosity=2)
