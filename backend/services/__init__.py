"""Service layer: pure-Python helpers that have no FastAPI dependency.

Putting domain logic here (instead of inside the route handlers) keeps the
routes thin and makes the underlying functions trivially unit-testable.
"""
