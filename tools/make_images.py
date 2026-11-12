#!/usr/bin/env python3
"""Draws the organisation README's pictures as SVG, light and dark in one file.

    python3 tools/make_images.py profile/images
"""
import sys
from xml.sax.saxutils import escape

OUT = sys.argv[1]

STYLE = """<style>
:root {
  --fg:#1f2328; --muted:#59636e; --card:#f6f8fa; --line:#d0d7de; --bg:#ffffff;
  --prog:#6c5ce7; --prog-soft:#f0eefe;
  --kern:#0e9384; --kern-soft:#e6f6f4;
  --vm:#d9692a; --vm-soft:#fdf0e8;
  --board:#2f6fdf; --board-soft:#eaf1fd;
  --stop:#d1242f;
}
@media (prefers-color-scheme: dark) {
  :root {
    --fg:#e6edf3; --muted:#9198a1; --card:#161b22; --line:#30363d; --bg:#0d1117;
    --prog:#a29bfe; --prog-soft:#1f1b3a;
    --kern:#3ec9b6; --kern-soft:#0f2a27;
    --vm:#f39a5c; --vm-soft:#33200f;
    --board:#6ea2ff; --board-soft:#132440;
    --stop:#ff7b72;
  }
}
text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; fill: var(--fg); }
.muted { fill: var(--muted); }
.mono { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
</style>"""


def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{escape(title)}">\n<title>{escape(title)}</title>\n{STYLE}\n{body}\n</svg>\n')


def text(x, y, s, size=18, weight=400, anchor="start", cls="", fill=None, extra=""):
    f = f' style="fill:var(--{fill})"' if fill else ""
    c = f' class="{cls}"' if cls else ""
    return (f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}"{c}{f}{extra}>'
            f'{escape(s)}</text>')


def rect(x, y, w, h, r=12, fill="card", stroke="line", sw=1.5, extra=""):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" '
            f'style="fill:var(--{fill});stroke:var(--{stroke})" stroke-width="{sw}"{extra}/>')


def arrow(x1, y1, x2, y2, color="muted", sw=2.5):
    """A line with a head at (x2, y2)."""
    import math
    a = math.atan2(y2 - y1, x2 - x1)
    hx1, hy1 = x2 - 12 * math.cos(a - 0.45), y2 - 12 * math.sin(a - 0.45)
    hx2, hy2 = x2 - 12 * math.cos(a + 0.45), y2 - 12 * math.sin(a + 0.45)
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" style="stroke:var(--{color})" '
            f'stroke-width="{sw}" stroke-linecap="round"/>'
            f'<path d="M{hx1:.1f},{hy1:.1f} L{x2:.1f},{y2:.1f} L{hx2:.1f},{hy2:.1f}" '
            f'style="fill:none;stroke:var(--{color})" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>')


# ---- devices, small icons ---------------------------------------------------

def chip_icon(cx, cy, s, color):
    """A microcontroller: a square with pins on all sides."""
    out = [rect(cx - s / 2, cy - s / 2, s, s, 8, f"{color}-soft", color, 2.5)]
    n = 4
    for i in range(n):
        p = cx - s / 2 + s * (i + 1) / (n + 1)
        q = cy - s / 2 + s * (i + 1) / (n + 1)
        for x1, y1, x2, y2 in ((p, cy - s / 2, p, cy - s / 2 - 10), (p, cy + s / 2, p, cy + s / 2 + 10),
                               (cx - s / 2, q, cx - s / 2 - 10, q), (cx + s / 2, q, cx + s / 2 + 10, q)):
            out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                       f'style="stroke:var(--{color})" stroke-width="3" stroke-linecap="round"/>')
    out.append(rect(cx - s / 4, cy - s / 4, s / 2, s / 2, 4, color, color, 0))
    return "".join(out)


def board_icon(cx, cy, w, h, color):
    """A small board: a long rectangle with a header row and a chip."""
    out = [rect(cx - w / 2, cy - h / 2, w, h, 8, f"{color}-soft", color, 2.5)]
    for i in range(8):
        x = cx - w / 2 + 14 + i * (w - 28) / 7
        out.append(f'<circle cx="{x:.1f}" cy="{cy - h / 2 + 12:.1f}" r="3.2" style="fill:var(--{color})"/>')
        out.append(f'<circle cx="{x:.1f}" cy="{cy + h / 2 - 12:.1f}" r="3.2" style="fill:var(--{color})"/>')
    out.append(rect(cx - 16, cy - 12, 32, 24, 4, color, color, 0))
    out.append(rect(cx + w / 2 - 18, cy - 8, 12, 16, 3, "card", color, 2))
    return "".join(out)


