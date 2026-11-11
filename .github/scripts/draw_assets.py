"""Draws the profile README's artwork into assets/: soft, clay-like 3D
shapes in pastel colours, built from plain SVG (isometric boxes, soft
shadows, a little CSS animation). No images, fonts or scripts are loaded,
so GitHub can show every file as an image.

Usage: python .github/scripts/draw_assets.py
"""
import math
import os
from html import escape as esc

OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'assets')

SANS = "'SF Pro Rounded', ui-rounded, 'Nunito', 'Segoe UI Variable Display', 'Segoe UI', system-ui, sans-serif"
MONO = "ui-monospace, 'SF Mono', 'Cascadia Mono', Consolas, 'Liberation Mono', monospace"

INK = '#2e2a36'
INK_SOFT = '#6f6878'
CREAM = '#f7f1e8'
CREAM_EDGE = '#e6dccd'

# Each clay colour: (top, left face, right face).
PEACH = ('#ffd6c4', '#f6b89f', '#e89d84')
SAGE = ('#d3e6cc', '#b2d0a9', '#97ba8e')
LILAC = ('#e0d7f7', '#c6b9ee', '#ab9bdd')
BUTTER = ('#fbe9ae', '#f3d483', '#e3c068')
SKY = ('#d3e6f7', '#acceec', '#8fb6dc')
ROSE = ('#fbd3dd', '#f3b3c3', '#e297aa')
STONE = ('#efe7da', '#ddd1bf', '#cbbda8')

C30, S30 = math.cos(math.pi / 6), 0.5

REDUCED = '@media (prefers-reduced-motion: reduce) { * { animation: none !important; } }'


def svg(w, h, label, body, style=''):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-label="{esc(label)}">\n<title>{esc(label)}</title>\n'
        f'<style>{style}\n{REDUCED}</style>\n{body}\n</svg>\n'
    )


