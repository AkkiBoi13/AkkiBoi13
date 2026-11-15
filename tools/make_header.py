"""Draw assets/header.svg: the name as a glyph matrix, with bubble-chamber tracks.

Run: python tools/make_header.py
"""
import math
import pathlib

FONT = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "G": ["01110", "10001", "10000", "10111", "10001", "10001", "01111"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "01010", "01010", "00100"],
    "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    " ": ["00000"] * 7,
}

W, H = 960, 330
PITCH = 12.5
R_ON, R_OFF = 4.4, 1.6
LINES = ["AKSHAY", "RAGHUVANSHI"]
COLS = 6 * max(len(s) for s in LINES) - 1  # widest line sets the grid
X0 = (W - (COLS - 1) * PITCH) / 2
Y0 = 46


def lit(line: str) -> set[tuple[int, int]]:
    on = set()
    start = (COLS - (6 * len(line) - 1)) // 2
    for i, ch in enumerate(line):
        for r, row in enumerate(FONT[ch]):
            for c, bit in enumerate(row):
                if bit == "1":
                    on.add((r, start + 6 * i + c))
    return on


def spiral(cx, cy, a, b, turns, start, sign=1, steps=220):
    """A charged track losing energy in a magnetic field: an inward spiral."""
    pts = []
    for k in range(steps + 1):
        t = start + k / steps * turns * 2 * math.pi
        rad = a * math.exp(-b * (t - start))
        pts.append((cx + rad * math.cos(sign * t), cy + rad * math.sin(sign * t)))
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)


out = [
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Akshay Raghuvanshi">',
    "<style>",
    ".off{fill:#1c1c1c}",
    ".on{fill:#f5f5f5;opacity:.12;animation:on .5s ease-out forwards,shimmer 7s ease-in-out 3s infinite}",
    "@keyframes on{to{opacity:1}}",
    "@keyframes shimmer{0%,100%{opacity:1}50%{opacity:.55}}",
    ".trk{fill:none;stroke:#f5f5f5;stroke-width:1.2;stroke-linecap:round;opacity:.55;stroke-dasharray:1400;stroke-dashoffset:1400;animation:draw 2.8s ease-out forwards}",
    ".trk.faint{opacity:.28;stroke-width:1}",
    "@keyframes draw{to{stroke-dashoffset:0}}",
    ".txt{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;fill:#9a9a9a;font-size:15px;letter-spacing:.18em;opacity:0;animation:on 1s ease-out 2.2s forwards}",
    ".red{fill:#ff3b30}",
    "@media (prefers-reduced-motion:reduce){.on,.trk,.txt{animation:none;opacity:1;stroke-dashoffset:0}}",
    "</style>",
    f'<rect width="{W}" height="{H}" rx="18" fill="#000"/>',
]

# Bubble-chamber tracks: a pair of opposite spirals from one vertex (pair
# production) under the name, and a few long, nearly straight tracks.
vx, vy = 112, 296
out += [
    f'<path class="trk" style="animation-delay:.4s" d="{spiral(vx + 24, vy - 12, 26, 0.18, 2.6, math.pi * 0.85, 1)}"/>',
    f'<path class="trk" style="animation-delay:.4s" d="{spiral(vx - 22, vy - 14, 25, 0.19, 2.5, math.pi * 0.1, -1)}"/>',
    f'<path class="trk faint" style="animation-delay:.1s" d="M0,{vy + 6} Q{vx * 0.6:.0f},{vy + 4} {vx},{vy}"/>',
    f'<path class="trk faint" style="animation-delay:.9s" d="M{W},{H - 70} Q{W * 0.7:.0f},{H - 40} {W * 0.45:.0f},{H}"/>',
    f'<path class="trk" style="animation-delay:1.2s" d="{spiral(W - 120, 70, 34, 0.2, 2.2, 0, 1)}"/>',
]

for li, line in enumerate(LINES):
    on = lit(line)
    top = Y0 + li * (7 * PITCH + 26)
    for r in range(7):
        for c in range(COLS):
            x, y = X0 + c * PITCH, top + r * PITCH
            if (r, c) in on:
                delay = 0.25 + c * 0.022 + li * 0.35
                out.append(f'<circle class="on" cx="{x:.1f}" cy="{y:.1f}" r="{R_ON}" style="animation-delay:{delay:.2f}s"/>')
            else:
                out.append(f'<circle class="off" cx="{x:.1f}" cy="{y:.1f}" r="{R_OFF}"/>')

ty = Y0 + 2 * (7 * PITCH + 26) + 14
out.append(f'<text class="txt" x="{W / 2}" y="{ty}" text-anchor="middle">AI TRAINING DATA · PHYSICS · TEACHING</text>')
# One red dot, like the recording light on a Nothing phone's glyph matrix.
out.append(f'<circle class="red" cx="{W - 34}" cy="30" r="5"><animate attributeName="opacity" values="1;.2;1" dur="2s" repeatCount="indefinite"/></circle>')
out.append("</svg>")

path = pathlib.Path(__file__).resolve().parent.parent / "assets" / "header.svg"
path.parent.mkdir(exist_ok=True)
path.write_text("\n".join(out), encoding="utf-8", newline="\n")
print(path, path.stat().st_size, "bytes")