def browser_icon(cx, cy, w, h, color):
    out = [rect(cx - w / 2, cy - h / 2, w, h, 10, f"{color}-soft", color, 2.5)]
    out.append(f'<line x1="{cx - w / 2}" y1="{cy - h / 2 + 22}" x2="{cx + w / 2}" y2="{cy - h / 2 + 22}" '
               f'style="stroke:var(--{color})" stroke-width="2"/>')
    for i in range(3):
        out.append(f'<circle cx="{cx - w / 2 + 14 + i * 13}" cy="{cy - h / 2 + 11}" r="3.5" style="fill:var(--{color})"/>')
    # a tiny scheduler trace in the window
    y0 = cy + 6
    pts = [(0, 0), (12, 0), (12, -14), (30, -14), (30, 0), (44, 0), (44, -14), (58, -14), (58, 0), (78, 0)]
    d = " ".join(f"{'M' if i == 0 else 'L'}{cx - 39 + x},{y0 + y}" for i, (x, y) in enumerate(pts))
    out.append(f'<path d="{d}" style="fill:none;stroke:var(--{color})" stroke-width="2.5" stroke-linejoin="round"/>')
    return "".join(out)


def wasm_file(cx, cy, w, h):
    """A document with a folded corner and '.wasm'."""
    x, y = cx - w / 2, cy - h / 2
    f = 22
    d = f"M{x + 10},{y} L{x + w - f},{y} L{x + w},{y + f} L{x + w},{y + h - 10} Q{x + w},{y + h} {x + w - 10},{y + h} " \
        f"L{x + 10},{y + h} Q{x},{y + h} {x},{y + h - 10} L{x},{y + 10} Q{x},{y} {x + 10},{y} Z"
    out = [f'<path d="{d}" style="fill:var(--prog-soft);stroke:var(--prog)" stroke-width="2.5"/>',
           f'<path d="M{x + w - f},{y} L{x + w - f},{y + f} L{x + w},{y + f}" style="fill:none;stroke:var(--prog)" stroke-width="2.5"/>',
           text(cx, cy + 8, ".wasm", 22, 700, "middle", "mono", "prog")]
    return "".join(out)


# ---- 1. header --------------------------------------------------------------

def header():
    W, H = 1200, 320
    b = []
    b.append(text(48, 130, "wasm-rtos", 72, 800))
    b.append(text(50, 182, "An operating system for microcontrollers", 26, 500))
    b.append(text(50, 216, "that runs WebAssembly programs like executables.", 26, 500))
    b.append(text(50, 262, "One .wasm file: on a chip, on a board, in the browser.", 19, 400, cls="muted"))
    fx, fy = 760, 160
    b.append(wasm_file(fx, fy, 96, 120))
    targets = [(1050, 62, "ESP32", "chip", 36), (1050, 160, "STM32", "board", 48), (1050, 258, "browser", "browser", 50)]
    for tx, ty, label, kind, half in targets:
        b.append(arrow(fx + 58, fy + (ty - fy) * 0.15, tx - 50 - half - 14, ty, "muted", 2.5))
        if kind == "chip":
            b.append(chip_icon(tx - 50, ty, 52, "board"))
        elif kind == "board":
            b.append(board_icon(tx - 50, ty, 96, 50, "board"))
        else:
            b.append(browser_icon(tx - 50, ty, 100, 64, "board"))
        b.append(text(tx + 12, ty + 7, label, 20, 600))
    return svg(W, H, "\n".join(b), "wasm-rtos: one .wasm file runs on an ESP32, an STM32 and in the browser")


# ---- 2. architecture --------------------------------------------------------

def chip_box(x, y, w, h, title, sub, color):
    return "".join([rect(x, y, w, h, 10, "card", color, 1.8),
                    text(x + 16, y + 28, title, 19, 650),
                    text(x + 16, y + 52, sub, 15.5, 400, cls="muted")])


