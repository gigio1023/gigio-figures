#!/usr/bin/env python3
"""Emit projection.svg: exact geometry of projecting x onto a unit direction r_hat and its complement.

Every canvas coordinate comes from the example vectors below through one scale for both axes (1:1).
Run: python3 projection.py  (writes projection.svg beside this file)
"""
from pathlib import Path

X = (3.0, 2.0)          # the vector
R_HAT = (1.0, 0.0)      # unit direction, aligned with the canvas x axis
S = 88                  # u per data unit, both axes
ORIGIN = (184, 256)     # canvas position of (0, 0)
EQ_X = 512              # equation column

dot = X[0] * R_HAT[0] + X[1] * R_HAT[1]                 # r_hat^T x
PROJ = (dot * R_HAT[0], dot * R_HAT[1])                  # (r_hat^T x) r_hat
REST = (X[0] - PROJ[0], X[1] - PROJ[1])                  # x - (r_hat^T x) r_hat
assert abs(REST[0] * R_HAT[0] + REST[1] * R_HAT[1]) < 1e-12   # orthogonal to r_hat


def c(p):
    """Data point -> canvas point (y up in data, down on canvas)."""
    return (ORIGIN[0] + S * p[0], ORIGIN[1] - S * p[1])


def f(v):
    return f"{round(v, 2):g}"


o = c((0, 0))
x_tip, p_tip, r_tip = c(X), c(PROJ), c(R_HAT)
rest_tip = c(REST)
OFF = 10                 # r_hat drawn this far below its own projection so its tip reads as a vector
AX_PAD = 36              # axes run this far past the data
TICK = 5
MARK = 12                # right-angle mark side

tex_proj = r"(\hat r^\top x)\,\hat r"
tex_rest = r"x - (\hat r^\top x)\,\hat r"
out = []
# axes: span(r_hat) horizontal, its orthogonal complement vertical
out.append('  <g data-id="axes">')
out.append(f'    <path class="guide" d="M{f(o[0] - 24)} {f(o[1])}H{f(c((X[0], 0))[0] + AX_PAD)}"/>')
out.append(f'    <path class="guide" d="M{f(o[0])} {f(o[1] + 24)}V{f(c((0, X[1]))[1] - AX_PAD)}"/>')
for k in range(1, int(X[0]) + 1):
    tx = c((k, 0))[0]
    out.append(f'    <path class="guide" d="M{f(tx)} {f(o[1] - TICK)}V{f(o[1] + TICK)}"/>')
for k in range(1, int(X[1]) + 1):
    ty = c((0, k))[1]
    out.append(f'    <path class="guide" d="M{f(o[0] - TICK)} {f(ty)}H{f(o[0] + TICK)}"/>')
out.append(f'    <text class="ta" x="{f(c((X[0], 0))[0] + AX_PAD + 6)}" y="{f(o[1])}" dominant-baseline="central" '
           f'data-tex="\\mathrm{{span}}(\\hat r)">span(r)</text>')
out.append(f'    <text class="ta" x="{f(o[0])}" y="{f(c((0, X[1]))[1] - AX_PAD - 12)}" text-anchor="middle" '
           f'dominant-baseline="central" data-tex="\\hat r^{{\\perp}}">r perp</text>')
out.append('  </g>')

# components of x: dotted, no arrowheads, closing the rectangle
out.append('  <g data-id="components">')
out.append(f'    <path class="leader" d="M{f(x_tip[0])} {f(x_tip[1])}V{f(p_tip[1])}"/>')
out.append(f'    <path class="leader" d="M{f(x_tip[0])} {f(x_tip[1])}H{f(rest_tip[0])}"/>')
out.append('  </g>')
# right angle where x - p meets span(r_hat), on the far side of the drop so it clears p's arrowhead
out.append(f'  <path class="mark" data-id="right-angle" d="M{f(p_tip[0] + MARK)} {f(p_tip[1])}V{f(p_tip[1] - MARK)}H{f(p_tip[0])}"/>')

# remainder in the complement (neutral ink)
out.append('  <g data-id="rest">')
out.append(f'    <path class="edge" d="M{f(o[0])} {f(o[1])}V{f(rest_tip[1])}" data-arrow="end"/>')
out.append(f'    <text class="tl" x="{f(o[0] - 12)}" y="{f(c((0, 1.5))[1])}" text-anchor="end" '
           f'dominant-baseline="central" data-tex="{tex_rest}">x - (r^T x) r</text>')
out.append('  </g>')
# x itself
out.append('  <g data-id="x">')
out.append(f'    <path class="edge" d="M{f(o[0])} {f(o[1])}L{f(x_tip[0])} {f(x_tip[1])}" data-arrow="end"/>')
out.append(f'    <text class="t" x="{f(x_tip[0] + 10)}" y="{f(x_tip[1] - 8)}" dominant-baseline="central" data-tex="x">x</text>')
out.append('  </g>')
# projection onto r_hat (magenta: lies along r_hat)
out.append('  <g data-id="proj">')
out.append(f'    <path class="edge emph magenta" d="M{f(o[0])} {f(o[1])}H{f(p_tip[0])}" data-arrow="end"/>')
out.append(f'    <text class="tl magenta" x="{f(c((2.25, 0))[0])}" y="{f(o[1] + 19)}" text-anchor="middle" '
           f'dominant-baseline="central" data-tex="{tex_proj}">(r^T x) r</text>')
out.append('  </g>')
# the unit direction, offset below its projection
out.append('  <g data-id="r-hat">')
out.append(f'    <path class="edge emph magenta" d="M{f(o[0])} {f(o[1] + OFF)}H{f(r_tip[0])}" data-arrow="end"/>')
out.append(f'    <text class="t magenta" x="{f(c((0.5, 0))[0])}" y="{f(o[1] + OFF + 16)}" text-anchor="middle" '
           f'dominant-baseline="central" data-tex="\\hat r">r</text>')
out.append('  </g>')

# equations with the example's values, aligned in one column
eq = [
    ("eq-values", "t2", rf"x = ({f(X[0])},\,{f(X[1])}),\quad \hat r = ({f(R_HAT[0])},\,{f(R_HAT[1])})"),
    ("eq-proj", "t2 magenta", rf"{tex_proj} = ({f(PROJ[0])},\,{f(PROJ[1])})"),
    ("eq-rest", "t2", rf"{tex_rest} = ({f(REST[0])},\,{f(REST[1])}) \perp \hat r"),
]
top = c((0, X[1]))[1] + 8
for i, (did, cls, tex) in enumerate(eq):
    out.append(f'  <text class="{cls}" data-id="{did}" x="{EQ_X}" y="{f(top + i * 32)}" dominant-baseline="central" '
               f'data-tex="{tex}">{did}</text>')

H = o[1] + OFF + 16 + 24
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 {f(H)}" data-figure="technical-figure">',
       f'  <!-- Generated by projection.py from x = {X}, r_hat = {R_HAT}, {S}u per unit; edit the script, not this file. -->',
       *out, '</svg>', '']
Path(__file__).with_name("projection.svg").write_text("\n".join(svg))
print(f"wrote projection.svg (720x{f(H)}u): r^T x = {dot:g}, proj = {PROJ}, rest = {REST}")
