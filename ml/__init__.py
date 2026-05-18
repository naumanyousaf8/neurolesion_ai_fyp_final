"""Machine-learning subpackage: model, data, training, inference, evaluation.

The package is deliberately flat (no further sub-folders) so the imports
read naturally from any consumer::

    from ml.model   import TinyUNet
    from ml.predict import load_model, predict_volume
    from ml.losses  import combined_loss, dice_score

Modules
-------
:mod:`ml.model`        - 2D U-Net architecture (compact, CPU-friendly).
:mod:`ml.losses`       - Dice loss, BCE+Dice combined loss, Dice metric.
:mod:`ml.dataset`      - PyTorch ``Dataset`` for preprocessed slices.
:mod:`ml.preprocess`   - Raw NIfTI -> normalised .npz slice converter.
:mod:`ml.train`        - Training loop (AdamW + Cosine LR, best-checkpoint).
:mod:`ml.predict`      - Volume-level inference helpers.
:mod:`ml.evaluate`     - Held-out test set Dice / Precision / Recall.
"""
