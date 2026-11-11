#!/usr/bin/env python3
"""Monte-Carlo model of a multihead (combination) weigher.

This is a SIMULATION. It predicts what the combination principle can achieve for
an assumed per-head charge distribution; it says nothing about a real weigher
until the charge distribution has been measured on product.

Model
  * n heads, each weigh hopper holds one charge ~ Normal(target/k, cv) truncated > 0
  * measurement noise per head: Normal(0, sigma_cell)
  * selection: subset of heads (not locked out) whose MEASURED sum is >= target and
    closest to it; if none within +over_limit, the heaviest head is flagged for
    re-feed and the cycle is skipped ("no combination")
  * used heads are refilled; a refilled head is unavailable for `settle` cycles
"""
import argparse, itertools, json, os, random, statistics


class MultiheadWeigher:
    def __init__(self, heads=10, target=40.0, k=3.5, cv=0.30, sigma_cell=0.15,
                 over_limit=None, settle=1, seed=1):
        self.n, self.target, self.k, self.cv = heads, target, k, cv
        self.sigma_cell, self.settle = sigma_cell, settle
        self.over_limit = over_limit if over_limit is not None else max(3.0, 0.10 * target)
        self.rng = random.Random(seed)
        self.true = [self._charge() for _ in range(heads)]
        self.lock = [0] * heads
        self.subsets = [c for r in range(1, heads + 1) for c in itertools.combinations(range(heads), r)]
        self.skips = 0

    def _charge(self):
        m = self.target / self.k
        return max(0.2 * m, self.rng.gauss(m, self.cv * m))

    def cycle(self):
        """One weigh cycle. Returns (true_weight, heads_used) or None if no combination."""
        meas = [w + self.rng.gauss(0, self.sigma_cell) for w in self.true]
        avail = {i for i in range(self.n) if self.lock[i] == 0}
        best, best_sum = None, None
        for c in self.subsets:
            if not avail.issuperset(c):
                continue
            s = sum(meas[i] for i in c)
            if s >= self.target and (best_sum is None or s < best_sum):
                best, best_sum = c, s
        self.lock = [max(0, x - 1) for x in self.lock]
        if best is None or best_sum > self.target + self.over_limit:
            self.skips += 1
            j = max(avail or range(self.n), key=lambda i: meas[i])   # recharge the worst head
            self.true[j] = self._charge()
            self.lock[j] = self.settle
            return None
        w = sum(self.true[i] for i in best)
        for i in best:
            self.true[i] = self._charge()
            self.lock[i] = self.settle
        return w, len(best)


def study(target, n=20000, **kw):
    wg = MultiheadWeigher(target=target, **kw)
    ws, hs = [], []
    while len(ws) < n:
        r = wg.cycle()
        if r:
            ws.append(r[0]); hs.append(r[1])
    ws_sorted = sorted(ws)
    mean = statistics.fmean(ws)
    return dict(target_g=target, dumps=n, mean_g=round(mean, 3), sd_g=round(statistics.pstdev(ws), 3),
                giveaway_g=round(mean - target, 3), giveaway_pct=round(100 * (mean - target) / target, 2),
                p0_1_g=round(ws_sorted[int(0.001 * n)], 2), p99_9_g=round(ws_sorted[int(0.999 * n)], 2),
                under_target_pct=round(100 * sum(w < target for w in ws) / n, 2),
                under_minus_TNE_pct=round(100 * sum(w < target - tne(target) for w in ws) / n, 3),
                mean_heads=round(statistics.fmean(hs), 2),
                skipped_cycles_pct=round(100 * wg.skips / (n + wg.skips), 2))


def tne(q):
    """Tolerable negative error, OIML R 87 / EU 76/211/EEC table."""
    if q <= 50: return 0.09 * q
    if q <= 100: return 4.5
    if q <= 200: return 0.045 * q
    if q <= 300: return 9.0
    if q <= 500: return 0.03 * q
    return 15.0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("-n", type=int, default=20000); a = ap.parse_args()
    rows = []
    for target, cv in ((40, 0.30), (40, 0.45), (30, 0.30), (100, 0.25), (150, 0.20), (200, 0.15)):
        r = study(target, n=a.n, cv=cv); r["charge_cv"] = cv; rows.append(r); print(r)
    r = study(40, n=a.n, cv=0.30, heads=4, k=2.0); r["charge_cv"] = 0.30; r["note"] = "4-head linear-style comparison"; rows.append(r); print(r)
    json.dump(rows, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "weigher_results.json"), "w"), indent=1)
