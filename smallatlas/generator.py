from dataclasses import asdict, dataclass
import random

from smallatlas.catalog import EVENTS, LAWS, MOOD_PROMPTS, PLACES, RESIDENTS

MOODS = tuple(MOOD_PROMPTS)


@dataclass(frozen=True)
class World:
    seed: int
    mood: str
    place: str
    law: str
    resident: str
    event: str
    writing_prompt: str

    def to_dict(self) -> dict[str, int | str]:
        return asdict(self)


def generate_world(seed: int, mood: str = "puitis") -> World:
    if mood not in MOOD_PROMPTS:
        choices = ", ".join(MOODS)
        raise ValueError(f"Nuansa tidak dikenal: {mood}. Pilihan: {choices}")

    rng = random.Random(seed)
    return World(
        seed=seed,
        mood=mood,
        place=rng.choice(PLACES),
        law=rng.choice(LAWS),
        resident=rng.choice(RESIDENTS),
        event=rng.choice(EVENTS),
        writing_prompt=MOOD_PROMPTS[mood],
    )
