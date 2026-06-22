# Tic-Tac-Toe-AI-Game

## Overview

A complete, single-file desktop application (built with Tkinter — a real windowed app, not a web page) featuring an AI opponent powered by four different search/AI algorithms, selectable live from the GUI.

| Algorithm | Type |
|---|---|
| Breadth-First Search (BFS) | Uninformed search |
| Depth-First Search (DFS) | Uninformed search |
| Minimax | Adversarial search |
| Minimax with Alpha-Beta Pruning | Optimized adversarial search |

The game includes a custom colorful logo, synthesized background music, and sound effects — all generated entirely in code, so the project stays fully self-contained with zero external assets.

## Project Structure

```
tic_tac_toe/
├── tic_tac_toe.py      # Complete game: logic, AI, GUI, sound, logo
└── assets/
    └── logo.png        # App logo shown at the top of the window
```

The game is a single Python file for all logic/AI/GUI/sound code, plus one small `assets/logo.png` image file that must stay next to it in its `assets/` folder (the script loads it from there automatically).

## How to Run

No external libraries are required to play.

```bash
cd tic_tac_toe
python tic_tac_toe.py
```

**Requirements:** Python 3.8+ with Tkinter (preinstalled with most Python distributions; on Linux you may need `sudo apt install python3-tk`).

**Optional** — for background music and sound effects:

```bash
pip install pygame
```

If pygame isn't installed, the game still runs perfectly — it just plays silently (no crash, no error).

## AI Algorithms Explained

1. **Breadth-First Search (BFS)** — Explores the game tree level-by-level, checking all moves at the current depth before going deeper. Included for academic comparison.
2. **Depth-First Search (DFS)** — Explores one branch as deep as possible before backtracking. Fast but not guaranteed to find the optimal move quickly in a large search space.
3. **Minimax** — A recursive adversarial-search algorithm that assumes the opponent plays optimally. It explores the reachable game tree and picks the move that maximizes the AI's guaranteed outcome.
4. **Minimax + Alpha-Beta Pruning** — The same idea as Minimax, but it prunes branches that can't possibly affect the final decision, making the search dramatically faster — this is the strongest and default AI.

## Features

- Clean, modern, dark-themed desktop UI (not a website — a real app)
- Custom colorful logo centered in the game window
- Synthesized background music and sound effects (no audio files)
- Switch AI algorithm live from a dropdown menu
- Unbeatable AI (Minimax / Alpha-Beta mode)
- Clean, well-commented, single-file code — easy to read for a viva

## Academic & Ethical Note

This project was developed as an academic exercise to demonstrate classical AI search algorithms (BFS, DFS, Minimax, Alpha-Beta Pruning) in a practical, interactive setting, in line with university course requirements (AI / Project module). All code is original and written for educational purposes.