"""Training loop for :class:`TinyUNet` on ISLES 2D stroke slices (CPU-friendly).

Optimises the BCE+Dice combined loss with AdamW and a cosine LR schedule.
After each epoch the validation Dice is measured on the held-out
validation split; the best model so far is written to
``checkpoints/best.pt`` and the latest to ``checkpoints/last.pt``.

Run with::

    python -m scripts.run_training --epochs 100 --batch-size 32
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import torch
from torch.utils.data import DataLoader

from ml.dataset import IslesSliceDataset
from ml.losses import combined_loss, dice_score
from ml.metrics import pixel_accuracy
from ml.model import TinyUNet
from ml.plot_metrics import plot_all_from_files


def evaluate(model, loader, device) -> tuple[float, float]:
    """Average validation Dice and pixel accuracy over a data-loader.

    Switches the model to ``eval`` mode for the duration of the call and
    restores ``train`` mode on the way out so the training loop can pick
    up where it left off.
    """
    model.eval()
    total_dice, total_acc, n = 0.0, 0.0, 0
    with torch.no_grad():
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            logits = model(x)
            total_dice += dice_score(logits, y) * x.size(0)
            total_acc += pixel_accuracy(logits, y) * x.size(0)
            n += x.size(0)
    model.train()
    denom = max(n, 1)
    return total_dice / denom, total_acc / denom


def main():
    """CLI entry-point: parse args, build loaders, run the training loop."""
    here = Path(__file__).resolve().parent.parent
    p = argparse.ArgumentParser(description="Train TinyUNet on ISLES 2D slices")
    p.add_argument("--data-root", default=str(here / "data_processed"))
    p.add_argument("--ckpt-dir", default=str(here / "checkpoints"))
    p.add_argument("--epochs", type=int, default=100)
    p.add_argument("--batch-size", type=int, default=32)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--num-workers", type=int, default=0)
    p.add_argument("--base-channels", type=int, default=16)
    args = p.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device} | torch threads: {torch.get_num_threads()}")

    # --- Data ----------------------------------------------------------------
    ckpt_dir = Path(args.ckpt_dir); ckpt_dir.mkdir(parents=True, exist_ok=True)
    train_ds = IslesSliceDataset(Path(args.data_root) / "train", train=True)
    val_ds = IslesSliceDataset(Path(args.data_root) / "val", train=False)
    print(f"train slices: {len(train_ds)}  val slices: {len(val_ds)}")

    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True,
                              num_workers=args.num_workers)
    val_loader = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False,
                            num_workers=args.num_workers)

    # --- Model + optimiser ---------------------------------------------------
    model = TinyUNet(in_channels=1, out_channels=1, base=args.base_channels).to(device)
    n_params = sum(p.numel() for p in model.parameters())
    print(f"model parameters: {n_params/1e3:.1f}K")

    optim = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(optim, T_max=args.epochs)

    # --- Training loop -------------------------------------------------------
    history = []; best_val = 0.0; t0 = time.time()
    for epoch in range(1, args.epochs + 1):
        model.train()
        epoch_loss, epoch_dice, epoch_acc, n = 0.0, 0.0, 0.0, 0; e_t0 = time.time()
        for step, (x, y) in enumerate(train_loader, 1):
            x, y = x.to(device), y.to(device)
            logits = model(x)
            loss = combined_loss(logits, y)
            optim.zero_grad(); loss.backward(); optim.step()
            with torch.no_grad():
                epoch_loss += loss.item() * x.size(0)
                epoch_dice += dice_score(logits, y) * x.size(0)
                epoch_acc += pixel_accuracy(logits, y) * x.size(0)
                n += x.size(0)
            if step % 25 == 0:
                print(f"  epoch {epoch} step {step}/{len(train_loader)} "
                      f"loss={epoch_loss/n:.4f} dice={epoch_dice/n:.4f} "
                      f"acc={epoch_acc/n:.4f}")
        sched.step()
        train_loss = epoch_loss / n; train_dice = epoch_dice / n
        train_acc = epoch_acc / n
        val_dice, val_acc = evaluate(model, val_loader, device); dt = time.time() - e_t0
        print(f"[epoch {epoch:02d}/{args.epochs}] loss={train_loss:.4f} "
              f"train_dice={train_dice:.4f} val_dice={val_dice:.4f} "
              f"train_acc={train_acc:.4f} val_acc={val_acc:.4f} time={dt/60:.1f}min")

        history.append({"epoch": epoch, "train_loss": train_loss,
                        "train_dice": train_dice, "val_dice": val_dice,
                        "train_accuracy": train_acc, "val_accuracy": val_acc,
                        "epoch_time_sec": dt})
        torch.save({"model": model.state_dict(), "epoch": epoch,
                    "val_dice": val_dice, "args": vars(args)}, ckpt_dir / "last.pt")
        if val_dice > best_val:
            best_val = val_dice
            torch.save({"model": model.state_dict(), "epoch": epoch,
                        "val_dice": val_dice, "args": vars(args)},
                       ckpt_dir / "best.pt")
            print(f"  -> new best (val_dice={val_dice:.4f}) saved best.pt")

    total_min = (time.time() - t0) / 60
    print(f"\nDone in {total_min:.1f}min  best_val_dice={best_val:.4f}")
    history_path = ckpt_dir / "history.json"
    with open(history_path, "w") as f:
        json.dump({"history": history, "best_val_dice": best_val,
                   "total_minutes": total_min, "args": vars(args)}, f, indent=2)

    plot_dir = ckpt_dir / "plots"
    saved = plot_all_from_files(history_path, None, plot_dir)
    if saved:
        print("\nTraining plots saved to:", plot_dir)
        for p in saved:
            print(f"  {p}")


if __name__ == "__main__":
    main()
