"""Draws the profile README's artwork into assets/ in a dark arcade theme:
soft, clay-like 3D shapes in pastel colours, real tool logos and a little
CSS animation. The shared palette and helpers live in theme.py; the live
GitHub stat cards are drawn by stat_cards.py in the same style.

Usage: python .github/scripts/draw_assets.py
"""
import math
import os

from theme import (BUTTER, CARD, CARD_TOP, EDGE, LILAC, LIP, MONO, PEACH, ROSE, SAGE, SANS, SKY, SLATE, SLATE_LIGHT,
                   SLOT, TEXT, TEXT_DIM, TEXT_SOFT, TWINKLE, Iso, esc, glow_filter, glyph, header, logo, orb, panel,
                   pixels, raised, shadow_filter, stars, svg)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'assets')

RUNNER_TOP = ['..####..', '.######.', '.#.##.#.', '.######.', 'rr####..', '..####..', '.######.', '..####..']
RUNNER_A = RUNNER_TOP + ['.##..##.', '##....##']
RUNNER_B = RUNNER_TOP + ['..####..', '..#..#..']
BUG = ['.#..#.', '######', '#.##.#', '.#..#.']
HEART = ['.##.##.', '#######', '#######', '.#####.', '..###..', '...#...']


def coin(cx, cy, r, uid):
    """A gold coin, flat-on; spin it with a scaleX animation."""
    return (f'<defs><linearGradient id="{uid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff3c4"/>'
            f'<stop offset=".5" stop-color="{BUTTER[1]}"/><stop offset="1" stop-color="#d6a94a"/></linearGradient></defs>'
            f'<circle cx="{cx}" cy="{cy + r * .18:.1f}" r="{r}" fill="#a87d2c"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#{uid})"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r * .68:.1f}" fill="none" stroke="#c99a3e" stroke-width="{r * .14:.1f}"/>'
            f'<rect x="{cx - r * .1:.1f}" y="{cy - r * .38:.1f}" width="{r * .2:.1f}" height="{r * .76:.1f}" rx="{r * .1:.1f}" fill="#c99a3e"/>')


# ─────────────────────────────── hero ───────────────────────────────

