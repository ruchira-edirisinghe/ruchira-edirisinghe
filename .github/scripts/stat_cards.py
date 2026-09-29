"""Render live profile counters (views, followers, repos) as SVG cards that
match the link buttons in assets/btn-*.svg. Run by .github/workflows/profile-assets.yml.

Usage: python stat_cards.py <github-user> <out-dir>
"""
import json
import os
import re
import sys
import urllib.request

USER, OUT = sys.argv[1], sys.argv[2]
FONT = "'Segoe UI', Ubuntu, 'Helvetica Neue', Arial, sans-serif"


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
    w, h = 226, 72
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{label}: {value}">
<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="18" fill="#0d1117" stroke="{color}" stroke-opacity="0.55" stroke-width="1.5"/>
<rect x="14" y="12" width="48" height="48" rx="14" fill="{color}" fill-opacity="0.18"/>
<g transform="translate(26 24)" fill="{color}"><path fill-rule="evenodd" d="{ICONS[kind]}"/></g>
<text x="76" y="36" font-family="{FONT}" font-size="22" font-weight="800" fill="#f0f6fc">{value}</text>
<text x="76" y="55" font-family="{FONT}" font-size="13" fill="#8b949e">{label}</text>
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
        'views': ('#00b4d8', fmt(safe(profile_views)), 'Profile views'),
        'followers': ('#a78bfa', fmt(user.get('followers')), 'Followers'),
        'repos': ('#ff5fd2', fmt(user.get('public_repos')), 'Public repos'),
    }
    for kind, (color, value, label) in cards.items():
        with open(os.path.join(OUT, f'stat-{kind}.svg'), 'w', encoding='utf-8') as f:
            f.write(card(kind, color, value, label))
        print(f'{label}: {value}')


if __name__ == '__main__':
    main()
