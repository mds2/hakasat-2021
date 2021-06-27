import numpy as np
from pwn import *

def open_up():
    r = remote("early-motive.satellitesabove.me", 5002)
    r.recvuntil("Ticket please:\n")
    r.sendline("ticket{lima250546quebec2:GB4fsmED4xP7yKsou_xAlplEA9MRkiEtykFP6CTd1it-HSqHzJPdRO3b_FG2tEIaZQ}")
    raw_data = r.recvuntil("Index Guesses (Comma Delimited):")
    data = raw_data.decode('utf-8').split("\n")[:-2]
    trailing = "\n".join(raw_data.decode('utf-8').split("\n")[-2:])
    data = [[float(x.strip()) for x in l.split(",")] for l in data]
    return r, data, trailing

def ingest_catalog():
    ifile = open("star_catalog.txt", "r")
    lines = ifile.readlines()
    lines = [l.split(",") for l in lines if len(l.split(",")) == 3]
    return [[float(x) for x in l] for l in lines]

def make_fit(data, catalog, ijmn):
    i,j,m,n = ijmn
    v1 = np.array(data[i])
    v2 = np.array(data[j])
    v2 = v2 - v1 * np.dot(v1, v2)
    v2 = v2 / np.linalg.norm(v2)
    v3 = np.cross(v1, v2)
    u1 = np.array(catalog[m])
    u2 = np.array(catalog[n])
    u2 = u2 - u1 * np.dot(u1, u2)
    u2 = u2 / np.linalg.norm(u2)
    u3 = np.cross(u1, u2)
    return np.dot(np.array([u1, u2, u3]).T, np.array([v1, v2, v3]))

def score_fit(data, catalog, m):
    assign = []
    sum_scores = 0.0
    for d in data:
        best_score = 1.0e6
        best = -1
        for i in range(len(catalog)):
            delta = np.dot(m, d) - catalog[i]
            score = np.dot(delta, delta)
            if score < best_score:
                best_score = score
                best = i
        sum_scores += best_score
        assign.append(best)
    return (sum_scores, assign)

def pick_pair(length):
    import random
    i = random.randrange(length)
    j = i
    while j == i:
        j = random.randrange(length)
    return (i,j)

def pick_match(data, catalog):
    ij = pick_pair(len(data))
    dist = np.linalg.norm(np.array(data[ij[0]]) - np.array(data[ij[1]]))
    m = random.randrange(len(catalog))
    closest = 1.0e6
    closest_n = -1
    for n in range(len(catalog)):
        d = np.linalg.norm(np.array(catalog[m]) -
                           np.array(catalog[n]))
        close = abs(d - dist)
        if close < closest:
            closest = close
            closest_n = n
    return [ij[0], ij[1], m, closest_n]

def find_best_fit(data, catalog, n_tries = 1000):
    best_score = 1.0e6
    best_assign = []
    for try_num in range(n_tries):
        ijmn = pick_match(data, catalog)
        m = make_fit(data, catalog, ijmn)
        score, assign = score_fit(data, catalog, m)
        if score < best_score:
            print("new best score is " + str(score) +
                  " on try " + str(try_num))
            print(assign[:5])
            best_score = score
            best_assign = assign
    return (best_score, best_assign)
    

if __name__ == "__main__":
    r, data, trailing = open_up()
    # print(data)
    catalog = ingest_catalog()
    print(len(data))
    print(len(catalog))
    print(trailing)
    find_best_fit(data, catalog)
    r.interactive()
    
