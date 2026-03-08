"""
convergence_monitor.py
=======================
Moving-window convergence detection for steady-state RANS iterations.

The solver continuously samples C_L and C_D every N iterations and declares
convergence only when the standard deviation of both coefficients falls below
a user-specified threshold (default: 10⁻⁴).
"""

from collections import deque
from typing import Optional

import numpy as np


class ConvergenceMonitor:
    """
    Monitors aerodynamic coefficient convergence using a moving-window
    standard-deviation criterion.

    Parameters
    ----------
    window_size : int
        Number of most recent samples to consider.
    threshold : float
        Maximum standard deviation of C_L and C_D for convergence.
    """

    def __init__(self, window_size: int = 50, threshold: float = 1e-4):
        self.window_size = window_size
        self.threshold = threshold
        self._cl_history: deque = deque(maxlen=window_size)
        self._cd_history: deque = deque(maxlen=window_size)

    def reset(self):
        """Clear all stored samples."""
        self._cl_history.clear()
        self._cd_history.clear()

    def update(self, cl: float, cd: float):
        """
        Add a new sample.

        Parameters
        ----------
        cl : float
            Current lift coefficient.
        cd : float
            Current drag coefficient.
        """
        self._cl_history.append(cl)
        self._cd_history.append(cd)

    def is_converged(self) -> bool:
        """
        Check whether both C_L and C_D have converged.

        Returns
        -------
        bool
            True if both coefficients have standard deviation below threshold.
        """
        if len(self._cl_history) < self.window_size:
            return False

        cl_std = np.std(list(self._cl_history))
        cd_std = np.std(list(self._cd_history))

        return cl_std < self.threshold and cd_std < self.threshold

    @property
    def current_cl(self) -> Optional[float]:
        """Most recent C_L value."""
        return self._cl_history[-1] if self._cl_history else None

    @property
    def current_cd(self) -> Optional[float]:
        """Most recent C_D value."""
        return self._cd_history[-1] if self._cd_history else None

    @property
    def cl_std(self) -> Optional[float]:
        """Current standard deviation of C_L window."""
        if len(self._cl_history) < 2:
            return None
        return float(np.std(list(self._cl_history)))

    @property
    def cd_std(self) -> Optional[float]:
        """Current standard deviation of C_D window."""
        if len(self._cd_history) < 2:
            return None
        return float(np.std(list(self._cd_history)))
