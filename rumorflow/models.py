
import random
from dataclasses import dataclass


@dataclass(frozen=True)
class Post:
    """Represents a rumor or information post."""
    content: str
    source_id: int


class User:
    """Base class for all social network users."""

    VALID_STATES = {"unseen", "frontier", "exposed"}

    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name
        self._state = "unseen"

    @property
    def state(self) -> str:
        """Read-only access to the user's state."""
        return self._state

    def set_state(self, state: str) -> None:
        """Update state with validation."""
        if state not in self.VALID_STATES:
            raise ValueError(f"Invalid state: {state}")
        self._state = state

    def receive(self, post: Post) -> bool:
        """Return whether the user forwards the post."""
        return False

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(id={self.id}, name={self.name!r})"
        )


class RegularUser(User):
    """Shares information with a configurable probability."""

    def __init__(
        self,
        id: int,
        name: str,
        share_probability: float = 0.5,
        rng: random.Random | None = None,
    ):
        super().__init__(id, name)

        if not 0 <= share_probability <= 1:
            raise ValueError("Probability must be between 0 and 1")

        self.share_probability = share_probability
        self.rng = rng if rng is not None else random.Random()

    def receive(self, post: Post) -> bool:
        return self.rng.random() < self.share_probability


class Influencer(User):
    """Always forwards information."""

    def __init__(
        self,
        id: int,
        name: str,
        reach_multiplier: int = 2,
    ):
        super().__init__(id, name)

        if reach_multiplier < 1:
            raise ValueError("Reach multiplier must be >= 1")

        self.reach_multiplier = reach_multiplier

    def receive(self, post: Post) -> bool:
        return True


class Bot(User):
    """Automatically forwards every post without filtering."""

    def receive(self, post: Post) -> bool:
        return True
