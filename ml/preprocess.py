"""
Convert raw ISLES NIfTI MRI volumes into normalized 64x64 .npz slice files.

Pipeline:
1. Load MRI volume + lesion mask
2. Apply z-score normalization
3. Convert 3D MRI into 2D axial slices
4. Remove empty slices
5. Resize slices to 64x64
6. Save processed slices as .npz files

Dataset split:
- Train = 80%
- Validation = 10%
- Test = 10%

This prevents patient-level data leakage.
"""


from __future__ import annotations

import argparse
import random
from pathlib import Path

import nibabel as nib
import numpy as np
import torch
import torch.nn.functional as F
from tqdm import tqdm


# ---------------------------------------------------------------------------
# Volume-level preprocessing primitives
# ---------------------------------------------------------------------------

def zscore_normalise(volume: np.ndarray) -> np.ndarray:
    """Z-score each voxel using the mean / std of non-zero brain voxels."""
    brain = volume[volume > 0]
    if brain.size == 0:
        return volume.astype(np.float32)
    mu, sigma = brain.mean(), brain.std() + 1e-8 #Compute Mean and Standard Deviation
    out = (volume - mu) / sigma #FORMULA OF Z-Score Normalization
    out[volume <= 0] = 0.0 
    return out.astype(np.float32)


def resize_2d(arr: np.ndarray, target: int, mode: str = "bilinear") -> np.ndarray:
    """Resize a 2D array to ``(target, target)`` (bilinear for images, nearest for masks)."""
    t = torch.from_numpy(arr).float().unsqueeze(0).unsqueeze(0)
    if mode == "bilinear":
        out = F.interpolate(t, size=(target, target), mode="bilinear", align_corners=False)
    else:
        out = F.interpolate(t, size=(target, target), mode="nearest")
    return out.squeeze().numpy()


def slice_volume(image: np.ndarray, mask: np.ndarray, target_size: int = 64):
    """Drop empty axial slices and resize the rest to a square of ``target_size``."""
    out_imgs, out_msks, kept = [], [], []
    for z in range(image.shape[2]):
        sl_img = image[:, :, z]
        sl_msk = mask[:, :, z]
        if (sl_img > 0).sum() < 50:
            continue
        img_r = resize_2d(sl_img.astype(np.float32), target_size, "bilinear").astype(np.float32)
        msk_r = (resize_2d(sl_msk.astype(np.float32), target_size, "nearest") > 0.5).astype(np.uint8)
        out_imgs.append(img_r); out_msks.append(msk_r); kept.append(z)
    return out_imgs, out_msks, kept


# ---------------------------------------------------------------------------
# Per-case + patient-level split helpers
# ---------------------------------------------------------------------------

def process_case(
    image_path: Path, mask_path: Path, out_dir: Path,
    case_id: str, target_size: int = 64,
) -> int:
    """Preprocess one patient and write each kept slice as a ``.npz`` file."""
    image = zscore_normalise(nib.load(str(image_path)).get_fdata())
    mask = (nib.load(str(mask_path)).get_fdata() > 0).astype(np.uint8)
    imgs, msks, idxs = slice_volume(image, mask, target_size)
    for img2d, msk2d, z in zip(imgs, msks, idxs):
        np.savez_compressed(out_dir / f"{case_id}_z{z:03d}.npz", image=img2d, mask=msk2d)
    return len(imgs)


def split_cases(case_ids: list[str], seed: int = 42, ratios=(0.8, 0.1, 0.1)):
    """Patient-disjoint random shuffle into ``(train, val, test)``."""
    random.Random(seed).shuffle(case_ids)
    n = len(case_ids); n_tr = int(n * ratios[0]); n_va = int(n * ratios[1])
    return case_ids[:n_tr], case_ids[n_tr:n_tr + n_va], case_ids[n_tr + n_va:]


# ---------------------------------------------------------------------------
# CLI entry-point (delegated to from ``scripts.run_preprocessing``)
# ---------------------------------------------------------------------------

def main():
    """CLI entry-point: discover cases, split them, write preprocessed slices."""
    here = Path(__file__).resolve().parent.parent
    p = argparse.ArgumentParser(description="Preprocess ISLES NIfTI volumes")
    p.add_argument("--data-root", default=str(here / "my_dataset"))
    p.add_argument("--out-root", default=str(here / "data_processed"))
    p.add_argument("--target-size", type=int, default=64)
    args = p.parse_args()

    img_dir = Path(args.data_root) / "images"
    msk_dir = Path(args.data_root) / "masks"
    case_ids = sorted([p.stem for p in img_dir.glob("case_*.nii")])
    print(f"Found {len(case_ids)} cases.")

    train_ids, val_ids, test_ids = split_cases(case_ids)
    print(f"Split -> train: {len(train_ids)}  val: {len(val_ids)}  test: {len(test_ids)}")

    splits = {"train": train_ids, "val": val_ids, "test": test_ids}
    totals = {}
    for split, ids in splits.items():
        out_dir = Path(args.out_root) / split
        out_dir.mkdir(parents=True, exist_ok=True)
        n = 0
        for cid in tqdm(ids, desc=f"[{split}]"):
            ip = img_dir / f"{cid}.nii"
            mp = msk_dir / f"{cid}_mask.nii"
            if ip.exists() and mp.exists():
                n += process_case(ip, mp, out_dir, cid, args.target_size)
        totals[split] = n
        print(f"  {split}: {n} slices -> {out_dir}")
    print("\nDone.")
    for k, v in totals.items():
        print(f"  {k:5s} slices: {v}")


if __name__ == "__main__":
    main()



