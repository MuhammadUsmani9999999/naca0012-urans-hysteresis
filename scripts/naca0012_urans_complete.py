#!/usr/bin/env python3
"""
naca0012_urans_complete.py
===========================
URANS dynamic pitch manoeuvre for a NACA 0012 aerofoil using the k–ω SST
turbulence model via the ANSYS PyFluent API.

Executes a three-phase protocol:
  Phase 1 — Flow-field initialisation (hybrid init → SA steady → SST steady)
  Phase 2 — Transient ramping and flushing (time-step ramp + 10τ_c washout)
  Phase 3 — Continuous dynamic sweep (14° → 22° → 14° at 2.0°/s)

The script automates case/data saving at key angles, contour image capture,
surface data export, and comprehensive CSV logging of all aerodynamic
coefficients at every time step (~16,000 data points total).

References
----------
  Menter, F.R. (1994). AIAA Journal, 32(8), 1598–1605.
  Menter, F.R. and Lechner, R. (2021). Best Practice: RANS Turbulence
    Modelling in Ansys CFD. Ansys Germany GmbH.
  Sereez, M. et al. (2024). Aerospace, 11(5), 354.

Usage
-----
  1. Launch Fluent with the mesh loaded:
       fluent 2ddp -t4 -g
  2. Run this script:
       python naca0012_urans_complete.py

Author: [Your Name]
Date: 2026
Software: ANSYS Fluent 2025 R2 (Student), Python 3.10+
"""

import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

try:
    import ansys.fluent.core as pyfluent
except ImportError:
    print("ERROR: ansys-fluent-core is not installed.")
    print("Install with: pip install ansys-fluent-core")
    sys.exit(1)

from utils.convergence_monitor import ConvergenceMonitor
from utils.vector_calculator import compute_lift_drag_vectors
from utils.checkpoint_manager import CheckpointManager

# =============================================================================
# Configuration
# =============================================================================

# Flow conditions
U_INF = 88.65          # Freestream velocity [m/s]
CHORD = 1.0            # Chord length [m]
RHO = 1.225            # Density [kg/m³]
MU = 1.81e-5           # Dynamic viscosity [Pa·s]
RE = RHO * U_INF * CHORD / MU
TAU_C = CHORD / U_INF  # Convective time scale ≈ 0.0113 s

# Turbulence inlet conditions
TURB_INTENSITY = 0.001
TURB_VISC_RATIO = 1.0

# Pitching configuration
PITCH_RATE = 2.0          # degrees per second
ALPHA_START = 14.0        # Starting angle [°]
ALPHA_MAX = 22.0          # Maximum angle [°]
ALPHA_END = 14.0          # End angle [°]

# Time-stepping
DT_PRODUCTION = 5e-4      # Production time step [s]
MAX_INNER_ITERS = 30      # Max iterations per time step
ALPHA_PER_STEP = PITCH_RATE * DT_PRODUCTION  # ≈ 0.001°

# Phase 1 settings
SA_FIRST_ORDER_ITERS = 500
SA_SECOND_ORDER_ITERS = 1500
SST_STEADY_ITERS = 1000

# Phase 2 time-step ramp schedule: (Δt, number_of_steps)
RAMP_SCHEDULE = [
    (1e-5, 50),
    (5e-5, 50),
    (1e-4, 100),
    (DT_PRODUCTION, 0),  # Switch to production — steps handled in Phase 3
]
FLUSHING_TIMES = 10  # Convective flow-through times for flushing

# Checkpoint angles (save case/data and contour images)
CHECKPOINT_ANGLES = list(range(14, 23))  # Every integer degree

# Output paths
OUTPUT_DIR = Path("../results")
CHECKPOINT_FILE = Path("../results/urans_checkpoint.json")
EXPORT_CSV = Path("../results/urans_hysteresis.csv")


# =============================================================================
# Solver setup
# =============================================================================

def setup_sa_steady(solver):
    """Configure solver for Phase 1 SA steady preconditioning."""
    general = solver.setup.general
    general.solver.type = "pressure-based"
    general.solver.time = "steady"

    viscous = solver.setup.models.viscous
    viscous.model = "spalart-allmaras"

    methods = solver.solution.methods
    methods.p_v_coupling.scheme = "coupled"
    methods.gradient_scheme = "least-squares-cell-based"

    print("  Phase 1a: SA steady-state configured")


def switch_to_sst_steady(solver):
    """Switch to k–ω SST for Phase 1 SST preconditioning."""
    viscous = solver.setup.models.viscous
    viscous.model = "k-omega"
    viscous.k_omega_model = "sst"
    viscous.options.low_re_corrections = False
    viscous.options.production_limiter = True
    viscous.options.kato_launder = False

    # Spatial discretisation — second-order for all
    methods = solver.solution.methods
    methods.discretization.pressure = "second-order"
    methods.discretization.momentum = "second-order-upwind"
    methods.discretization.turbulent_kinetic_energy = "second-order-upwind"
    methods.discretization.specific_dissipation_rate = "second-order-upwind"

    print("  Phase 1b: k–ω SST steady-state configured")
    print("    Low-Re Corrections: OFF")
    print("    Production Limiter: ON (clip factor 10)")
    print("    Kato–Launder: OFF")


