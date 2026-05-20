#!/usr/bin/env python3
"""
╔═══════════════════════════════╗
║       CLUCKY KEYS 🐔          ║
║  Save your chicken from the   ║
║      evil farmer!             ║
╚═══════════════════════════════╝
Run with:  python3 clucky_keys.py
"""

import curses
import time
import random
import sys

# ─── Word Lists ───────────────────────────────────────────────────────────────
WORDS = {
    "easy": [
        "cat", "dog", "hen", "sun", "run", "egg", "cup", "hat", "big", "red",
        "jump", "blue", "fish", "tree", "farm", "bird", "play", "cake", "star", "milk",
        "frog", "lamp", "rock", "wind", "fog",  "nest", "barn", "hay",  "mud",  "pen",
    ],
    "medium": [
        "stone", "chicken", "farmer", "typing", "rescue", "danger", "sprint", "escape",
        "battle", "hammer", "castle", "frozen", "dragon", "button", "signal", "target",
        "forest", "basket", "garden", "window", "golden", "silver", "shadow", "market",
        "bridge", "rocket", "carpet", "mirror", "broken", "goblin",
    ],
    "hard": [
        "accurately", "precision", "challenge", "character", "butterfly", "dangerous",
        "adventure", "frantically", "carefully", "emergency", "difficult", "incredible",
        "wonderful", "mysterious", "continuous", "responsible", "knowledge", "important",
        "fantastic", "spectacular", "achievement", "umberland", "mischievous", "terrifying",
        "consequence", "perseverance", "comfortable", "spectacular", "overwhelming", "magnificent",
    ],
}

DIFF_CONFIG = {
    "easy":   {"time": 45, "penalty": 14, "reward": 20, "points_base": 10, "label": "EASY"},
    "medium": {"time": 35, "penalty": 20, "reward": 26, "points_base": 18, "label": "MEDIUM"},
    "hard":   {"time": 28, "penalty": 28, "reward": 34, "points_base": 30, "label": "HARD"},
}

STONE_MIN  = 3    # row (0=top): stone danger zone
STONE_MAX  = 14   # row: stone start position (close to bottom of scene)
SCENE_H    = 18   # height of the visual scene area

PRAISE = ["Nice!", "Great!", "Nailed it!", "Excellent!", "Perfect!", "Boom!", "Yes!"]

# ─── Color pair IDs ───────────────────────────────────────────────────────────
C_TITLE   = 1
C_AMBER   = 2
C_GREEN   = 3
C_RED     = 4
C_MUTED   = 5
C_WHITE   = 6
C_DANGER  = 7
C_CORRECT = 8
C_WRONG   = 9
C_STONE   = 10
C_FARMER  = 11
C_CHICKEN = 12
C_BG_DIM  = 13


def init_colors():
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(C_TITLE,   curses.COLOR_YELLOW,  -1)
    curses.init_pair(C_AMBER,   curses.COLOR_YELLOW,  -1)
    curses.init_pair(C_GREEN,   curses.COLOR_GREEN,   -1)
    curses.init_pair(C_RED,     curses.COLOR_RED,     -1)
    curses.init_pair(C_MUTED,   8,                    -1)  # dark gray if supported
    curses.init_pair(C_WHITE,   curses.COLOR_WHITE,   -1)
    curses.init_pair(C_DANGER,  curses.COLOR_WHITE,   curses.COLOR_RED)
    curses.init_pair(C_CORRECT, curses.COLOR_GREEN,   -1)
    curses.init_pair(C_WRONG,   curses.COLOR_RED,     -1)
    curses.init_pair(C_STONE,   curses.COLOR_CYAN,    -1)
    curses.init_pair(C_FARMER,  curses.COLOR_MAGENTA, -1)
    curses.init_pair(C_CHICKEN, curses.COLOR_YELLOW,  -1)
    curses.init_pair(C_BG_DIM,  curses.COLOR_BLACK,   curses.COLOR_RED)


def safe_addstr(win, y, x, text, attr=0):
    """addstr that silently ignores out-of-bounds errors."""
    try:
        h, w = win.getmaxyx()
        if y < 0 or y >= h or x < 0:
            return
        text = text[:max(0, w - x - 1)]
        if text:
            win.addstr(y, x, text, attr)
    except curses.error:
        pass


