"""Gives the contribution snake (from Platane/snk) a title plate and caption
that match the rest of the README (see theme.py), without a panel around it.
Run by .github/workflows/profile-assets.yml after the snake is generated.

Usage: python frame_snake.py <snake.svg> <out.svg>
"""
import re
import sys

from theme import MONO, PAD, SAGE, TEXT_DIM, plate, shadow_filter, svg


def main():
    src, out = sys.argv[1], sys.argv[2]
    with open(src, encoding='utf-8') as f:
        snake = f.read()
    vb = re.search(r'viewBox="([^"]+)"', snake).group(1)
    vx, vy, vw, vh = (float(v) for v in vb.split())
    inner = re.sub(r'^.*?<svg[^>]*>|</svg>\s*$', '', snake, flags=re.S)

    # snk leaves a 16px margin round the grid and room under it that the snake never uses; trim
    # both so the grid lines up with the panels' edges and the caption sits close.
    vx, vw, vh = vx + 14, vw - 28, vh - 36
    vb = f'{vx:g} {vy:g} {vw:g} {vh:g}'
    W = 1000
    h = vh * W / vw
    title, _ = plate('eating my contributions', 'SNAKE.EXE', SAGE)
    top = 70
    H = round(top + h + 18 + PAD)
    body = f'''<defs>{shadow_filter('soft', 6, 6, 0.35)}</defs>
<g filter="url(#soft)">{title}</g>
<text x="{W}" y="34" font-family="{MONO}" font-size="12" font-weight="700" letter-spacing="1.4" fill="{TEXT_DIM}" text-anchor="end">HIGH SCORE: EVERY GREEN SQUARE</text>
<svg x="0" y="{top}" width="{W}" height="{h:.0f}" viewBox="{vb}">{inner}</svg>
<text x="{W / 2}" y="{H - PAD - 4}" font-family="{MONO}" font-size="11" font-weight="700" letter-spacing="1.4" fill="{TEXT_DIM}" text-anchor="middle">ONE SQUARE = ONE DAY OF CONTRIBUTIONS · LAST 12 MONTHS</text>'''
    with open(out, 'w', encoding='utf-8', newline='\n') as f:
        f.write(svg(W, H, 'A snake eating my contribution graph', body))


if __name__ == '__main__':
    main()