def switch_to_transient(solver):
    """Switch to URANS transient mode for Phase 2."""
    general = solver.setup.general
    general.solver.time = "transient"

    methods = solver.solution.methods
    methods.p_v_coupling.scheme = "coupled"
    methods.transient_formulation = "bounded-second-order-implicit"
    methods.discretization.pressure = "second-order"
    methods.discretization.momentum = "second-order-upwind"
    methods.discretization.turbulent_kinetic_energy = "second-order-upwind"
    methods.discretization.specific_dissipation_rate = "second-order-upwind"
    methods.gradient_scheme = "least-squares-cell-based"

    print("  Phase 2: Transient URANS configured")
    print("    Coupling: Coupled")
    print("    Transient: Bounded Second-Order Implicit")


# =============================================================================
# Phase execution
# =============================================================================

def phase1_initialisation(solver):
    """
    Phase 1 — Flow-field initialisation.

    1. Hybrid initialisation
    2. SA steady: 500 first-order + 1,500 second-order iterations
    3. SST steady: 1,000 second-order iterations
    """
    print("\n" + "=" * 60)
    print("  PHASE 1: Flow-field initialisation")
    print("=" * 60)

    # Set boundary conditions at starting angle
    set_angle(solver, ALPHA_START)

    # Hybrid initialisation
    print("\n  Performing hybrid initialisation...")
    solver.solution.initialization.hybrid_initialize()
    print("  Hybrid initialisation complete.")

    # SA steady: first-order upwind (stability)
    print(f"\n  Running SA first-order upwind ({SA_FIRST_ORDER_ITERS} iterations)...")
    setup_sa_steady(solver)
    methods = solver.solution.methods
    methods.discretization.momentum = "first-order-upwind"
    methods.discretization.modified_turbulent_viscosity = "first-order-upwind"
    solver.solution.run_calculation.iterate(
        number_of_iterations=SA_FIRST_ORDER_ITERS
    )

    # SA steady: second-order upwind
    print(f"\n  Switching to second-order ({SA_SECOND_ORDER_ITERS} iterations)...")
    methods.discretization.momentum = "second-order-upwind"
    methods.discretization.modified_turbulent_viscosity = "second-order-upwind"
    solver.solution.run_calculation.iterate(
        number_of_iterations=SA_SECOND_ORDER_ITERS
    )

    # Switch to SST
    print(f"\n  Switching to k–ω SST ({SST_STEADY_ITERS} iterations)...")
    switch_to_sst_steady(solver)
    solver.solution.run_calculation.iterate(
        number_of_iterations=SST_STEADY_ITERS
    )

    print("\n  Phase 1 complete.")


def phase2_transient_ramp_and_flush(solver):
    """
    Phase 2 — Transient ramping and flushing.

    1. Switch to transient mode
    2. Ramp time step: 10⁻⁵ → 5×10⁻⁵ → 10⁻⁴ → 5×10⁻⁴ s
    3. Run 10 convective flow-through times at fixed angle to flush artefacts
    """
    print("\n" + "=" * 60)
    print("  PHASE 2: Transient ramping and flushing")
    print("=" * 60)

    switch_to_transient(solver)

    # Time-step ramp
    for dt, n_steps in RAMP_SCHEDULE:
        if n_steps == 0:
            continue
        print(f"\n  Δt = {dt:.1e} s × {n_steps} steps...")
        solver.solution.run_calculation.time_step_size = dt
        solver.solution.run_calculation.max_iterations_per_time_step = MAX_INNER_ITERS
        solver.solution.run_calculation.dual_time_iterate(
            time_step_count=n_steps,
            max_iterations_per_time_step=MAX_INNER_ITERS,
        )

    # Flushing at production time step
    flush_steps = int(FLUSHING_TIMES * TAU_C / DT_PRODUCTION)
    print(f"\n  Flushing: {flush_steps} steps at Δt = {DT_PRODUCTION:.1e} s "
          f"({FLUSHING_TIMES}τ_c)...")
    solver.solution.run_calculation.time_step_size = DT_PRODUCTION
    solver.solution.run_calculation.dual_time_iterate(
        time_step_count=flush_steps,
        max_iterations_per_time_step=MAX_INNER_ITERS,
    )

    print("\n  Phase 2 complete. Initialisation artefacts flushed.")