def centered(win, y, text, attr=0):
    _, w = win.getmaxyx()
    x = max(0, (w - len(text)) // 2)
    safe_addstr(win, y, x, text, attr)


# ─── Scene Renderer ───────────────────────────────────────────────────────────
def draw_scene(win, stone_row, danger=False, scared_chicken=False, laugh_farmer=False):
    """Draw the 18-row game scene."""
    h, w = win.getmaxyx()
    scene_w = min(w, 60)
    off = max(0, (w - scene_w) // 2)

    for row in range(SCENE_H):
        safe_addstr(win, row, off, " " * scene_w)

    # Ground
    ground_row = SCENE_H - 1
    safe_addstr(win, ground_row, off, "═" * scene_w, curses.color_pair(C_MUTED))

    # Gallows frame  (left side)
    post_col = off + 4
    arm_row   = 1
    arm_col   = off + 4
    arm_len   = 8

    # post
    for r in range(arm_row, ground_row):
        safe_addstr(win, r, post_col, "║", curses.color_pair(C_MUTED))
    # arm
    safe_addstr(win, arm_row, arm_col, "╔" + "═" * (arm_len - 1), curses.color_pair(C_MUTED))
    # base brace
    safe_addstr(win, ground_row - 1, off + 2, "╚╗", curses.color_pair(C_MUTED))

    # Rope from arm tip down to stone
    rope_tip_col = arm_col + arm_len
    for r in range(arm_row + 1, stone_row):
        safe_addstr(win, r, rope_tip_col, "│", curses.color_pair(C_AMBER))

    # Stone
    stone_attr = curses.color_pair(C_STONE) | curses.A_BOLD
    if danger:
        stone_attr = curses.color_pair(C_RED) | curses.A_BOLD | curses.A_BLINK
    safe_addstr(win, stone_row, rope_tip_col - 1, "[●]", stone_attr)

    # Chicken (sits on ground, under stone column)
    chicken_row = ground_row - 1
    chicken_col = rope_tip_col - 1
    chicken_str = ">}" if not scared_chicken else "!}"
    chicken_attr = curses.color_pair(C_CHICKEN) | curses.A_BOLD
    if scared_chicken:
        chicken_attr |= curses.A_BLINK
    safe_addstr(win, chicken_row, chicken_col, chicken_str, chicken_attr)

    # Farmer (right side)
    farmer_col = off + scene_w - 8
    farmer_str = "('_')" if not laugh_farmer else "(^_^)"
    farmer_attr = curses.color_pair(C_FARMER) | curses.A_BOLD
    safe_addstr(win, chicken_row - 1, farmer_col, "  /|\\", farmer_attr)
    safe_addstr(win, chicken_row,     farmer_col, farmer_str, farmer_attr)

    # Danger warning bar
    if danger:
        warn = " !! DANGER !! "
        safe_addstr(win, 0, off + (scene_w - len(warn)) // 2, warn,
                    curses.color_pair(C_DANGER) | curses.A_BOLD)


# ─── HUD ──────────────────────────────────────────────────────────────────────
def draw_hud(win, score, time_left, words_done, total_words, accuracy, diff):
    h, w = win.getmaxyx()
    hud_row = SCENE_H
    safe_addstr(win, hud_row, 0, "─" * w, curses.color_pair(C_MUTED))

    urgency = time_left <= 8
    t_attr  = (curses.color_pair(C_RED) | curses.A_BOLD) if urgency else (curses.color_pair(C_WHITE) | curses.A_BOLD)

    items = [
        (f" SCORE: {score:>5}", curses.color_pair(C_AMBER) | curses.A_BOLD),
        (f"  TIME: {time_left:>3}s", t_attr),
        (f"  WORDS: {words_done}/{total_words}", curses.color_pair(C_WHITE)),
        (f"  ACC: {accuracy:>3}%", curses.color_pair(C_GREEN) if accuracy >= 80 else curses.color_pair(C_RED)),
        (f"  [{diff}]", curses.color_pair(C_MUTED)),
    ]
    col = 0
    for text, attr in items:
        safe_addstr(win, hud_row + 1, col, text, attr)
        col += len(text)


# ─── Word Display ─────────────────────────────────────────────────────────────
def draw_word(win, word, typed, row):
    h, w = win.getmaxyx()
    col = max(0, (w - len(word) * 2) // 2)
    for i, ch in enumerate(word):
        if i < len(typed):
            attr = (curses.color_pair(C_CORRECT) | curses.A_BOLD) if typed[i] == ch \
                   else (curses.color_pair(C_WRONG) | curses.A_BOLD)
        else:
            attr = curses.color_pair(C_WHITE) | curses.A_BOLD
        safe_addstr(win, row, col + i * 2, ch.upper(), attr)


# ─── Start Screen ─────────────────────────────────────────────────────────────
def start_screen(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(False)
    diff = "medium"
    diff_order = ["easy", "medium", "hard"]

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        centered(stdscr, 1,  "╔══════════════════════════╗", curses.color_pair(C_AMBER))
        centered(stdscr, 2,  "║      CLUCKY  KEYS        ║", curses.color_pair(C_AMBER) | curses.A_BOLD)
        centered(stdscr, 3,  "╚══════════════════════════╝", curses.color_pair(C_AMBER))
        centered(stdscr, 5,  ">}  Save your chicken from the evil farmer!  >}", curses.color_pair(C_CHICKEN))
        centered(stdscr, 7,  "Type words correctly to RAISE the stone.", curses.color_pair(C_WHITE))
        centered(stdscr, 8,  "Mistakes LOWER it toward your chicken.", curses.color_pair(C_MUTED))
        centered(stdscr, 9,  "Complete all words before time runs out!", curses.color_pair(C_MUTED))

        centered(stdscr, 11, "─── SELECT DIFFICULTY ───", curses.color_pair(C_MUTED))
        labels = {"easy": " EASY ", "medium": " MEDIUM ", "hard": " HARD "}
        diff_line = ""
        for d in diff_order:
            if d == diff:
                diff_line += f"[{labels[d]}]  "
            else:
                diff_line += f" {labels[d]}   "
        centered(stdscr, 13, diff_line.strip(), curses.color_pair(C_AMBER) | curses.A_BOLD)

        centered(stdscr, 15, "← → to change difficulty", curses.color_pair(C_MUTED))
        centered(stdscr, 16, "ENTER to start   Q to quit", curses.color_pair(C_MUTED))

        stdscr.refresh()
        key = stdscr.getch()

        if key in (curses.KEY_RIGHT, ord('d'), ord('D')):
            diff = diff_order[(diff_order.index(diff) + 1) % 3]
        elif key in (curses.KEY_LEFT, ord('a'), ord('A')):
            diff = diff_order[(diff_order.index(diff) - 1) % 3]
        elif key in (ord('\n'), ord('\r'), curses.KEY_ENTER):
            return diff
        elif key in (ord('q'), ord('Q')):
            return None


# ─── End Screen ───────────────────────────────────────────────────────────────
def end_screen(stdscr, won, score, accuracy, words_done, diff):
    curses.curs_set(0)
    stdscr.nodelay(False)

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        if won:
            centered(stdscr, 2, "★  CHICKEN SAVED!  ★", curses.color_pair(C_GREEN) | curses.A_BOLD)
            centered(stdscr, 3, ">}  Your chicken lives to cluck another day!  >}", curses.color_pair(C_CHICKEN))
        else:
            centered(stdscr, 2, "✗  GAME OVER  ✗", curses.color_pair(C_RED) | curses.A_BOLD)
            centered(stdscr, 3, "The farmer got your chicken...", curses.color_pair(C_MUTED))

        centered(stdscr, 5, "─── YOUR RESULTS ───", curses.color_pair(C_MUTED))
        centered(stdscr, 7,  f"Score     : {score}", curses.color_pair(C_AMBER) | curses.A_BOLD)
        centered(stdscr, 8,  f"Accuracy  : {accuracy}%", curses.color_pair(C_GREEN) if accuracy >= 80 else curses.color_pair(C_RED))
        centered(stdscr, 9,  f"Words     : {words_done}", curses.color_pair(C_WHITE))
        centered(stdscr, 10, f"Difficulty: {diff.upper()}", curses.color_pair(C_WHITE))

        grade = "S" if score >= 500 else "A" if score >= 300 else "B" if score >= 150 else "C" if score >= 80 else "D"
        grade_attr = curses.color_pair(C_GREEN) | curses.A_BOLD if grade in ("S","A") else curses.color_pair(C_AMBER) | curses.A_BOLD
        centered(stdscr, 12, f"GRADE: {grade}", grade_attr)

        centered(stdscr, 14, "ENTER to play again   Q to quit", curses.color_pair(C_MUTED))
        stdscr.refresh()

        key = stdscr.getch()
        if key in (ord('\n'), ord('\r'), curses.KEY_ENTER):
            return True
        elif key in (ord('q'), ord('Q')):
            return False


# ─── Main Game Loop ───────────────────────────────────────────────────────────
def run_game(stdscr, diff):
    cfg   = DIFF_CONFIG[diff]
    words = random.sample(WORDS[diff], min(len(WORDS[diff]), 15))

    word_idx  = 0
    # Row 0 = top of screen; lower row number = stone higher up = rope taut = safe.
    # Correct keystrokes decrease stone_row (raise stone); mistakes increase it (lower stone).
    stone_row = 4          # starts near top — rope fully stretched, chicken safe
    STONE_GROUND = SCENE_H - 3   # danger: stone nearly on chicken

    score         = 0
    time_left     = cfg["time"]
    typed         = ""
    total_chars   = 0
    correct_chars = 0
    words_done    = 0
    status_msg    = ""
    status_timer  = 0
    scared        = False
    scared_timer  = 0
    laugh         = False
    laugh_timer   = 0
    danger        = False

    last_tick = time.time()

    curses.curs_set(1)
    stdscr.nodelay(True)

    while True:
        now = time.time()

        # ── Timer tick ──────────────────────────────────────────
        if now - last_tick >= 1.0:
            time_left -= 1
            last_tick  = now
            if time_left <= 0:
                return False, score, (correct_chars * 100 // max(1, total_chars)), words_done

        # ── Decay temp states ────────────────────────────────────
        if scared_timer and now > scared_timer:
            scared = False; scared_timer = 0
        if laugh_timer and now > laugh_timer:
            laugh = False; laugh_timer = 0
        if status_timer and now > status_timer:
            status_msg = ""; status_timer = 0

        # ── Input ────────────────────────────────────────────────
        key = stdscr.getch()
        if key == curses.ERR:
            pass
        elif key in (ord('q'), ord('Q')) and not typed:
            return False, score, (correct_chars * 100 // max(1, total_chars)), words_done
        elif key in (curses.KEY_BACKSPACE, 127, 8):
            typed = typed[:-1]
        elif key == 27:   # ESC clears
            typed = ""
        elif 32 <= key <= 126:
            ch = chr(key)
            word = words[word_idx]
            pos  = len(typed)
            total_chars += 1
            if pos < len(word) and ch == word[pos]:
                correct_chars += 1
                typed += ch
                # Raise stone (stone_row decreases = moves up = good)
                stone_row = max(STONE_MIN, stone_row - (cfg["reward"] // 10))
            else:
                # Wrong key — lower stone
                stone_row = min(STONE_GROUND, stone_row + (cfg["penalty"] // 8))
                scared = True;  scared_timer = now + 0.4
                laugh  = True;  laugh_timer  = now + 0.5
                # Don't append wrong character — just penalize

            # Check word complete
            if typed == word:
                words_done += 1
                bonus = time_left * 2 + len(word) * 3
                score += cfg["points_base"] + bonus
                stone_row = max(STONE_MIN, stone_row - (cfg["reward"] // 5))
                status_msg   = random.choice(PRAISE)
                status_timer = now + 1.0
                typed        = ""
                word_idx    += 1
                if word_idx >= len(words):
                    return True, score, (correct_chars * 100 // max(1, total_chars)), words_done

        # ── Win/lose checks ──────────────────────────────────────
        danger = stone_row >= STONE_GROUND - 1
        if stone_row >= STONE_GROUND:
            return False, score, (correct_chars * 100 // max(1, total_chars)), words_done

        # ── Draw ─────────────────────────────────────────────────
        stdscr.erase()
        h, w = stdscr.getmaxyx()

        draw_scene(stdscr, stone_row, danger, scared, laugh)

        # HUD
        accuracy = correct_chars * 100 // max(1, total_chars)
        draw_hud(stdscr, score, time_left, words_done, len(words), accuracy, cfg["label"])

        # Word display
        word_row = SCENE_H + 3
        word = words[word_idx]
        centered(stdscr, word_row, "─" * min(40, w - 2), curses.color_pair(C_MUTED))
        draw_word(stdscr, word, typed, word_row + 1)

        # Input echo
        inp_row = word_row + 3
        input_label = "TYPE > "
        _, W = stdscr.getmaxyx()
        inp_x = max(0, (W - 30) // 2)
        safe_addstr(stdscr, inp_row, inp_x, input_label, curses.color_pair(C_AMBER))
        safe_addstr(stdscr, inp_row, inp_x + len(input_label), typed + "_",
                    curses.color_pair(C_WHITE) | curses.A_BOLD)

        # Status message
        if status_msg:
            centered(stdscr, inp_row + 1, status_msg, curses.color_pair(C_GREEN) | curses.A_BOLD)

        # Hint
        centered(stdscr, h - 1, "BACKSPACE to erase  |  Q to quit", curses.color_pair(C_MUTED))

        # Cursor
        cursor_x = min(inp_x + len(input_label) + len(typed), W - 2)
        try:
            stdscr.move(inp_row, cursor_x)
        except curses.error:
            pass

        stdscr.refresh()
        time.sleep(0.03)   # ~30 fps


# ─── Entry Point ──────────────────────────────────────────────────────────────
def main(stdscr):
    init_colors()

    while True:
        diff = start_screen(stdscr)
        if diff is None:
            break

        won, score, accuracy, words_done = run_game(stdscr, diff)

        play_again = end_screen(stdscr, won, score, accuracy, words_done, diff)
        if not play_again:
            break


def entry():
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
    print("\nThanks for playing Clucky Keys! 🐔\n")


if __name__ == "__main__":
    if sys.version_info < (3, 6):
        print("Python 3.6+ required.")
        sys.exit(1)
    entry()