def band(y, h, color, name, repo, items, cols):
    out = [rect(20, y, 1160, h, 16, f"{color}-soft", color, 2)]
    out.append(text(44, y + 46, name, 24, 750, fill=color))
    out.append(text(44, y + 74, repo, 16, 500, cls="muted mono"))
    x0, x1 = 250, 1160
    gap = 16
    rows = (len(items) + cols - 1) // cols
    cw = (x1 - x0 - gap * (cols - 1)) / cols
    ch = 66
    top = y + (h - rows * ch - (rows - 1) * gap) / 2
    for i, (t, s) in enumerate(items):
        r, c = divmod(i, cols)
        out.append(chip_box(x0 + c * (cw + gap), top + r * (ch + gap), cw, ch, t, s, color))
    return "".join(out)


def architecture():
    W = 1200
    b = []
    y = 16
    layers = [
        ("prog", "Programs", ".wasm files", [("C / C++ with WASI", "printf, files, clocks, arguments"),
                                             ("Arduino sketches", "setup(), loop(), Serial, Wire, SPI"),
                                             ("Other languages", "anything that compiles to Wasm")], 3, 110,
         "imports: WASI and the wasm-rtos ABI 1.8"),
        ("kern", "Kernel", "wasm-rtos", [("Scheduler", "priorities, slices of fuel"),
                                         ("Sync objects", "queues, mutexes, events, timers"),
                                         ("Processes", "spawn, wait, kill, argv, files"),
                                         ("Drivers", "GPIO, display, buses, PWM, UART"),
                                         ("Memory policy", "RAM budget, page store, swap"),
                                         ("Snapshots", "save a task, continue elsewhere")], 3, 196,
         "runs slices, links imports, moves frames"),
        ("vm", "Interpreter", "wasm-rtos-vm", [("Fuel", "every instruction counted"),
                                               ("MMU", "frames, TLB, pager"),
                                               ("Code cache", "records made on first call"),
                                               ("Snapshots", "positions in the module")], 4, 110,
         "a clock and device ports"),
        ("board", "Board", "or the browser", [("ESP32, STM32, ...", "clock, GPIO, buses, DMA"),
                                              ("Storage", "SD card, SPI RAM, FRAM, flash"),
                                              ("Simulator", "the same kernel in WebAssembly")], 3, 110, None),
    ]
    for color, name, repo, items, cols, h, link in layers:
        b.append(band(y, h, color, name, repo, items, cols))
        y += h
        if link:
            b.append(arrow(600, y + 6, 600, y + 50, "muted", 3))
            b.append(text(622, y + 35, link, 17, 500, cls="muted"))
            y += 56
    return svg(W, y + 16, "\n".join(b), "How programs, the kernel, the interpreter and the board fit together")


# ---- 3. fuel and snapshots --------------------------------------------------

def fuel():
    W, H = 1200, 420
    b = []
    ops = ["local.get", "i32.load", "i32.const", "i32.add", "i32.store", "br_if", "call", "local.set"]
    x0, tw, gap, ty = 40, 128, 12, 70
    stop_after = 4  # fuel runs out after the 5th instruction
    b.append(text(40, 34, "fuel left", 16, 500, cls="muted"))
    for i, op in enumerate(ops):
        x = x0 + i * (tw + gap)
        done = i <= stop_after
        fill, stroke = ("vm-soft", "vm") if done else ("card", "line")
        b.append(rect(x, ty, tw, 58, 10, fill, stroke, 2))
        b.append(text(x + tw / 2, ty + 36, op, 18, 600, "middle", "mono", None if done else "muted"))
        if done:
            b.append(text(x + tw / 2, ty - 14, str(stop_after - i), 18, 700, "middle", fill="vm"))
    sx = x0 + (stop_after + 1) * (tw + gap) - gap / 2
    b.append(f'<line x1="{sx}" y1="{ty - 34}" x2="{sx}" y2="{ty + 84}" style="stroke:var(--stop)" stroke-width="4" stroke-linecap="round"/>')
    b.append(text(sx + 12, ty + 106, "stops here: fuel 0, between two instructions", 17, 600, fill="stop"))
    # the snapshot and where it goes
    cy = 300
    b.append(arrow(sx, ty + 118, 560, cy - 54, "muted", 2.5))
    b.append(rect(300, cy - 50, 520, 118, 14, "card", "vm", 2))
    b.append(text(324, cy - 18, "snapshot", 20, 700, fill="vm"))
    b.append(text(324, cy + 12, "function 12, instruction at 0x3f4", 17, 500, cls="mono"))
    b.append(text(324, cy + 40, "value stack, calls, globals, memory", 17, 500, cls="mono muted"))
    b.append(chip_icon(150, cy + 8, 60, "board"))
    b.append(text(150, cy + 84, "ESP32", 17, 600, "middle"))
    b.append(arrow(200, cy + 8, 296, cy + 8, "muted", 2.5))
    b.append(arrow(824, cy + 8, 950, cy + 8, "muted", 2.5))
    b.append(browser_icon(1030, cy + 8, 120, 80, "board"))
    b.append(text(1030, cy + 84, "goes on in the browser", 17, 600, "middle"))
    return svg(W, H, "\n".join(b), "Fuel counts every instruction; a stopped program is a portable snapshot")


