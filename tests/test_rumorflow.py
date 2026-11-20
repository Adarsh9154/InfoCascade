
"""Automated tests for RumorFlow."""

import random

import pytest

from rumorflow.models import (
    Post,
    User,
    RegularUser,
    Influencer,
    Bot,
)
from rumorflow.network import Network


def create_network():
    network = Network()

    for i in range(1, 6):
        network.add_user(Influencer(i, f"User {i}"))

    for u, v in [(1, 2), (1, 3), (2, 4), (3, 5)]:
        network.add_edge(u, v)

    return network


def test_bfs_levels():
    network = create_network()

    result = network.propagate(
        Post("News", 1), 1, "bfs"
    )

    assert result.steps[0].newly_exposed == [1]
    assert result.steps[1].newly_exposed == [2, 3]
    assert result.steps[2].newly_exposed == [4, 5]


def test_dfs_no_revisits():
    network = create_network()

    result = network.propagate(
        Post("News", 1), 1, "dfs"
    )

    assert len(result.traversal_order) == 5
    assert len(set(result.traversal_order)) == 5


def test_cycle_safety():
    network = create_network()

    network.add_edge(4, 5)
    network.add_edge(5, 1)

    result = network.propagate(
        Post("News", 1), 1
    )

    assert len(result.exposed) == 5


def test_disconnected_graph():
    network = Network()

    network.add_user(Influencer(1, "Alice"))
    network.add_user(Influencer(2, "Bob"))

    result = network.propagate(
        Post("News", 1), 1
    )

    assert result.exposed == {1}
    assert result.reach_percentage == 50.0


def test_polymorphism():
    post = Post("News", 1)

    regular = RegularUser(
        1, "Regular",
        share_probability=0.0,
        rng=random.Random(42),
    )

    influencer = Influencer(2, "Influencer")
    bot = Bot(3, "Bot")

    assert regular.receive(post) is False
    assert influencer.receive(post) is True
    assert bot.receive(post) is True


def test_invalid_source():
    network = create_network()

    with pytest.raises(ValueError):
        network.propagate(Post("News", 99), 99)


def test_non_forwarding_user():
    network = Network()

    network.add_user(Influencer(1, "Source"))
    network.add_user(
        RegularUser(2, "Non-sharer", 0.0)
    )
    network.add_user(Influencer(3, "Target"))

    network.add_edge(1, 2)
    network.add_edge(2, 3)

    result = network.propagate(
        Post("News", 1), 1
    )

    assert result.exposed == {1, 2}
    assert 3 not in result.exposed


def test_empty_network():
    network = Network()

    with pytest.raises(ValueError):
        network.propagate(Post("News", 1), 1)


def test_duplicate_user():
    network = Network()
    network.add_user(User(1, "Alice"))

    with pytest.raises(ValueError):
        network.add_user(User(1, "Duplicate"))


def test_bfs_dfs_reach():
    network = create_network()
    post = Post("News", 1)

    bfs = network.propagate(post, 1, "bfs")
    dfs = network.propagate(post, 1, "dfs")

    assert bfs.exposed == dfs.exposed
    assert bfs.total_steps == 3
    assert dfs.total_steps == 5
