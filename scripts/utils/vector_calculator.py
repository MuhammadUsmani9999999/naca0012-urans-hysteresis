"""
vector_calculator.py
=====================
Computes lift and drag direction vectors for an arbitrary angle of attack.

For a freestream at angle α to the horizontal:
  - Drag direction:  (cos α, sin α)     — aligned with freestream
  - Lift direction:  (-sin α, cos α)    — perpendicular to freestream
"""

import math
from typing import Tuple


def compute_lift_drag_vectors(
    alpha_deg: float,
) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    """
    Compute unit direction vectors for lift and drag forces.

    Parameters
    ----------
    alpha_deg : float
        Angle of attack in degrees.

    Returns
    -------
    lift_dir : tuple[float, float]
        (x, y) components of the lift direction unit vector.
    drag_dir : tuple[float, float]
        (x, y) components of the drag direction unit vector.
    """
    alpha_rad = math.radians(alpha_deg)

    drag_dir = (math.cos(alpha_rad), math.sin(alpha_rad))
    lift_dir = (-math.sin(alpha_rad), math.cos(alpha_rad))

    return lift_dir, drag_dir


def compute_velocity_components(
    u_inf: float, alpha_deg: float
) -> Tuple[float, float]:
    """
    Compute freestream velocity components.

    Parameters
    ----------
    u_inf : float
        Freestream velocity magnitude [m/s].
    alpha_deg : float
        Angle of attack in degrees.

    Returns
    -------
    u_x, u_y : tuple[float, float]
        Velocity components [m/s].
    """
    alpha_rad = math.radians(alpha_deg)
    return u_inf * math.cos(alpha_rad), u_inf * math.sin(alpha_rad)
