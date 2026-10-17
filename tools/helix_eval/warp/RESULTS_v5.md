# Pass 5 warp tables (raw output)

## crop_ab.js, 9-point, all 55 sequences (features _v5)
| **median all** | 55 | 7.53 | 7.22 | 7.17 | 7.27 | 7.17 | 7.58 | 7.12 | 7.17 | 7.31 | 6.99 | 7.12 |
| median H | | 4.41 | 4.59 | 4.36 | 4.94 | 4.65 | 4.34 | 4.44 | 4.43 | 4.40 | 4.48 | 4.21 |
| median V | | 4.74 | 4.76 | 4.36 | 4.61 | 4.46 | 4.57 | 4.86 | 4.59 | 4.67 | 4.47 | 4.86 |
| cbp | median | 6.86 | 7.22 | 7.14 | 7.54 | 8.04 | 7.80 | 7.66 | 7.66 | 7.21 | 6.78 | 6.98 |
| cbp720 | median | 6.91 | 7.01 | 6.69 | 7.05 | 6.88 | 6.62 | 6.15 | 6.21 | 6.09 | 6.05 | 6.15 |
| medvedev | median | 7.58 | 7.58 | 7.62 | 7.58 | 7.50 | 7.58 | 7.03 | 7.27 | 7.58 | 6.79 | 7.08 |
| zara | median | 10.33 | 10.26 | 9.97 | 10.20 | 10.03 | 10.57 | 9.73 | 10.09 | 9.29 | 9.30 | 10.03 |
| cbp1080 | median | 6.54 | 5.86 | 6.07 | 6.28 | 5.60 | 6.26 | 6.18 | 6.34 | 6.64 | 5.84 | 6.18 |
| wins vs base | | 0/55 | 30/55 | 35/55 | 30/55 | 34/55 | 27/55 | 37/55 | 32/55 | 37/55 | 37/55 | 37/55 |

| variant | median all 55 | mean Δ [95% CI] | wins | sign p | subjects better (7-cond) | subjects better (seeds) | main28 median | seeds median |
|---|---|---|---|---|---|---|---|---|
| base | 7.53 | +0.00 [+0.00, +0.00] | 0/55 | 0.000 | 0/5 | 0/5 | 7.97 | 6.87 |
| base@cv | 7.22 | -0.21 [-0.55, +0.09] | 30/55 | 0.590 | 3/5 | 3/5 | 7.69 | 6.96 |
| base+tb@cv | 7.17 | -0.29 [-0.60, +0.01] | 35/55 | 0.058 | 4/5 | 3/5 | 7.58 | 6.53 |
| base+lid@cv | 7.27 | -0.16 [-0.52, +0.17] | 30/55 | 0.590 | 3/5 | 2/5 | 7.67 | 6.96 |
| base+tb+lid@cv | 7.17 | -0.24 [-0.57, +0.10] | 34/55 | 0.105 | 4/5 | 3/5 | 7.75 | 6.59 |
| base+tb+lid | 7.58 | -0.04 [-0.32, +0.23] | 27/55 | 1.000 | 2/5 | 3/5 | 8.09 | 6.53 |
| base+p10:pca12@cv | 7.12 | -0.37 [-0.72, -0.05] | 37/55 | 0.014 | 3/5 | 5/5 | 7.57 | 6.11 |
| base+p10:pca12 | 7.17 | -0.29 [-0.62, +0.03] | 32/55 | 0.281 | 3/5 | 4/5 | 7.57 | 6.46 |
| base+p5@cv | 7.31 | -0.41 [-0.76, -0.07] | 37/55 | 0.014 | 3/5 | 4/5 | 7.58 | 6.07 |
| base+tb+lid+p10:pca12@cv | 6.99 | -0.45 [-0.76, -0.16] | 37/55 | 0.014 | 4/5 | 4/5 | 7.59 | 6.02 |
| selB | 7.12 | -0.35 [-0.68, -0.04] | 37/55 | 0.014 | 3/5 | 5/5 | 7.73 | 6.11 |

