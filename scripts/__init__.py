"""Thin CLI wrappers around the heavy lifting in :mod:`ml`.

Each ``run_*.py`` simply prepends the project root to ``sys.path`` (so
``ml.*`` imports work when the script is invoked directly) and then
delegates to the corresponding ``main()`` from :mod:`ml`.

Run from the project root with::

    python -m scripts.run_preprocessing
    python -m scripts.run_training
    python -m scripts.run_evaluation
"""
