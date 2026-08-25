"""Recompute the assumption graph from docs/architecture/assumptions.md.

The committed ledger table is the source of truth: no second data file exists to
drift from it.  Every derived figure -- tier, load, the metrics, the cycles -- is
computed here, and the ledger's own `load` column is checked rather than trusted.

    python3 recompute.py docs/architecture/assumptions.md          # report
    python3 recompute.py docs/architecture/assumptions.md --check  # exit 1 on drift
"""
import re, sys
from collections import Counter, defaultdict, deque

ROW = re.compile(r"^\| `(A-\d+)` \| (.*?) \| `(\w+)` \| (.*?) \| (\d+) \| (.*?) \|$", re.M)
TIERS = ("ESTABLISHED", "IMPLEMENTED", "OBSERVED", "ASSUMED")

def parse(path):
    B = {}
    for bid, stmt, tag, deps, ld, src in ROW.findall(open(path).read()):
        assert tag in TIERS, f"{bid}: unknown tag {tag}"
        assert bid not in B, f"{bid}: duplicate row"
        B[bid] = dict(s=stmt.split("<br>")[0], tier=tag, src=src,
                      deps=re.findall(r"A-\d+", deps), stated_load=int(ld))
    dangling = [(k, d) for k, v in B.items() for d in v["deps"] if d not in B]
    assert not dangling, f"dependencies that resolve to no row: {dangling}"
    return B

def analyse(B):
    up   = {k: set(v["deps"]) for k, v in B.items()}
    down = defaultdict(set)
    for k, ds in up.items():
        for d in ds: down[d].add(k)
    E = sum(len(v) for v in up.values())

    idx, low, on, st, c, sccs = {}, {}, set(), [], [0], []
    sys.setrecursionlimit(10000)
    def sc(v):
        idx[v] = low[v] = c[0]; c[0] += 1; st.append(v); on.add(v)
        for w in up[v]:
            if w not in idx: sc(w); low[v] = min(low[v], low[w])
            elif w in on:    low[v] = min(low[v], idx[w])
        if low[v] == idx[v]:
            comp = []
            while True:
                w = st.pop(); on.discard(w); comp.append(w)
                if w == v: break
            sccs.append(sorted(comp))
    for v in B:
        if v not in idx: sc(v)

    comp_of = {v: i for i, cc in enumerate(sccs) for v in cc}
    cup = defaultdict(set)
    for k, ds in up.items():
        for d in ds:
            if comp_of[d] != comp_of[k]: cup[comp_of[k]].add(comp_of[d])
    ct = {}
    def CT(i):
        if i not in ct: ct[i] = 0 if not cup[i] else 1 + max(CT(j) for j in cup[i])
        return ct[i]
    for i in range(len(sccs)): CT(i)
    tier = {v: ct[comp_of[v]] for v in B}

    def load(v):
        seen, q = set(), deque(down[v])
        while q:
            x = q.popleft()
            if x in seen: continue
            seen.add(x); q.extend(down[x])
        return len(seen)
    L = {v: load(v) for v in B}

    und = defaultdict(set)
    for k, ds in up.items():
        for d in ds: und[k].add(d); und[d].add(k)
    seen, P = set(), 0
    for v in B:
        if v in seen: continue
        P += 1; q = deque([v])
        while q:
            x = q.popleft()
            if x in seen: continue
            seen.add(x); q.extend(und[x])
    return dict(up=up, down=down, E=E, P=P, tier=tier, load=L,
                cycles=[s for s in sccs if len(s) > 1],
                isolated=sorted(v for v in B if not up[v] and not down[v]))

def main():
    path = sys.argv[1]
    check = "--check" in sys.argv
    B = parse(path); a = analyse(B); N = len(B)
    drift = [(v, B[v]["stated_load"], a["load"][v])
             for v in B if B[v]["stated_load"] != a["load"][v]]
    print(f"N={N} E={a['E']} P={a['P']} M={a['E']-N+2*a['P']} "
          f"density={a['E']/(N*(N-1)):.4f} depth={max(a['tier'].values())} "
          f"branching={a['E']/N:.2f}")
    print("tiers:", dict(Counter(v["tier"] for v in B.values())))
    print("cycles:", a["cycles"] or "none")
    for t in sorted(set(a["tier"].values())):
        ids = [v for v in B if a["tier"][v] == t]
        ev = sum(1 for v in ids if B[v]["tier"] != "ASSUMED")
        print(f"  tier {t}: {len(ids):3d} blocks, {ev:3d} evidenced ({100*ev/len(ids):.0f}%)")
    for v, n in sorted(a["load"].items(), key=lambda kv: -kv[1])[:10]:
        print(f"  {n:3d}  {v} [{B[v]['tier']:11s}] tier{a['tier'][v]}  {B[v]['s'][:64]}")
    print("isolated:", a["isolated"])
    if drift:
        print("\nLOAD COLUMN DRIFT -- the table disagrees with the edges:")
        for v, was, now in drift: print(f"  {v}: table says {was}, edges give {now}")
    else:
        print("\nload column agrees with the edges for all", N, "rows")
    if check and drift: sys.exit(1)

main()
