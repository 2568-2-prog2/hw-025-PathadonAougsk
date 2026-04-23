import random
from dataclasses import dataclass, field


@dataclass
class RollResult:
    results: list
    num_rolls: int
    counts: dict = field(default_factory=dict)
    frequencies: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "results": self.results,
            "num_rolls": self.num_rolls,
            "counts": self.counts,
            "frequencies": self.frequencies,
        }


FACES = [1, 2, 3, 4, 5, 6]
UNIFORM = [round(1 / 6, 10)] * 6


class Dice:
    def __init__(self, probabilities: list = None, num_rolls: int = 1):

        if probabilities is None:
            probabilities = UNIFORM[:]

        self.probabilities = self._validate_probabilities(probabilities)
        self.num_rolls = self._validate_num_rolls(num_rolls)

    @staticmethod
    def _validate_probabilities(probs) -> list:
        if not isinstance(probs, (list, tuple)) or len(probs) != 6:
            raise ValueError("probabilities must be a list of exactly 6 values.")
        probs = [float(p) for p in probs]
        if any(p < 0 for p in probs):
            raise ValueError("All probabilities must be non-negative.")
        if abs(sum(probs) - 1.0) > 1e-6:
            raise ValueError(f"Probabilities must sum to 1.0, got {sum(probs):.8f}.")
        return probs

    @staticmethod
    def _validate_num_rolls(n) -> int:
        n = int(n)
        if n < 1:
            raise ValueError("num_rolls must be at least 1.")
        return n

    def roll(self, num_rolls: int = None) -> RollResult:

        n = (
            self._validate_num_rolls(num_rolls)
            if num_rolls is not None
            else self.num_rolls
        )
        results = random.choices(FACES, weights=self.probabilities, k=n)

        counts = {face: results.count(face) for face in FACES}
        frequencies = {face: round(counts[face] / n, 4) for face in FACES}

        return RollResult(
            results=results,
            num_rolls=n,
            counts=counts,
            frequencies=frequencies,
        )

    def set_probabilities(self, probabilities: list):
        self.probabilities = self._validate_probabilities(probabilities)

    def set_num_rolls(self, num_rolls: int):
        self.num_rolls = self._validate_num_rolls(num_rolls)

    def __repr__(self):
        probs = [round(p, 4) for p in self.probabilities]
        return f"Dice(probabilities={probs}, num_rolls={self.num_rolls})"


if __name__ == "__main__":
    # Fair die, 10 rolls
    d = Dice(num_rolls=10)
    result = d.roll()
    print("Fair die — 10 rolls")
    print("Results   :", result.results)
    print("Counts    :", result.counts)
    print("Frequencies:", result.frequencies)
    print()

    # Biased die, 20 rolls
    biased = Dice(probabilities=[0.1, 0.2, 0.3, 0.1, 0.2, 0.1], num_rolls=20)
    result2 = biased.roll()
    print("Biased die — 20 rolls")
    print("Results   :", result2.results)
    print(result2.to_dict())