def hero():
    W, H = 1000, 480
    iso = Iso(712, 176)

    slab = iso.box(0, 0, 0, 260, 200, 24, SLATE)
    rim = iso.poly([iso.p(0, 0, 24), iso.p(260, 0, 24), iso.p(260, 30, 24), iso.p(0, 30, 24)], '#5a5478')

    monitor = [
        iso.box(95, 6, 24, 70, 44, 6, SLATE_LIGHT),
        iso.box(122, 20, 30, 16, 10, 40, SLATE_LIGHT),
        iso.box(36, 26, 66, 188, 10, 104, LILAC),
    ]
    face = iso.front_face(36, 36, 170)
    game = f'''<g transform="{face}">
  <clipPath id="screen" clipPathUnits="userSpaceOnUse"><rect x="9" y="9" width="170" height="86" rx="7"/></clipPath>
  <rect x="9" y="9" width="170" height="86" rx="7" fill="#1d2235"/>
  <g clip-path="url(#screen)">
    <rect x="9" y="9" width="170" height="86" fill="url(#sky)"/>
    <circle cx="150" cy="30" r="9" fill="{BUTTER[0]}" opacity=".85"/>
    <g class="cloud"><rect x="40" y="24" width="18" height="5" rx="2.5" fill="#fff" opacity=".35"/><rect x="46" y="20" width="10" height="5" rx="2.5" fill="#fff" opacity=".35"/></g>
    <g class="cloud slow"><rect x="120" y="40" width="14" height="4" rx="2" fill="#fff" opacity=".25"/></g>
    <rect x="9" y="80" width="170" height="15" fill="#3d5a44"/>
    <rect x="9" y="78" width="170" height="3" fill="{SAGE[1]}"/>
    <g transform="translate(108 66)">{pixels(BUG, 3, {'#': '#f08aa0'})}</g>
    <text class="xp" x="117" y="56" font-family="{MONO}" font-size="10" font-weight="700" fill="{BUTTER[0]}" text-anchor="middle">+1 xp</text>
    <g class="run"><g class="hop">
      <g class="leg-a">{pixels(RUNNER_A, 3, {'#': '#fff4e8', 'r': PEACH[1]}, 0, 48)}</g>
      <g class="leg-b">{pixels(RUNNER_B, 3, {'#': '#fff4e8', 'r': PEACH[1]}, 0, 48)}</g>
    </g></g>
    <text x="16" y="23" font-family="{MONO}" font-size="9" font-weight="700" fill="{SKY[0]}" opacity=".85">1-1</text>
  </g>
  <rect class="scan" x="9" y="9" width="170" height="86" rx="7" fill="url(#scan)"/>
</g>'''

    kb = iso.box(58, 92, 24, 128, 40, 7, SLATE_LIGHT)
    keys = [f'<rect x="{6 + col * 11.8:.1f}" y="{5 + row * 11}" width="9" height="8.5" rx="2" fill="#8c85b0"/>'
            for row in range(3) for col in range(10)]
    keys.append('<rect class="key" x="41.4" y="27" width="44" height="8.5" rx="2" fill="#8c85b0"/>')
    keys.append(f'<rect class="key k2" x="6" y="5" width="9" height="8.5" rx="2" fill="#8c85b0"/>')
    keyboard = f'{kb}<g transform="{iso.top_face(58, 92, 31)}">{"".join(keys)}</g>'

    note = (f'<g transform="{iso.top_face(196, 70, 24.5)}">'
            f'<rect x="2" y="3" width="40" height="40" rx="3" fill="{BUTTER[2]}"/>'
            f'<rect x="0" y="0" width="40" height="40" rx="3" fill="{BUTTER[0]}"/>'
            f'<path d="M7 12 H31 M7 20 H27 M7 28 H22" stroke="#d8b25a" stroke-width="2.4" stroke-linecap="round"/></g>')
    pad_shape = 'M14 4 H58 C68 4 74 12 72 22 L70 32 C69 39 62 42 56 37 L50 32 H22 L16 37 C10 42 3 39 2 32 L0 22 C-2 12 4 4 14 4 Z'
    controller = (f'<g transform="{iso.top_face(98, 146, 24)}">'
                  f'<path d="{pad_shape}" fill="{SAGE[2]}" transform="translate(4 6)"/>'
                  f'<path d="{pad_shape}" fill="{SAGE[0]}"/>'
                  f'<path d="M15 14 v10 M10 19 h10" stroke="#2e2a36" stroke-width="3.2" stroke-linecap="round"/>'
                  f'<circle cx="54" cy="15" r="3.2" fill="#f08aa0" class="blink"/><circle cx="61" cy="21" r="3.2" fill="#8fb6dc"/></g>')

    mug_x, mug_y = 226, 136
    mx, my = iso.p(mug_x, mug_y, 24)
    mug = (iso.cylinder(mug_x, mug_y, 24, 17, 34, PEACH)
           + f'<ellipse cx="{mx:.1f}" cy="{my - 34:.1f}" rx="14.5" ry="7.4" fill="#6b4336"/>'
           + f'<path d="M{mx + 19:.1f} {my - 26:.1f} c12 0 12 18 0 18" fill="none" stroke="{PEACH[1]}" stroke-width="6" stroke-linecap="round"/>'
           + ''.join(f'<path class="steam s{i}" d="M{mx - 6 + i * 6:.1f} {my - 44:.1f} c-6 -8 6 -12 0 -20 c-6 -8 6 -12 0 -20" fill="none" stroke="#fff" stroke-width="3.2" stroke-linecap="round"/>' for i in range(3)))
    px, py = iso.p(26, 168, 24)
    leaves = ''.join(
        f'<ellipse cx="0" cy="-22" rx="8" ry="22" fill="{c}" transform="rotate({a})"/>'
        for a, c in [(-38, SAGE[1]), (34, SAGE[1]), (-12, SAGE[0]), (14, '#c2dcb9')])
    plant = (iso.cylinder(26, 168, 24, 16, 26, ROSE)
             + f'<g class="sway" transform="translate({px:.1f} {py - 30:.1f})"><g>{leaves}</g></g>')

    gx, gy = iso.p(130, 30, 120)
    screen_glow = f'<ellipse class="glow" cx="{gx:.0f}" cy="{gy:.0f}" rx="170" ry="110" fill="url(#screenglow)"/>'
    desk = '\n'.join([slab, rim, *monitor, game, keyboard, note, controller, mug, plant])

    floaters = '\n'.join([
        f'<g class="float f1">{orb(958, 104, 22, PEACH, "ball")}</g>',
        f'<g class="float f2">{Iso(574, 82).box(0, 0, 0, 28, 28, 28, BUTTER)}</g>',
        f'<g class="float f3"><ellipse cx="946" cy="352" rx="20" ry="9" fill="none" stroke="{LILAC[1]}" stroke-width="9"/></g>',
        f'<g transform="translate(560 330)"><g class="float f4"><g class="spin">{coin(0, 0, 15, "coinA")}</g></g></g>',
    ])

    sx, sy = iso.p(130, 100, -40)
    ground = f'<ellipse class="shade" cx="{sx:.1f}" cy="{sy + 70:.1f}" rx="200" ry="26" fill="#000" opacity=".45"/>'

    # Words on the left.
    def name(text, y):
        layers = ''.join(f'<text x="60" y="{y + d}" font-family="{SANS}" font-size="64" font-weight="800" fill="{c}">{text}</text>'
                         for d, c in [(7, '#2b2346'), (5, '#4a3f78'), (3, '#6c5fa3')])
        return layers + f'<text x="60" y="{y}" font-family="{SANS}" font-size="64" font-weight="800" fill="url(#namefill)">{text}</text>'

    def chip(x, label, col):
        w = 40 + len(label) * 8.4
        return (f'<g transform="translate({x} 350)">{raised(0, 0, round(w), 34, 17, CARD, LIP, 4, CARD_TOP)}'
                f'<circle cx="18" cy="17" r="5" fill="{col[1]}"/>'
                f'<text x="30" y="22.5" font-family="{SANS}" font-size="14" font-weight="700" fill="{col[0]}">{label}</text></g>')

    hearts = ''.join(f'<g transform="translate({118 + i * 26} 37)">{pixels(HEART, 3, {"#": ROSE[1] if i < 3 else "#3a3452"})}</g>' for i in range(4))
    hud = f'''<g>
  <rect x="58" y="34" width="44" height="24" rx="8" fill="{BUTTER[1]}"/>
  <text x="80" y="51" font-family="{MONO}" font-size="13" font-weight="800" fill="#2e2a36" text-anchor="middle">1P</text>
  {hearts}
  <text x="942" y="51" font-family="{MONO}" font-size="12" font-weight="700" letter-spacing="1.4" fill="{TEXT_DIM}" text-anchor="end">STAGE 1-1 · PROFILE</text>
</g>'''

    words = '\n'.join([
        f'<text x="62" y="126" font-family="{MONO}" font-size="15" fill="{BUTTER[0]}">&gt; player 1 has joined: hi, i\'m</text>',
        name('Ruchira', 196),
        name('Edirisinghe', 266),
        f'<text x="62" y="318" font-family="{SANS}" font-size="19" font-weight="600" fill="{TEXT_SOFT}">I design interfaces, then make them playable.</text>',
        chip(60, 'UI/UX engineer', SKY),
        chip(222, 'game developer', PEACH),
        chip(384, 'vibe coder', LILAC),
        f'<text class="press" x="62" y="432" font-family="{MONO}" font-size="14" font-weight="800" letter-spacing="2.5" fill="{TEXT}">▶ PRESS START</text>',
    ])

    defs = f'''<defs>
  {shadow_filter('soft', 16, 16, 0.55)}
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2c3352"/><stop offset="1" stop-color="#5b5f8c"/></linearGradient>
  <linearGradient id="scan" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".12"/><stop offset=".5" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <radialGradient id="screenglow"><stop offset="0" stop-color="{LILAC[1]}" stop-opacity=".35"/><stop offset="1" stop-color="{LILAC[1]}" stop-opacity="0"/></radialGradient>
  <linearGradient id="namefill" x1="0" y1="0" x2="0" y2="1"><stop offset=".2" stop-color="#fffaf3"/><stop offset="1" stop-color="{LILAC[0]}"/></linearGradient>
</defs>'''

    style = TWINKLE + '''
.desk { animation: bob 6s ease-in-out infinite; }
.shade { animation: shade 6s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }
@keyframes bob { 50% { transform: translateY(-7px); } }
@keyframes shade { 50% { transform: scale(.94); opacity: .3; } }
.glow { animation: glow 4s ease-in-out infinite; }
@keyframes glow { 50% { opacity: .65; } }
.float { animation: bob 5s ease-in-out infinite; }
.f2 { animation-duration: 6.5s; animation-delay: -2s; }
.f3 { animation-duration: 7s; animation-delay: -4s; }
.f4 { animation-duration: 4.4s; animation-delay: -1s; }
.spin { animation: spin 2.2s linear infinite; transform-box: fill-box; transform-origin: center; }
@keyframes spin { 0%, 100% { transform: scaleX(1); } 50% { transform: scaleX(.12); } }
.steam { opacity: 0; animation: steam 3.6s ease-out infinite; }
.s1 { animation-delay: 1.2s; } .s2 { animation-delay: 2.4s; }
@keyframes steam { 0% { opacity: 0; transform: translateY(6px); } 30% { opacity: .6; } 100% { opacity: 0; transform: translateY(-14px); } }
.sway > g { animation: sway 4s ease-in-out infinite; transform-origin: 0 0; }
@keyframes sway { 50% { transform: rotate(5deg); } }
.blink { animation: blink 2.4s steps(1) infinite; }
@keyframes blink { 50% { opacity: .35; } }
.key { animation: key 3.2s ease-in-out infinite; }
.k2 { animation-delay: -1.4s; }
@keyframes key { 0%, 80%, 100% { fill: #8c85b0; } 88% { fill: #e0d7f7; } }
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
.press { animation: press 1.4s steps(1) infinite; }
@keyframes press { 60% { opacity: .2; } }
'''
    body = f'''{defs}
{panel(W, H, (LILAC[2], .75, .45, .55), 'h')}
{stars(W, H, 46)}
{hud}
{screen_glow}
{ground}
<g class="desk" filter="url(#soft)">
{desk}
</g>
{floaters}
{words}'''
    return svg(W, H, "Ruchira Edirisinghe: UI/UX engineer, game developer and vibe coder. I design interfaces, then make them playable.", body, style)


