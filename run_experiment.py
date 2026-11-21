#!/usr/bin/env python3
"""Homework 1 - Image enhancement pipeline.

Usage:
    python run_experiment.py                       # default parameters
    python run_experiment.py --seed 42 --contrast 0.45 --noise-sigma 6

For every image in images/original/ it:
  1. resizes it (longest side = --max-side),
  2. creates a degraded version (lower contrast + Gaussian noise, fixed seed),
  3. applies all methods to the degraded image,
  4. computes PSNR, SSIM and MAE against the ORIGINAL image,
  5. saves processed images, side-by-side figures, luminance histograms and
     results/metrics.csv  (+ results/metrics_table.md).
"""
import argparse
import sys
from pathlib import Path

import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent / "src"))
from enhance import build_methods, degrade, stretch_luminance   # noqa: E402
from metrics import all_metrics               # noqa: E402

IMG_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}


def load_resized(path, max_side):
    img = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if img is None:
        raise IOError(f"cannot read {path}")
    h, w = img.shape[:2]
    scale = max_side / max(h, w)
    if scale < 1.0:
        img = cv2.resize(img, (round(w * scale), round(h * scale)), interpolation=cv2.INTER_AREA)
    return img


def rgb(img_bgr):
    return cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="images/original")
    ap.add_argument("--out", default="results")
    ap.add_argument("--degraded-dir", default="images/degraded")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--contrast", type=float, default=0.45, help="contrast factor (1 = none)")
    ap.add_argument("--noise-sigma", type=float, default=6.0, help="Gaussian noise std (0-255)")
    ap.add_argument("--max-side", type=int, default=1024)
    ap.add_argument("--p-low", type=float, default=0.0, help="low percentile for stretching")
    ap.add_argument("--p-high", type=float, default=100.0, help="high percentile for stretching")
    ap.add_argument("--nlm-h", type=float, default=6.0, help="non-local means strength")
    args = ap.parse_args()

    in_dir, out_dir, deg_dir = Path(args.input), Path(args.out), Path(args.degraded_dir)
    proc_dir, fig_dir = out_dir / "processed", out_dir / "figures"
    for d in (proc_dir, fig_dir, deg_dir):
        d.mkdir(parents=True, exist_ok=True)

    paths = sorted(p for p in in_dir.iterdir() if p.suffix.lower() in IMG_EXT)
    if not paths:
        sys.exit(f"No images found in {in_dir}")

    METHODS = build_methods(args.p_low, args.p_high, args.nlm_h)
    rows, sens_rows = [], []
    for idx, path in enumerate(paths):
        name = path.stem
        original = load_resized(path, args.max_side)
        # Fixed seed per image -> identical noise every run, different noise per image.
        rng = np.random.default_rng(args.seed + idx)
        degraded = degrade(original, args.contrast, args.noise_sigma, rng)
        cv2.imwrite(str(deg_dir / f"{name}_degraded.png"), degraded)

        # Sensitivity study: how much does the percentile clipping matter?
        for pl, ph in [(0, 100), (0.1, 99.9), (0.5, 99.5), (1, 99), (5, 95)]:
            m = all_metrics(original, stretch_luminance(degraded, pl, ph))
            sens_rows.append({"image": name, "p_low": pl, "p_high": ph, **m})

        results = {}
        for mname, fn in METHODS.items():
            res = fn(degraded)
            results[mname] = res
            safe = mname.replace(" ", "").replace("(", "_").replace(")", "")
            cv2.imwrite(str(proc_dir / f"{name}__{safe}.jpg"), res, [cv2.IMWRITE_JPEG_QUALITY, 95])
            m = all_metrics(original, res)
            rows.append({"image": name, "method": mname, **m})
        # reference: the original itself is not a method, so it is not in the table.

        # ---- side-by-side figure -------------------------------------------
        panels = [("Original (reference)", original)]
        for mname, res in results.items():
            row = next(r for r in rows if r["image"] == name and r["method"] == mname)
            title = "Degraded (baseline)" if mname == "baseline" else mname
            panels.append((f"{title}\nPSNR {row['PSNR']:.2f} dB | SSIM {row['SSIM']:.3f}", res))
        ncols = 3
        nrows = int(np.ceil(len(panels) / ncols))
        fig, axes = plt.subplots(nrows, ncols, figsize=(4.2 * ncols, 3.4 * nrows * original.shape[0] / original.shape[1] * 1.0 + 0.6 * nrows))
        for ax in np.ravel(axes):
            ax.axis("off")
        for ax, (title, im) in zip(np.ravel(axes), panels):
            ax.imshow(rgb(im))
            ax.set_title(title, fontsize=9)
        fig.suptitle(f"{name}", fontsize=11)
        fig.tight_layout()
        fig.savefig(fig_dir / f"{name}_comparison.png", dpi=100)
        plt.close(fig)

        # ---- luminance histograms -------------------------------------------
        fig, ax = plt.subplots(figsize=(6, 3))
        for label, im in [("original", original), ("degraded", degraded),
                          ("stretch_lum", results["stretch_lum"]),
                          ("hist_eq_lab", results["hist_eq_lab"])]:
            L = cv2.cvtColor(im, cv2.COLOR_BGR2LAB)[:, :, 0]
            h = cv2.calcHist([L], [0], None, [256], [0, 256]).ravel()
            ax.plot(h / h.sum(), label=label, linewidth=1)
        ax.set_xlabel("L value (0-255)")
        ax.set_ylabel("fraction of pixels")
        ax.set_title(f"Luminance histograms - {name}", fontsize=10)
        ax.legend(fontsize=8)
        fig.tight_layout()
        fig.savefig(fig_dir / f"{name}_histograms.png", dpi=100)
        plt.close(fig)
        print(f"[ok] {name}")

    df = pd.DataFrame(rows)
    df.to_csv(out_dir / "metrics.csv", index=False, float_format="%.4f")
    sens = pd.DataFrame(sens_rows)
    sens.to_csv(out_dir / "stretch_sensitivity.csv", index=False, float_format="%.4f")
    print("\nStretch sensitivity (mean over images):")
    print(sens.groupby(["p_low", "p_high"])[["PSNR", "SSIM", "MAE"]].mean().round(3))
    # compact markdown table (one row per image/method) + mean per method
    with open(out_dir / "metrics_table.md", "w") as f:
        f.write(df.to_markdown(index=False, floatfmt=".3f") if _has_tabulate() else df.round(3).to_string(index=False))
        f.write("\n\nMean over images:\n\n")
        mean = df.groupby("method", sort=False)[["PSNR", "SSIM", "MAE"]].mean()
        f.write(mean.to_markdown(floatfmt=".3f") if _has_tabulate() else mean.round(3).to_string())
        f.write("\n")
    print(df.round(3).to_string(index=False))
    print("\nMean over images:")
    print(df.groupby("method", sort=False)[["PSNR", "SSIM", "MAE"]].mean().round(3))


def _has_tabulate():
    try:
        import tabulate  # noqa: F401
        return True
    except ImportError:
        return False


if __name__ == "__main__":
    main()
