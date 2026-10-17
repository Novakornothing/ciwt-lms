"""Ground-truth gaze sequences from real face video by re-rendering the irises.

For each output frame we pick a real source frame (ping-pong through the clip, so the head keeps
its natural motion), compute where each eye must look to hit a known screen target - using that
frame's eye position, distance and head pose - and move the iris there (4x supersampled, clipped by
the eyelid contour, original iris inpainted). The frames then go through the real MediaPipe engine
(bench.html). Ground truth is therefore known exactly, but only the iris moves: eyelids do not
follow vertical gaze, and there is no corneal reflection change. See RESULTS.md.

usage: evalenv/bin/python gen.py <subject_dir> [--only cond,...]
"""
import json, math, os, sys
import cv2
import numpy as np

SUBJ = sys.argv[1].rstrip('/')
ONLY = None
# --seed N: a repeat with different source-frame alignment (other head poses / expressions at each
# target) and different sensor noise; written to <cond>_s<N>/
SEED = int(sys.argv[sys.argv.index('--seed') + 1]) if '--seed' in sys.argv else 0
if '--only' in sys.argv:
    ONLY = set(sys.argv[sys.argv.index('--only') + 1].split(','))
HFOV = 60.0
SW, SH, CM_PER_PX = 1440, 900, 0.0213        # 30.7 cm wide laptop screen, camera centred above it
EYEBALL_CM, IRIS_CM = 1.2, 1.17
R_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
L_EYE = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
EYES = [  # contour, corner a, corner b, upper, lower, iris centre, iris ring
    (R_EYE, 33, 133, 159, 145, 468, [469, 470, 471, 472]),
    (L_EYE, 362, 263, 386, 374, 473, [474, 475, 476, 477]),
]
rng = np.random.default_rng(7 + 1000 * SEED)
UPPER = {33: [33, 246, 161, 160, 159, 158, 157, 173, 133], 362: [362, 398, 384, 385, 386, 387, 388, 466, 263]}
LOWER = {33: [33, 7, 163, 144, 145, 153, 154, 155, 133], 362: [362, 382, 381, 380, 374, 373, 390, 249, 263]}

src_dir = os.path.join(SUBJ, 'src')
_meta = json.load(open(os.path.join(src_dir, 'frames.json')))
W, H, FPS = _meta['w'], _meta['h'], _meta.get('fps', 15)
lmj = json.load(open(os.path.join(src_dir, 'landmarks.json')))['frames']
src_files = sorted(f for f in os.listdir(src_dir) if f.endswith('.jpg'))
valid = [i for i, f in enumerate(lmj) if f]
# Real heads and eyelids move smoothly; per-frame landmark jitter would otherwise be rendered into
# the iris position and show up as error no tracker could remove. Smooth landmarks and pose over
# time (Gaussian, sigma 1.5 frames) before using them as the geometry for rendering.
_L = np.array([lmj[i]['lm'] for i in valid], dtype=np.float64)
_P = np.array([[lmj[i]['pose']['yaw'], lmj[i]['pose']['pitch']] for i in valid])
_k = np.exp(-0.5 * (np.arange(-4, 5) / 1.5) ** 2); _k /= _k.sum()
def _smooth(a):
    pad = np.concatenate([a[:1].repeat(4, 0), a, a[-1:].repeat(4, 0)])
    return sum(_k[j] * pad[j:j + len(a)] for j in range(len(_k)))
_Ls, _Ps = _smooth(_L), _smooth(_P)
for _n, _i in enumerate(valid):
    lmj[_i] = {'lm': _Ls[_n].tolist(), 'pose': {'yaw': float(_Ps[_n][0]), 'pitch': float(_Ps[_n][1])}, 'dist': lmj[_i].get('dist')}
F = W / (2 * math.tan(math.radians(HFOV / 2)))
order = valid + valid[::-1][1:-1]            # ping-pong over frames with a face


def src_index(k):
    return order[k % len(order)]


def head_angles(fr):
    lm = np.array(fr['lm'])
    cr, cl, top, chin, nose = lm[234], lm[454], lm[10], lm[152], lm[1]
    mid = (cr + cl) / 2
    fw = np.linalg.norm(cl - cr) or 1
    fh = np.linalg.norm(chin - top) or 1
    yaw = math.asin(max(-0.9, min(0.9, (nose[0] - mid[0]) / (fw / 2))))
    pitch = math.asin(max(-0.9, min(0.9, (nose[1] - (top[1] + chin[1]) / 2) / (fh / 2))))
    return yaw, pitch


