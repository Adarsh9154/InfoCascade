
"""RumorFlow: reproducible network diffusion experiments."""

from pathlib import Path
import random

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd

from rumorflow.models import Bot, Influencer, Post, RegularUser
from rumorflow.network import Network


SEED = 42
TRIALS = 100
N_USERS = 20
OUTPUT_DIR = Path("outputs")

TEAL = "#28D7C0"
CORAL = "#FF6F61"
AMBER = "#FFCA5F"
BACKGROUND = "#101820"

TOPOLOGIES = ["Random", "Small-world", "Scale-free"]
SOURCE_TYPES = ["Regular", "Influencer", "Bot"]
SOURCE_POSITIONS = ["High-degree", "Low-degree"]
ALGORITHMS = ["bfs", "dfs"]


def generate_graph(topology: str, seed: int) -> nx.Graph:
    """Generate a reproducible 20-user network."""

    if topology == "Random":
        graph = nx.erdos_renyi_graph(
            N_USERS, p=0.18, seed=seed
        )

    elif topology == "Small-world":
        graph = nx.watts_strogatz_graph(
            N_USERS, k=4, p=0.2, seed=seed
        )

    elif topology == "Scale-free":
        graph = nx.barabasi_albert_graph(
            N_USERS, m=2, seed=seed
        )

    else:
        raise ValueError("Unknown topology")

    return graph


def choose_source(graph, position):
    """Choose a high-degree or low-degree source."""

    degrees = dict(graph.degree())

    if position == "High-degree":
        return max(
            degrees,
            key=lambda node: (degrees[node], -node)
        )

    if position == "Low-degree":
        return min(
            degrees,
            key=lambda node: (degrees[node], node)
        )

    raise ValueError("Unknown source position")


def create_network(graph, source_id, source_type, seed):
    """Convert a NetworkX graph to RumorFlow classes."""

    network = Network()

    for node in sorted(graph.nodes()):

        if node == source_id and source_type == "Influencer":
            user = Influencer(
                node, f"User {node}", reach_multiplier=2
            )

        elif node == source_id and source_type == "Bot":
            user = Bot(node, f"User {node}")

        else:
            user = RegularUser(
                node,
                f"User {node}",
                share_probability=0.5,
                rng=random.Random(seed * 1000 + node),
            )

        network.add_user(user)

    for u, v in sorted(graph.edges()):
        network.add_edge(u, v)

    return network


def add_influencer_reach(graph, source_id, seed):
    """
    Model influencer reach through extra direct contacts.

    The multiplier doubles the source's initial degree,
    up to the number of available users.
    """

    graph = graph.copy()
    rng = random.Random(seed)

    original_degree = graph.degree(source_id)

    candidates = [
        node for node in graph.nodes()
        if node != source_id
        and not graph.has_edge(source_id, node)
    ]

    rng.shuffle(candidates)

    extra_contacts = min(
        original_degree,
        len(candidates),
    )

    for node in candidates[:extra_contacts]:
        graph.add_edge(source_id, node)

    return graph


def run_trial(
    topology,
    source_type,
    position,
    algorithm,
    trial,
):
    """Run one deterministic diffusion experiment."""

    seed = SEED + trial

    graph = generate_graph(topology, seed)

    source_id = choose_source(graph, position)

    # Explicit influencer reach intervention.
    if source_type == "Influencer":
        graph = add_influencer_reach(
            graph, source_id, seed
        )

    network = create_network(
        graph,
        source_id,
        source_type,
        seed,
    )

    post = Post(
        content="RumorFlow experimental rumor",
        source_id=source_id,
    )

    result = network.propagate(
        post,
        source=source_id,
        mode=algorithm,
    )

    # Mean shortest-path distance among exposed nodes.
    # This is a structural metric, not a transmission delay.
    distances = nx.single_source_shortest_path_length(
        graph, source_id
    )

    exposed_distances = [
        distances[node]
        for node in result.exposed
        if node in distances
    ]

    mean_distance = float(
        np.mean(exposed_distances)
    ) if exposed_distances else 0.0

    return {
        "topology": topology,
        "source_type": source_type,
        "source_position": position,
        "algorithm": algorithm,
        "trial": trial,
        "source_id": source_id,
        "reach_percent": result.reach_percentage,
        "steps_to_saturation": result.total_steps,
        "spread_speed": (
            len(result.exposed) / result.total_steps
            if result.total_steps else 0.0
        ),
        "mean_exposed_distance": mean_distance,
        "exposed_count": len(result.exposed),
        "edge_count": graph.number_of_edges(),
    }


def run_experiments():
    """Run all experiment configurations."""

    records = []

    total = (
        len(TOPOLOGIES)
        * len(SOURCE_TYPES)
        * len(SOURCE_POSITIONS)
        * len(ALGORITHMS)
        * TRIALS
    )

    print(f"Running {total} simulations...")

    for topology in TOPOLOGIES:
        for source_type in SOURCE_TYPES:
            for position in SOURCE_POSITIONS:
                for algorithm in ALGORITHMS:
                    for trial in range(TRIALS):

                        record = run_trial(
                            topology,
                            source_type,
                            position,
                            algorithm,
                            trial,
                        )

                        records.append(record)

        print(f"Completed: {topology}")

    return pd.DataFrame(records)


