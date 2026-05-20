# 🐔 Clucky Keys

> A terminal typing game — save your chicken from the evil farmer!

```
╔══════════════════════════╗
║      CLUCKY  KEYS        ║
╚══════════════════════════╝

  ║                        >}  your chicken
  ║                       (^_^) the farmer
  [●] ← the stone
  ═══════════════════════════
```

Type words correctly to **raise the stone** and keep your chicken safe.  
Every mistake **lowers the stone** toward it. Complete all words before time runs out!

---

## Features

- 🎮 Three difficulty levels — Easy, Medium, Hard
- 🪨 Animated stone that rises/falls in real time with your accuracy
- 🌈 Full terminal colour — green for correct letters, red for wrong
- 😱 Reactive characters — the chicken panics and the farmer laughs at mistakes
- 📊 Score, accuracy, words-per-game tracking with an S–D grade
- ⌨️ Zero dependencies — uses only Python's built-in `curses` library

---

## Requirements

| Requirement | Detail |
|---|---|
| Python | 3.6 or higher |
| OS | Linux, macOS, Windows (WSL recommended) |
| Terminal | Any terminal that supports colour (80×24 minimum) |
| Dependencies | None — standard library only |

---

## Installation

```bash
# Clone the repo
git clone https://github.com/your-username/clucky-keys.git
cd clucky-keys

# Run the game
python3 clucky_keys.py
```

No `pip install` needed.

---

## Controls

| Key | Action |
|---|---|
| Any letter | Type the current word |
| `Backspace` | Delete last character |
| `Esc` | Clear current input |
| `← →` | Change difficulty (menu only) |
| `Enter` | Start / play again |
| `Q` | Quit (from menu or in-game when input is empty) |

---

## Gameplay

1. A word appears on screen — type it exactly as shown
2. Each **correct keystroke** raises the stone (more rope = safer chicken)
3. Each **wrong keystroke** lowers the stone — no character is added, only a penalty
4. Complete all 15 words before the timer hits zero to win
5. If the stone reaches the ground, the game is over

### Scoring

```
word_score = points_base + (time_remaining × 2) + (word_length × 3)
```

| Difficulty | Time | Base Points | Penalty | Reward |
|---|---|---|---|---|
| Easy | 45 s | 10 | Low | High |
| Medium | 35 s | 18 | Medium | Medium |
| Hard | 28 s | 30 | High | Low |

### Grades

| Grade | Score |
|---|---|
| S | ≥ 500 |
| A | ≥ 300 |
| B | ≥ 150 |
| C | ≥ 80 |
| D | < 80 |

---

## Project Structure

```
clucky-keys/
├── clucky_keys.py   # entire game — single file, no dependencies
├── README.md
├── LICENSE
└── .gitignore
```

---

## Windows Note

`curses` is not included in the Windows standard Python distribution.  
Options:
- **WSL** (recommended): install Python inside Windows Subsystem for Linux
- **windows-curses**: `pip install windows-curses`, then run normally

---

## Contributing

Pull requests are welcome! Some ideas for extensions:

- High-score persistence (`json` / `sqlite3`)
- Custom word lists loaded from a file
- Multiplayer race mode over a socket
- More scenes / animations

Please open an issue first for larger changes.

---

## License

MIT — see [LICENSE](LICENSE)

---

*Built as part of a university game-design project at Riga Technical University, 2025.*
