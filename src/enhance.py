"""Image enhancement methods (classical, no deep learning).

Every method takes and returns a BGR uint8 image (OpenCV convention).
"""
import cv2
import numpy as np


# ----------------------------------------------------------------------------
# Degradation (used to create the synthetic "degraded" version of each image)
# ----------------------------------------------------------------------------
def degrade(img_bgr, contrast=0.45, noise_sigma=6.0, rng=None):
    """Reduce contrast around mid-gray and add Gaussian noise.

    out = 127.5 + contrast * (img - 127.5) + N(0, noise_sigma^2)

    contrast    : factor in (0, 1]; 1 = unchanged, 0.45 = strong loss of contrast
    noise_sigma : standard deviation of the noise, in gray levels (0-255 scale)
    rng         : numpy Generator, so that the noise is reproducible
    """
    if rng is None:
        rng = np.random.default_rng(0)
    x = img_bgr.astype(np.float32)
    x = 127.5 + contrast * (x - 127.5)
    x = x + rng.normal(0.0, noise_sigma, size=x.shape).astype(np.float32)
    return np.clip(np.rint(x), 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------
# Method 1: baseline (no processing)
# ----------------------------------------------------------------------------
def baseline(img_bgr):
    return img_bgr.copy()


# ----------------------------------------------------------------------------
# Method 2: linear contrast stretching
# ----------------------------------------------------------------------------
def _stretch(channel, p_low=0.0, p_high=100.0):
    """Linearly map the [p_low, p_high] percentiles of `channel` to [0, 255].

    p_low=0, p_high=100 is the classic min-max stretch. Larger clipping
    (e.g. 1 and 99) saturates more pixels: punchier image, but it moves away
    from the original reference (see the sensitivity study).
    """
    lo, hi = np.percentile(channel, [p_low, p_high])
    if hi - lo < 1e-6:
        return channel.copy()
    y = (channel.astype(np.float32) - lo) * (255.0 / (hi - lo))
    return np.clip(y, 0, 255).astype(np.uint8)


def stretch_luminance(img_bgr, p_low=0.0, p_high=100.0):
    """MAIN variant: stretch only the L (lightness) channel in CIE Lab.

    The chromatic channels a, b are kept, so hues are (almost) preserved.
    """
    lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
    lab[:, :, 0] = _stretch(lab[:, :, 0], p_low, p_high)
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)


def stretch_per_channel(img_bgr, p_low=0.0, p_high=100.0):
    """EXTRA variant: stretch B, G, R independently (can shift colors)."""
    out = np.empty_like(img_bgr)
    for c in range(3):
        out[:, :, c] = _stretch(img_bgr[:, :, c], p_low, p_high)
    return out


# ----------------------------------------------------------------------------
# Method 3: histogram equalization (on luminance only)
# ----------------------------------------------------------------------------
def hist_equalization_lab(img_bgr):
    """Equalize the L channel of CIE Lab; a and b are kept unchanged."""
    lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
    lab[:, :, 0] = cv2.equalizeHist(lab[:, :, 0])
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)


# ----------------------------------------------------------------------------
# Method 4 (our choice): luminance stretch + non-local means denoising
# Motivation: stretching multiplies the noise by the same factor as the signal,
# so we denoise afterwards. Denoising can smooth fine details (trade-off).
# ----------------------------------------------------------------------------
def stretch_then_nlm(img_bgr, p_low=0.0, p_high=100.0, h=6, h_color=6):
    stretched = stretch_luminance(img_bgr, p_low, p_high)
    return cv2.fastNlMeansDenoisingColored(stretched, None, h, h_color, 7, 21)


def build_methods(p_low=0.0, p_high=100.0, nlm_h=6):
    """Return the ordered dict of methods with FIXED parameters.

    Order matters: it is the column order in the figures and tables.
    """
    return {
        "baseline": baseline,
        "stretch_lum": lambda im: stretch_luminance(im, p_low, p_high),
        "hist_eq_lab": hist_equalization_lab,
        "stretch_nlm": lambda im: stretch_then_nlm(im, p_low, p_high, nlm_h, nlm_h),
        "stretch_rgb (extra)": lambda im: stretch_per_channel(im, p_low, p_high),
    }


METHODS = build_methods()
