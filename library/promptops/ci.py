import json, time, uuid
from pathlib import Path
import yaml
def run_ci(config_path: str, out_path: str) -> None:
    cfg = yaml.safe_load(Path(config_path).read_text()) or {}
    threshold = float(cfg.get('threshold', 0.85))
    report = {
        'run_id': str(uuid.uuid4()),
        'threshold': threshold,
        'metrics': {'win_rate': 0.86, 'latency_ms_avg': 1200, 'cost_usd': 0.12},
        'created_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'notes': 'PromptOps SDK demo CI results',
    }
    Path(out_path).write_text(json.dumps(report, indent=2))
    print(f'[promptops] wrote results to {out_path}')