# Head angle in image axes. The landmark ratio above is biased by face shape, so only its change
# from the clip median is used (calibration absorbs the constant part), scaled to radians with the
# MediaPipe matrix (fit over the clip), which is a proper rigid-pose estimate.
ha = np.array([head_angles(lmj[i]) for i in valid])
mat = np.array([[lmj[i]['pose']['yaw'], lmj[i]['pose']['pitch']] for i in valid])
gain, sign = [], []
for a in range(2):
    x, y = ha[:, a] - ha[:, a].mean(), mat[:, a] - mat[:, a].mean()
    c = float(np.dot(x, y) / (np.linalg.norm(x) * np.linalg.norm(y) + 1e-9))
    g = float(np.dot(x, y) / (np.dot(x, x) + 1e-9))
    gain.append(abs(g) if abs(c) > 0.3 else 1.0)
    sign.append(c)
HA_MED = np.median(ha, axis=0)


def head_rel(fr):
    y, p = head_angles(fr)
    return (y - HA_MED[0]) * gain[0], (p - HA_MED[1]) * gain[1]


def screen_to_cam(sx, sy):
    # camera coords (cm): x = image-right (= the user's left), y = image-down, camera at origin
    return -(sx - SW / 2) * CM_PER_PX, sy * CM_PER_PX + 0.6


def transform_lm(lm, A):
    pts = np.hstack([lm, np.ones((len(lm), 1))])
    return pts @ A.T