def summarize_results(df):
    """Calculate average results per configuration."""

    summary = (
        df.groupby(
            [
                "topology",
                "source_type",
                "source_position",
                "algorithm",
            ],
            as_index=False,
        )
        .agg(
            mean_reach=("reach_percent", "mean"),
            std_reach=("reach_percent", "std"),
            mean_steps=("steps_to_saturation", "mean"),
            mean_speed=("spread_speed", "mean"),
            mean_distance=(
                "mean_exposed_distance", "mean"
            ),
        )
    )

    return summary.round(3)


def setup_plot():
    """Apply RumorFlow dark styling."""

    plt.rcParams.update({
        "figure.facecolor": BACKGROUND,
        "axes.facecolor": "#192630",
        "axes.labelcolor": "white",
        "axes.edgecolor": "#667788",
        "text.color": "white",
        "xtick.color": "white",
        "ytick.color": "white",
        "font.size": 10,
    })


def plot_topology_comparison(df):
    """Compare average reach across network models."""

    data = (
        df[df["algorithm"] == "bfs"]
        .groupby("topology")["reach_percent"]
        .mean()
        .reindex(TOPOLOGIES)
    )

    fig, ax = plt.subplots(figsize=(9, 5))

    bars = ax.bar(
        data.index,
        data.values,
        color=[TEAL, CORAL, AMBER],
    )

    ax.bar_label(bars, fmt="%.1f%%", padding=4)

    ax.set_title("Average Rumor Reach by Network Type")
    ax.set_ylabel("Average Reach (%)")
    ax.set_ylim(0, 110)

    fig.tight_layout()

    fig.savefig(
        OUTPUT_DIR / "topology_comparison.png",
        dpi=160,
    )

    plt.close(fig)


def plot_source_comparison(df):
    """Compare the effect of source-user types."""

    data = (
        df[df["algorithm"] == "bfs"]
        .groupby("source_type")["reach_percent"]
        .mean()
        .reindex(SOURCE_TYPES)
    )

    fig, ax = plt.subplots(figsize=(9, 5))

    bars = ax.bar(
        data.index,
        data.values,
        color=[TEAL, AMBER, CORAL],
    )

    ax.bar_label(bars, fmt="%.1f%%", padding=4)

    ax.set_title("Rumor Reach by Source Type")
    ax.set_ylabel("Average Reach (%)")
    ax.set_ylim(0, 110)

    fig.tight_layout()

    fig.savefig(
        OUTPUT_DIR / "source_comparison.png",
        dpi=160,
    )

    plt.close(fig)


def plot_degree_comparison(df):
    """Compare high-degree and low-degree sources."""

    data = (
        df[df["algorithm"] == "bfs"]
        .groupby("source_position")["reach_percent"]
        .mean()
        .reindex(SOURCE_POSITIONS)
    )

    fig, ax = plt.subplots(figsize=(8, 5))

    bars = ax.bar(
        data.index,
        data.values,
        color=[TEAL, CORAL],
    )

    ax.bar_label(bars, fmt="%.1f%%", padding=4)

    ax.set_title("Influence of Source Connectivity")
    ax.set_ylabel("Average Reach (%)")
    ax.set_ylim(0, 110)

    fig.tight_layout()

    fig.savefig(
        OUTPUT_DIR / "degree_comparison.png",
        dpi=160,
    )

    plt.close(fig)


def plot_algorithm_comparison(df):
    """Compare BFS and DFS processing step counts."""

    data = (
        df.groupby("algorithm")["steps_to_saturation"]
        .mean()
        .reindex(ALGORITHMS)
    )

    fig, ax = plt.subplots(figsize=(8, 5))

    bars = ax.bar(
        ["BFS", "DFS"],
        data.values,
        color=[TEAL, CORAL],
    )

    ax.bar_label(bars, fmt="%.2f", padding=4)

    ax.set_title("BFS vs DFS Processing Steps")
    ax.set_ylabel("Average Processing Steps")
    ax.set_ylim(bottom=0)

    fig.tight_layout()

    fig.savefig(
        OUTPUT_DIR / "algorithm_comparison.png",
        dpi=160,
    )

    plt.close(fig)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    setup_plot()

    df = run_experiments()

    summary = summarize_results(df)

    df.to_csv(
        OUTPUT_DIR / "experiment_results.csv",
        index=False,
    )

    summary.to_csv(
        OUTPUT_DIR / "experiment_summary.csv",
        index=False,
    )

    plot_topology_comparison(df)
    plot_source_comparison(df)
    plot_degree_comparison(df)
    plot_algorithm_comparison(df)

    print("\nEXPERIMENT SUMMARY")
    print("=" * 70)
    print(summary.to_string(index=False))

    print("\nAll experiment outputs saved to outputs/")


if __name__ == "__main__":
    main()
