import numpy as np
from pwn import *

MAX_PANEL_POWER = 0.36878177829

def directions():
    for S in "+-":
        for ax in "XYZ":
            yield S + ax + "-Axis"

def direction_map():
    res = {}
    for s in range(2):
        for ax in range(3):
            name = "+-"[s] + "XYZ"[ax] + "-Axis"
            val = [0,0,0]
            val[ax] = [1, -1][s]
            res[name] = val
    return res

def open_up():
    r = remote("main-fleet.satellitesabove.me", 5005)
    r.recvuntil("Ticket please:\n")
    r.sendline("ticket{foxtrot225533oscar2:GDxFDFpPwD2aZQaecPo5UVtnNA3bspFW-RjJUWXsuWqLlNVJ3DA3ZjwnaZCAcCTGnw}")
    r.recvuntil("(Format answers as a single float):")
    r.sendline(str(MAX_PANEL_POWER))
    r.recvuntil("The final answer should be a unit vector")
    r.sendline("r:0,0,0")
    return r

def parse_results(lines):
    res = {}
    for l in lines:
        if l.find(":") <= 0:
            continue
        p = l.split(":")
        res[p[0]] = float(p[1])
    return res

def scoop_vals(r):
    r.recvuntil("><")
    line = r.recvuntil(">")
    return (r, parse_results(line.decode('utf-8').split("\n")))

def send_mat(r, m):
    s = "r:" + ",".join(["{:1.9f}".format(v) for v in m.reshape((9,))])
    r.sendline(s)
    return r

def iterate_rot_mats():
    for i in range(3):
        for s in [-1, 1]:
            r1 = [0,0,0]
            r1[i] = s
            for j in range(i+1, i+3):
                for sj in [-1, 1]:
                    r2 = [0,0,0]
                    r2[j % 3] = sj
                    r3 = list(np.cross(r1, r2))
                    yield np.array([r1, r2, r3])

def tightness(results, skip):
    l = []
    for m,d in results:
        for k in d:
            if k != skip and d[k] > 0.0:
                l.append(d[k])
    v1 = min(l)
    v2 = max(l)
    v3 = v1
    best_dist = 0.0
    for x in l:
        dist = min(abs(x - v1), abs(x - v2))
        if dist > best_dist:
            dist = best_dist
            v3 = x
    worst_score = 0.0
    for x in l:
        score = min(abs(x - v1), min(abs(x-v2), abs(x-v3)))
        if score > worst_score:
            worst_score = score
    return worst_score
        
def find_odd_one_out(results):
    d_out = None
    best_tightness = 10.0
    for d in directions():
        t = tightness(results, d)
        if t < best_tightness:
            best_tightness = t
            d_out = d
    return d_out

if __name__ == "__main__":
    r = open_up()
    results = []
    for m in iterate_rot_mats():
        send_mat(r, m)
        r, vals = scoop_vals(r)
        results.append((m, vals))
    failing = find_odd_one_out(results)
    print(failing)

