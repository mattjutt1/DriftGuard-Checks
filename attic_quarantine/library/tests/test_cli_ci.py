import json, subprocess, sys, pathlib

def test_cli_ci(tmp_path: pathlib.Path):
    cfg = tmp_path / '.promptops.yml'; cfg.write_text('threshold: 0.85\ndataset: x\n')
    out = tmp_path / 'results.json'
    subprocess.check_call([sys.executable, '-m', 'promptops.cli', 'ci', '--config', str(cfg), '--out', str(out)])
    d=json.loads(out.read_text()); assert d['metrics']['win_rate'] >= d['threshold']
