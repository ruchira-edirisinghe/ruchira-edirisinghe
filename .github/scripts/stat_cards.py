"""Render live profile counters (views, followers, repos) as soft clay cards
that match the artwork in assets/ (drawn by draw_assets.py). Run by .github/workflows/profile-assets.yml.

Usage: python stat_cards.py <github-user> <out-dir>
"""
import json
import os
import re
import sys
import urllib.request

USER, OUT = sys.argv[1], sys.argv[2]
FONT = "'SF Pro Rounded', ui-rounded, 'Nunito', 'Segoe UI', Ubuntu, system-ui, sans-serif"
INK, INK_SOFT = '#2e2a36', '#6f6878'


def get(url, headers=None):
    req = urllib.request.Request(url, headers={'User-Agent': 'profile-stat-cards', **(headers or {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode('utf-8')


def github_user():
    headers = {'Accept': 'application/vnd.github+json'}
    if os.environ.get('GITHUB_TOKEN'):
        headers['Authorization'] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    return json.loads(get(f'https://api.github.com/users/{USER}', headers))


def profile_views():
    # komarev only increments on requests from GitHub's camo proxy, so reading it here doesn't inflate the count
    svg = get(f'https://komarev.com/ghpvc/?username={USER}')
    nums = re.findall(r'>([\d,]+)<', svg)
    return int(nums[-1].replace(',', '')) if nums else None


def fmt(n):
    if n is None:
        return '—'
    if n >= 1_000_000:
        return f'{n / 1_000_000:.1f}M'.replace('.0M', 'M')
    if n >= 10_000:
        return f'{n / 1000:.1f}k'.replace('.0k', 'k')
    return f'{n:,}'


ICONS = {
    'views': 'M12 5C6.5 5 2.7 9.3 1.5 12c1.2 2.7 5 7 10.5 7s9.3-4.3 10.5-7C21.3 9.3 17.5 5 12 5Zm0 11.5a4.5 4.5 0 1 1 0-9 4.5 4.5 0 0 1 0 9Zm0-2.5a2 2 0 1 0 0-4 2 2 0 0 0 0 4Z',
    'followers': 'M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8Zm-7 9c0-3.3 3.1-6 7-6s7 2.7 7 6v1H2v-1Zm15.5-9a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7Zm.5 2c-.9 0-1.7.2-2.4.5A7.5 7.5 0 0 1 18 20v1h5v-1.5c0-3.6-2.2-6.5-5-6.5Z',
    'repos': 'M4 3.5A2.5 2.5 0 0 1 6.5 1H20v17H6.5a.5.5 0 0 0 0 1H20v2H6.5A2.5 2.5 0 0 1 4 18.5v-15ZM8 5v2h8V5H8Z',
}


def card(kind, color, value, label):
    """color is (top, edge) of the card's clay icon."""
    w, h = 226, 76
    top, edge = color
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{label}: {value}">
<rect x="2" y="7" width="{w-4}" height="{h-10}" rx="20" fill="#e6dccd"/>
<rect x="2" y="2" width="{w-4}" height="{h-10}" rx="20" fill="#fbf6ef"/>
<rect x="14" y="16" width="40" height="40" rx="13" fill="{edge}"/>
<rect x="14" y="12" width="40" height="40" rx="13" fill="{top}"/>
<g transform="translate(22 20)" fill="{INK}" fill-opacity="0.8"><path fill-rule="evenodd" d="{ICONS[kind]}"/></g>
<text x="68" y="36" font-family="{FONT}" font-size="22" font-weight="800" fill="{INK}">{value}</text>
<text x="68" y="54" font-family="{FONT}" font-size="13" fill="{INK_SOFT}">{label}</text>
</svg>'''


def safe(fn):
    try:
        return fn()
    except Exception as e:  # one flaky source shouldn't block the other cards
        print(f'::warning::{fn.__name__} failed: {e}')
        return None


def main():
    os.makedirs(OUT, exist_ok=True)
    user = github_user()
    cards = {
        'views': (('#d3e6f7', '#8fb6dc'), fmt(safe(profile_views)), 'Profile views'),
        'followers': (('#e0d7f7', '#ab9bdd'), fmt(user.get('followers')), 'Followers'),
        'repos': (('#ffd6c4', '#e89d84'), fmt(user.get('public_repos')), 'Public repos'),
    }
    for kind, (color, value, label) in cards.items():
        with open(os.path.join(OUT, f'stat-{kind}.svg'), 'w', encoding='utf-8') as f:
            f.write(card(kind, color, value, label))
        print(f'{label}: {value}')


if __name__ == '__main__':
    main()
