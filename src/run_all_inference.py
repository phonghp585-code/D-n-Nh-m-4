import argparse,json
from src import run_part2,run_part4,run_combinations_inference
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--rerun',action='store_true');p.add_argument('--validate',action='store_true');a=p.parse_args()
    for module in (run_part2,run_part4,run_combinations_inference):print(json.dumps(module.run() if a.rerun else module.validate_outputs(),ensure_ascii=False))
