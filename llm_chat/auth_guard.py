"""Shared credential rejection latch extracted from first_observation.execute.

Preserves 8021aca's typed-auth semantics; other API errors do not block a batch.
"""
from threading import Lock

class AuthFailureLatch:
    def __init__(self, auth_error_types=()):
        self.auth_error_types=auth_error_types
        self.failure=None
        self._lock=Lock()

    def observe(self, exc):
        if self.auth_error_types and isinstance(exc,self.auth_error_types):
            with self._lock:
                if self.failure is None:self.failure=type(exc).__name__
        return self.failure