# ─────────────────────────────── buttons ───────────────────────────────

def button(kind, label, col, delay):
    W, H = 196, 62
    w = W - 8
    if kind == 'portfolio':
        icon = glyph('sparkles', 20, 16, 22, col[0], 2.3)
    else:
        icon = logo({'email': 'gmail'}.get(kind, kind), 21, 17, 20, '#1769ff' if kind == 'behance' else None)
    style = f'''
.cap {{ animation: tap 7s ease-in-out infinite; animation-delay: {delay}s; }}
@keyframes tap {{ 0%, 6%, 100% {{ transform: translateY(0); }} 3% {{ transform: translateY(4px); }} }}
.shine {{ animation: shine 7s ease-in-out infinite; animation-delay: {delay}s; }}
@keyframes shine {{ 0%, 4% {{ transform: skewX(-20deg) translateX(-60px); }} 18%, 100% {{ transform: skewX(-20deg) translateX(260px); }} }}
'''
    body = f'''<defs>{shadow_filter('s', 5, 5, 0.45)}
<clipPath id="pill"><rect x="4" y="5" width="{w}" height="44" rx="22"/></clipPath>
<linearGradient id="g" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".16"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient></defs>
<g filter="url(#s)">
<rect x="4" y="10" width="{w}" height="44" rx="22" fill="{LIP}"/>
<g class="cap">
<rect x="4" y="5" width="{w}" height="44" rx="22" fill="{CARD}"/>
<rect x="4.75" y="5.75" width="{w - 1.5}" height="42.5" rx="21.25" fill="none" stroke="{col[1]}" stroke-opacity=".55" stroke-width="1.5"/>
<g clip-path="url(#pill)"><rect class="shine" x="0" y="0" width="50" height="60" fill="url(#g)" transform="skewX(-20)"/></g>
<circle cx="31" cy="27" r="16" fill="{CARD_TOP}"/>
{icon}
<text x="56" y="32.5" font-family="{SANS}" font-size="16" font-weight="700" fill="{TEXT}">{label}</text>
<path d="M{w - 22} 22 l6 5 l-6 5" fill="none" stroke="{col[1]}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>
</g></g>'''
    return svg(W, H, label, body, style)


