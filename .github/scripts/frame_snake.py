"""Puts the contribution snake (from Platane/snk) in a panel that matches the
rest of the README (see theme.py). Run by .github/workflows/profile-assets.yml
after the snake is generated.

Usage: python frame_snake.py <snake.svg> <out.svg>
"""
import re
import sys

from theme import SAGE, panel, header, stars, svg, TWINKLE, TEXT_DIM, MONO


def main():
    src, out = sys.argv[1], sys.argv[2]
    with open(src, encoding='utf-8') as f:
        snake = f.read()
    vb = re.search(r'viewBox="([^"]+)"', snake).group(1)
    _, _, vw, vh = (float(v) for v in vb.split())
    inner = re.sub(r'^.*?<svg[^>]*>|</svg>\s*$', '', snake, flags=re.S)

    W, w = 1000, 900
    h = vh * w / vw
    H = round(124 + h + 40)
    body = f'''{panel(W, H, (SAGE[2], .5, 1, .6), 'sn')}
{stars(W, H, 18, 5)}
{header('eating my contributions', 'SNAKE.EXE', SAGE, 'HIGH SCORE: EVERY GREEN SQUARE', 50, 40)}
<svg x="{(W - w) / 2}" y="124" width="{w}" height="{h:.0f}" viewBox="{vb}">{inner}</svg>
<text x="{W / 2}" y="{H - 22}" font-family="{MONO}" font-size="11" font-weight="700" letter-spacing="1.4" fill="{TEXT_DIM}" text-anchor="middle">ONE SQUARE = ONE DAY OF CONTRIBUTIONS · LAST 12 MONTHS</text>'''
    with open(out, 'w', encoding='utf-8', newline='\n') as f:
        f.write(svg(W, H, 'A snake eating my contribution graph', body, TWINKLE))


if __name__ == '__main__':
    main()