def render(img, lm, target, glare=False):
    """Move both irises to look at target (screen px). img/lm already in output geometry."""
    out = img.copy()
    irisr = np.mean([np.linalg.norm(lm[e[6][0]] - lm[e[6][2]]) for e in EYES]) / 2
    D = F * IRIS_CM / (2 * irisr)
    hy, hp = head_rel_cur
    tx, ty = screen_to_cam(*target)
    info = []
    for contour, a, b, up, lo, ic, ring in EYES:
        A, B = lm[a], lm[b]
        if A[0] > B[0]:
            A, B = B, A
        ax = B - A
        ew = np.linalg.norm(ax)
        e = ax / ew
        n = np.array([-e[1], e[0]])
        c = (A + B) / 2
        lidmid = (lm[up] + lm[lo]) / 2
        neutral = c + n * np.dot(lidmid - c, n)
        # eye 3D position and the world angle to the target
        X, Y = (lm[ic][0] - W / 2) / F * D, (lm[ic][1] - H / 2) / F * D
        yaw_w, pitch_w = math.atan2(tx - X, D), math.atan2(ty - Y, D)
        ex, ey = yaw_w - hy, pitch_w - hp                      # eye-in-head rotation
        rpx = EYEBALL_CM * F / D
        new = neutral + rpx * (math.sin(ex) * e + math.sin(ey) * n)
        r = float(np.mean([np.linalg.norm(lm[q] - lm[ic]) for q in ring]))
        info.append({'ex': ex, 'ey': ey, 'shift_px': float(np.linalg.norm(new - lm[ic]))})
        # ---- supersampled eye crop
        S = 4
        pts = lm[contour]
        x0, y0 = np.floor(pts.min(0) - r * 2).astype(int)
        x1, y1 = np.ceil(pts.max(0) + r * 2).astype(int)
        x0, y0 = max(0, x0), max(0, y0)
        x1, y1 = min(W, x1), min(H, y1)
        crop = out[y0:y1, x0:x1]
        big = cv2.resize(crop, ((x1 - x0) * S, (y1 - y0) * S), interpolation=cv2.INTER_CUBIC)
        poly = ((pts - [x0, y0]) * S).astype(np.int32)
        emask = np.zeros(big.shape[:2], np.uint8)
        cv2.fillPoly(emask, [poly], 255)
        oc = (lm[ic] - [x0, y0]) * S
        nc = (new - [x0, y0]) * S
        R = r * S
        iris_m = np.zeros_like(emask)
        cv2.circle(iris_m, tuple(np.round(oc).astype(int)), int(R * 1.0), 255, -1)
        # iris texture: visible pixels of the original iris, median colour where lids cover it
        vis = (iris_m > 0) & (emask > 0)
        if vis.sum() < 10:
            continue
        med = np.median(big[vis], axis=0)
        tex = big.copy()
        tex[(iris_m > 0) & ~(emask > 0)] = med
        # remove the original iris (inpaint inside the eye opening)
        hole = cv2.bitwise_and(cv2.dilate(iris_m, np.ones((3, 3), np.uint8)), emask)
        # sclera colour: brighter half of the eye-opening pixels outside the iris
        ring_px = big[(emask > 0) & (iris_m == 0)]
        if len(ring_px) > 10:
            lum = ring_px.astype(np.float32) @ np.array([0.114, 0.587, 0.299], np.float32)
            sclera = np.median(ring_px[lum >= np.median(lum)], axis=0)
        else:
            sclera = med
        fill = big.astype(np.float32).copy()
        fill[hole > 0] = sclera
        soft = cv2.GaussianBlur(hole.astype(np.float32) / 255, (0, 0), S * 0.7)[..., None]
        clean = big * (1 - soft) + cv2.GaussianBlur(fill, (0, 0), S * 0.7) * soft
        # eyelids follow vertical gaze (upper lid ~75 % of the iris travel, lower lid ~25 %)
        dU, dL = 0.75 * rpx * math.sin(ey) * S, 0.25 * rpx * math.sin(ey) * S
        up_pts = (lm[UPPER[a]] - [x0, y0]) * S
        lo_pts = (lm[LOWER[a]] - [x0, y0]) * S
        hh, ww = big.shape[:2]
        xs = np.arange(ww, dtype=np.float32)
        ou, ol = np.argsort(up_pts[:, 0]), np.argsort(lo_pts[:, 0])
        yu = np.interp(xs, up_pts[ou, 0], up_pts[ou, 1])
        yl = np.interp(xs, lo_pts[ol, 0], lo_pts[ol, 1])
        xa, xb = min(up_pts[:, 0].min(), lo_pts[:, 0].min()), max(up_pts[:, 0].max(), lo_pts[:, 0].max())
        taper = np.clip(np.sin(np.pi * np.clip((xs - xa) / max(1, xb - xa), 0, 1)), 0, 1) ** 0.7
        sig = 0.35 * ew * S
        Y = np.arange(hh, dtype=np.float32)[:, None]
        between = np.clip((Y - yu[None]) / np.maximum(1, (yl - yu)[None]), 0, 1)
        dmap = np.where(Y < yu[None], dU * np.exp(-((yu[None] - Y) / sig) ** 2),
                        np.where(Y > yl[None], dL * np.exp(-((Y - yl[None]) / sig) ** 2), dU + (dL - dU) * between))
        dmap = (dmap * taper[None]).astype(np.float32)
        mx, my = np.meshgrid(xs, np.arange(hh, dtype=np.float32))
        clean = cv2.remap(clean.astype(np.float32), mx, my - dmap, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        # warped eye opening for clipping the iris
        def moved(pts, d):
            q = pts.copy()
            t = np.interp(q[:, 0], xs, taper)
            q[:, 1] += d * t
            return q
        poly2 = np.vstack([moved(up_pts, dU), moved(lo_pts, dL)[::-1]]).astype(np.int32)
        emask = np.zeros(big.shape[:2], np.uint8)
        cv2.fillPoly(emask, [poly2], 255)
        # paste shifted iris, clipped by the eyelids, soft edge
        M = np.float32([[1, 0, nc[0] - oc[0]], [0, 1, nc[1] - oc[1]]])
        tex_s = cv2.warpAffine(tex, M, (big.shape[1], big.shape[0]), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        alpha = np.zeros(big.shape[:2], np.float32)
        cv2.circle(alpha, tuple(np.round(nc).astype(int)), int(R * 1.08), 1.0, -1)
        alpha = cv2.GaussianBlur(alpha, (0, 0), S * 0.6)
        inner = cv2.erode(emask, np.ones((S + 1, S + 1), np.uint8))        # stay ~1 px inside the lids
        alpha *= cv2.GaussianBlur(inner.astype(np.float32) / 255, (0, 0), S * 0.5)
        comp = clean * (1 - alpha[..., None]) + tex_s * alpha[..., None]
        if glare:   # glasses: specular blob on the lens, fixed relative to the eye (not the iris)
            gc = tuple(np.round((c - [x0, y0]) * S + np.array([0.18, -0.35]) * ew * S).astype(int))
            gl = np.zeros(big.shape[:2], np.float32)
            cv2.ellipse(gl, gc, (int(ew * S * 0.22), int(ew * S * 0.12)), -20, 0, 360, 1.0, -1)
            gl = cv2.GaussianBlur(gl, (0, 0), S * 1.2) * 0.85
            comp = comp * (1 - gl[..., None]) + 250 * gl[..., None]
        out[y0:y1, x0:x1] = cv2.resize(np.clip(comp, 0, 255).astype(np.uint8), (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA)
    return out, D, info


def glasses_frame(img, lm):
    for contour, a, b, up, lo, ic, ring in EYES:
        pts = lm[contour]
        cx, cy = pts.mean(0)
        w = (pts[:, 0].max() - pts[:, 0].min()) * 0.9
        h = w * 0.75
        cv2.ellipse(img, (int(cx), int(cy + h * 0.1)), (int(w), int(h)), 0, 0, 360, (25, 25, 25), 2, cv2.LINE_AA)
    a, b = lm[133], lm[362]
    cv2.line(img, tuple(a.astype(int)), tuple(b.astype(int)), (25, 25, 25), 2, cv2.LINE_AA)


def degrade(img, cond, k):
    if cond == 'webcam':
        img = cv2.GaussianBlur(img, (0, 0), 0.8)
        img = np.clip(img + rng.normal(0, 5, img.shape), 0, 255).astype(np.uint8)
        return img, 55
    if cond == 'lowlight':
        f = (img.astype(np.float32) / 255) ** 1.6 * 0.38 * 255
        img = np.clip(f + rng.normal(0, 4, img.shape), 0, 255).astype(np.uint8)
        return img, 70
    return img, 90


def grid(nx, ny, mx, my):
    return [(mx + (SW - 2 * mx) * i / (nx - 1), my + (SH - 2 * my) * j / (ny - 1)) for j in range(ny) for i in range(nx)]


CAL9 = grid(3, 3, 0.1 * SW, 0.1 * SH)
VAL16 = grid(4, 4, 0.175 * SW, 0.175 * SH)
rng_t = np.random.default_rng(3)
CLICKS = [(float(rng_t.uniform(0.15, 0.85) * SW), float(rng_t.uniform(0.15, 0.85) * SH)) for _ in range(12)]


def fixation_phase(name, pts, n=20, sacc=2):
    fr = []
    prev = None
    for p in pts:
        for j in range(n):
            if prev is not None and j < sacc:          # ~100 ms saccade, linear
                a = (j + 1) / (sacc + 1)
                t = (prev[0] + a * (p[0] - prev[0]), prev[1] + a * (p[1] - prev[1]))
            else:
                t = p
            fr.append({'phase': name, 'target': [float(p[0]), float(p[1])], 'eye': [float(t[0]), float(t[1])], 'j': j})
        prev = p
    return fr


def pursuit_phase(seconds=9.0, lag_frames=2):
    n = int(seconds * FPS)
    path = []
    for k in range(n + lag_frames):
        s = k / FPS
        x = SW / 2 + 0.42 * SW * math.sin(2 * math.pi * s / 4.5)
        y = SH / 2 + 0.40 * SH * math.sin(2 * math.pi * s / 3.0 + 0.6)
        path.append((x, y))
    fr = []
    for k in range(n):
        dot = path[k + lag_frames]          # the dot leads; the eye trails it by lag_frames
        eye = path[k]
        fr.append({'phase': 'pursuit', 'target': [dot[0], dot[1]], 'eye': [eye[0], eye[1]], 'j': k})
    return fr


def reading_phase():
    """Reading: fixations 180-320 ms on words along 6 lines, return sweeps; truth fixations kept."""
    fr, fixes = [], []
    y0, lh, x0, x1 = 0.25 * SH, 0.09 * SH, 0.12 * SW, 0.88 * SW
    for line in range(6):
        x = x0
        y = y0 + line * lh
        while x < x1:
            dur = int(rng_t.integers(3, 6))          # 3-5 frames = 200-333 ms at 15 fps
            fixes.append({'x': x, 'y': y, 'start': len(fr), 'n': dur})
            for j in range(dur):
                fr.append({'phase': 'read', 'target': [x, y], 'eye': [x, y], 'j': j})
            x += float(rng_t.uniform(0.06, 0.11) * SW)
    return fr, fixes


CONDS = {
    'clean': {}, 'webcam': {}, 'lowlight': {}, 'glare': {'glare': True},
    'twofaces': {'second': True}, 'occlusion': {'occlude': True}, 'moved': {'moved': True},
}
other = {'medvedev': 'zara', 'zara': 'cbp', 'cbp': 'medvedev', 'cbp720': 'zara', 'cbp1080': 'zara'}.get(os.path.basename(SUBJ), 'zara')
other_img = cv2.imread(os.path.join(os.path.dirname(SUBJ), other, 'src', '0040.jpg'))

for cond, opt in CONDS.items():
    if ONLY and cond not in ONLY:
        continue
    seq = fixation_phase('cal', CAL9)
    fixes = []
    if cond == 'moved':
        seq += fixation_phase('val', VAL16) + fixation_phase('click', CLICKS, n=10) + fixation_phase('val2', VAL16)
    else:
        seq += pursuit_phase() + fixation_phase('val', VAL16)
        if cond == 'clean':
            rd, fixes = reading_phase()
            base = len(seq)
            for f in fixes:
                f['start'] += base
            seq += rd
    od = os.path.join(SUBJ, cond + (f'_s{SEED}' if SEED else ''))
    os.makedirs(od, exist_ok=True)
    for f in os.listdir(od):
        if f.endswith('.jpg'):
            os.remove(os.path.join(od, f))
    names, truth = [], []
    start = (37 if cond != 'clean' else 0) + 53 * SEED   # different conditions/seeds start at different clip points
    for k, fr in enumerate(seq):
        si = src_index(start + k)
        img = cv2.imread(os.path.join(src_dir, src_files[si]))
        lm = np.array(lmj[si]['lm'], dtype=np.float64)
        head_rel_cur = head_rel(lmj[si])
        A = np.float32([[1, 0, 0], [0, 1, 0]])
        if opt.get('moved') and fr['phase'] != 'cal':
            # head moved ~4 cm sideways and ~10% closer after calibration (translation + scale)
            D0 = F * IRIS_CM / (np.mean([np.linalg.norm(lm[e[6][0]] - lm[e[6][2]]) for e in EYES]))
            s = 1.10
            dx = 4.0 * F / D0 * s
            cx, cy = lm[1]
            A = np.float32([[s, 0, (1 - s) * cx + dx], [0, s, (1 - s) * cy]])
            img = cv2.warpAffine(img, A, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            lm = transform_lm(lm, A)
        img, D, info = render(img, lm, fr['eye'], glare=opt.get('glare'))
        if opt.get('glare'):
            glasses_frame(img, lm)
        if opt.get('second') and other_img is not None:
            sm = cv2.resize(other_img, (int(W * 0.42), int(H * 0.42)))
            ox = 8 if lm[1][0] > W / 2 else W - sm.shape[1] - 8
            img[H - sm.shape[0] - 8:H - 8, ox:ox + sm.shape[1]] = sm
        if opt.get('occlude'):
            ph = (k // 45) % 3       # cycles: none / hand over mouth+chin / hand over one eye edge
            if ph == 1:
                cv2.ellipse(img, tuple(np.round(lm[17]).astype(int)), (int(abs(lm[454][0] - lm[234][0]) * 0.45), int(abs(lm[152][1] - lm[10][1]) * 0.22)), 0, 0, 360, (120, 150, 200), -1)
            elif ph == 2:
                cxy = lm[263] + (lm[263] - lm[362]) * 0.35
                cv2.ellipse(img, tuple(np.round(cxy).astype(int)), (int(np.linalg.norm(lm[263] - lm[362]) * 0.55), int(abs(lm[152][1] - lm[10][1]) * 0.25)), 15, 0, 360, (120, 150, 200), -1)
        img, qual = degrade(img, cond, k)
        name = f'{k:04d}.jpg'
        cv2.imwrite(os.path.join(od, name), img, [cv2.IMWRITE_JPEG_QUALITY, qual])
        names.append(name)
        truth.append({**fr, 'D': round(float(D), 2), 'src': int(si),
                      'head': [round(head_rel_cur[0], 4), round(head_rel_cur[1], 4)],
                      'shift': round(float(np.mean([i['shift_px'] for i in info])) if info else 0, 2),
                      'occl': int(((k // 45) % 3) if opt.get('occlude') else 0)})
    json.dump({'w': W, 'h': H, 'fps': FPS, 'frames': names}, open(os.path.join(od, 'frames.json'), 'w'))
    json.dump({'subject': os.path.basename(SUBJ), 'cond': cond, 'seed': SEED, 'screen': [SW, SH], 'cmPerPx': CM_PER_PX, 'hfov': HFOV,
               'gain': gain, 'sign_corr': sign, 'truth': truth, 'fixations': fixes},
              open(os.path.join(od, 'truth.json'), 'w'))
    print(cond, len(seq), 'frames; head-angle gain', [round(g, 3) for g in gain], 'corr', [round(c, 2) for c in sign], flush=True)