def panel(w, h):
    """The cream card every section sits on, so it reads the same on GitHub's light and dark themes."""
    return (f'<rect width="{w}" height="{h}" rx="30" fill="#fbf6ef"/>'
            f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="29" fill="none" stroke="{CREAM_EDGE}" stroke-width="2"/>')


def shadow_filter(fid, dy=10, blur=12, opacity=0.16, color='#5b4a3a'):
    return (
        f'<filter id="{fid}" x="-30%" y="-30%" width="160%" height="180%">'
        f'<feDropShadow dx="0" dy="{dy}" stdDeviation="{blur}" flood-color="{color}" flood-opacity="{opacity}"/></filter>'
    )


class Iso:
    """Isometric projection with its origin at screen (ox, oy)."""

    def __init__(self, ox, oy):
        self.ox, self.oy = ox, oy

    def p(self, x, y, z=0):
        return (self.ox + (x - y) * C30, self.oy + (x + y) * S30 - z)

    def poly(self, pts, fill, extra=''):
        d = 'M' + ' L'.join(f'{a:.1f} {b:.1f}' for a, b in pts) + ' Z'
        # A stroke in the face's own colour rounds the corners, like clay.
        return f'<path d="{d}" fill="{fill}" stroke="{fill}" stroke-width="5" stroke-linejoin="round"{extra}/>'

    def box(self, x, y, z, w, d, h, col):
        top, left, right = col
        p = self.p
        return '\n'.join([
            self.poly([p(x, y + d, z), p(x + w, y + d, z), p(x + w, y + d, z + h), p(x, y + d, z + h)], left),
            self.poly([p(x + w, y, z), p(x + w, y + d, z), p(x + w, y + d, z + h), p(x + w, y, z + h)], right),
            self.poly([p(x, y, z + h), p(x + w, y, z + h), p(x + w, y + d, z + h), p(x, y + d, z + h)], top),
        ])

    def top_face(self, x, y, z):
        """A transform that draws 2D shapes (u right, v down) onto a top face."""
        ex, ey = self.p(x, y, z)
        return f'matrix({C30:.4f} {S30} {-C30:.4f} {S30} {ex:.1f} {ey:.1f})'

    def front_face(self, x, y, z):
        """Draws onto the face that looks down-left (the plane y = const)."""
        ex, ey = self.p(x, y, z)
        return f'matrix({C30:.4f} {S30} 0 1 {ex:.1f} {ey:.1f})'

    def cylinder(self, x, y, z, r, h, col):
        top, side, _ = col
        cx, cy = self.p(x, y, z)
        rx, ry = r * 1.2, r * 0.62
        return (
            f'<path d="M{cx - rx:.1f} {cy - h:.1f} V{cy:.1f} A{rx:.1f} {ry:.1f} 0 0 0 {cx + rx:.1f} {cy:.1f} V{cy - h:.1f} Z" fill="{side}"/>'
            f'<ellipse cx="{cx:.1f}" cy="{cy - h:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{top}"/>'
        )


def pixels(rows, size, colors, x0=0, y0=0):
    out = []
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch in colors:
                out.append(f'<rect x="{x0 + i * size}" y="{y0 + j * size}" width="{size}" height="{size}" fill="{colors[ch]}"/>')
    return ''.join(out)


RUNNER_TOP = ['..####..', '.######.', '.#.##.#.', '.######.', 'rr####..', '..####..', '.######.', '..####..']
RUNNER_A = RUNNER_TOP + ['.##..##.', '##....##']
RUNNER_B = RUNNER_TOP + ['..####..', '..#..#..']
BUG = ['.#..#.', '######', '#.##.#', '.#..#.']


# ─────────────────────────────── hero ───────────────────────────────

def hero():
    W, H = 1000, 470
    iso = Iso(712, 168)
    parts = []

    # The floating desk: a slab with things on it.
    slab = iso.box(0, 0, 0, 260, 200, 24, STONE)
    sheen = f'<path d="M{iso.p(0, 0, 24)[0]:.1f} {iso.p(0, 0, 24)[1]:.1f} L{iso.p(260, 0, 24)[0]:.1f} {iso.p(260, 0, 24)[1]:.1f} L{iso.p(260, 40, 24)[0]:.1f} {iso.p(260, 40, 24)[1]:.1f} L{iso.p(0, 40, 24)[0]:.1f} {iso.p(0, 40, 24)[1]:.1f} Z" fill="#fff" opacity="0.35"/>'

    # Monitor: stand, neck, then the screen box with a tiny game on it.
    monitor = [
        iso.box(95, 6, 24, 70, 44, 6, STONE),
        iso.box(122, 20, 30, 16, 10, 40, STONE),
        iso.box(36, 26, 66, 188, 10, 104, LILAC),
    ]
    face = iso.front_face(36, 36, 170)
    game = f'''<g transform="{face}">
  <clipPath id="screen" clipPathUnits="userSpaceOnUse"><rect x="9" y="9" width="170" height="86" rx="7"/></clipPath>
  <rect x="9" y="9" width="170" height="86" rx="7" fill="#33394b"/>
  <g clip-path="url(#screen)">
    <rect x="9" y="9" width="170" height="86" fill="url(#sky)"/>
    <g class="cloud"><rect x="40" y="24" width="18" height="5" rx="2.5" fill="#fff" opacity=".5"/><rect x="46" y="20" width="10" height="5" rx="2.5" fill="#fff" opacity=".5"/></g>
    <g class="cloud slow"><rect x="120" y="32" width="14" height="4" rx="2" fill="#fff" opacity=".35"/></g>
    <rect x="9" y="80" width="170" height="15" fill="#5d7a5a"/>
    <rect x="9" y="78" width="170" height="3" fill="#97ba8e"/>
    <g transform="translate(108 66)">{pixels(BUG, 3, {'#': '#f08aa0'})}</g>
    <text class="xp" x="117" y="56" font-family="{MONO}" font-size="10" font-weight="700" fill="#fbe9ae" text-anchor="middle">+1 xp</text>
    <g class="run"><g class="hop">
      <g class="leg-a">{pixels(RUNNER_A, 3, {'#': '#fff4e8', 'r': '#f6b89f'}, 0, 48)}</g>
      <g class="leg-b">{pixels(RUNNER_B, 3, {'#': '#fff4e8', 'r': '#f6b89f'}, 0, 48)}</g>
    </g></g>
    <text x="172" y="23" font-family="{MONO}" font-size="9" font-weight="700" fill="#d3e6f7" text-anchor="end" opacity=".8">LV 1-1</text>
  </g>
</g>'''

    # Keyboard with keys drawn on its top face.
    kb = iso.box(58, 92, 24, 128, 40, 7, STONE)
    keys = []
    for row in range(3):
        for col in range(10):
            keys.append(f'<rect x="{6 + col * 11.8:.1f}" y="{5 + row * 11}" width="9" height="8.5" rx="2" fill="#fbf7f1"/>')
    keys.append('<rect class="key" x="41.4" y="27" width="44" height="8.5" rx="2" fill="#fbf7f1"/>')
    keyboard = f'{kb}<g transform="{iso.top_face(58, 92, 31)}">{"".join(keys)}</g>'

    # Sticky note and a controller lying on the desk.
    note = (f'<g transform="{iso.top_face(196, 70, 24.5)}">'
            f'<rect x="2" y="3" width="40" height="40" rx="3" fill="#e3c068"/>'
            f'<rect x="0" y="0" width="40" height="40" rx="3" fill="#fbe9ae"/>'
            f'<path d="M7 12 H31 M7 20 H27 M7 28 H22" stroke="#d8b25a" stroke-width="2.4" stroke-linecap="round"/></g>')
    pad_shape = 'M14 4 H58 C68 4 74 12 72 22 L70 32 C69 39 62 42 56 37 L50 32 H22 L16 37 C10 42 3 39 2 32 L0 22 C-2 12 4 4 14 4 Z'
    controller = (f'<g transform="{iso.top_face(98, 146, 24)}">'
                  f'<path d="{pad_shape}" fill="{SAGE[2]}" transform="translate(4 6)"/>'
                  f'<path d="{pad_shape}" fill="{SAGE[0]}"/>'
                  f'<path d="M15 14 v10 M10 19 h10" stroke="{INK}" stroke-width="3.2" stroke-linecap="round"/>'
                  f'<circle cx="54" cy="15" r="3.2" fill="#f08aa0" class="blink"/><circle cx="61" cy="21" r="3.2" fill="#8fb6dc"/></g>')

    # A mug with steam, and a plant in the front corner.
    mug_x, mug_y = 226, 136
    mx, my = iso.p(mug_x, mug_y, 24)
    mug = (iso.cylinder(mug_x, mug_y, 24, 17, 34, PEACH)
           + f'<ellipse cx="{mx:.1f}" cy="{my - 34:.1f}" rx="14.5" ry="7.4" fill="#8a5a4a"/>'
           + f'<path d="M{mx + 19:.1f} {my - 26:.1f} c12 0 12 18 0 18" fill="none" stroke="{PEACH[1]}" stroke-width="6" stroke-linecap="round"/>'
           + ''.join(f'<path class="steam s{i}" d="M{mx - 6 + i * 6:.1f} {my - 44:.1f} c-6 -8 6 -12 0 -20 c-6 -8 6 -12 0 -20" fill="none" stroke="#fff" stroke-width="3.2" stroke-linecap="round"/>' for i in range(3)))
    px, py = iso.p(26, 168, 24)
    leaves = ''.join(
        f'<ellipse cx="0" cy="-22" rx="8" ry="22" fill="{c}" transform="rotate({a})"/>'
        for a, c in [(-38, SAGE[1]), (34, SAGE[1]), (-12, SAGE[0]), (14, '#c2dcb9')])
    plant = (iso.cylinder(26, 168, 24, 16, 26, ROSE)
             + f'<g class="sway" transform="translate({px:.1f} {py - 30:.1f})"><g>{leaves}</g></g>')

    desk = '\n'.join([slab, sheen, *monitor, game, keyboard, note, controller, mug, plant])

    # Things floating around the desk.
    sphere = '<g class="float f1"><circle cx="958" cy="96" r="22" fill="url(#ball)"/></g>'
    ciso = Iso(574, 74)
    cube = f'<g class="float f2">{ciso.box(0, 0, 0, 28, 28, 28, BUTTER)}</g>'
    ring = '<g class="float f3"><ellipse cx="948" cy="342" rx="20" ry="9" fill="none" stroke="#c6b9ee" stroke-width="9"/></g>'

    sx, sy = iso.p(130, 100, -40)
    ground = f'<ellipse class="shade" cx="{sx:.1f}" cy="{sy + 70:.1f}" rx="200" ry="26" fill="#5b4a3a" opacity=".10"/>'

    # Words on the left.
    def name(text, y):
        return (f'<text x="62" y="{y + 5}" font-family="{SANS}" font-size="64" font-weight="800" fill="{CREAM_EDGE}">{text}</text>'
                f'<text x="60" y="{y}" font-family="{SANS}" font-size="64" font-weight="800" fill="{INK}">{text}</text>')

    def chip(x, label, col):
        w = 26 + len(label) * 8.4
        return (f'<g transform="translate({x} 362)"><rect y="4" width="{w:.0f}" height="34" rx="17" fill="{col[2]}"/>'
                f'<rect width="{w:.0f}" height="34" rx="17" fill="{col[0]}"/>'
                f'<text x="{w / 2:.0f}" y="22.5" font-family="{SANS}" font-size="14" font-weight="700" fill="{INK}" text-anchor="middle">{label}</text></g>')

    words = '\n'.join([
        f'<text x="62" y="122" font-family="{MONO}" font-size="15" fill="{INK_SOFT}">hi there, i\'m</text>',
        name('Ruchira', 192),
        name('Edirisinghe', 262),
        f'<text x="62" y="312" font-family="{SANS}" font-size="19" font-weight="600" fill="{INK_SOFT}">I design interfaces, then make them playable.</text>',
        chip(60, 'UI/UX engineer', SKY),
        chip(212, 'game developer', PEACH),
        chip(364, 'vibe coder', LILAC),
    ])

    defs = f'''<defs>
  {shadow_filter('soft', 14, 16, 0.18)}
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fbf6ef"/><stop offset="1" stop-color="#f3ebe0"/></linearGradient>
  <radialGradient id="blush" cx="0.75" cy="0.45" r="0.5"><stop offset="0" stop-color="#fde3d6"/><stop offset="1" stop-color="#fde3d6" stop-opacity="0"/></radialGradient>
  <radialGradient id="ball" cx="0.35" cy="0.3" r="0.75"><stop offset="0" stop-color="#ffe9df"/><stop offset="0.55" stop-color="#f6b89f"/><stop offset="1" stop-color="#e2917a"/></radialGradient>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3f4a66"/><stop offset="1" stop-color="#6a6f92"/></linearGradient>
</defs>'''

    style = '''
.desk { animation: bob 6s ease-in-out infinite; }
.shade { animation: shade 6s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }
@keyframes bob { 50% { transform: translateY(-7px); } }
@keyframes shade { 50% { transform: scale(.94); opacity: .07; } }
.float { animation: bob 5s ease-in-out infinite; }
.f2 { animation-duration: 6.5s; animation-delay: -2s; }
.f3 { animation-duration: 7s; animation-delay: -4s; }
.steam { opacity: 0; animation: steam 3.6s ease-out infinite; }
.s1 { animation-delay: 1.2s; } .s2 { animation-delay: 2.4s; }
@keyframes steam { 0% { opacity: 0; transform: translateY(6px); } 30% { opacity: .75; } 100% { opacity: 0; transform: translateY(-14px); } }
.sway > g { animation: sway 4s ease-in-out infinite; transform-origin: 0 0; }
@keyframes sway { 50% { transform: rotate(5deg); } }
.blink { animation: blink 2.4s steps(1) infinite; }
@keyframes blink { 50% { opacity: .35; } }
.key { animation: key 3.2s ease-in-out infinite; }
@keyframes key { 0%, 80%, 100% { fill: #fbf7f1; } 88% { fill: #c6b9ee; } }
.run { animation: run 6s linear infinite; }
@keyframes run { from { transform: translateX(-30px); } to { transform: translateX(196px); } }
.hop { animation: hop 6s linear infinite; }
@keyframes hop { 0%, 52% { transform: translateY(0); } 59% { transform: translateY(-28px); } 66%, 100% { transform: translateY(0); } }
.leg-a { animation: legs .32s steps(1) infinite; }
.leg-b { animation: legs .32s steps(1) infinite reverse; }
@keyframes legs { 0% { opacity: 1; } 50% { opacity: 0; } }
.xp { opacity: 0; animation: xp 6s linear infinite; }
@keyframes xp { 0%, 58% { opacity: 0; transform: translateY(4px); } 62% { opacity: 1; } 75% { opacity: 0; transform: translateY(-6px); } 100% { opacity: 0; } }
.cloud { animation: drift 14s linear infinite; }
.cloud.slow { animation-duration: 22s; }
@keyframes drift { from { transform: translateX(150px); } to { transform: translateX(-160px); } }
'''
    body = f'''{defs}
<rect width="{W}" height="{H}" rx="30" fill="url(#bg)"/>
<rect width="{W}" height="{H}" rx="30" fill="url(#blush)"/>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="29" fill="none" stroke="{CREAM_EDGE}" stroke-width="2"/>
{ground}
<g class="desk" filter="url(#soft)">
{desk}
</g>
{sphere}
{cube}
{ring}
{words}'''
    return svg(W, H, "Ruchira Edirisinghe: UI/UX engineer, game developer and vibe coder. I design interfaces, then make them playable.", body, style)


# ─────────────────────────────── buttons ───────────────────────────────

ICON = {
    'portfolio': '<path d="M0 -9 C1.5 -2 2 -1.5 9 0 C2 1.5 1.5 2 0 9 C-1.5 2 -2 1.5 -9 0 C-2 -1.5 -1.5 -2 0 -9 Z" fill="{c}"/>',
    'linkedin': '<text y="5.5" font-family="{sans}" font-size="16" font-weight="800" fill="{c}" text-anchor="middle">in</text>',
    'behance': '<text y="5.5" font-family="{sans}" font-size="15" font-weight="800" fill="{c}" text-anchor="middle">Bē</text>',
    'instagram': '<rect x="-8" y="-8" width="16" height="16" rx="5" fill="none" stroke="{c}" stroke-width="2.6"/><circle r="3.6" fill="none" stroke="{c}" stroke-width="2.6"/><circle cx="4.6" cy="-4.6" r="1.4" fill="{c}"/>',
    'email': '<rect x="-9" y="-6.5" width="18" height="13" rx="3" fill="none" stroke="{c}" stroke-width="2.6"/><path d="M-7.5 -4 L0 1.5 L7.5 -4" fill="none" stroke="{c}" stroke-width="2.6" stroke-linejoin="round" stroke-linecap="round"/>',
}


def button(kind, label, col, delay):
    W, H = 196, 62
    w = W - 8
    icon = ICON[kind].format(c=col[2], sans=SANS)
    style = f'''
.cap {{ animation: press 7s ease-in-out infinite; animation-delay: {delay}s; }}
@keyframes press {{ 0%, 6%, 100% {{ transform: translateY(0); }} 3% {{ transform: translateY(4px); }} }}
'''
    body = f'''<defs>{shadow_filter('s', 4, 4, 0.16)}<linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".55"/><stop offset=".6" stop-color="#fff" stop-opacity="0"/></linearGradient></defs>
<g filter="url(#s)">
<rect x="4" y="10" width="{w}" height="44" rx="22" fill="{col[2]}"/>
<g class="cap">
<rect x="4" y="5" width="{w}" height="44" rx="22" fill="{col[0]}"/>
<rect x="4" y="5" width="{w}" height="44" rx="22" fill="url(#g)"/>
<circle cx="31" cy="27" r="16" fill="#fffaf4"/>
<g transform="translate(31 27)">{icon}</g>
<text x="56" y="32.5" font-family="{SANS}" font-size="16" font-weight="700" fill="{INK}">{label}</text>
<path d="M{w - 22} 22 l6 5 l-6 5" fill="none" stroke="{INK_SOFT}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>
</g></g>'''
    return svg(W, H, label, body, style)


# ─────────────────────────────── about ───────────────────────────────

def about():
    W, H = 1000, 356
    cards = [
        (PEACH, 'briefcase', 'working at', ['Funextreme', 'Technology LLC'], 'UI/UX + game dev'),
        (LILAC, 'cap', 'studied', ['BSc (Hons)', 'Computer Security'], 'University of Plymouth, UK'),
        (SAGE, 'pad', 'exploring', ['Game design', '& motion'], 'making things feel good'),
        (SKY, 'cube', 'also into', ['3D & AI-powered', 'workflows'], 'Blender, Spline, Claude'),
    ]

    def object_(kind, col):
        if kind == 'briefcase':
            return (f'<path d="M-12 -24 v-6 a5 5 0 0 1 5 -5 h14 a5 5 0 0 1 5 5 v6" fill="none" stroke="{col[2]}" stroke-width="5"/>'
                    f'<rect x="-30" y="-20" width="60" height="42" rx="10" fill="{col[2]}"/>'
                    f'<rect x="-30" y="-26" width="60" height="42" rx="10" fill="{col[0]}"/>'
                    f'<rect x="-6" y="-10" width="12" height="9" rx="3" fill="{col[1]}"/>')
        if kind == 'cap':
            return (f'<path d="M-18 -6 v12 c0 7 36 7 36 0 v-12" fill="{col[1]}"/>'
                    f'<path d="M0 -30 L36 -14 L0 2 L-36 -14 Z" fill="{col[2]}" transform="translate(0 4)"/>'
                    f'<path d="M0 -30 L36 -14 L0 2 L-36 -14 Z" fill="{col[0]}"/>'
                    f'<path d="M0 -14 L26 -4 V12" fill="none" stroke="{BUTTER[1]}" stroke-width="3" stroke-linecap="round"/>'
                    f'<circle cx="26" cy="14" r="4" fill="{BUTTER[1]}"/>')
        if kind == 'pad':
            shape = 'M-22 -14 H22 C32 -14 38 -6 36 4 L34 14 C33 21 26 24 20 19 L14 14 H-14 L-20 19 C-26 24 -33 21 -34 14 L-36 4 C-38 -6 -32 -14 -22 -14 Z'
            return (f'<path d="{shape}" fill="{col[2]}" transform="translate(0 6)"/><path d="{shape}" fill="{col[0]}"/>'
                    f'<path d="M-21 -6 v12 M-27 0 h12" stroke="{INK}" stroke-width="3.6" stroke-linecap="round"/>'
                    f'<circle cx="18" cy="-4" r="4" fill="#f08aa0"/><circle cx="26" cy="4" r="4" fill="#8fb6dc"/>')
        ciso = Iso(0, -40)
        return ciso.box(0, 0, 0, 34, 34, 34, col)

    out = []
    cw, ch, gap, x0, y0 = 212, 220, 18, 49, 104
    for i, (col, kind, kicker, lines, sub) in enumerate(cards):
        x = x0 + i * (cw + gap)
        text_lines = ''.join(
            f'<text x="20" y="{142 + j * 22}" font-family="{SANS}" font-size="18" font-weight="800" fill="{INK}">{esc(t)}</text>'
            for j, t in enumerate(lines))
        out.append(f'''<g transform="translate({x} {y0})"><g>
  <rect y="6" width="{cw}" height="{ch}" rx="24" fill="{CREAM_EDGE}"/>
  <rect width="{cw}" height="{ch}" rx="24" fill="#fffaf3"/>
  <rect width="{cw}" height="{ch}" rx="24" fill="none" stroke="#efe5d6" stroke-width="1.5"/>
  <ellipse cx="62" cy="86" rx="34" ry="7" fill="#5b4a3a" opacity=".09"/>
  <g transform="translate(62 62)"><g class="obj o{i}">{object_(kind, col)}</g></g>
  <text x="20" y="116" font-family="{MONO}" font-size="12.5" fill="{col[2]}" font-weight="700">{kicker}</text>
  {text_lines}
  <text x="20" y="{142 + len(lines) * 22 + 6}" font-family="{SANS}" font-size="13" fill="{INK_SOFT}">{esc(sub)}</text>
</g></g>''')

    style = '''
.obj { animation: lift 4.5s ease-in-out infinite; }
.o1 { animation-delay: -1.1s; } .o2 { animation-delay: -2.2s; } .o3 { animation-delay: -3.3s; }
@keyframes lift { 50% { transform: translate(0, -6px); } }
'''
    body = f'''<defs>{shadow_filter('soft', 10, 12, 0.13)}</defs>
{panel(W, H)}
<text x="50" y="60" font-family="{SANS}" font-size="30" font-weight="800" fill="{INK}">a little about me</text>
<text x="52" y="84" font-family="{MONO}" font-size="13" fill="{INK_SOFT}">// designer who codes, coder who plays</text>
<g filter="url(#soft)">{''.join(out)}</g>'''
    return svg(W, H, 'About me: UI/UX engineer and game developer at Funextreme Technology LLC; BSc (Hons) Computer Security, University of Plymouth, UK; exploring game design, motion, 3D and AI-powered workflows.', body, style)


# ─────────────────────────────── stack ───────────────────────────────

GROUPS = [
    ('design & 3d', PEACH, [('Figma', '#f24e1e'), ('Framer', '#0055ff'), ('Spline', '#9d7cf2'), ('Photoshop', '#31a8ff'), ('Illustrator', '#ff9a00'), ('Blender', '#ea7600')]),
    ('code & games', SKY, [('HTML', '#e34f26'), ('CSS', '#1572b6'), ('JavaScript', '#e8c90f'), ('TypeScript', '#3178c6'), ('React', '#2bb4d6'), ('Tailwind', '#06b6d4'), ('Python', '#3776ab'), ('Unity', '#222222'), ('C#', '#68217a')]),
    ('ai & workflow', LILAC, [('Claude', '#d97757'), ('ChatGPT', '#10a37f'), ('Gemini', '#8e75b2'), ('Cursor', '#2e2a36'), ('Copilot', '#6e40c9'), ('Midjourney', '#2e2a36'), ('Git', '#f05032'), ('GitHub', '#2e2a36'), ('Vercel', '#2e2a36')]),
]


def stack():
    W = 1000
    out, y, n = [], 120, 0
    for title, col, tools in GROUPS:
        out.append(f'<text x="52" y="{y}" font-family="{MONO}" font-size="13" font-weight="700" fill="{col[2]}">{esc(title)}</text>')
        y += 16
        x = 50
        for name, brand in tools:
            w = 52 + len(name) * 8.6
            if x + w > W - 50:
                x, y = 50, y + 62
            out.append(f'''<g transform="translate({x:.0f} {y})"><g class="k" style="animation-delay:{n * 0.11:.2f}s">
  <rect y="7" width="{w:.0f}" height="44" rx="13" fill="{col[2]}"/>
  <rect width="{w:.0f}" height="44" rx="13" fill="{col[0]}"/>
  <rect x="5" y="4" width="{w - 10:.0f}" height="30" rx="10" fill="#fff" opacity=".42"/>
  <circle cx="22" cy="21" r="6" fill="{brand}"/>
  <text x="36" y="26.5" font-family="{SANS}" font-size="15" font-weight="700" fill="{INK}">{esc(name)}</text>
</g></g>''')
            x += w + 12
            n += 1
        y += 92
    H = y - 6
    style = '''
.k { animation: tap 8s ease-in-out infinite; }
@keyframes tap { 0%, 5%, 100% { transform: translateY(0); } 2.5% { transform: translateY(5px); } }
'''
    body = f'''<defs>{shadow_filter('soft', 6, 6, 0.12)}</defs>
{panel(W, H)}
<text x="50" y="60" font-family="{SANS}" font-size="30" font-weight="800" fill="{INK}">my toolbox</text>
<text x="52" y="84" font-family="{MONO}" font-size="13" fill="{INK_SOFT}">// the keys i press most</text>
<g filter="url(#soft)">{''.join(out)}</g>'''
    names = ', '.join(name for _, _, tools in GROUPS for name, _ in tools)
    return svg(W, H, f'My toolbox: {names}', body, style)


# ─────────────────────────────── divider & footer ───────────────────────────────

def divider():
    W, H = 1000, 34
    beads = ''.join(
        f'<circle class="b" style="animation-delay:{i * 0.18:.2f}s" cx="{440 + i * 30}" cy="17" r="7" fill="{c[1]}"/>'
        for i, c in enumerate([PEACH, BUTTER, SAGE, SKY, LILAC]))
    style = '''
.b { animation: bead 3s ease-in-out infinite; }
@keyframes bead { 0%, 40%, 100% { transform: translateY(0); } 20% { transform: translateY(-5px); } }
'''
    body = (f'<path d="M60 17 H400 M600 17 H940" stroke="{CREAM_EDGE}" stroke-width="2.5" stroke-linecap="round" stroke-dasharray="1 9"/>{beads}')
    return svg(W, H, '', body, style)


def footer():
    W, H = 1000, 230
    iso = Iso(780, 70)
    base = iso.box(0, 0, 0, 120, 120, 18, SAGE)
    bx, by = iso.p(60, 60, 18)
    button_ = (f'<g class="btn"><ellipse cx="{bx:.1f}" cy="{by + 4:.1f}" rx="44" ry="23" fill="#d67f93"/>'
               f'<ellipse cx="{bx:.1f}" cy="{by - 6:.1f}" rx="44" ry="23" fill="#f3b3c3"/>'
               f'<ellipse cx="{bx - 10:.1f}" cy="{by - 12:.1f}" rx="18" ry="7" fill="#fff" opacity=".45"/></g>')
    style = '''
.btn { animation: push 3s ease-in-out infinite; }
@keyframes push { 0%, 70%, 100% { transform: translateY(0); } 80% { transform: translateY(8px); } }
.spark { opacity: 0; animation: spark 3s ease-out infinite; transform-box: fill-box; transform-origin: center; }
@keyframes spark { 0%, 78% { opacity: 0; transform: scale(.6); } 85% { opacity: 1; } 100% { opacity: 0; transform: scale(1.25); } }
.caret { animation: caret 1s steps(1) infinite; }
@keyframes caret { 50% { opacity: 0; } }
'''
    sparks = ''.join(
        f'<path d="M{845 + 70 * math.cos(a):.0f} {72 + 38 * math.sin(a):.0f} l{12 * math.cos(a):.0f} {8 * math.sin(a):.0f}" stroke="{INK_SOFT}" stroke-width="3" stroke-linecap="round"/>'
        for a in [math.radians(d) for d in (200, 235, 270, 305, 340)])
    body = f'''<defs>{shadow_filter('soft', 12, 14, 0.16)}</defs>
<rect width="{W}" height="{H}" rx="30" fill="#fbf6ef"/>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="29" fill="none" stroke="{CREAM_EDGE}" stroke-width="2"/>
<text x="60" y="96" font-family="{SANS}" font-size="34" font-weight="800" fill="{INK}">thanks for stopping by!</text>
<text x="62" y="134" font-family="{SANS}" font-size="18" font-weight="600" fill="{INK_SOFT}">press the big button to see what i'm building lately</text>
<text x="62" y="176" font-family="{MONO}" font-size="15" fill="{PEACH[2]}">ruchiraedirisinghe.vercel.app<tspan class="caret" fill="{INK}">_</tspan></text>
<g class="spark">{sparks}</g>
<g filter="url(#soft)">{base}{button_}</g>'''
    return svg(W, H, "Thanks for stopping by! Press the button to visit my website.", body, style)


def main():
    files = {
        'hero.svg': hero(),
        'about.svg': about(),
        'stack.svg': stack(),
        'divider.svg': divider(),
        'footer.svg': footer(),
        'btn-portfolio.svg': button('portfolio', 'Portfolio', PEACH, 0.0),
        'btn-linkedin.svg': button('linkedin', 'LinkedIn', SKY, 0.35),
        'btn-behance.svg': button('behance', 'Behance', LILAC, 0.7),
        'btn-instagram.svg': button('instagram', 'Instagram', ROSE, 1.05),
        'btn-email.svg': button('email', 'Email', BUTTER, 1.4),
    }
    os.makedirs(OUT, exist_ok=True)
    for name, text in files.items():
        with open(os.path.join(OUT, name), 'w', encoding='utf-8', newline='\n') as f:
            f.write(text)
        print(f'{name}: {len(text):,} bytes')


if __name__ == '__main__':
    main()