# ─────────────────────────────── about: quest log ───────────────────────────────

def about():
    W, H = 1000, 404
    cards = [
        (PEACH, 'briefcase', 'MAIN QUEST', 'IN PROGRESS', ['Funextreme', 'Technology LLC'], 'UI/UX + game dev', .72),
        (LILAC, 'cap', 'CLEARED', 'COMPLETE', ['BSc (Hons)', 'Computer Security'], 'University of Plymouth, UK', 1),
        (SAGE, 'pad', 'SIDE QUEST', 'ACTIVE', ['Game design', '& motion'], 'making things feel good', .58),
        (SKY, 'cube', 'UNLOCKED', 'NEW SKILL', ['3D & AI-powered', 'workflows'], 'Blender, Spline, Claude', .86),
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
                    f'<path d="M-21 -6 v12 M-27 0 h12" stroke="#2e2a36" stroke-width="3.6" stroke-linecap="round"/>'
                    f'<circle cx="18" cy="-4" r="4" fill="#f08aa0"/><circle cx="26" cy="4" r="4" fill="#8fb6dc"/>')
        return Iso(0, -40).box(0, 0, 0, 34, 34, 34, col)

    out = []
    cw, ch, gap, x0, y0 = 212, 262, 18, 49, 118
    for i, (col, kind, kicker, status, lines, sub, pct) in enumerate(cards):
        x = x0 + i * (cw + gap)
        text_lines = ''.join(
            f'<text x="20" y="{150 + j * 22}" font-family="{SANS}" font-size="18" font-weight="800" fill="{TEXT}">{esc(t)}</text>'
            for j, t in enumerate(lines))
        sw = 18 + len(status) * 6.9
        done = pct >= 1
        bar_w = cw - 40
        check = (f'<path d="M{cw - 26} {ch - 47} l3 3 l6 -6" fill="none" stroke="{col[1]}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>'
                 if done else f'<text x="{cw - 20}" y="{ch - 42}" font-family="{MONO}" font-size="11" font-weight="700" fill="{col[1]}" text-anchor="end">{round(pct * 100)}%</text>')
        out.append(f'''<g transform="translate({x} {y0})">
  {raised(0, 0, cw, ch, 24)}
  <rect x="{cw - 16 - sw:.0f}" y="16" width="{sw:.0f}" height="20" rx="10" fill="{col[2]}" fill-opacity=".18" stroke="{col[1]}" stroke-opacity=".5"/>
  <text x="{cw - 16 - sw / 2:.0f}" y="29.5" font-family="{MONO}" font-size="10" font-weight="800" letter-spacing=".8" fill="{col[0]}" text-anchor="middle">{status}</text>
  <ellipse cx="62" cy="90" rx="34" ry="7" fill="#000" opacity=".4"/>
  <g transform="translate(62 64)"><g class="obj o{i}">{object_(kind, col)}</g></g>
  <text x="20" y="124" font-family="{MONO}" font-size="11.5" letter-spacing="1.2" fill="{col[1]}" font-weight="800">{kicker}</text>
  {text_lines}
  <text x="20" y="{150 + len(lines) * 22 + 4}" font-family="{SANS}" font-size="13" fill="{TEXT_SOFT}">{esc(sub)}</text>
  <text x="20" y="{ch - 42}" font-family="{MONO}" font-size="11" font-weight="700" fill="{TEXT_DIM}">{'CLEARED' if done else 'PROGRESS'}</text>
  {check}
  <rect x="20" y="{ch - 32}" width="{bar_w}" height="12" rx="6" fill="{LIP}"/>
  <clipPath id="bar{i}"><rect x="20" y="{ch - 32}" width="{bar_w * pct:.0f}" height="12" rx="6"/></clipPath>
  <g clip-path="url(#bar{i})">
    <rect x="20" y="{ch - 32}" width="{bar_w}" height="12" fill="{col[1]}"/>
    <rect x="20" y="{ch - 32}" width="{bar_w}" height="5" fill="#fff" opacity=".3"/>
    <rect class="sheen" style="animation-delay:{i * .6:.1f}s" x="-20" y="{ch - 32}" width="26" height="12" fill="#fff" opacity=".45" transform="skewX(-20)"/>
  </g>
</g>''')

    style = '''
.obj { animation: lift 4.5s ease-in-out infinite; }
.o1 { animation-delay: -1.1s; } .o2 { animation-delay: -2.2s; } .o3 { animation-delay: -3.3s; }
@keyframes lift { 50% { transform: translate(0, -6px); } }
.sheen { animation: sheen 3.2s ease-in-out infinite; }
@keyframes sheen { 0% { transform: skewX(-20deg) translateX(0); } 60%, 100% { transform: skewX(-20deg) translateX(260px); } }
'''
    body = f'''<defs>{shadow_filter('soft', 10, 12, 0.45)}</defs>
{panel(W, H, (PEACH[2], .1, 0, .6), 'a')}
{header('a little about me', 'QUEST LOG', PEACH, '4 QUESTS · 1 CLEARED', 50, 40)}
<g filter="url(#soft)">{''.join(out)}</g>'''
    return svg(W, H, 'About me: UI/UX engineer and game developer at Funextreme Technology LLC; BSc (Hons) Computer Security, University of Plymouth, UK; exploring game design, motion, 3D and AI-powered workflows.', body, style)


