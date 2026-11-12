"""Turns the README's titles into vector outlines (titles.json), set in Epic Pro, the
display face of my portfolio site. Only these words are stored, as artwork; the font
itself (© Glyphonic) is not in this repo. theme.title() draws them.

Run it on a machine that has the font, after changing TITLES:
    py .github/scripts/make_titles.py "<path to epicpro.ttf>"
"""
import json
import os
import sys

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

TITLES = [
    'Ruchira', 'Edirisinghe',
    'A Little About Me', 'Featured Projects', 'My Toolbox', 'My Streak', 'Top Languages', 'Thanks For Playing!',
]
TRACKING = 0.04  # extra space between letters, in em, like the site's letter-spacing

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'titles.json')


def outline(font, text):
    upm = font['head'].unitsPerEm
    cmap, glyphs, hmtx = font.getBestCmap(), font.getGlyphSet(), font['hmtx']
    pen = SVGPathPen(glyphs, ntos=lambda v: f'{v:.0f}')
    x = 0
    for i, ch in enumerate(text):
        name = cmap.get(ord(ch)) or cmap.get(ord(ch.upper()))
        if name is None:
            raise SystemExit(f'Epic Pro has no glyph for {ch!r} in {text!r}')
        # Font units are y-up; flip so the path drops straight into SVG with its baseline at y=0.
        glyphs[name].draw(TransformPen(pen, (1, 0, 0, -1, x, 0)))
        x += hmtx[name][0] + (TRACKING * upm if i < len(text) - 1 else 0)
    return {'d': pen.getCommands(), 'width': round(x), 'upm': upm}


def main():
    font = TTFont(sys.argv[1])
    data = {t: outline(font, t) for t in TITLES}
    with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(data, f, separators=(',', ':'))
    print(f'{len(data)} titles, {os.path.getsize(OUT):,} bytes')


if __name__ == '__main__':
    main()
