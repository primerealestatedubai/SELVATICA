import json, sys
from collections import deque
import numpy as np
from PIL import Image

img = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(int)
H, W, _ = img.shape
lum = img.mean(2)
white = lum > 190
fill = (lum > 38) & (lum < 120)           # the gray unit fill (dark navy bg is < 35)

# --- label connected fill regions (4-neighbour BFS) ---
lab = np.zeros((H, W), int); n = 0; sizes = {}
for y in range(H):
    for x in range(W):
        if fill[y, x] and lab[y, x] == 0:
            n += 1; q = deque([(y, x)]); lab[y, x] = n; c = 0
            while q:
                cy, cx = q.popleft(); c += 1
                for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)):
                    ny, nx = cy+dy, cx+dx
                    if 0 <= ny < H and 0 <= nx < W and fill[ny, nx] and lab[ny, nx] == 0:
                        lab[ny, nx] = n; q.append((ny, nx))
            sizes[n] = c
big = [k for k, v in sizes.items() if v > 4000]
print('regions', len(sizes), 'big', len(big), [sizes[k] for k in big])

def dilate(m, r):
    out = m.copy()
    for _ in range(r):
        p = np.pad(out, 1)
        out = out | p[:-2,1:-1] | p[2:,1:-1] | p[1:-1,:-2] | p[1:-1,2:]
    return out

def fill_holes(m):
    # flood the outside, everything not outside is inside
    h, w = m.shape; out = np.zeros((h, w), bool); q = deque()
    for x in range(w):
        for y in (0, h-1):
            if not m[y, x] and not out[y, x]: out[y, x] = True; q.append((y, x))
    for y in range(h):
        for x in (0, w-1):
            if not m[y, x] and not out[y, x]: out[y, x] = True; q.append((y, x))
    while q:
        cy, cx = q.popleft()
        for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)):
            ny, nx = cy+dy, cx+dx
            if 0 <= ny < h and 0 <= nx < w and not m[ny, nx] and not out[ny, nx]:
                out[ny, nx] = True; q.append((ny, nx))
    return ~out

def trace(m):
    # follow the pixel edges between inside and outside; returns the longest closed loop (clockwise on screen)
    p = np.pad(m, 1); h, w = p.shape
    nxt = {}
    ys, xs = np.nonzero(p)
    for y, x in zip(ys, xs):
        if not p[y-1, x]: nxt.setdefault((x, y), []).append((x+1, y))
        if not p[y, x+1]: nxt.setdefault((x+1, y), []).append((x+1, y+1))
        if not p[y+1, x]: nxt.setdefault((x+1, y+1), []).append((x, y+1))
        if not p[y, x-1]: nxt.setdefault((x, y+1), []).append((x, y))
    seen = set(); best = []
    for start in list(nxt):
        if start in seen: continue
        loop = [start]; cur = start; seen.add(cur)
        while True:
            outs = nxt.get(cur)
            if not outs: break
            cur = outs.pop()
            if cur == start: break
            loop.append(cur); seen.add(cur)
        if len(loop) > len(best): best = loop
    return [(x-1, y-1) for x, y in best]

def rdp(pts, eps):
    if len(pts) < 3: return pts
    a = np.array(pts[0], float); b = np.array(pts[-1], float); ab = b - a
    L = np.hypot(*ab)
    P = np.array(pts, float)
    d = np.abs(ab[0]*(P[:,1]-a[1]) - ab[1]*(P[:,0]-a[0])) / L if L else np.hypot(*(P - a).T)
    i = int(np.argmax(d))
    if d[i] > eps:
        l = rdp(pts[:i+1], eps); r = rdp(pts[i:], eps); return l[:-1] + r
    return [pts[0], pts[-1]]

known = {8:(410,175), 9:(503,375), 7:(338,420), 4:(865,533), 1:(1143,645), 6:(340,712), 5:(530,712), 3:(740,712), 2:(953,712)}
units = {}
for k in big:
    m = fill_holes(lab == k)
    m = dilate(m, 3)                       # move the outline onto the centre of the white wall
    pts = trace(m)
    # close/simplify
    simp = rdp(pts + [pts[0]], 2.2)[:-1]
    ys, xs = np.nonzero(m)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    holes = fill_holes(lab == k) & ~(lab == k)
    hy, hx = np.nonzero(holes)
    cx = (hx.min() + hx.max()) / 2; cy = (hy.min() + hy.max()) / 2; th = hy.max() - hy.min()
    # which unit?
    uid = min(known, key=lambda u: (known[u][0]-cx)**2 + (known[u][1]-cy)**2)
    units[uid] = {'pts': [(int(x), int(y)) for x, y in simp], 'label': (round(float(cx),1), round(float(cy),1)), 'bbox': (int(x0), int(y0), int(x1), int(y1)), 'text_h': int(th)}
    print(uid, len(simp), 'verts', 'bbox', units[uid]['bbox'], 'label', units[uid]['label'], 'text_h', th)

allx = [p[0] for u in units.values() for p in u['pts']]; ally = [p[1] for u in units.values() for p in u['pts']]
bounds = (min(allx), min(ally), max(allx), max(ally))
print('bounds', bounds)
json.dump({'bounds': bounds, 'units': {str(k): v for k, v in sorted(units.items())}}, open(sys.argv[2], 'w'))
