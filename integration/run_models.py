"""Run selected public models into new folders and collect official results."""
import argparse
from datetime import datetime
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--models-root', type=Path, default=Path('C:/Users/User/Desktop/WAAM_Validator-main/tests'))
    parser.add_argument('--models', nargs='+', choices=['01','02','03','04','05','06'], default=['01','02','03','04','05','06'])
    parser.add_argument('--out', type=Path, default=ROOT/'runs'/datetime.now().strftime('matrix_%Y%m%d_%H%M%S'))
    parser.add_argument('--reuse-index', type=Path, help='Saved benchmark index with task_file per model')
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    reuse = json.loads(args.reuse_index.read_text(encoding='utf-8')) if args.reuse_index else {}
    results = {}
    for number in args.models:
        destination = out/number
        command = [sys.executable,str(ROOT/'run_pipeline.py'),'--job',str(args.models_root.resolve()/number),
                   '--out',str(destination),'--scheduler','layer']
        if number in reuse:
            path = (ROOT/reuse[number]['task_file']).resolve()
            command.extend(['--tasks-json',str(path)])
        completed = subprocess.run(command)
        report = destination/'run.json'
        data = json.loads(report.read_text(encoding='utf-8')) if report.exists() else dict(status='ERROR',error='No run report')
        results[number] = dict(status=data['status'],exit_code=completed.returncode,
                               makespan_s=data.get('makespan_s'),error=data.get('error'),run_file=str(report))
        (out/'matrix.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    return 0 if all(r['status']=='PASS' and r['exit_code']==0 for r in results.values()) else 1

if __name__ == '__main__':
    sys.exit(main())
