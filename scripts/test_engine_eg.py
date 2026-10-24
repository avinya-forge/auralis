import sys
sys.path.insert(0, '.')
import json
import os
from src.engine.master_dry_run_engine import MasterDryRunEngine

data = json.load(open('cached_dry_run_results.json', encoding='utf-8'))['tracks']
eg = [v for v in data if not v.get('is_duplicate') and v.get('language') == 'Hindi' and v.get('category') == 'Evergreen Classics']

engine = MasterDryRunEngine([], min_folder_threshold=3)
print("Testing engine.resolve_deep_audio_and_taxonomy on first 20 Evergreen tracks:")
for t in eg[:20]:
    t_copy = dict(t)
    t_copy['is_generic'] = False
    res = engine.resolve_deep_audio_and_taxonomy(t_copy)
    print(f"FN: {t['filename']} -> Lang: {res['language']}, Cat: {res['category']}, Album: {res['album']}, Decision: {res['decision_source']}")
