"""Read-only inventory of preserved inputs/checkpoints and published evidence."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent.parent
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    checkpoints = []
    for path in sorted((BASE/'sample').rglob('*.zip')):
        item = dict(path=str(path), bytes=path.stat().st_size, sha256=digest(path))
        with zipfile.ZipFile(path) as archive:
            if 'data' in archive.namelist():
                data = json.loads(archive.read('data'))
                # Serialized spaces are inventoried without executing pickle data.
                item['contract'] = {k:data.get(k) for k in ('observation_space','action_space','num_timesteps','seed')}
        checkpoints.append(item)
    originals = {str(p.relative_to(ROOT)):digest(p) for p in (ROOT/'originals').glob('*.py')}
    summaries = {}
    for path in sorted((ROOT.parent/'progress').rglob('*.json')):
        summaries[str(path.relative_to(ROOT.parent))] = dict(sha256=digest(path), data=json.loads(path.read_text(encoding='utf-8')))
    local = BASE/'sample/0929/code_ver.1/model05_ppo_official_v1/ppo_comparison_summary.json'
    if local.exists():
        summaries[str(local)] = dict(sha256=digest(local), data=json.loads(local.read_text(encoding='utf-8')))
    (ROOT/'source_inventory.json').write_text(json.dumps(dict(checkpoints=checkpoints, originals=originals, evidence=summaries, missing_attachment='enviornment.py'), ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Preserved checkpoints: {len(checkpoints)}')

if __name__ == '__main__':
    main()