# ─────────────────────────────── stack: inventory ───────────────────────────────

GROUPS = [
    ('DESIGN & 3D', PEACH, [('Figma', 'figma'), ('Framer', 'framer'), ('Spline', 'spline'), ('Photoshop', 'photoshop'),
                            ('Illustrator', 'illustrator'), ('Blender', 'blender')]),
    ('CODE & GAMES', SKY, [('HTML', 'html'), ('CSS', 'css'), ('JavaScript', 'javascript'), ('TypeScript', 'typescript'),
                           ('React', 'react'), ('Tailwind', 'tailwind'), ('Python', 'python'), ('Unity', 'unity'), ('C#', 'csharp')]),
    ('AI & WORKFLOW', LILAC, [('Claude', 'claude'), ('ChatGPT', 'chatgpt'), ('Gemini', 'gemini'), ('Cursor', 'cursor'),
                              ('Copilot', 'copilot'), ('Midjourney', 'midjourney'), ('Git', 'git'), ('GitHub', 'github'), ('Vercel', 'vercel')]),
]


def stack():
    W = 1000
    sw, sh, gap = 88, 100, 14
    x0 = (W - (9 * sw + 8 * gap)) / 2
    out, y, n = [], 136, 0
    total = sum(len(t) for _, _, t in GROUPS)
    for title, col, tools in GROUPS:
        out.append(f'<circle cx="{x0 + 5}" cy="{y - 5}" r="4" fill="{col[1]}"/>'
                   f'<text x="{x0 + 16}" y="{y}" font-family="{MONO}" font-size="12" font-weight="800" letter-spacing="1.4" fill="{col[0]}">{esc(title)}</text>'
                   f'<path d="M{x0 + 30 + len(title) * 8.4:.0f} {y - 4} H{W - x0}" stroke="{EDGE}" stroke-width="1.5" stroke-dasharray="2 6" stroke-linecap="round"/>')
        y += 16
        for i, (name, key) in enumerate(tools):
            x = x0 + i * (sw + gap)
            out.append(f'''<g transform="translate({x:.0f} {y})">
  {raised(0, 0, sw, sh, 18)}
  <rect x="8" y="8" width="{sw - 16}" height="60" rx="13" fill="{SLOT}"/>
  <rect x="8.75" y="8.75" width="{sw - 17.5}" height="58.5" rx="12.25" fill="none" stroke="{col[2]}" stroke-opacity=".35" stroke-width="1.5"/>
  <ellipse cx="{sw / 2}" cy="60" rx="18" ry="3.5" fill="#000" opacity=".5"/>
  <g class="item" style="animation-delay:{-n * .37:.2f}s">{logo(key, sw / 2 - 17, 21, 34)}</g>
  <clipPath id="c{n}"><rect x="8" y="8" width="{sw - 16}" height="60" rx="13"/></clipPath>
  <g clip-path="url(#c{n})"><rect class="glint" style="animation-delay:{n * .16:.2f}s" x="-30" y="0" width="22" height="80" fill="#fff" opacity=".13" transform="skewX(-22)"/></g>
  <text x="{sw / 2}" y="88" font-family="{SANS}" font-size="12.5" font-weight="700" fill="{TEXT}" text-anchor="middle">{esc(name)}</text>
</g>''')
            n += 1
        y += sh + 44
    H = y - 14
    style = '''
.item { animation: hover 3.6s ease-in-out infinite; }
@keyframes hover { 50% { transform: translateY(-3px); } }
.glint { animation: glint 9s ease-in-out infinite; }
@keyframes glint { 0% { transform: skewX(-22deg) translateX(0); } 8%, 100% { transform: skewX(-22deg) translateX(150px); } }
'''
    body = f'''<defs>{shadow_filter('soft', 6, 6, 0.45)}</defs>
{panel(W, H, (SKY[2], .9, .1, .6), 's')}
{header('my toolbox', 'INVENTORY', SKY, f'{total}/{total} ITEMS EQUIPPED', x0, 40)}
<g filter="url(#soft)">{''.join(out)}</g>'''
    names = ', '.join(name for _, _, tools in GROUPS for name, _ in tools)
    return svg(W, H, f'My toolbox: {names}', body, style)