# ---- 4. memory --------------------------------------------------------------

def memory():
    W, H = 1200, 470
    b = []
    # left: paged memory
    b.append(text(40, 40, "A program's memory, in frames of 4 KiB", 20, 700))
    states = "RRSRZZSRRZSZ"  # R in RAM, S in storage, Z never touched
    fw, fg, fy = 40, 8, 64
    for i, s in enumerate(states):
        x = 40 + i * (fw + fg)
        if s == "R":
            b.append(rect(x, fy, fw, fw, 6, "vm", "vm", 0))
        elif s == "S":
            b.append(rect(x, fy, fw, fw, 6, "board-soft", "board", 2))
        else:
            b.append(rect(x, fy, fw, fw, 6, "card", "line", 1.5, ' stroke-dasharray="5 4"'))
    lx = 40
    for fill, stroke, dash, label in (("vm", "vm", "", "in RAM"), ("board-soft", "board", "", "in the page store"),
                                      ("card", "line", ' stroke-dasharray="4 3"', "never touched: costs nothing")):
        b.append(rect(lx, 128, 18, 18, 4, fill, stroke, 1.8, dash))
        b.append(text(lx + 26, 143, label, 15.5, 500, cls="muted"))
        lx += 26 + len(label) * 8.2 + 26
    # RAM and store
    b.append(rect(40, 178, 250, 150, 14, "vm-soft", "vm", 2))
    b.append(text(60, 212, "RAM", 20, 700, fill="vm"))
    b.append(text(60, 240, "a budget of frames;", 16, 500, cls="muted"))
    b.append(text(60, 262, "a TLB finds them", 16, 500, cls="muted"))
    for i in range(5):
        b.append(rect(60 + i * 42, 280, 34, 30, 5, "vm", "vm", 0))
    b.append(rect(330, 178, 250, 150, 14, "board-soft", "board", 2))
    b.append(text(350, 212, "Page store", 20, 700, fill="board"))
    b.append(text(350, 240, "SD card, SPI RAM,", 16, 500, cls="muted"))
    b.append(text(350, 262, "FRAM or flash", 16, 500, cls="muted"))
    b.append(f'<rect x="350" y="280" width="54" height="34" rx="5" style="fill:var(--card);stroke:var(--board)" stroke-width="2"/>')
    b.append(f'<path d="M350,292 L362,280" style="stroke:var(--board)" stroke-width="2"/>')
    b.append(arrow(292, 226, 326, 226, "muted", 2.2))
    b.append(arrow(326, 282, 292, 282, "muted", 2.2))
    b.append(text(40, 368, "Touched: the frame comes in, the program waits, others run.", 16, 500, cls="muted"))
    b.append(text(40, 392, "Out of room: one not touched lately goes;", 16, 500, cls="muted"))
    b.append(text(40, 416, "only a written (dirty) frame is stored again.", 16, 500, cls="muted"))
    # right: code cache
    b.append(f'<line x1="620" y1="30" x2="620" y2="440" style="stroke:var(--line)" stroke-width="1.5"/>')
    b.append(text(660, 40, "Code as a cache", 20, 700))
    funcs = [("main", "on the stack: kept", 190, "kern"), ("crc16", "records", 140, "vm"),
             ("list_find", "records", 170, "vm"), ("matrix_mul", "records", 115, "vm"),
             ("printf", "never called: no records", 0, "line"), ("setup_uart", "dropped, made again if called", 0, "line")]
    for i, (name, note, w, color) in enumerate(funcs):
        y = 70 + i * 58
        b.append(text(660, y + 27, name, 17, 600, cls="mono"))
        if w:
            b.append(rect(800, y + 6, w, 30, 6, f"{color}-soft" if color != "kern" else "kern-soft", color, 2))
        else:
            b.append(rect(800, y + 6, 70, 30, 6, "card", "line", 1.5, ' stroke-dasharray="5 4"'))
        b.append(text(800 + (w if w else 70) + 12, y + 27, note, 15.5, 500, cls="muted"))
    b.append(text(660, 438, "Memory comes first: records go when a frame needs the room.", 16, 500, cls="muted"))
    return svg(W, H, "\n".join(b), "Paged memory with a page store, and predecoded code kept as a cache")


