
import sys
import json
import time
import random

def load_records(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def make_dict(records):
    return {r['transaction_id']: r for r in records}

def linear_search(records, tid):
    for r in records:
        if r['transaction_id'] == tid:
            return r
    return None

def time_searches(records, keys_to_search, repeats=100):
    d = make_dict(records)
    # time linear
    t0 = time.perf_counter()
    for _ in range(repeats):
        for k in keys_to_search:
            linear_search(records, k)
    t_linear = time.perf_counter() - t0
    # time dict
    t0 = time.perf_counter()
    for _ in range(repeats):
        for k in keys_to_search:
            _ = d.get(k)
    t_dict = time.perf_counter() - t0
    return t_linear, t_dict

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python dsa/dsa_compare.py path/to/transactions.json")
        sys.exit(1)
    records = load_records(sys.argv[1])
    if len(records) < 20:
        # replicate some records to reach 100
        while len(records) < 100:
            r = dict(records[random.randrange(len(records))])
            r['transaction_id'] = r['transaction_id'] + f"-dup{len(records)}"
            records.append(r)
    # pick 20 random keys
    keys = [r['transaction_id'] for r in random.sample(records, 20)]
    t_linear, t_dict = time_searches(records, keys, repeats=200)
    print("Linear search total time: {:.6f} seconds".format(t_linear))
    print("Dictionary lookup total time: {:.6f} seconds".format(t_dict))
    print("Dict is {:.2f}x faster".format(t_linear / t_dict if t_dict>0 else float('inf')))
