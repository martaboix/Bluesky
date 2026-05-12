# Bluesky Social Network Analysis & Reporting Tool

This project was developed as part of the **Algorithms and Programming II** course at UPC (Universitat Politècnica de Catalunya). It consists of a Python-based tool that acts as a "Data Start-up" service, providing deep insights and analytical reports for users of the **Bluesky** social network.

## Project Overview
The tool analyzes a user's social environment by fetching real-time data through the Bluesky API. It builds complex graph structures to visualize and quantify social interactions and follower networks.

## Key Features
* **Graph Generation:** * **Follower Graph ($G_U$):** A subgraph representing the direct connections and relationships between a client's followers.
    * **Thread Fusion Graph:** An aggregated graph built from interaction threads (posts and replies) to visualize content propagation.
* **Network Analysis:** * Implementation of **PageRank** to identify high-reputation followers.
    * **Community Detection** using `label_components` and topological analysis.
    * **Influence Measurement:** Analysis of propagation distance and "Betweenness Centrality" to find key users who expand the client's reach.
* **Automated Reporting:** Generates a comprehensive PDF report using `fpdf2`, including data summaries and graph visualizations (SVG/PDF).

## Technologies Used
* **Python 3** (Core logic)
* **graph-tool:** High-performance library for graph manipulation and visualization.
* **Click:** For creating a robust Command Line Interface (CLI).
* **Pixi:** For package management and environment reproducibility.
* **Asynchronous Programming:** `aiohttp` for efficient, concurrent API requests.

## How to Run
This project uses **Pixi** for dependency management.
1. Install Pixi: `curl -fsSL https://pixi.sh/install.sh | sh`
2. Install dependencies: `pixi install`
3. Run the analysis: `pixi run python main.py [client_handle]`

## Project Architecture
* `bsky.py`: API wrapper and CLI commands.
* `analysis.py`: Implementation of graph algorithms and metrics.
* `report_gen.py`: Logic for automated PDF generation and visualization.