## warp_eval.js: pass-4 model (CROPVEC=0) vs experimental crop model, same frames
| set | metric | pass-4 model | pass-5 model | wins | sign p | mean Δ [95% CI] |
|---|---|---|---|---|---|---|
| main 28 (4 subjects x 7 conditions) | 9-pt | 7.97° | 7.75° | 19/28 | 0.087 | -0.28 [-0.82, +0.22] |
| main 28 (4 subjects x 7 conditions) | follow+3 dots | 7.59° | 7.73° | 11/24 | 0.839 | +0.26 [-0.05, +0.58] |
| held-out subjects (medvedev, cbp720) | 9-pt | 7.56° | 7.18° | 9/14 | 0.424 | -0.09 [-0.46, +0.26] |
| seed repeats (5 subjects x clean/webcam x 2 seeds) | 9-pt | 6.87° | 6.58° | 11/20 | 0.824 | -0.08 [-0.62, +0.45] |
| cbp1080 (7 conditions) | 9-pt | 7.02° | 6.63° | 4/7 | 1.000 | -0.38 [-0.98, +0.11] |
| all 55 | 9-pt | 7.53° | 7.19° | 34/55 | 0.105 | -0.22 [-0.55, +0.13] |
| all 55 | follow+3 dots | 7.03° | 7.29° | 20/50 | 0.203 | +0.20 [-0.05, +0.46] |

| subject | clean | 7 conditions | seeds (4) |
|---|---|---|---|
| cbp | 6.86 → 7.02 | 7.53 → 8.48 | 6.35 → 6.50 |
| cbp720 | 5.83 → 5.61 | 7.54 → 7.08 | 6.42 → 5.96 |
| cbp1080 | 5.90 → 5.18 | 7.02 → 6.63 | 5.28 → 5.07 |
| medvedev | 6.72 → 6.33 | 7.58 → 7.20 | 7.98 → 7.94 |
| zara | 11.54 → 10.63 | 10.84 → 10.03 | 9.93 → 9.99 |

| condition (main 28) | pass-4 | pass-5 |
|---|---|---|
| clean | 6.79° | 6.67° |
| webcam | 7.56° | 7.21° |
| lowlight | 8.64° | 9.38° |
| glare | 9.59° | 8.89° |
| twofaces | 7.76° | 8.02° |
| occlusion | 8.43° | 7.83° |
| moved | 6.26° | 8.12° |

moved (no clicks / after 12 clicks), pass-4 -> pass-5:
  ('cbp', 8.86, 11.1, 8.81, 8.58)
  ('cbp720', 8.53, 8.57, 7.39, 7.89)
  ('medvedev', 4.59, 4.77, 5.32, 6.08)
  ('zara', 15, 14.35, 13.2, 14.37)
  ('cbp1080', 8.83, 8.22, 7.16, 7.33)
median moved no clicks 8.83 -> 8.57; after clicks 7.39 -> 7.89

## Timing log
```
== cbp/clean &crop=0
testdata/warp/cbp/clean: 866 frames, face 866, 22808 ms, infer 24 ms, crop None ms
== cbp/clean &crop=view
testdata/warp/cbp/clean: 866 frames, face 866, 24677 ms, infer 22 ms, crop 2 ms
== cbp/clean &crop=view&tb=0
testdata/warp/cbp/clean: 866 frames, face 866, 22383 ms, infer 22.8 ms, crop 0.7 ms
== cbp720/clean &crop=0
testdata/warp/cbp720/clean: 866 frames, face 866, 28137 ms, infer 29 ms, crop None ms
== cbp720/clean &crop=view
testdata/warp/cbp720/clean: 866 frames, face 866, 29907 ms, infer 28.7 ms, crop 2.3 ms
== cbp720/clean &crop=view&tb=0
testdata/warp/cbp720/clean: 866 frames, face 866, 30193 ms, infer 32.4 ms, crop 0.8 ms
== cbp1080/clean &crop=0
testdata/warp/cbp1080/clean: 866 frames, face 866, 39386 ms, infer 39.9 ms, crop None ms
== cbp1080/clean &crop=view
testdata/warp/cbp1080/clean: 866 frames, face 866, 41033 ms, infer 39.9 ms, crop 2.4 ms
== cbp1080/clean &crop=view&tb=0
testdata/warp/cbp1080/clean: 866 frames, face 866, 40197 ms, infer 44.2 ms, crop 0.8 ms
== cbp1080/clean &crop=0&dw=1280
testdata/warp/cbp1080/clean: 866 frames, face 866, 36988 ms, infer 36.3 ms, crop None ms
== cbp/clean mobile=1 crop=0
testdata/warp/cbp/clean: 866 frames, face 866, 21792 ms, infer 25.9 ms, crop None ms
== cbp/clean mobile=1 crop=feat(forced) tb=0
testdata/warp/cbp/clean: 866 frames, face 866, 21521 ms, infer 20.8 ms, crop 0.7 ms
```
