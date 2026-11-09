#!/usr/bin/env python3
"""Symmetric (Bennet-type) mix/rate decomposition of AOV change over non-overlapping segments.
dAOV = sum_s (w1-w0)*(a0+a1)/2  [mix]  +  sum_s (a1-a0)*(w0+w1)/2  [rate]  -- exact, no residual."""
import json, csv, os, sys
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def decompose(segs):  # segs: [(name, n0, s0, n1, s1)]
    N0 = sum(s[1] for s in segs); N1 = sum(s[3] for s in segs)
    rows = []; M = V = 0
    for name, n0, s0, n1, s1 in segs:
        w0, w1 = n0/N0, n1/N1; a0 = s0/n0 if n0 else 0; a1 = s1/n1 if n1 else 0
        if n0 and n1: m = (w1-w0)*(a0+a1)/2; v = (a1-a0)*(w0+w1)/2
        else: m = w1*a1 - w0*a0; v = 0.0   # segment exists in one period only -> all mix
        M += m; V += v; rows.append([name, n0, round(w0,4), round(a0,2), n1, round(w1,4), round(a1,2), round(m,2), round(v,2)])
    A0 = sum(s[2] for s in segs)/N0; A1 = sum(s[4] for s in segs)/N1
    return rows, A0, A1, M, V
if __name__ == '__main__':
    d = json.load(open(os.path.join(root, 'data', 'salla_sales_by_device_w45.json')))
    rows, A0, A1, M, V = decompose([(r[0], r[3], r[4], r[1], r[2]) for r in d['rows']])  # (name, prev_n, prev_s, cur_n, cur_s)
    fn = os.path.join(root, 'output', '10_decomp_channel.csv')
    with open(fn, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f); w.writerow(['channel','prev_orders','prev_share','prev_aov','cur_orders','cur_share','cur_aov','mix_effect_sar','within_effect_sar'])
        w.writerows(rows); w.writerow(['TOTAL', '', '', round(A0,2), '', '', round(A1,2), round(M,2), round(V,2)])
    print(open(fn, encoding='utf-8-sig').read())
