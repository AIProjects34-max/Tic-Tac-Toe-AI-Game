import os
import sys
import math
import struct
import tempfile
import wave
import tkinter as tk
from tkinter import messagebox, ttk

# SOUND ENGINE

try:
    import pygame
    pygame.mixer.init()
    _SOUND_AVAILABLE = True
except Exception:
    _SOUND_AVAILABLE = False

_CACHE_DIR = os.path.join(tempfile.gettempdir(), "ai_games_sfx_cache")
os.makedirs(_CACHE_DIR, exist_ok=True)
SAMPLE_RATE = 44100


def _generate_tone(filepath, frequencies, duration=0.15, volume=0.35):
    n_samples = int(SAMPLE_RATE * duration)
    frames = bytearray()
    for i in range(n_samples):
        t = i / SAMPLE_RATE
        sample = sum(math.sin(2 * math.pi * f * t) for f in frequencies) / len(frequencies)
        fade_len = n_samples * 0.15
        if i < fade_len:
            sample *= i / fade_len
        elif i > n_samples - fade_len:
            sample *= (n_samples - i) / fade_len
        value = max(-32767, min(32767, int(sample * volume * 32767)))
        frames += struct.pack("<h", value)
    with wave.open(filepath, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(bytes(frames))


def _generate_music(filepath):
    progression = [
        (261.6, 329.6, 392.0),
        (293.7, 349.2, 440.0),
        (220.0, 277.2, 329.6),
        (246.9, 311.1, 392.0),
    ]
    note_duration = 1.4
    n = int(SAMPLE_RATE * note_duration)
    frames = bytearray()
    for chord in progression:
        for i in range(n):
            t = i / SAMPLE_RATE
            sample = 0.0
            for freq in chord:
                sample += math.sin(2 * math.pi * freq * t) * 0.5
                sample += math.sin(2 * math.pi * (freq / 2) * t) * 0.2
            sample /= len(chord)
            fade_len = n * 0.08
            if i < fade_len:
                sample *= i / fade_len
            elif i > n - fade_len:
                sample *= (n - i) / fade_len
            value = max(-32767, min(32767, int(sample * 0.18 * 32767)))
            frames += struct.pack("<h", value)
    with wave.open(filepath, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(bytes(frames))


_SOUND_DEFS = {
    "click": ([440.0], 0.07),
    "move": ([523.25], 0.10),
    "win": ([523.25, 659.25, 783.99], 0.35),
    "lose": ([220.0, 196.0], 0.35),
    "draw": ([330.0, 330.0], 0.25),
    "invalid": ([180.0], 0.12),
}
_cached_sounds = {}
_music_path = os.path.join(_CACHE_DIR, "background_music.wav")
_music_playing = False


def play_sound(name):
    if not _SOUND_AVAILABLE or name not in _SOUND_DEFS:
        return
    try:
        if name not in _cached_sounds:
            path = os.path.join(_CACHE_DIR, f"{name}.wav")
            if not os.path.exists(path):
                freqs, dur = _SOUND_DEFS[name]
                _generate_tone(path, freqs, dur)
            _cached_sounds[name] = pygame.mixer.Sound(path)
        _cached_sounds[name].play()
    except Exception:
        pass


def toggle_music(volume=0.4):
    global _music_playing
    if not _SOUND_AVAILABLE:
        return False
    try:
        if _music_playing:
            pygame.mixer.music.stop()
            _music_playing = False
        else:
            if not os.path.exists(_music_path):
                _generate_music(_music_path)
            pygame.mixer.music.load(_music_path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loops=-1)
            _music_playing = True
    except Exception:
        pass
    return _music_playing


def start_music(volume=0.4):
    global _music_playing
    if not _SOUND_AVAILABLE:
        return False
    try:
        if not os.path.exists(_music_path):
            _generate_music(_music_path)
        pygame.mixer.music.load(_music_path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(loops=-1)
        _music_playing = True
    except Exception:
        pass
    return _music_playing

# GAME LOGIC

HUMAN = "X"
AI = "O"
EMPTY = " "

WIN_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6),
]


def check_winner(board):
    for a, b, c in WIN_LINES:
        if board[a] != EMPTY and board[a] == board[b] == board[c]:
            return board[a]
    if EMPTY not in board:
        return "Draw"
    return None


def available_moves(board):
    return [i for i, v in enumerate(board) if v == EMPTY]


# BFS
def bfs_move(board):
    from collections import deque
    queue = deque()
    for move in available_moves(board):
        nb = board.copy()
        nb[move] = AI
        queue.append((nb, move))
    best_move = available_moves(board)[0]
    while queue:
        current_board, first_move = queue.popleft()
        result = check_winner(current_board)
        if result == AI:
            return first_move
        for move in available_moves(current_board):
            nb = current_board.copy()
            nb[move] = HUMAN if current_board.count(AI) > current_board.count(HUMAN) else AI
            queue.append((nb, first_move))
    return best_move


# DFS
def dfs_move(board):
    def dfs(b, is_ai_turn):
        winner = check_winner(b)
        if winner == AI:
            return True
        if winner == HUMAN or winner == "Draw":
            return False
        for move in available_moves(b):
            nb = b.copy()
            nb[move] = AI if is_ai_turn else HUMAN
            if dfs(nb, not is_ai_turn) and is_ai_turn:
                return True
        return False

    for move in available_moves(board):
        nb = board.copy()
        nb[move] = AI
        if dfs(nb, False):
            return move
    return available_moves(board)[0]


# Minimax
def minimax(board, is_maximizing):
    winner = check_winner(board)
    if winner == AI:
        return 1
    if winner == HUMAN:
        return -1
    if winner == "Draw":
        return 0
    if is_maximizing:
        best = -float("inf")
        for move in available_moves(board):
            nb = board.copy()
            nb[move] = AI
            best = max(best, minimax(nb, False))
        return best
    else:
        best = float("inf")
        for move in available_moves(board):
            nb = board.copy()
            nb[move] = HUMAN
            best = min(best, minimax(nb, True))
        return best


def minimax_move(board):
    best_score, best_move = -float("inf"), None
    for move in available_moves(board):
        nb = board.copy()
        nb[move] = AI
        score = minimax(nb, False)
        if score > best_score:
            best_score, best_move = score, move
    return best_move


# Minimax + Alpha-Beta Pruning
def alphabeta(board, is_maximizing, alpha, beta):
    winner = check_winner(board)
    if winner == AI:
        return 1
    if winner == HUMAN:
        return -1
    if winner == "Draw":
        return 0
    if is_maximizing:
        value = -float("inf")
        for move in available_moves(board):
            nb = board.copy()
            nb[move] = AI
            value = max(value, alphabeta(nb, False, alpha, beta))
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return value
    else:
        value = float("inf")
        for move in available_moves(board):
            nb = board.copy()
            nb[move] = HUMAN
            value = min(value, alphabeta(nb, True, alpha, beta))
            beta = min(beta, value)
            if alpha >= beta:
                break
        return value


def alphabeta_move(board):
    best_score, best_move = -float("inf"), None
    alpha, beta = -float("inf"), float("inf")
    for move in available_moves(board):
        nb = board.copy()
        nb[move] = AI
        score = alphabeta(nb, False, alpha, beta)
        if score > best_score:
            best_score, best_move = score, move
        alpha = max(alpha, best_score)
    return best_move


ALGORITHMS = {
    "Minimax + Alpha-Beta (Best)": alphabeta_move,
    "Minimax": minimax_move,
    "Depth-First Search (DFS)": dfs_move,
    "Breadth-First Search (BFS)": bfs_move,
}


BG_COLOR = "#15151f"
PANEL_COLOR = "#1c1c2b"
CELL_COLOR = "#262638"
CELL_HOVER = "#32324a"
X_COLOR = "#7dd3fc"
O_COLOR = "#fca5a5"
ACCENT = "#a78bfa"
ACCENT_DARK = "#7c5fd6"
TEXT_COLOR = "#e8e8f5"
MUTED_TEXT = "#9999b3"


class TicTacToeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe - AI Desktop Edition")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)

        self.board = [EMPTY] * 9
        self.buttons = []
        self.game_over = False
        self.score = {"wins": 0, "losses": 0, "draws": 0}

        self._build_titlebar()
        self._build_score_panel()
        self._build_algo_selector()
        self._build_board()
        self._build_status_bar()
        self._build_footer()

        start_music()
        self._update_music_btn()

    # UI builders
    def _build_titlebar(self):
        bar = tk.Frame(self.root, bg=PANEL_COLOR)
        bar.pack(fill="x")

        top_row = tk.Frame(bar, bg=PANEL_COLOR)
        top_row.pack(fill="x")
        self.music_btn = tk.Button(
            top_row, text="Music", font=("Segoe UI", 9, "bold"), bg=PANEL_COLOR, fg=ACCENT,
            bd=0, relief="flat", cursor="hand2", activebackground=PANEL_COLOR,
            command=self._toggle_music
        )
        self.music_btn.pack(side=tk.RIGHT, padx=10, pady=(8, 0))

        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo.png")
        try:
            self.logo_image = tk.PhotoImage(file=logo_path)
            logo_label = tk.Label(bar, image=self.logo_image, bg=PANEL_COLOR)
            logo_label.pack(pady=(0, 10))
        except Exception:
            tk.Label(
                bar, text="TIC TAC TOE", font=("Segoe UI", 20, "bold"),
                bg=PANEL_COLOR, fg=ACCENT
            ).pack(pady=(10, 10))

        tk.Label(
            bar, text="AI DESKTOP EDITION", font=("Segoe UI", 8, "bold"),
            bg=PANEL_COLOR, fg=MUTED_TEXT
        ).pack(pady=(0, 12))

    def _build_score_panel(self):
        frame = tk.Frame(self.root, bg=BG_COLOR)
        frame.pack(pady=(12, 4))
        self.score_label = tk.Label(
            frame, text=self._score_text(), font=("Segoe UI", 10),
            bg=BG_COLOR, fg=MUTED_TEXT
        )
        self.score_label.pack()

    def _score_text(self):
        s = self.score
        return f"Wins: {s['wins']}    Losses: {s['losses']}    Draws: {s['draws']}"

    def _build_algo_selector(self):
        frame = tk.Frame(self.root, bg=BG_COLOR)
        frame.pack(pady=(6, 10))
        tk.Label(frame, text="AI Engine:", bg=BG_COLOR, fg=TEXT_COLOR,
                 font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 8))

        self.algo_var = tk.StringVar(value=list(ALGORITHMS.keys())[0])
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TCombobox", fieldbackground=CELL_COLOR, background=CELL_COLOR,
                         foreground=TEXT_COLOR, arrowcolor=ACCENT)
        algo_menu = ttk.Combobox(
            frame, textvariable=self.algo_var, values=list(ALGORITHMS.keys()),
            state="readonly", width=27, font=("Segoe UI", 9)
        )
        algo_menu.pack(side=tk.LEFT)
        algo_menu.bind("<<ComboboxSelected>>", lambda e: play_sound("click"))

    def _build_board(self):
        outer = tk.Frame(self.root, bg=PANEL_COLOR, padx=14, pady=14)
        outer.pack(padx=24, pady=4)
        for i in range(9):
            btn = tk.Button(
                outer, text=EMPTY, font=("Segoe UI", 30, "bold"),
                width=4, height=2, bg=CELL_COLOR, fg=TEXT_COLOR,
                activebackground=CELL_HOVER, bd=0, relief="flat", cursor="hand2",
                command=lambda idx=i: self.human_move(idx)
            )
            btn.grid(row=i // 3, column=i % 3, padx=5, pady=5)
            btn.bind("<Enter>", lambda e, b=btn: self._on_hover(b, True))
            btn.bind("<Leave>", lambda e, b=btn: self._on_hover(b, False))
            self.buttons.append(btn)

    def _on_hover(self, btn, entering):
        if btn["text"] == EMPTY and not self.game_over:
            btn.config(bg=CELL_HOVER if entering else CELL_COLOR)

    def _build_status_bar(self):
        self.status = tk.Label(
            self.root, text="Your turn - make a move", font=("Segoe UI", 12, "bold"),
            bg=BG_COLOR, fg=TEXT_COLOR, pady=14
        )
        self.status.pack()

    def _build_footer(self):
        footer = tk.Frame(self.root, bg=BG_COLOR)
        footer.pack(pady=(0, 18))
        restart_btn = tk.Button(
            footer, text="New Game", font=("Segoe UI", 10, "bold"),
            bg=ACCENT, fg="#15151f", bd=0, relief="flat", padx=16, pady=8,
            cursor="hand2", activebackground=ACCENT_DARK, command=self.restart
        )
        restart_btn.pack()
        self.sound_note = tk.Label(
            self.root, text=self._sound_status_text(), font=("Segoe UI", 8),
            bg=BG_COLOR, fg=MUTED_TEXT
        )
        self.sound_note.pack(pady=(0, 10))

    def _sound_status_text(self):
        if not _SOUND_AVAILABLE:
            return "Sound: unavailable (run: pip install pygame)"
        return "Music: ON" if _music_playing else "Music: OFF"

    def _toggle_music(self):
        toggle_music()
        self._update_music_btn()

    def _update_music_btn(self):
        self.sound_note.config(text=self._sound_status_text())

    # Game flow
    def human_move(self, idx):
        if self.game_over or self.board[idx] != EMPTY:
            play_sound("invalid")
            return
        self.board[idx] = HUMAN
        play_sound("move")
        self.refresh()
        result = check_winner(self.board)
        if result:
            self.end_game(result)
            return
        self.status.config(text="AI is thinking...")
        self.root.update()
        self.root.after(300, self.ai_move)

    def ai_move(self):
        algo_func = ALGORITHMS[self.algo_var.get()]
        move = algo_func(self.board.copy())
        if move is not None:
            self.board[move] = AI
            play_sound("move")
        self.refresh()
        result = check_winner(self.board)
        if result:
            self.end_game(result)
        else:
            self.status.config(text="Your turn - make a move")

    def refresh(self):
        for i, val in enumerate(self.board):
            color = X_COLOR if val == HUMAN else O_COLOR if val == AI else TEXT_COLOR
            self.buttons[i].config(text=val, fg=color, bg=CELL_COLOR)

    def end_game(self, result):
        self.game_over = True
        if result == "Draw":
            self.score["draws"] += 1
            self.status.config(text="It's a Draw!")
            play_sound("draw")
            messagebox.showinfo("Game Over", "It's a Draw!")
        elif result == HUMAN:
            self.score["wins"] += 1
            self.status.config(text="You Win!")
            play_sound("win")
            messagebox.showinfo("Game Over", "Congratulations, You Win!")
        else:
            self.score["losses"] += 1
            self.status.config(text="AI Wins!")
            play_sound("lose")
            messagebox.showinfo("Game Over", "AI Wins! Better luck next time.")
        self.score_label.config(text=self._score_text())

    def restart(self):
        play_sound("click")
        self.board = [EMPTY] * 9
        self.game_over = False
        self.refresh()
        self.status.config(text="Your turn - make a move")


if __name__ == "__main__":
    root = tk.Tk()
    app = TicTacToeApp(root)
    root.mainloop()