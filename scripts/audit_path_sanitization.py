import json
import re

with open('cached_dry_run_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

tracks = data.get('tracks', [])
print(f"Total tracks analyzed: {len(tracks)}")

bracket_violations = []
symbol_violations = []
repeated_prefix_violations = []

dirty_symbols_re = re.compile(r'[$%!@~+^=;#`]')

for i, t in enumerate(tracks):
    p = t.get('proposed_path', '')
    if not p:
        continue
    # 1. Check brackets
    if any(b in p for b in ['(', ')', '[', ']', '{', '}']):
        bracket_violations.append((t.get('source_path'), p))
    # 2. Check dirty symbols
    if dirty_symbols_re.search(p):
        symbol_violations.append((t.get('source_path'), p))
    # 3. Check repeated prefix in filename
    fname = p.split('\\')[-1]
    stem = fname.rsplit('.', 1)[0]
    parts = [part.strip() for part in stem.split(' - ')]
    if len(parts) >= 2 and parts[0].lower() == parts[1].lower():
        repeated_prefix_violations.append((fname, p))

print(f"Bracket violations: {len(bracket_violations)}")
print(f"Symbol violations: {len(symbol_violations)}")
print(f"Repeated prefix violations: {len(repeated_prefix_violations)}")

if bracket_violations:
    print("Sample bracket violations:")
    for b in bracket_violations[:5]:
        print(" ", b)

if symbol_violations:
    print("Sample symbol violations:")
    for s in symbol_violations[:5]:
        print(" ", s)

if repeated_prefix_violations:
    print("Sample repeated prefix violations:")
    for r in repeated_prefix_violations[:5]:
        print(" ", r)
