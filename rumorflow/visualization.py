
"""Visualization tools for RumorFlow."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import networkx as nx

from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from rumorflow.models import Bot, Influencer
from rumorflow.network import Network, PropagationResult


# Dark theme
BACKGROUND = "#101820"
PANEL = "#192630"
TEXT = "#F1F5F9"

TEAL = "#28D7C0"
CORAL = "#FF6F61"
AMBER = "#FFCA5F"
GREY = "#667788"

OUTPUT_DIR = Path("outputs")


def setup_theme():
    """Configure a consistent dark theme."""
    plt.rcParams.update({
        "figure.facecolor": BACKGROUND,
        "axes.facecolor": PANEL,
        "axes.edgecolor": GREY,
        "axes.labelcolor": TEXT,
        "text.color": TEXT,
        "xtick.color": TEXT,
        "ytick.color": TEXT,
        "grid.color": GREY,
        "font.size": 11,
    })


def build_nx_graph(network: Network) -> nx.Graph:
    """Convert the adjacency list to a NetworkX graph."""
    graph = nx.Graph()

    for user_id, neighbors in network.get_graph().items():
        graph.add_node(user_id)

        for neighbor in neighbors:
            graph.add_edge(user_id, neighbor)

    return graph


def draw_network(
    network: Network,
    exposed=None,
    frontier=None,
    title="RumorFlow Social Network",
    ax=None,
    pos=None,
):
    """Draw the network with user-type and state styling."""

    setup_theme()

    graph = build_nx_graph(network)
    users = network.get_users()

    exposed = set(exposed or [])
    frontier = set(frontier or [])

    if ax is None:
        _, ax = plt.subplots(figsize=(10, 7))

    if pos is None:
        pos = nx.spring_layout(graph, seed=42)

    ax.set_facecolor(PANEL)

    nx.draw_networkx_edges(
        graph,
        pos,
        ax=ax,
        edge_color=GREY,
        alpha=0.45,
        width=1.5,
    )

    # Different shapes for user types
    for user_type, shape, size in [
        (Influencer, "s", 1050),
        (Bot, "D", 850),
        (None, "o", 650),
    ]:
        selected = []

        for user_id, user in users.items():
            if user_type is None:
                if not isinstance(user, (Influencer, Bot)):
                    selected.append(user_id)
            elif isinstance(user, user_type):
                selected.append(user_id)

        if not selected:
            continue

        colors = []

        for user_id in selected:
            if user_id in exposed:
                colors.append(CORAL)
            elif user_id in frontier:
                colors.append(AMBER)
            else:
                colors.append(GREY)

        nx.draw_networkx_nodes(
            graph,
            pos,
            nodelist=selected,
            node_color=colors,
            node_shape=shape,
            node_size=size,
            edgecolors=TEAL,
            linewidths=1.5,
            ax=ax,
        )

    nx.draw_networkx_labels(
        graph,
        pos,
        labels={uid: str(uid) for uid in graph.nodes()},
        font_color=BACKGROUND,
        font_weight="bold",
        ax=ax,
    )

    legend = [
        Patch(color=GREY, label="Unseen"),
        Patch(color=AMBER, label="Frontier"),
        Patch(color=CORAL, label="Exposed"),
        Line2D(
            [0], [0], marker="o", color="none",
            markerfacecolor=TEAL, markersize=9,
            label="Regular User",
        ),
        Line2D(
            [0], [0], marker="s", color="none",
            markerfacecolor=TEAL, markersize=9,
            label="Influencer",
        ),
        Line2D(
            [0], [0], marker="D", color="none",
            markerfacecolor=TEAL, markersize=9,
            label="Bot",
        ),
    ]

    ax.legend(
        handles=legend,
        loc="upper left",
        facecolor=PANEL,
        labelcolor=TEXT,
        fontsize=8,
    )

    ax.set_title(title, fontsize=15, fontweight="bold")
    ax.axis("off")

    return ax


def plot_bfs_bar_chart(result: PropagationResult):
    """Save a bar chart of newly exposed users per step."""

    setup_theme()
    OUTPUT_DIR.mkdir(exist_ok=True)

    steps = [s.step_no for s in result.steps]
    counts = [len(s.newly_exposed) for s in result.steps]

    fig, ax = plt.subplots(figsize=(9, 5))

    bars = ax.bar(steps, counts, color=TEAL, width=0.65)

    ax.bar_label(bars, padding=4, color=TEXT)
    ax.set_title("Users Exposed per BFS Step")
    ax.set_xlabel("BFS Step")
    ax.set_ylabel("Newly Exposed Users")
    ax.set_xticks(steps)
    ax.grid(axis="y", alpha=0.2)

    fig.tight_layout()
    fig.savefig(
        OUTPUT_DIR / "bfs_exposure_bar.png",
        dpi=160,
    )
    plt.close(fig)


def plot_spread_curve(result: PropagationResult):
    """Save a cumulative rumor spread line chart."""

    setup_theme()
    OUTPUT_DIR.mkdir(exist_ok=True)

    steps = [0] + [s.step_no for s in result.steps]
    totals = [0] + [s.exposed_total for s in result.steps]

    fig, ax = plt.subplots(figsize=(9, 5))

    ax.plot(
        steps,
        totals,
        color=CORAL,
        marker="o",
        linewidth=3,
    )

    ax.fill_between(steps, totals, color=CORAL, alpha=0.12)

    ax.set_title("Cumulative Rumor Spread")
    ax.set_xlabel("Propagation Step")
    ax.set_ylabel("Total Exposed Users")
    ax.set_xticks(steps)
    ax.set_ylim(bottom=0)
    ax.grid(alpha=0.2)

    fig.tight_layout()
    fig.savefig(
        OUTPUT_DIR / "cumulative_spread.png",
        dpi=160,
    )
    plt.close(fig)


def animate_spread(
    network: Network,
    result: PropagationResult,
    filename="rumorflow_animation.gif",
):
    """Save an animated GIF and static PNG frames."""

    setup_theme()

    OUTPUT_DIR.mkdir(exist_ok=True)
    frames_dir = OUTPUT_DIR / "frames"
    frames_dir.mkdir(exist_ok=True)

    graph = build_nx_graph(network)
    pos = nx.spring_layout(graph, seed=42)

    # Build a snapshot for every propagation step.
    snapshots = []

    exposed = set()

    snapshots.append({
        "exposed": set(),
        "frontier": {result.source_id},
        "step": 0,
    })

    for step in result.steps:
        exposed.update(step.newly_exposed)

        snapshots.append({
            "exposed": exposed.copy(),
            "frontier": set(step.frontier),
            "step": step.step_no,
        })

    fig, ax = plt.subplots(figsize=(10, 7))

    def update(frame_index):
        ax.clear()

        snapshot = snapshots[frame_index]

        draw_network(
            network,
            exposed=snapshot["exposed"],
            frontier=snapshot["frontier"],
            title=(
                f"RumorFlow | Step {snapshot['step']} "
                f"| Exposed: {len(snapshot['exposed'])}"
            ),
            ax=ax,
            pos=pos,
        )

        return []

    # Save static frames
    for index in range(len(snapshots)):
        update(index)

        fig.savefig(
            frames_dir / f"step_{index:03d}.png",
            dpi=140,
            bbox_inches="tight",
        )

    animation = FuncAnimation(
        fig,
        update,
        frames=len(snapshots),
        interval=900,
        repeat=False,
    )

    animation.save(
        OUTPUT_DIR / filename,
        writer=PillowWriter(fps=1),
    )

    plt.close(fig)


def generate_all_visuals(
    network: Network,
    result: PropagationResult,
):
    """Generate every visualization for a simulation."""

    OUTPUT_DIR.mkdir(exist_ok=True)

    plot_bfs_bar_chart(result)
    plot_spread_curve(result)

    animate_spread(network, result)

    print("\nVisualizations saved to outputs/")
