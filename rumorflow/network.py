
"""Graph engine for the RumorFlow simulator."""

from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Set

from rumorflow.models import User, Post


@dataclass
class Step:
    """One recorded propagation step."""

    step_no: int
    newly_exposed: List[int]
    frontier: List[int]
    exposed_total: int


@dataclass
class PropagationResult:
    """Complete results of a rumor propagation run."""

    mode: str
    source_id: int
    steps: List[Step]
    traversal_order: List[int]
    exposed: Set[int]
    forwarding_users: Set[int]
    total_users: int

    @property
    def reach_percentage(self) -> float:
        if self.total_users == 0:
            return 0.0

        return len(self.exposed) / self.total_users * 100

    @property
    def total_steps(self) -> int:
        return len(self.steps)


class Network:
    """Social network represented using an adjacency list."""

    def __init__(self):
        # Private graph and user registry
        self.__adjacency: Dict[int, List[int]] = {}
        self.__users: Dict[int, User] = {}

    def add_user(self, user: User) -> None:
        """Add a user to the social network."""

        if user.id in self.__users:
            raise ValueError(
                f"User ID {user.id} already exists."
            )

        self.__users[user.id] = user
        self.__adjacency[user.id] = []

    def add_edge(self, user1: int, user2: int) -> None:
        """Create an undirected friendship between users."""

        if user1 not in self.__users:
            raise ValueError(f"User {user1} not found.")

        if user2 not in self.__users:
            raise ValueError(f"User {user2} not found.")

        if user1 == user2:
            raise ValueError("Self-loops are not allowed.")

        if user2 not in self.__adjacency[user1]:
            self.__adjacency[user1].append(user2)
            self.__adjacency[user2].append(user1)

    def neighbors(self, user_id: int) -> List[int]:
        """Return a copy of the user's neighbor list."""

        if user_id not in self.__users:
            raise ValueError(f"User {user_id} not found.")

        return self.__adjacency[user_id].copy()

    def get_user(self, user_id: int) -> User:
        """Return a user by ID."""

        if user_id not in self.__users:
            raise ValueError(f"User {user_id} not found.")

        return self.__users[user_id]

    def get_users(self) -> Dict[int, User]:
        """Return a copy of the user registry."""

        return self.__users.copy()

    def get_graph(self) -> Dict[int, List[int]]:
        """Return a copy of the adjacency list."""

        return {
            user_id: neighbors.copy()
            for user_id, neighbors
            in self.__adjacency.items()
        }

    def reset_states(self) -> None:
        """Reset all users before a new simulation."""

        for user in self.__users.values():
            user.set_state("unseen")

    def propagate(
        self,
        post: Post,
        source: int,
        mode: str = "bfs",
    ) -> PropagationResult:
        """
        Simulate information diffusion using BFS or DFS.

        BFS: Queue using collections.deque.
        DFS: Iterative stack using a Python list.

        A seen set ensures each user is exposed once.
        Each step records the complete frontier.
        """

        mode = mode.lower()

        if mode not in {"bfs", "dfs"}:
            raise ValueError(
                "Mode must be either 'bfs' or 'dfs'."
            )

        if source not in self.__users:
            raise ValueError(
                f"Invalid source user: {source}"
            )

        if post.source_id != source:
            raise ValueError(
                "Post source_id must match source."
            )

        self.reset_states()

        seen: Set[int] = {source}
        exposed: Set[int] = set()
        forwarding_users: Set[int] = set()

        traversal_order: List[int] = []
        steps: List[Step] = []

        self.__users[source].set_state("frontier")

        # BFS uses a queue; DFS uses a stack.
        if mode == "bfs":
            frontier = deque([source])
        else:
            frontier = [source]

        step_no = 0

        while frontier:

            # One BFS step processes a whole level.
            # One DFS step processes one stack item.
            batch_size = (
                len(frontier)
                if mode == "bfs"
                else 1
            )

            newly_exposed = []

            for _ in range(batch_size):

                if mode == "bfs":
                    current = frontier.popleft()
                else:
                    current = frontier.pop()

                user = self.__users[current]

                # Source starts the rumor.
                if current == source:
                    should_share = True
                else:
                    should_share = user.receive(post)

                user.set_state("exposed")

                exposed.add(current)
                traversal_order.append(current)
                newly_exposed.append(current)

                if should_share:
                    forwarding_users.add(current)

                    neighbors = self.__adjacency[current]

                    # Reverse push order for DFS so the
                    # first neighbor is explored first.
                    if mode == "dfs":
                        neighbors = list(reversed(neighbors))

                    for neighbor in neighbors:

                        if neighbor not in seen:
                            seen.add(neighbor)

                            self.__users[neighbor].set_state(
                                "frontier"
                            )

                            frontier.append(neighbor)

            step_no += 1

            steps.append(
                Step(
                    step_no=step_no,
                    newly_exposed=newly_exposed.copy(),
                    frontier=list(frontier),
                    exposed_total=len(exposed),
                )
            )

        return PropagationResult(
            mode=mode,
            source_id=source,
            steps=steps,
            traversal_order=traversal_order,
            exposed=exposed,
            forwarding_users=forwarding_users,
            total_users=len(self.__users),
        )
