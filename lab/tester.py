import random, time 
import q1w5
import qfpw5
import sys

sys.setrecursionlimit(int(1e6))

def make_ops(m, seed=0): 
    rng = random.Random(seed) 
    ops, cid = [], 1 
    for _ in range(m): 
        r = rng.random() 
        if r < 0.45:                        #1  c  L: register
            ops.append([1, cid, rng.randint(1, 3)]); cid += 1 
        elif r < 0.90:                     # 3: extract 
            ops.append([3]) 
        elif r < 0.95:                     # 2: peek 
            ops.append([2]) 
        else:                                 # 4: size 
            ops.append([4]) 
    return ops 
def time_run(module, ops): 
    state = (module.PriorityQueue() if hasattr(module, "PriorityQueue") 
                 else module.PQ(module.EMPTY, module.EMPTY, module.EMPTY, 0))      
    start = time.perf_counter() 
    for op in ops: 
        state, _ = module.run(state, op) 
    return time.perf_counter()- start

if __name__ == "__main__":
    for i in range(20):
        ops = 1<<i
        seed = random.randint(1, 1000)
        t1 = time_run(q1w5, make_ops(ops, seed))
        t2 = time_run(qfpw5, make_ops(ops, seed))

        print(t2/t1)