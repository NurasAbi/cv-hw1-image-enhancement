# Homework 1 - Image Enhancement (Computer Vision, Fall 2026)

Classical image enhancement pipeline (no deep learning): linear contrast
stretching, histogram equalization and a stretch + non-local-means combination,
compared with PSNR, SSIM and MAE on synthetically degraded images.

## Requirements
- Python 3.13 (tested; 3.9+ should work)
- Dependencies: `pip install -r requirements.txt`
  (numpy, opencv-python, scikit-image, matplotlib, pandas; tested with
  OpenCV 5.0, NumPy 2.5, scikit-image 0.26)

## Run the whole experiment
```bash
pip install -r requirements.txt
python run_experiment.py
```
Optional parameters (defaults are the ones used in the report):
```bash
python run_experiment.py --seed 42 --contrast 0.45 --noise-sigma 6 --max-side 1024 \
                         --p-low 0 --p-high 100 --nlm-h 6
```

## What it does
1. Reads every image in `images/original/` and resizes it (longest side 1024 px).
2. Degrades it: `127.5 + contrast*(I-127.5) + N(0, sigma^2)`, clipped to [0,255].
   Random seed = `--seed` + image index (sorted file order), so results are reproducible.
3. Applies the methods with fixed parameters:
   - `baseline`: degraded image, no processing
   - `stretch_lum`: linear min-max stretch of the L channel (CIE Lab)
   - `hist_eq_lab`: histogram equalization of the L channel (CIE Lab)
   - `stretch_nlm`: luminance stretch + non-local means denoising (our 4th method)
   - `stretch_rgb (extra)`: stretch applied independently to B, G, R (colour-shift illustration)
4. Computes PSNR, SSIM (scikit-image) and MAE against the original image.
5. Saves processed images, side-by-side figures, luminance histograms and metrics.

## File structure
```
run_experiment.py        main script
src/enhance.py           degradation + enhancement methods
src/metrics.py           PSNR, SSIM, MAE
images/original/         original photographs (own photos)
images/degraded/         degraded versions (created by the script)
results/processed/       processed images (<image>__<method>.jpg, JPEG quality 95;
                         metrics are computed in memory, before saving)
results/figures/         comparison figures and luminance histograms
results/metrics.csv      metrics per image and method
results/metrics_table.md same table + mean per method
results/stretch_sensitivity.csv  effect of percentile clipping in the stretch
report/                  LaTeX source and PDF of the report
```

## Image sources and licenses
`board1.jpg`, `board2.jpg`, `board3.jpg` (classroom whiteboard), `room_dark.jpg` (dark room), `night_street.jpg` (night scene through a window): own photographs
(November 2026), included in the repository.