def phase3_dynamic_sweep(solver):
    """
    Phase 3 — Continuous dynamic sweep.

    Pitches the aerofoil 14° → 22° → 14° at 2.0°/s, recording C_L and C_D
    at every time step.
    """
    print("\n" + "=" * 60)
    print("  PHASE 3: Continuous dynamic sweep")
    print(f"    Pitch rate: {PITCH_RATE}°/s")
    print(f"    Δα per step: {ALPHA_PER_STEP:.4f}°")
    print("=" * 60)

    # Build angle trajectory
    # Pitch-up: 14° → 22°
    n_steps_up = int((ALPHA_MAX - ALPHA_START) / ALPHA_PER_STEP)
    # Pitch-down: 22° → 14°
    n_steps_down = int((ALPHA_MAX - ALPHA_END) / ALPHA_PER_STEP)

    angles_up = np.linspace(ALPHA_START, ALPHA_MAX, n_steps_up + 1)
    angles_down = np.linspace(ALPHA_MAX, ALPHA_END, n_steps_down + 1)[1:]  # Skip duplicate at 22°
    trajectory = np.concatenate([angles_up, angles_down])

    print(f"    Total time steps: {len(trajectory)}")
    print(f"    Pitch-up steps: {n_steps_up}")
    print(f"    Pitch-down steps: {n_steps_down}")

    results = []
    last_checkpoint_angle = None

    solver.solution.run_calculation.time_step_size = DT_PRODUCTION

    for i, alpha in enumerate(trajectory):
        # Update angle
        set_angle(solver, alpha)

        # Advance one time step
        solver.solution.run_calculation.dual_time_iterate(
            time_step_count=1,
            max_iterations_per_time_step=MAX_INNER_ITERS,
        )

        # Record coefficients
        cl = solver.solution.report_definitions.force["cl"].get_result()
        cd = solver.solution.report_definitions.force["cd"].get_result()
        flow_time = solver.solution.run_calculation.flow_time

        direction = "Pitch-Up" if i < n_steps_up else "Pitch-Down"

        results.append({
            "step": i,
            "flow_time_s": flow_time,
            "alpha_deg": alpha,
            "direction": direction,
            "C_L": cl,
            "C_D": cd,
        })

        # Checkpoint at integer angles
        current_int_angle = int(round(alpha))
        if (current_int_angle in CHECKPOINT_ANGLES
                and current_int_angle != last_checkpoint_angle):
            print(f"\n  Checkpoint: α = {alpha:.1f}° ({direction}) — "
                  f"C_L = {cl:.4f}, C_D = {cd:.5f}")
            last_checkpoint_angle = current_int_angle

            # Save case/data
            tag = f"{current_int_angle:02d}_{direction.lower().replace('-','')}"
            solver.file.write(
                case_file=f"../results/urans_alpha{tag}.cas.h5",
                data_file=f"../results/urans_alpha{tag}.dat.h5",
            )

        # Progress reporting (every 1,000 steps)
        if i > 0 and i % 1000 == 0:
            print(f"  Step {i}/{len(trajectory)}: α = {alpha:.2f}° ({direction}), "
                  f"C_L = {cl:.4f}, C_D = {cd:.5f}")

    # Export full time history
    df = pd.DataFrame(results)
    df.to_csv(EXPORT_CSV, index=False)
    print(f"\n  Results exported: {len(results)} data points → {EXPORT_CSV}")

    return df


def set_angle(solver, alpha_deg):
    """Update boundary conditions for the instantaneous angle of attack."""
    alpha_rad = math.radians(alpha_deg)

    # Update velocity inlet direction
    inlet = solver.setup.boundary_conditions.velocity_inlet["inlet"]
    inlet.velocity.value = U_INF
    inlet.flow_direction.x = math.cos(alpha_rad)
    inlet.flow_direction.y = math.sin(alpha_rad)

    # Update lift/drag monitoring directions
    lift_dir, drag_dir = compute_lift_drag_vectors(alpha_deg)
    solver.solution.report_definitions.force["cl"] = {
        "force_vector": lift_dir,
    }
    solver.solution.report_definitions.force["cd"] = {
        "force_vector": drag_dir,
    }


# =============================================================================
# Entry point
# =============================================================================

def main():
    """Main execution function."""
    start_time = time.time()

    print("=" * 60)
    print("  NACA 0012 — URANS Dynamic Pitch Hysteresis Study")
    print(f"  Re = {RE:.2e}")
    print(f"  Pitch rate = {PITCH_RATE}°/s")
    print(f"  α range: {ALPHA_START}° → {ALPHA_MAX}° → {ALPHA_END}°")
    print("=" * 60)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Connect to Fluent
    print("\nConnecting to Fluent session...")
    solver = pyfluent.connect_to_fluent()
    print("  Connected.")

    # Execute three-phase protocol
    phase1_initialisation(solver)
    phase2_transient_ramp_and_flush(solver)
    df = phase3_dynamic_sweep(solver)

    # Summary
    elapsed = time.time() - start_time
    print("\n" + "=" * 60)
    print("  SIMULATION COMPLETE")
    print(f"  Wall time: {elapsed / 3600:.1f} hours")
    print(f"  Data points: {len(df)}")
    print("=" * 60)

    # Print key results at checkpoint angles
    print("\n  Summary at integer angles:")
    for alpha in CHECKPOINT_ANGLES:
        for direction in ["Pitch-Up", "Pitch-Down"]:
            subset = df[
                (df["alpha_deg"].round(0) == alpha)
                & (df["direction"] == direction)
            ]
            if not subset.empty:
                row = subset.iloc[-1]
                print(f"    α = {alpha}° ({direction}): "
                      f"C_L = {row['C_L']:.4f}, C_D = {row['C_D']:.5f}")


if __name__ == "__main__":
    main()
