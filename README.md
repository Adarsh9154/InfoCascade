# RumorFlow
## Graph-Based Social Network Simulator for Rumor and Information Diffusion

### 1. Project Overview

RumorFlow is a Python-based simulation that models how information spreads across a social network. It combines graph data structures, BFS and DFS algorithms, object-oriented programming, and statistical experiments.

### 2. Problem Statement

Information spreads through online social networks at different rates depending on the network's connectivity and the behavior of its users. RumorFlow simulates this process to study how graph topology, source connectivity, and forwarding decisions affect information exposure.

### 3. Objectives

- Represent a social network using an adjacency-list graph.
- Implement BFS and DFS for information propagation.
- Use inheritance, polymorphism, and encapsulation.
- Simulate different user-sharing behaviors.
- Visualize rumor spread through charts and animations.
- Compare random, small-world, and scale-free networks.

### 4. Technologies Used

- **Python:** Core programming language
- **NetworkX:** Graph generation and analysis
- **Matplotlib:** Data visualization and animation
- **Pandas:** Experimental data processing
- **NumPy:** Numerical analysis
- **Pytest:** Automated testing

### 5. Methodology

1. Create a social network with users as vertices and friendships as undirected edges.
2. Select a source user and initialize the rumor.
3. Propagate information using BFS or DFS.
4. Use a hash set to prevent repeated exposure.
5. Apply user-specific forwarding decisions.
6. Record propagation steps, exposure counts, and frontier states.
7. Generate visualizations and experimental summaries.

### 6. Algorithms

**Breadth-First Search (BFS):** Processes the rumor frontier level by level using a queue.

**Depth-First Search (DFS):** Explores one path at a time using an iterative stack.

Both algorithms use a hash set for cycle-safe traversal.

### 7. Complexity Analysis

| Operation | Time Complexity |
|---|---|
| BFS traversal | O(V + E) |
| DFS traversal | O(V + E) |
| Hash set lookup (average) | O(1) |
| Adding a user | O(1) average |
| Traversal auxiliary space | O(V) |

The overall graph representation requires O(V + E) storage.

### 8. Experiments

Three graph models are compared:

- Erdős–Rényi random network
- Watts–Strogatz small-world network
- Barabási–Albert scale-free network

The experiments use 20 users and 100 seeded trials per setting, resulting in 3,600 simulation runs.

Metrics include reach percentage, processing steps, average exposure per processing step, and mean graph distance among exposed users.

### 9. Results

The initial six-user demonstration produced:

| Metric | BFS | DFS |
|---|---|---|
| Users exposed | 6 | 6 |
| Reach | 100% | 100% |
| Processing steps | 3 | 6 |

BFS processed users in three waves, while DFS processed users individually. Both algorithms reached the same users in this demonstration.

The larger network experiments generate CSV summaries and comparison plots for further analysis.

### 10. Limitations

- Sharing probabilities are simplified representations of human behavior.
- Processing steps are not equivalent to real-world elapsed time.
- The simulator does not model changing beliefs or repeated exposures.
- Influencer reach is approximated using additional graph connections.
- Bot and regular source behavior are identical under the current source-initiation rule.

### 11. Future Scope

- Fake-news classification using machine learning.
- Time-based propagation and transmission delays.
- Multiple competing rumors.
- Interactive Streamlit dashboard.
- Community detection and influence maximization.
- Rumor containment and misinformation intervention strategies.

### 12. Conclusion

RumorFlow demonstrates how graph algorithms and user behavior can be combined to simulate information diffusion. It provides a reproducible environment for examining the relationship between network structure, source connectivity, and rumor exposure.

The project also demonstrates practical applications of data structures, object-oriented programming, simulation, testing, and data visualization.