# ─────────────────────────────── divider & footer ───────────────────────────────

def divider():
    W, H = 1000, 44
    coins = ''.join(
        f'<g transform="translate({440 + i * 30} 20)"><g class="b" style="animation-delay:{i * .18:.2f}s">'
        f'<g class="spin" style="animation-delay:{-i * .3:.1f}s">{coin(0, 0, 9, f"c{i}")}</g></g></g>' for i in range(5))
    style = '''
.b { animation: bead 3s ease-in-out infinite; }
@keyframes bead { 0%, 40%, 100% { transform: translateY(0); } 20% { transform: translateY(-6px); } }
.spin { animation: spin 2.4s linear infinite; transform-box: fill-box; transform-origin: center; }
@keyframes spin { 0%, 100% { transform: scaleX(1); } 50% { transform: scaleX(.12); } }
'''
    body = (f'<path d="M60 22 H400 M600 22 H940" stroke="{LILAC[2]}" stroke-opacity=".55" stroke-width="2.5" stroke-linecap="round" stroke-dasharray="1 9"/>{coins}')
    return svg(W, H, '', body, style)


def footer():
    W, H = 1000, 250
    iso = Iso(790, 84)
    base = iso.box(0, 0, 0, 120, 120, 22, SLATE)
    bx, by = iso.p(60, 60, 22)
    button_ = (f'<g class="btn"><ellipse cx="{bx:.1f}" cy="{by + 4:.1f}" rx="44" ry="23" fill="#c76a82"/>'
               f'<ellipse cx="{bx:.1f}" cy="{by - 6:.1f}" rx="44" ry="23" fill="{ROSE[1]}"/>'
               f'<ellipse cx="{bx - 10:.1f}" cy="{by - 12:.1f}" rx="18" ry="7" fill="#fff" opacity=".45"/></g>')
    gx, gy = iso.p(60, 60, 0)
    halo = f'<ellipse class="halo" cx="{gx:.0f}" cy="{gy - 20:.0f}" rx="150" ry="80" fill="url(#halo)"/>'
    sparks = ''.join(
        f'<path d="M{bx + 66 * math.cos(a):.0f} {by - 6 + 38 * math.sin(a):.0f} l{12 * math.cos(a):.0f} {8 * math.sin(a):.0f}" stroke="{BUTTER[1]}" stroke-width="3" stroke-linecap="round"/>'
        for a in [math.radians(d) for d in (200, 235, 270, 305, 340)])
    digits = ''.join(f'<text class="d" style="animation-delay:{k - 10}s{";opacity:1" if k == 0 else ""}" x="186" y="160" '
                     f'font-family="{MONO}" font-size="20" font-weight="800" fill="{ROSE[0]}">{9 - k}</text>' for k in range(10))
    style = TWINKLE + '''
.btn { animation: push 3s ease-in-out infinite; }
@keyframes push { 0%, 70%, 100% { transform: translateY(0); } 80% { transform: translateY(8px); } }
.spark { opacity: 0; animation: spark 3s ease-out infinite; transform-box: fill-box; transform-origin: center; }
@keyframes spark { 0%, 78% { opacity: 0; transform: scale(.6); } 85% { opacity: 1; } 100% { opacity: 0; transform: scale(1.25); } }
.halo { animation: halo 3s ease-in-out infinite; }
@keyframes halo { 0%, 70%, 100% { opacity: .5; } 82% { opacity: 1; } }
.caret, .coin { animation: caret 1s steps(1) infinite; }
@keyframes caret { 50% { opacity: 0; } }
.d { opacity: 0; animation: cd 10s steps(1) infinite; }
@keyframes cd { 0% { opacity: 1; } 10%, 100% { opacity: 0; } }
'''
    body = f'''<defs>{shadow_filter('soft', 14, 14, 0.55)}
<radialGradient id="halo"><stop offset="0" stop-color="{ROSE[1]}" stop-opacity=".3"/><stop offset="1" stop-color="{ROSE[1]}" stop-opacity="0"/></radialGradient></defs>
{panel(W, H, (ROSE[2], .8, .5, .5), 'f')}
{stars(W, H, 22, 11)}
<text x="62" y="72" font-family="{MONO}" font-size="13" font-weight="800" letter-spacing="2" fill="{ROSE[1]}">GAME OVER? NOT YET.</text>
<text x="60" y="118" font-family="{SANS}" font-size="36" font-weight="800" fill="{TEXT}">thanks for playing!</text>
<text x="62" y="160" font-family="{MONO}" font-size="20" font-weight="800" fill="{BUTTER[0]}">CONTINUE?</text>{digits}
<text x="62" y="194" font-family="{SANS}" font-size="16" font-weight="600" fill="{TEXT_SOFT}">press the big button to see what i'm building lately</text>
<text x="62" y="224" font-family="{MONO}" font-size="14" fill="{PEACH[1]}">ruchiraedirisinghe.vercel.app<tspan class="caret" fill="{TEXT}">_</tspan></text>
{halo}
<g class="spark">{sparks}</g>
<g filter="url(#soft)">{base}{button_}</g>
<text class="coin" x="{gx:.0f}" y="232" font-family="{MONO}" font-size="12" font-weight="800" letter-spacing="2" fill="{BUTTER[1]}" text-anchor="middle">INSERT COIN</text>'''
    return svg(W, H, "Thanks for playing! Press the button to visit my website.", body, style)


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
