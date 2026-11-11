"""Draws the live GitHub stat cards in the README's dark arcade theme (see
theme.py): player stats with a level and XP bar, the contribution streak,
top languages, contributions per month and achievements. Run by
.github/workflows/profile-assets.yml, which publishes them to the `output` branch.

Usage: GITHUB_TOKEN=... python stat_cards.py <github-user> <out-dir>
"""
import datetime as dt
import json
import math
import os
import re
import sys
import urllib.request
from collections import Counter

from theme import (BUTTER, CARD_TOP, EDGE, LILAC, LIP, MONO, PEACH, ROSE, SAGE, SANS, SKY, SLATE, SLOT, TEXT, TEXT_DIM,
                   TEXT_SOFT, TWINKLE, esc, glyph, header, orb, panel, raised, shadow_filter, stars, svg)

INK = '#2e2a36'


# ───────────────────────────── data ─────────────────────────────

def get(url, data=None, headers=None):
    req = urllib.request.Request(url, data=data, headers={'User-Agent': 'profile-stat-cards', **(headers or {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode('utf-8')


def gql(query, **variables):
    body = json.dumps({'query': query, 'variables': variables}).encode()
    res = json.loads(get('https://api.github.com/graphql', body, {'Authorization': f"Bearer {os.environ['GITHUB_TOKEN']}"}))
    if res.get('errors'):
        raise RuntimeError(res['errors'])
    return res['data']


USER_QUERY = '''query($login: String!) { user(login: $login) {
  createdAt
  followers { totalCount }
  pullRequests { totalCount }
  issues { totalCount }
  repositoriesContributedTo(contributionTypes: [COMMIT, ISSUE, PULL_REQUEST, REPOSITORY]) { totalCount }
  allRepos: repositories(ownerAffiliations: OWNER, privacy: PUBLIC) { totalCount }
  repositories(first: 100, ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC) { nodes {
    stargazerCount
    primaryLanguage { name color }
    languages(first: 10, orderBy: { field: SIZE, direction: DESC }) { edges { size node { name color } } }
  } }
  contributionsCollection { contributionYears }
} }'''

YEAR_QUERY = '''query($login: String!, $from: DateTime!, $to: DateTime!) { user(login: $login) {
  contributionsCollection(from: $from, to: $to) {
    totalCommitContributions
    contributionCalendar { weeks { contributionDays { date contributionCount } } }
  }
} }'''


def profile_views(user):
    # komarev only counts requests from GitHub's image proxy, so reading it here doesn't add a view.
    try:
        nums = re.findall(r'>([\d,]+)<', get(f'https://komarev.com/ghpvc/?username={user}'))
        return int(nums[-1].replace(',', '')) if nums else None
    except Exception as e:
        print(f'::warning::profile views: {e}')
        return None


def collect(login):
    u = gql(USER_QUERY, login=login)['user']
    days, commits = {}, 0
    for year in u['contributionsCollection']['contributionYears']:
        c = gql(YEAR_QUERY, login=login, **{'from': f'{year}-01-01T00:00:00Z', 'to': f'{year}-12-31T23:59:59Z'})
        cc = c['user']['contributionsCollection']
        commits += cc['totalCommitContributions']
        for week in cc['contributionCalendar']['weeks']:
            for d in week['contributionDays']:
                days[dt.date.fromisoformat(d['date'])] = d['contributionCount']

    today = dt.datetime.now(dt.timezone.utc).date()
    days = {d: n for d, n in days.items() if d <= today}
    order = sorted(days)

    # Streaks. Today doesn't break the current streak until it's over.
    longest, run, run_start, best = 0, 0, None, (None, None)
    for d in order:
        if days[d]:
            run_start = d if run == 0 else run_start
            run += 1
            if run > longest:
                longest, best = run, (run_start, d)
        else:
            run = 0
    current, cur_end = 0, today if days.get(today) else today - dt.timedelta(days=1)
    d = cur_end
    while days.get(d):
        current += 1
        d -= dt.timedelta(days=1)
    cur_start = d + dt.timedelta(days=1)

    # Contributions in each of the last 12 months, this month included.
    months = []
    y, m = today.year, today.month
    for _ in range(12):
        months.append((y, m))
        y, m = (y, m - 1) if m > 1 else (y - 1, 12)
    months.reverse()
    per_month = Counter()
    for d in order:
        per_month[(d.year, d.month)] += days[d]

    langs, lang_color, repos_per_lang, stars_ = Counter(), {}, Counter(), 0
    for r in u['repositories']['nodes']:
        stars_ += r['stargazerCount']
        if r['primaryLanguage']:
            repos_per_lang[r['primaryLanguage']['name']] += 1
        for e in r['languages']['edges']:
            langs[e['node']['name']] += e['size']
            lang_color[e['node']['name']] = e['node']['color'] or '#8b8b9e'

    return {
        'joined': dt.date.fromisoformat(u['createdAt'][:10]),
        'today': today,
        'total': sum(days.values()),
        'commits': commits,
        'prs': u['pullRequests']['totalCount'],
        'issues': u['issues']['totalCount'],
        'contributed': u['repositoriesContributedTo']['totalCount'],
        'followers': u['followers']['totalCount'],
        'repos': u['allRepos']['totalCount'],
        'stars': stars_,
        'views': profile_views(login),
        'current': current, 'current_range': (cur_start, cur_end) if current else None,
        'longest': longest, 'longest_range': best,
        'months': [(dt.date(y, m, 1), per_month[(y, m)]) for y, m in months],
        'langs': [(name, size, lang_color[name]) for name, size in langs.most_common()],
        'repos_per_lang': repos_per_lang,
    }


# ───────────────────────────── helpers ─────────────────────────────

def fmt(n):
    if n is None:
        return '—'
    if n >= 1_000_000:
        return f'{n / 1_000_000:.1f}M'.replace('.0M', 'M')
    if n >= 10_000:
        return f'{n / 1000:.1f}k'.replace('.0k', 'k')
    return f'{n:,}'


def day(d):
    return f'{d:%b} {d.day}, {d.year}' if d else ''


def span(r):
    if not r or not r[0]:
        return 'start one today'
    a, b = r
    if a == b:
        return day(a)
    return f'{a:%b} {a.day} – {b:%b} {b.day}, {b.year}' if a.year == b.year else f'{day(a)} – {day(b)}'


def level(xp):
    lv = int(math.sqrt(xp / 20)) + 1
    lo, hi = 20 * (lv - 1) ** 2, 20 * lv ** 2
    title = next(t for cap, t in [(5, 'Rookie'), (10, 'Adventurer'), (15, 'Hero'), (20, 'Champion'), (30, 'Mythic'), (10 ** 9, 'Legend')] if lv < cap)
    return lv, title, (xp - lo) / (hi - lo), hi - xp


_bars = [0]


def bar(x, y, w, h, pct, color, cls='fill', delay=0):
    """A sunken track with a clay fill; a glint runs along the fill now and then."""
    fw = max(w * min(pct, 1), h if pct > 0 else 0)
    track = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h / 2}" fill="{LIP}"/>'
    if not fw:
        return track
    _bars[0] += 1
    cid = f'bar{_bars[0]}'
    return (track
            + f'<clipPath id="{cid}"><rect x="{x}" y="{y}" width="{fw:.1f}" height="{h}" rx="{h / 2}"/></clipPath>'
            f'<g clip-path="url(#{cid})"><rect x="{x}" y="{y}" width="{fw:.1f}" height="{h}" fill="{color}"/>'
            f'<rect x="{x}" y="{y + h * .15:.1f}" width="{fw:.1f}" height="{h * .3:.1f}" fill="#fff" opacity=".3"/>'
            f'<rect class="{cls}" style="animation-delay:{delay}s" x="{x - 30}" y="{y - 2}" width="18" height="{h + 4}" fill="#fff" opacity=".45"/></g>')


GROW = '''
.fill { animation: glint 4s ease-in-out infinite; }
@keyframes glint { 0% { transform: translateX(0); } 45%, 100% { transform: translateX(400px); } }
'''


# ───────────────────────────── cards ─────────────────────────────

def player(s):
    W, H = 1000, 340
    lv, title, pct, to_next = level(s['total'])
    tiles = [
        ('star', BUTTER, s['stars'], 'Stars earned'),
        ('git-commit-horizontal', PEACH, s['commits'], 'Commits'),
        ('git-pull-request', LILAC, s['prs'], 'Pull requests'),
        ('bug', ROSE, s['issues'], 'Issues opened'),
        ('folder-git-2', SKY, s['contributed'], 'Contributed to'),
        ('users', SAGE, s['followers'], 'Followers'),
        ('book-marked', PEACH, s['repos'], 'Public repos'),
        ('eye', SKY, s['views'], 'Profile views'),
    ]
    tw, th, gap, tx0, ty0 = 128, 92, 12, 418, 128
    out = []
    for i, (icon, col, value, label) in enumerate(tiles):
        x, y = tx0 + (i % 4) * (tw + gap), ty0 + (i // 4) * (th + gap + 4)
        out.append(f'''<g transform="translate({x} {y})">{raised(0, 0, tw, th, 18)}
  <g class="pop" style="animation-delay:{-i * .4:.1f}s"><circle cx="30" cy="30" r="16" fill="{col[1]}"/><circle cx="30" cy="27" r="16" fill="{col[0]}"/>{glyph(icon, 21, 18, 18, INK, 2.4)}</g>
  <text x="54" y="25" font-family="{SANS}" font-size="11.5" font-weight="600" fill="{TEXT_SOFT}">{esc(label.split(' ')[0])}</text>
  <text x="54" y="39" font-family="{SANS}" font-size="11.5" font-weight="600" fill="{TEXT_SOFT}">{esc(' '.join(label.split(' ')[1:]))}</text>
  <text x="16" y="76" font-family="{SANS}" font-size="25" font-weight="800" fill="{TEXT}">{fmt(value)}</text>
</g>''')

    medal = f'''<g transform="translate(118 196)"><g class="bob">
  <ellipse cx="0" cy="78" rx="52" ry="9" fill="#000" opacity=".45" class="shadow"/>
  <circle cx="0" cy="8" r="62" fill="#5f4f99"/>
  {orb(0, 0, 62, LILAC, 'medal')}
  <circle cx="0" cy="0" r="48" fill="none" stroke="#fff" stroke-opacity=".45" stroke-width="3" stroke-dasharray="3 7" class="ring"/>
  <text x="0" y="-14" font-family="{MONO}" font-size="14" font-weight="800" letter-spacing="2" fill="#4a3f78" text-anchor="middle">LV</text>
  <text x="0" y="28" font-family="{SANS}" font-size="44" font-weight="900" fill="{INK}" text-anchor="middle">{lv}</text>
</g></g>'''
    stats_text = f'''
<text x="206" y="166" font-family="{MONO}" font-size="11.5" font-weight="800" letter-spacing="1.5" fill="{LILAC[1]}">CLASS</text>
<text x="206" y="192" font-family="{SANS}" font-size="24" font-weight="800" fill="{TEXT}">{title}</text>
<text x="206" y="218" font-family="{SANS}" font-size="13" fill="{TEXT_SOFT}">{fmt(s['total'])} XP earned</text>
<text x="206" y="236" font-family="{SANS}" font-size="13" fill="{TEXT_SOFT}">since {s['joined']:%b %Y}</text>
<text x="56" y="296" font-family="{MONO}" font-size="11" font-weight="800" letter-spacing="1.2" fill="{TEXT_DIM}">XP</text>
<text x="380" y="296" font-family="{MONO}" font-size="11" font-weight="700" fill="{BUTTER[0]}" text-anchor="end">{fmt(to_next)} TO LV {lv + 1}</text>
{bar(56, 304, 324, 14, pct, BUTTER[1])}'''
    style = GROW + '''
.bob { animation: bob 4s ease-in-out infinite; }
@keyframes bob { 50% { transform: translateY(-6px); } }
.ring { animation: ring 14s linear infinite; transform-box: fill-box; transform-origin: center; }
@keyframes ring { to { transform: rotate(360deg); } }
.pop { animation: pop 6s ease-in-out infinite; }
@keyframes pop { 0%, 8%, 100% { transform: translateY(0); } 4% { transform: translateY(-4px); } }
'''
    body = f'''<defs>{shadow_filter('soft', 8, 8, 0.45)}</defs>
{panel(W, H, (LILAC[2], .12, .6, .5), 'pl')}
{header('my stats', 'PLAYER STATS', LILAC, f'1 CONTRIBUTION = 1 XP · SYNCED {s["today"]:%b} {s["today"].day}'.upper(), 50, 40)}
<g filter="url(#soft)">{medal}{''.join(out)}</g>
{stats_text}'''
    label = (f"Level {lv} {title}: {s['total']:,} contributions. Stars {s['stars']}, commits {s['commits']}, pull requests {s['prs']}, "
             f"issues {s['issues']}, contributed to {s['contributed']} repos, {s['followers']} followers, {s['repos']} public repos, {fmt(s['views'])} profile views.")
    return svg(W, H, label, body, style)


def streak(s):
    W, H = 490, 290
    cx = W / 2

    def column(x, value, label, sub, col):
        return (f'<text x="{x}" y="196" font-family="{SANS}" font-size="28" font-weight="800" fill="{TEXT}" text-anchor="middle">{value}</text>'
                f'<text x="{x}" y="222" font-family="{SANS}" font-size="13" font-weight="700" fill="{col}" text-anchor="middle">{label}</text>'
                f'<text x="{x}" y="242" font-family="{SANS}" font-size="11" fill="{TEXT_DIM}" text-anchor="middle">{esc(sub)}</text>')

    ring = f'''<g transform="translate({cx} 170)">
  <circle r="52" fill="{LIP}"/>
  <circle r="46" fill="none" stroke="url(#ringg)" stroke-width="9" class="spin" stroke-dasharray="230 60" stroke-linecap="round"/>
  <circle r="36" fill="{CARD_TOP}"/>
  <text y="12" font-family="{SANS}" font-size="32" font-weight="900" fill="{TEXT}" text-anchor="middle">{s['current']}</text>
  <g transform="translate(0 -60)" class="flame"><g transform="translate(-17 -24)">
    <path d="M17 2c3 7 13 11 13 23a13 13 0 0 1-26 0c0-6 3-10 6-13 0 5 3 7 5 7-1-6 0-12 2-17Z" fill="{PEACH[2]}"/>
    <path d="M17 14c2 5 7 7 7 13a7 7 0 0 1-14 0c0-3 2-5 3-6 1 3 2 4 3 4 0-4 0-7 1-11Z" fill="{BUTTER[0]}"/>
  </g></g>
</g>'''
    body = f'''<defs>{shadow_filter('soft', 8, 8, 0.45)}
<linearGradient id="ringg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BUTTER[1]}"/><stop offset="1" stop-color="{PEACH[2]}"/></linearGradient></defs>
{panel(W, H, (PEACH[2], .5, .6, .5), 'st')}
{stars(W, H, 14, 3)}
{header('streak', 'COMBO', PEACH, '', 36, 34)}
<text x="{W - 36}" y="50.5" font-family="{MONO}" font-size="12" font-weight="700" letter-spacing="1.4" fill="{TEXT_DIM}" text-anchor="end">x{s['current']} COMBO</text>
{column(78, fmt(s['total']), 'Total XP', f"since {s['joined']:%b} {s['joined'].year}", SKY[1])}
{column(W - 78, s['longest'], 'Best combo', span(s['longest_range']), LILAC[1])}
<g filter="url(#soft)">{ring}</g>
<text x="{cx}" y="252" font-family="{SANS}" font-size="13" font-weight="700" fill="{PEACH[1]}" text-anchor="middle">Current streak</text>
<text x="{cx}" y="270" font-family="{SANS}" font-size="11" fill="{TEXT_DIM}" text-anchor="middle">{esc(span(s['current_range']))}</text>'''
    style = TWINKLE + '''
.spin { animation: spin 6s linear infinite; transform-box: fill-box; transform-origin: center; }
@keyframes spin { to { transform: rotate(360deg); } }
.flame { animation: flick 1.2s ease-in-out infinite; transform-box: fill-box; transform-origin: 50% 100%; }
@keyframes flick { 50% { transform: scale(1.08, .94) rotate(-3deg); } }
'''
    label = f"Contribution streak: {s['current']} days now, best {s['longest']} days, {s['total']:,} contributions in total."
    return svg(W, H, label, body, style)


def languages(s):
    W, H = 490, 290
    top = s['langs'][:6]
    total = sum(size for _, size, _ in s['langs']) or 1
    rows = []
    for i, (name, size, color) in enumerate(top):
        y = 112 + i * 28
        n = s['repos_per_lang'].get(name, 0)
        rows.append(f'<circle cx="42" cy="{y + 6}" r="5" fill="{color}"/>'
                    f'<text x="54" y="{y + 11}" font-family="{SANS}" font-size="13.5" font-weight="700" fill="{TEXT}">{esc(name)}</text>'
                    f'{bar(150, y, 180, 12, size / total, color, "fill", i * .12)}'
                    f'<text x="384" y="{y + 11}" font-family="{MONO}" font-size="12" font-weight="700" fill="{TEXT_SOFT}" text-anchor="end">{size / total * 100:.1f}%</text>'
                    + (f'<text x="{W - 36}" y="{y + 11}" font-family="{MONO}" font-size="11" fill="{TEXT_DIM}" text-anchor="end">{n} repo{"s" if n > 1 else ""}</text>' if n else ''))
    body = f'''{panel(W, H, (SKY[2], .9, .1, .6), 'lg')}
{header('top languages', 'SKILL TREE', SKY, '', 36, 34)}
<text x="{W - 36}" y="50.5" font-family="{MONO}" font-size="12" font-weight="700" letter-spacing="1.4" fill="{TEXT_DIM}" text-anchor="end">BY CODE SIZE</text>
{''.join(rows)}'''
    label = 'Top languages: ' + ', '.join(f'{n} {sz / total * 100:.0f}%' for n, sz, _ in top)
    return svg(W, H, label, body, GROW)


def activity(s):
    W, H = 1000, 320
    months = s['months']
    peak = max((n for _, n in months), default=0) or 1
    best = max(range(len(months)), key=lambda i: months[i][1])
    step, bw, x0, base, maxh = 72, 40, 76, 262, 130
    out = []
    floor = (f'<path d="M{x0 - 26} {base + 4} H{x0 + step * 11 + bw + 26} l14 -10 H{x0 - 12} Z" fill="{SLATE[0]}"/>'
             f'<rect x="{x0 - 26}" y="{base + 4}" width="{step * 11 + bw + 52}" height="14" rx="3" fill="{SLATE[2]}"/>')
    for i, (month, n) in enumerate(months):
        h = max(n / peak * maxh, 4)
        x = x0 + i * step
        col = BUTTER if i == best and n else (SAGE if n else SLATE)
        top = base - h
        out.append(f'''<g class="col" style="animation-delay:{-i * .23:.2f}s">
  <path d="M{x + bw} {top} l10 -8 V{base - 8} l-10 8 Z" fill="{col[2]}"/>
  <path d="M{x} {top} l10 -8 H{x + bw + 10} l-10 8 Z" fill="{col[0]}"/>
  <rect x="{x}" y="{top}" width="{bw}" height="{h}" fill="{col[1]}"/>
  <rect x="{x + 5}" y="{top + 4}" width="6" height="{max(h - 10, 0):.1f}" rx="3" fill="#fff" opacity=".25"/>
</g>
<text x="{x + bw / 2 + 5}" y="{top - 16:.0f}" font-family="{MONO}" font-size="11.5" font-weight="700" fill="{BUTTER[0] if i == best else TEXT_SOFT}" text-anchor="middle">{fmt(n)}</text>
<text x="{x + bw / 2}" y="{base + 40}" font-family="{MONO}" font-size="11" font-weight="700" fill="{TEXT_DIM}" text-anchor="middle">{month:%b}</text>''')
    bx = x0 + best * step + bw / 2 + 5
    btop = base - max(months[best][1] / peak * maxh, 4)
    crown = (f'<g transform="translate({bx} {btop - 46:.0f})"><g class="crown">{glyph("crown", -11, -11, 22, BUTTER[1], 2.4)}</g></g>'
             if months[best][1] else '')
    year_total = sum(n for _, n in months)
    body = f'''<defs>{shadow_filter('soft', 8, 8, 0.45)}</defs>
{panel(W, H, (SAGE[2], .5, .9, .6), 'ac')}
{header('xp per month', 'ACTIVITY LOG', SAGE, f'{fmt(year_total)} XP IN THE LAST 12 MONTHS', 50, 40)}
<g filter="url(#soft)">{floor}{''.join(out)}</g>
{crown}'''
    style = '''
.col { animation: eq 2.8s ease-in-out infinite; transform-box: fill-box; transform-origin: bottom; }
@keyframes eq { 0%, 100% { transform: scaleY(1); } 50% { transform: scaleY(.93); } }
.crown { animation: crown 2.4s ease-in-out infinite; }
@keyframes crown { 50% { transform: translateY(-5px) rotate(-6deg); } }
'''
    label = 'Contributions per month: ' + ', '.join(f'{m:%b %Y} {n}' for m, n in months)
    return svg(W, H, label, body, style)


def achievements(s):
    W = 1000
    langs = len(s['langs'])
    list_ = [
        ('hand-metal', 'Hello World', 'First contribution', s['total'], 1, SKY),
        ('flame', 'On Fire', 'A 7-day streak', s['longest'], 7, PEACH),
        ('zap', 'Unstoppable', 'A 30-day streak', s['longest'], 30, BUTTER),
        ('swords', 'Grinder', '1,000 contributions', s['total'], 1000, ROSE),
        ('git-merge', 'Merge Master', '100 pull requests', s['prs'], 100, LILAC),
        ('bug', 'Bug Hunter', '10 issues opened', s['issues'], 10, SAGE),
        ('code-xml', 'Polyglot', '5 languages used', langs, 5, SKY),
        ('star', 'Rising Star', '10 stars earned', s['stars'], 10, BUTTER),
        ('users', 'Party Up', '10 followers', s['followers'], 10, PEACH),
        ('compass', 'Explorer', 'Help out 10 repos', s['contributed'], 10, LILAC),
    ]
    got = sum(v >= goal for _, _, _, v, goal, _ in list_)
    tw, th, gap = 172, 118, 10
    x0, y0 = (W - (5 * tw + 4 * gap)) / 2, 128
    out = []
    for i, (icon, name, desc, value, goal, col) in enumerate(list_):
        x, y = x0 + (i % 5) * (tw + gap), y0 + (i // 5) * (th + gap + 6)
        done = value >= goal
        medal = (f'<g class="medal" style="animation-delay:{-i * .5:.1f}s"><circle cx="34" cy="40" r="22" fill="{col[2]}"/><circle cx="34" cy="37" r="22" fill="{col[0]}"/>'
                 f'<circle cx="34" cy="37" r="17" fill="none" stroke="#fff" stroke-opacity=".5" stroke-width="1.5"/>'
                 f'{glyph(icon, 24, 27, 20, INK, 2.3)}</g>'
                 if done else
                 f'<circle cx="34" cy="40" r="22" fill="{LIP}"/><circle cx="34" cy="37" r="22" fill="{SLOT}"/>'
                 f'<circle cx="34" cy="37" r="21" fill="none" stroke="{EDGE}" stroke-width="1.5" stroke-dasharray="3 4"/>'
                 f'{glyph("lock", 26, 29, 16, TEXT_DIM, 2.2)}')
        out.append(f'''<g transform="translate({x:.0f} {y})">{raised(0, 0, tw, th, 18)}
  {medal}
  <text x="66" y="36" font-family="{SANS}" font-size="14" font-weight="800" fill="{TEXT if done else TEXT_SOFT}">{esc(name)}</text>
  <text x="66" y="53" font-family="{SANS}" font-size="11" fill="{TEXT_DIM}">{esc(desc)}</text>
  <text x="14" y="88" font-family="{MONO}" font-size="10" font-weight="800" letter-spacing="1" fill="{col[1] if done else TEXT_DIM}">{'UNLOCKED' if done else 'LOCKED'}</text>
  <text x="{tw - 14}" y="88" font-family="{MONO}" font-size="10" font-weight="700" fill="{TEXT_SOFT}" text-anchor="end">{fmt(min(value, goal))}/{fmt(goal)}</text>
  {bar(14, 96, tw - 28, 8, value / goal, col[1] if done else SLATE[0], 'fill', i * .08)}
</g>''')
    H = y0 + 2 * th + gap + 46
    style = GROW + '''
.medal { animation: medal 5s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }
@keyframes medal { 0%, 84%, 100% { transform: rotate(0); } 88% { transform: rotate(-12deg) scale(1.06); } 94% { transform: rotate(8deg) scale(1.06); } }
'''
    body = f'''<defs>{shadow_filter('soft', 6, 6, 0.45)}</defs>
{panel(W, H, (BUTTER[2], .85, .1, .5), 'ach')}
{header('trophy case', 'ACHIEVEMENTS', BUTTER, f'{got}/{len(list_)} UNLOCKED', 50, 40)}
<g filter="url(#soft)">{''.join(out)}</g>'''
    label = f'Achievements, {got} of {len(list_)} unlocked: ' + ', '.join(f"{n} ({'unlocked' if v >= g else f'{v}/{g}'})" for _, n, _, v, g, _ in list_)
    return svg(W, H, label, body, style)


def main():
    login, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    s = collect(login)
    cards = {
        'stats-player.svg': player(s),
        'stats-streak.svg': streak(s),
        'stats-languages.svg': languages(s),
        'stats-activity.svg': activity(s),
        'stats-achievements.svg': achievements(s),
    }
    for name, text in cards.items():
        with open(os.path.join(out, name), 'w', encoding='utf-8', newline='\n') as f:
            f.write(text)
    print({k: v for k, v in s.items() if k not in ('months', 'langs')})


if __name__ == '__main__':
    main()
