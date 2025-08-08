import argparse
from .ci import run_ci

def main():
    p=argparse.ArgumentParser(prog='promptops')
    s=p.add_subparsers(dest='cmd', required=True)
    ci=s.add_parser('ci'); ci.add_argument('--config', required=True); ci.add_argument('--out', default='results.json')
    a=p.parse_args()
    if a.cmd=='ci': run_ci(a.config,a.out)
