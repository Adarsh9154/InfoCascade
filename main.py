
"""Test the RumorFlow graph engine."""

from rumorflow.models import (
    Post,
    RegularUser,
    Influencer,
    Bot,
)

from rumorflow.network import Network


def build_demo_network() -> Network:
    network = Network()

    # Create six users
    network.add_user(Influencer(1, "Alice"))
    network.add_user(RegularUser(
        2, "Bob", share_probability=1.0
    ))
    network.add_user(Bot(3, "Charlie"))
    network.add_user(RegularUser(
        4, "David", share_probability=1.0
    ))
    network.add_user(Influencer(5, "Emma"))
    network.add_user(RegularUser(
        6, "Frank", share_probability=1.0
    ))

    # Add friendships
    edges = [
        (1, 2),
        (1, 3),
        (2, 4),
        (2, 5),
        (3, 6),
        (4, 5),
        (5, 6),
    ]

    for u, v in edges:
        network.add_edge(u, v)

    return network


def print_result(result):
    print(f"\nAlgorithm: {result.mode.upper()}")
    print("-" * 65)

    print(
        f"{'Step':<8}"
        f"{'Newly Exposed':<22}"
        f"{'Frontier':<22}"
        f"{'Total':<8}"
    )

    print("-" * 65)

    for step in result.steps:
        print(
            f"{step.step_no:<8}"
            f"{str(step.newly_exposed):<22}"
            f"{str(step.frontier):<22}"
            f"{step.exposed_total:<8}"
        )

    print("-" * 65)

    print("Traversal:", result.traversal_order)
    print("Reach:", f"{result.reach_percentage:.1f}%")
    print("Total Steps:", result.total_steps)



if __name__ == "__main__":

    from rumorflow.visualization import generate_all_visuals

    network = build_demo_network()

    post = Post(
        content="Breaking News: RumorFlow launched!",
        source_id=1,
    )

    bfs_result = network.propagate(
        post, source=1, mode="bfs"
    )

    print_result(bfs_result)

    dfs_result = network.propagate(
        post, source=1, mode="dfs"
    )

    print_result(dfs_result)

    # Visualize BFS propagation
    generate_all_visuals(network, bfs_result)
