"""Quality metrics against the original (reference) image."""
import numpy as np
from skimage.metrics import peak_signal_noise_ratio, structural_similarity


def psnr(ref, img):
    return float(peak_signal_noise_ratio(ref, img, data_range=255))


def ssim(ref, img):
    return float(structural_similarity(ref, img, channel_axis=2, data_range=255))


def mae(ref, img):
    return float(np.mean(np.abs(ref.astype(np.float32) - img.astype(np.float32))))


def all_metrics(ref, img):
    return {"PSNR": psnr(ref, img), "SSIM": ssim(ref, img), "MAE": mae(ref, img)}
