from pathlib import Path

source = Path('src/MissionChief_Map_Command_Toolkit.user.js').read_text(encoding='utf-8').splitlines()
ranges = [
    (2314, 2380, 'base panel CSS'),
    (13990, 14422, 'layout and device functions'),
    (26132, 26345, 'desktop position and drag functions'),
    (26818, 27190, 'panel DOM construction'),
    (28490, 28530, 'resize listeners'),
    (28645, 28710, 'cleanup'),
]
out = []
for start, end, title in ranges:
    out.append(f'### {title} · source lines {start}-{end}')
    for line_no in range(start, end + 1):
        out.append(f'{line_no:>6}: {source[line_no - 1]}')
    out.append('')
Path('.github/diagnostics/issue-73-exact-slices.txt').write_text('\n'.join(out) + '\n', encoding='utf-8')