# ---- 5. numbers -------------------------------------------------------------

def numbers():
    W, H = 1200, 220
    cards = [("18", "programs at once", "ESP32, 280 KB of heap", "vm"),
             ("9", "programs at once", "STM32, 128 KB of RAM", "kern"),
             ("34.7 KB", "the whole interpreter", "on an Arduino Uno", "prog"),
             ("27 437", "spec checks passed", "WebAssembly 2.0", "board")]
    b = []
    cw, gap = 276, 18
    for i, (num, l1, l2, color) in enumerate(cards):
        x = 20 + i * (cw + gap)
        b.append(rect(x, 16, cw, 188, 16, f"{color}-soft", color, 2))
        b.append(text(x + 24, 98, num, 54, 800, fill=color))
        b.append(text(x + 24, 140, l1, 19, 650))
        b.append(text(x + 24, 168, l2, 16, 500, cls="muted"))
    return svg(W, H, "\n".join(b), "18 programs on an ESP32, 9 on an STM32, a 34.7 KB interpreter, 27437 spec checks")


# ---- 6. timeline ------------------------------------------------------------

def timeline():
    W, H = 1200, 400
    items = [("Jul 2026", "Kernel starts", ["objects, queues, timers,", "tickless clock"], "kern"),
             ("Aug 2026", "Libraries", ["shared Wasm libraries,", "programs loaded at run time"], "kern"),
             ("Oct 31", "Processes and files", ["spawn, wait, kill;", "a virtual file system"], "kern"),
             ("Nov 1–2", "ABI 1.0 and devices", ["GPIO, display, buses, PWM,", "UART, Arduino core, snapshots"], "prog"),
             ("Nov 7", "On a real ESP32", ["ABI 1.8: 1-Wire, counters,", "analog outputs"], "prog"),
             ("Nov 9", "Own interpreter", ["wasm-rtos-vm, packed records,", "pluggable drivers"], "vm"),
             ("Nov 11", "MMU", ["paging, TLB, page store,", "swap in the background"], "vm"),
             ("Nov 12", "Code cache and CI", ["+50% programs at once;", "every configuration checked"], "board")]
    b = []
    y = H / 2
    x0, x1 = 150, 1050
    b.append(f'<line x1="{x0 - 40}" y1="{y}" x2="{x1 + 40}" y2="{y}" style="stroke:var(--line)" stroke-width="4" stroke-linecap="round"/>')
    step = (x1 - x0) / (len(items) - 1)
    for i, (date, title, lines, color) in enumerate(items):
        x = x0 + i * step
        up = i % 2 == 0
        stem_end = y - 40 if up else y + 40
        b.append(f'<line x1="{x}" y1="{y}" x2="{x}" y2="{stem_end}" style="stroke:var(--{color})" stroke-width="2.5"/>')
        b.append(f'<circle cx="{x}" cy="{y}" r="11" style="fill:var(--bg);stroke:var(--{color})" stroke-width="4"/>')
        b.append(f'<circle cx="{x}" cy="{y}" r="4.5" style="fill:var(--{color})"/>')
        if up:
            ty = y - 52 - 22 * (len(lines) + 1)
        else:
            ty = y + 70
        b.append(text(x, ty, date, 16, 700, "middle", fill=color))
        b.append(text(x, ty + 24, title, 18, 700, "middle"))
        for k, l in enumerate(lines):
            b.append(text(x, ty + 48 + k * 21, l, 14.5, 500, "middle", "muted"))
    return svg(W, H, "\n".join(b), "Timeline of wasm-rtos from July to November 2026")


for name, fn in (("header", header), ("architecture", architecture), ("fuel", fuel), ("memory", memory),
                 ("numbers", numbers), ("timeline", timeline)):
    with open(f"{OUT}/{name}.svg", "w") as f:
        f.write(fn())
print("ok")
