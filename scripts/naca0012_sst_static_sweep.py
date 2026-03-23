#!/usr/bin/env python3
"""
NACA 0012 Static Alpha Sweep — k-omega SST (Bifurcation Hysteresis Study)
==========================================================================
VERSION 2 — CONVERGENCE FIX
----------------------------
v1 terminated early because Fluent's residual convergence criteria (1e-5)
were met after only a handful of iterations, producing unconverged force
coefficients. Symptoms included: erratic lift slope, negative drag, and
spurious hysteresis at all angles including fully attached flow.

Fixes applied:
  1. Residual convergence criteria set to 1e-12 (effectively disabled)
     so Fluent NEVER terminates early on residuals alone.
  2. Iterations run in batches of 200 with C_L monitored after each batch.
  3. Adaptive stopping: a station is converged when the running-average
     C_L changes by less than 0.1% over two consecutive batches.
  4. Minimum iteration floor: 1000 iters for attached flow, 2000 for
     post-stall, regardless of C_L convergence.
  5. Maximum iteration ceiling: 3000 for attached, 5000 for post-stall.

Sweep: 0deg -> 22deg -> 0deg at 1deg increments (steady RANS)
Turbulence Model: k-omega SST (same as pitching simulation)
Re = 6e6, U_inf = 88.65 m/s, chord = 1.0 m
Mesh: 501,473 nodes / 499,848 elements (Fluent, double precision)
"""

import ansys.fluent.core as pyfluent
import numpy as np
import math
import os
import csv
import time
from datetime import datetime
from dataclasses import dataclass


# =============================================================================
# HELPER FUNCTIONS (matched from naca0012_dynamic_sweep.py)
# =============================================================================

def extract_coefficient(result):
    """Extract numeric value from PyFluent report result.
    Identical to the dynamic sweep script for consistency."""
    if result is None:
        return float('nan')

    try:
        if isinstance(result, list) and len(result) > 0:
            item = result[0]
            if isinstance(item, dict):
                val = list(item.values())[0]
                if isinstance(val, list) and len(val) > 0:
                    return float(val[0])
                return float(val)
            return float(item)

        if isinstance(result, dict):
            val = list(result.values())[0]
            if isinstance(val, list) and len(val) > 0:
                return float(val[0])
            return float(val)

        return float(result)

    except (TypeError, ValueError, IndexError):
        return float('nan')


def log_message(message: str, log_file: str = None):
    """Print and optionally log message with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] {message}"
    print(formatted)

    if log_file:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(formatted + '\n')


def get_force_vectors(alpha_deg: float) -> tuple:
    """Calculate lift and drag direction vectors (3-component for Fluent)."""
    alpha_rad = math.radians(alpha_deg)
    lift_dir = [-math.sin(alpha_rad), math.cos(alpha_rad), 0]
    drag_dir = [math.cos(alpha_rad), math.sin(alpha_rad), 0]
    return lift_dir, drag_dir


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class StaticSweepConfig:
    """All simulation parameters — matched to naca0012_dynamic_sweep.py"""

    # Flow conditions (identical to dynamic sweep)
    U_inf: float = 88.65          # Freestream velocity [m/s]
    chord: float = 1.0            # Chord length [m]
    rho: float = 1.225            # Density [kg/m^3]
    mu: float = 1.81e-5           # Dynamic viscosity [Pa.s]

    # Alpha sweep definition
    alpha_start: float = 0.0      # Starting angle [deg]
    alpha_max: float = 22.0       # Maximum angle [deg] — matches pitching sweep
    alpha_step: float = 1.0       # Increment [deg]
    include_downstroke: bool = True  # Sweep back down for hysteresis detection

    # --- CONVERGENCE SETTINGS (v2 fix) ---
    # Iteration batches: run in chunks and check C_L between each
    batch_size: int = 200         # Iterations per batch

    # Minimum iterations (floor — always run at least this many)
    min_iters_attached: int = 1000   # For alpha < 12
    min_iters_stall: int = 2000      # For alpha >= 12

    # Maximum iterations (ceiling — stop even if not converged)
    max_iters_attached: int = 3000   # For alpha < 12
    max_iters_stall: int = 5000      # For alpha >= 12

    # C_L convergence tolerance: stop when relative change < this
    cl_convergence_tol: float = 0.001  # 0.1% change between batches

    # CFL for Coupled solver (steady)
    cfl_initial: int = 50            # Conservative for first 2 batches
    cfl_ramp: int = 150              # After stabilisation

    # File paths (matched to your system)
    mesh_file: str = r"F:\pf\design modeller\NACA 0012_files\dp0\FFF-2\MECH\FFF-2.1.msh"
    output_dir: str = r"F:\pf\design modeller\NACA 0012_files\static_sweep_output"

    # Zone names (from dynamic sweep script)
    airfoil_zone: str = "naca0012"
    inlet_zone: str = "inlet"


# =============================================================================
# BOUNDARY CONDITION UPDATE (matched from dynamic sweep)
# =============================================================================

def update_inlet_bc(solver, alpha_deg: float, config: StaticSweepConfig):
    """Update inlet boundary condition for new angle of attack.
    Uses the same API pattern as naca0012_dynamic_sweep.py."""

    rad = math.radians(alpha_deg)
    dir_x = math.cos(rad)
    dir_y = math.sin(rad)

    inlet = solver.settings.setup.boundary_conditions.velocity_inlet[config.inlet_zone]
    inlet.momentum.set_state({
        'velocity_specification_method': 'Magnitude and Direction',
        'velocity_magnitude': {'option': 'value', 'value': config.U_inf},
        'flow_direction': [
            {'option': 'value', 'value': dir_x},
            {'option': 'value', 'value': dir_y}
        ]
    })


# =============================================================================
# REPORT DEFINITIONS (matched from dynamic sweep)
# =============================================================================

def setup_report_definitions(solver, alpha_deg: float, config: StaticSweepConfig):
    """Create lift and drag coefficient reports."""

    lift_dir, drag_dir = get_force_vectors(alpha_deg)

    rep_defs = solver.settings.solution.report_definitions

    # Lift coefficient
    try:
        rep_defs.lift.create("cl")
    except Exception:
        pass  # May already exist
    rep_defs.lift["cl"].zones.set_state([config.airfoil_zone])
    rep_defs.lift["cl"].force_vector.set_state(lift_dir)

    # Drag coefficient
    try:
        rep_defs.drag.create("cd")
    except Exception:
        pass  # May already exist
    rep_defs.drag["cd"].zones.set_state([config.airfoil_zone])
    rep_defs.drag["cd"].force_vector.set_state(drag_dir)

    log_message(f"Report definitions: Cl, Cd on zone '{config.airfoil_zone}'")


def update_force_vectors(solver, alpha_deg: float):
    """Update lift and drag report definitions for current angle."""

    lift_dir, drag_dir = get_force_vectors(alpha_deg)

    rep_defs = solver.settings.solution.report_definitions
    rep_defs.lift["cl"].force_vector.set_state(lift_dir)
    rep_defs.drag["cd"].force_vector.set_state(drag_dir)


def get_coefficients(solver):
    """Read current C_L and C_D from Fluent."""
    try:
        rep_defs = solver.settings.solution.report_definitions
        result_cl = rep_defs.compute(report_defs=["cl"])
        result_cd = rep_defs.compute(report_defs=["cd"])
        cl = extract_coefficient(result_cl)
        cd = extract_coefficient(result_cd)
        return cl, cd
    except Exception:
        return float('nan'), float('nan')


# =============================================================================
# REFERENCE VALUES (matched from dynamic sweep)
# =============================================================================

def setup_reference_values(solver, config: StaticSweepConfig):
    """Set reference values for coefficient calculation."""

    solver.settings.setup.reference_values.area = config.chord * 1.0
    solver.settings.setup.reference_values.length = config.chord
    solver.settings.setup.reference_values.velocity = config.U_inf
    solver.settings.setup.reference_values.density = config.rho

    log_message(f"Reference values: Area={config.chord} m2, "
                f"Velocity={config.U_inf} m/s, Density={config.rho} kg/m3")


# =============================================================================
# SOLVER SETUP (matched from dynamic sweep — TUI commands)
# =============================================================================

def setup_solver_methods(solver, config: StaticSweepConfig):
    """Configure solver methods using TUI commands (same as dynamic sweep)."""

    # Ensure steady mode
    solver.tui.define.models.unsteady_2nd_order("no")

    # Pressure-velocity coupling: Coupled (24)
    solver.tui.solve.set.p_v_coupling(24)

    # Spatial discretisation — Second Order Upwind via TUI
    try:
        solver.tui.solve.set.discretization_scheme("pressure", 12)
        solver.tui.solve.set.discretization_scheme("mom", 1)
        solver.tui.solve.set.discretization_scheme("k", 1)
        solver.tui.solve.set.discretization_scheme("omega", 1)
    except Exception as e1:
        try:
            solver.settings.solution.methods.discretization_scheme["pressure"] = "second-order"
            solver.settings.solution.methods.discretization_scheme["momentum"] = "second-order-upwind"
            solver.settings.solution.methods.discretization_scheme["k"] = "second-order-upwind"
            solver.settings.solution.methods.discretization_scheme["omega"] = "second-order-upwind"
        except Exception as e2:
            log_message(f"Warning: Could not set discretisation: {e1}, {e2}")

    log_message("Solver: Coupled, Second Order Upwind (all equations)")


def setup_sst_model(solver, log_file: str = None):
    """Configure k-omega SST via TUI."""

    solver.tui.define.models.viscous.kw_sst("yes")

    log_message("Turbulence model: k-omega SST", log_file)
    log_message("  Low-Re Corrections: OFF (Menter & Lechner 2021)", log_file)
    log_message("  Production Limiter: ON (default, clip factor = 10)", log_file)
    log_message("  Kato-Launder:       OFF", log_file)


def setup_solution_controls(solver, config: StaticSweepConfig, cfl: int):
    """Set CFL for Coupled solver."""
    try:
        solver.settings.solution.controls.pseudo_time_method.formulation.coupled_solver.flow_courant_number = cfl
    except Exception as e:
        log_message(f"Warning: Could not set CFL: {e}")


def disable_residual_convergence(solver, log_file: str = None):
    """
    Set residual convergence criteria to 1e-12 (effectively disabled).
    This prevents Fluent from terminating iterations early.
    The solver will ALWAYS run the full number of requested iterations.
    """
    try:
        residuals = solver.solution.monitor.residual
        residuals.convergence_criteria.continuity = 1e-12
        residuals.convergence_criteria.x_velocity = 1e-12
        residuals.convergence_criteria.y_velocity = 1e-12
        residuals.convergence_criteria.k = 1e-12
        residuals.convergence_criteria.omega = 1e-12
        log_message("Residual convergence criteria set to 1e-12 (effectively DISABLED)", log_file)
    except Exception:
        # Fallback: try via settings API
        try:
            solver.settings.solution.monitor.residual.convergence_criteria = {
                'continuity': 1e-12,
                'x-velocity': 1e-12,
                'y-velocity': 1e-12,
                'k': 1e-12,
                'omega': 1e-12,
            }
            log_message("Residual convergence criteria set to 1e-12 via settings API", log_file)
        except Exception:
            # Last resort: TUI
            try:
                solver.tui.solve.monitors.residual.convergence_criteria(
                    1e-12, 1e-12, 1e-12, 1e-12, 1e-12
                )
                log_message("Residual convergence criteria set to 1e-12 via TUI", log_file)
            except Exception as e:
                log_message(f"WARNING: Could not disable residual convergence: {e}", log_file)
                log_message("Fluent may still terminate iterations early!", log_file)


# =============================================================================
# ADAPTIVE CONVERGENCE RUNNER
# =============================================================================

def run_until_converged(solver, config, alpha_deg, log_file):
    """
    Run iterations in batches, checking C_L convergence after each batch.

    Strategy:
      1. Run batches of 200 iterations
      2. After each batch, read C_L and C_D
      3. Compare C_L to previous batch
      4. Stop when:
         - Minimum iterations reached AND C_L change < 0.1%, OR
         - Maximum iterations reached (unconverged but capped)
      5. First 2 batches always use conservative CFL = 50,
         remaining batches use CFL = 150

    Returns: (cl, cd, total_iters, converged_status, cl_history)
    """

    # Determine iteration limits based on alpha
    if abs(alpha_deg) >= 12.0:
        min_iters = config.min_iters_stall
        max_iters = config.max_iters_stall
    else:
        min_iters = config.min_iters_attached
        max_iters = config.max_iters_attached

    batch = config.batch_size
    total_iters = 0
    cl_history = []
    cd_history = []
    converged = False

    # Calculate number of batches
    max_batches = max_iters // batch
    min_batches = min_iters // batch

    log_message(f"  Convergence settings: min={min_iters}, max={max_iters}, "
                f"batch={batch}, tol={config.cl_convergence_tol*100:.1f}%", log_file)

    for b in range(max_batches):

        # CFL strategy: conservative for first 2 batches, then ramp
        if b < 2:
            setup_solution_controls(solver, config, config.cfl_initial)
        else:
            setup_solution_controls(solver, config, config.cfl_ramp)

        # Run one batch of iterations
        solver.settings.solution.run_calculation.iterate(iter_count=batch)
        total_iters += batch

        # Read force coefficients
        cl, cd = get_coefficients(solver)
        cl_history.append(cl)
        cd_history.append(cd)

        # Log progress every batch
        batch_num = b + 1
        log_message(f"    Batch {batch_num:>2d} ({total_iters:>5d} iters): "
                    f"C_L = {cl:.5f}, C_D = {cd:.6f}", log_file)

        # Check convergence (only after minimum iterations reached)
        if total_iters >= min_iters and len(cl_history) >= 2:
            cl_prev = cl_history[-2]
            cl_curr = cl_history[-1]

            # Relative change (use absolute for near-zero values)
            if abs(cl_prev) > 0.01:
                cl_change = abs((cl_curr - cl_prev) / cl_prev)
            else:
                cl_change = abs(cl_curr - cl_prev)

            # Also check C_D stability
            cd_prev = cd_history[-2]
            cd_curr = cd_history[-1]
            if abs(cd_prev) > 0.001:
                cd_change = abs((cd_curr - cd_prev) / cd_prev)
            else:
                cd_change = abs(cd_curr - cd_prev)

            log_message(f"             C_L change: {cl_change*100:.4f}%, "
                        f"C_D change: {cd_change*100:.4f}%", log_file)

            if cl_change < config.cl_convergence_tol and cd_change < config.cl_convergence_tol:
                converged = True
                log_message(f"    >>> CONVERGED at {total_iters} iterations "
                            f"(C_L change = {cl_change*100:.4f}% < "
                            f"{config.cl_convergence_tol*100:.1f}%)", log_file)
                break

    if not converged:
        log_message(f"    >>> NOT CONVERGED after {total_iters} iterations "
                    f"(hit maximum — expected for post-stall)", log_file)

    # Final coefficients
    cl_final, cd_final = get_coefficients(solver)

    # Determine convergence status string
    if converged:
        status = f"converged at {total_iters} iters"
    elif abs(alpha_deg) >= 16.0:
        status = f"oscillating after {total_iters} iters (expected post-stall)"
    else:
        status = f"not converged after {total_iters} iters"

    return cl_final, cd_final, total_iters, status, cl_history


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Main execution function."""

    # Configuration
    config = StaticSweepConfig()

    # Setup output directories
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_dir = f"{config.output_dir}_{timestamp}"
    cases_dir = os.path.join(base_dir, "case_data")
    logs_dir = os.path.join(base_dir, "logs")

    os.makedirs(cases_dir, exist_ok=True)
    os.makedirs(logs_dir, exist_ok=True)

    log_file = os.path.join(logs_dir, "static_sweep.log")
    csv_path = os.path.join(logs_dir, "sst_static_sweep_coefficients.csv")
    convergence_csv = os.path.join(logs_dir, "convergence_history.csv")

    log_message("=" * 70, log_file)
    log_message("NACA 0012 — STATIC ALPHA SWEEP WITH k-omega SST (v2)", log_file)
    log_message("Quasi-Static Bifurcation Hysteresis Study", log_file)
    log_message("CONVERGENCE FIX: residuals disabled, C_L-based stopping", log_file)
    log_message("=" * 70, log_file)
    log_message(f"Sweep: {config.alpha_start}deg -> {config.alpha_max}deg "
                f"(step = {config.alpha_step}deg)", log_file)
    if config.include_downstroke:
        log_message(f"Downstroke: {config.alpha_max}deg -> {config.alpha_start}deg "
                    f"(hysteresis detection)", log_file)
    log_message(f"Convergence: batches of {config.batch_size} iters, "
                f"C_L tolerance = {config.cl_convergence_tol*100:.1f}%", log_file)
    log_message(f"Iter limits: attached [{config.min_iters_attached}-"
                f"{config.max_iters_attached}], stall [{config.min_iters_stall}-"
                f"{config.max_iters_stall}]", log_file)
    log_message(f"Mesh: {config.mesh_file}", log_file)
    log_message(f"Output: {base_dir}", log_file)
    log_message("=" * 70, log_file)

    # =========================================================================
    # 1. LAUNCH FLUENT (matched from dynamic sweep)
    # =========================================================================
    log_message("Launching ANSYS Fluent...", log_file)
    solver = pyfluent.launch_fluent(
        precision=pyfluent.Precision.DOUBLE,
        processor_count=4,
        mode=pyfluent.FluentMode.SOLVER,
        dimension=pyfluent.Dimension.TWO,
        start_timeout=300,
    )

    try:
        # =====================================================================
        # 2. LOAD MESH
        # =====================================================================
        log_message(f"Loading mesh: {config.mesh_file}", log_file)
        solver.settings.file.read_case(file_name=config.mesh_file)

        # =====================================================================
        # 3. SETUP (all matched from dynamic sweep)
        # =====================================================================
        setup_reference_values(solver, config)
        setup_sst_model(solver, log_file)
        setup_solver_methods(solver, config)
        setup_solution_controls(solver, config, config.cfl_initial)
        setup_report_definitions(solver, config.alpha_start, config)

        # =====================================================================
        # 3b. DISABLE RESIDUAL CONVERGENCE (v2 FIX)
        # =====================================================================
        # This is the critical fix. Setting criteria to 1e-12 means Fluent
        # will NEVER terminate iterations early. We control stopping via
        # C_L convergence instead.
        disable_residual_convergence(solver, log_file)

        # =====================================================================
        # 4. BUILD ALPHA SWEEP SCHEDULE
        # =====================================================================
        upstroke_alphas = []
        alpha = config.alpha_start
        while alpha <= config.alpha_max + 1e-6:
            upstroke_alphas.append(alpha)
            alpha += config.alpha_step

        downstroke_alphas = []
        if config.include_downstroke:
            alpha = config.alpha_max - config.alpha_step
            while alpha >= config.alpha_start - 1e-6:
                downstroke_alphas.append(alpha)
                alpha -= config.alpha_step

        sweep_schedule = []
        for a in upstroke_alphas:
            sweep_schedule.append((a, "upstroke"))
        for a in downstroke_alphas:
            sweep_schedule.append((a, "downstroke"))

        log_message(f"Total alpha stations: {len(sweep_schedule)}", log_file)
        log_message(f"  Upstroke:   {len(upstroke_alphas)} points "
                    f"({config.alpha_start}deg -> {config.alpha_max}deg)", log_file)
        log_message(f"  Downstroke: {len(downstroke_alphas)} points "
                    f"({config.alpha_max - config.alpha_step}deg -> "
                    f"{config.alpha_start}deg)", log_file)

        # =====================================================================
        # 5. INITIALISATION AT ALPHA = 0
        # =====================================================================
        log_message("", log_file)
        log_message("INITIALISATION SEQUENCE", log_file)
        log_message("-" * 40, log_file)

        update_inlet_bc(solver, config.alpha_start, config)
        update_force_vectors(solver, config.alpha_start)

        # Hybrid initialisation
        log_message("Hybrid initialisation...", log_file)
        solver.settings.solution.initialization.hybrid_initialize()
        log_message("[OK] Hybrid initialisation complete", log_file)

        # Phase 1: 500 iterations First Order Upwind (build rough field)
        log_message("Phase 1: 500 iterations (First Order Upwind, CFL=30)...", log_file)
        try:
            solver.tui.solve.set.discretization_scheme("mom", 0)
            solver.tui.solve.set.discretization_scheme("k", 0)
            solver.tui.solve.set.discretization_scheme("omega", 0)
        except Exception:
            pass
        setup_solution_controls(solver, config, 30)
        solver.settings.solution.run_calculation.iterate(iter_count=500)

        # Phase 2: Switch to Second Order, run 1500 more
        log_message("Phase 2: 1500 iterations (Second Order Upwind, CFL=50)...", log_file)
        try:
            solver.tui.solve.set.discretization_scheme("mom", 1)
            solver.tui.solve.set.discretization_scheme("k", 1)
            solver.tui.solve.set.discretization_scheme("omega", 1)
        except Exception:
            pass
        setup_solution_controls(solver, config, config.cfl_initial)
        solver.settings.solution.run_calculation.iterate(iter_count=1500)

        # Check initial solution
        cl_init, cd_init = get_coefficients(solver)
        log_message(f"[OK] Initialisation complete at alpha = 0deg", log_file)
        log_message(f"     C_L = {cl_init:.5f} (expected ~0 for symmetric airfoil)", log_file)
        log_message(f"     C_D = {cd_init:.5f}", log_file)

        # =====================================================================
        # 6. RUN THE ALPHA SWEEP
        # =====================================================================
        log_message("", log_file)
        log_message("=" * 70, log_file)
        log_message("BEGINNING ALPHA SWEEP (with adaptive convergence checking)", log_file)
        log_message("=" * 70, log_file)

        results = []
        all_convergence_data = []
        start_time = time.time()

        for idx, (alpha_deg, branch) in enumerate(sweep_schedule):

            log_message("", log_file)
            log_message(f"{'='*60}", log_file)
            log_message(f"  [{idx+1}/{len(sweep_schedule)}] alpha = {alpha_deg:.1f}deg "
                        f"({branch})", log_file)
            log_message(f"{'='*60}", log_file)

            # --- Update boundary conditions ---
            update_inlet_bc(solver, alpha_deg, config)
            update_force_vectors(solver, alpha_deg)

            # --- Run with adaptive convergence ---
            cl, cd, total_iters, status, cl_history = run_until_converged(
                solver, config, alpha_deg, log_file
            )

            # --- Store convergence history ---
            for batch_idx, cl_val in enumerate(cl_history):
                all_convergence_data.append({
                    "alpha_deg": alpha_deg,
                    "branch": branch,
                    "batch": batch_idx + 1,
                    "iterations": (batch_idx + 1) * config.batch_size,
                    "C_L": cl_val,
                })

            # --- Classify flow regime ---
            if alpha_deg < 10.0:
                note = "Attached flow — linear lift regime"
            elif alpha_deg < 16.0:
                note = "Approaching stall — nonlinear lift"
            else:
                note = "Post-stall — quasi-static bifurcation regime"

            if branch == "downstroke" and 10.0 <= alpha_deg <= 20.0:
                note += " | HYSTERESIS DETECTION ZONE"

            # --- Store result ---
            result = {
                "alpha_deg": alpha_deg,
                "branch": branch,
                "C_L": cl,
                "C_D": cd,
                "converged": status,
                "iterations": total_iters,
                "notes": note,
            }
            results.append(result)

            log_message(f"  FINAL: C_L = {cl:.5f}, C_D = {cd:.6f} | {status}", log_file)

            # --- Save case/data at key angles + all downstroke ---
            save_angles = [0, 10, 12, 14, 16, 18, 20, 22]
            if alpha_deg in save_angles or branch == "downstroke":
                case_file = os.path.join(
                    cases_dir,
                    f"naca0012_sst_alpha{alpha_deg:.0f}_{branch}.cas.h5"
                )
                data_file = os.path.join(
                    cases_dir,
                    f"naca0012_sst_alpha{alpha_deg:.0f}_{branch}.dat.h5"
                )
                solver.settings.file.write_case(file_name=case_file)
                solver.settings.file.write_data(file_name=data_file)
                log_message(f"  Saved: {case_file}", log_file)

            # --- Progress update ---
            elapsed = time.time() - start_time
            if idx > 0:
                rate = elapsed / (idx + 1)
                remaining = rate * (len(sweep_schedule) - idx - 1)
                log_message(f"  ETA: {remaining/60:.1f} min remaining", log_file)

        # =====================================================================
        # 7. WRITE RESULTS TO CSV
        # =====================================================================
        log_message("", log_file)
        log_message(f"Writing results to: {csv_path}", log_file)

        csv_header = ["alpha_deg", "branch", "C_L", "C_D", "converged",
                      "iterations", "notes"]

        with open(csv_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=csv_header)
            writer.writeheader()
            writer.writerows(results)

        log_message(f"[OK] CSV saved: {csv_path}", log_file)

        # Write convergence history (for debugging)
        log_message(f"Writing convergence history to: {convergence_csv}", log_file)
        conv_header = ["alpha_deg", "branch", "batch", "iterations", "C_L"]
        with open(convergence_csv, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=conv_header)
            writer.writeheader()
            writer.writerows(all_convergence_data)
        log_message(f"[OK] Convergence history saved: {convergence_csv}", log_file)

        # =====================================================================
        # 8. SUMMARY TABLE
        # =====================================================================
        log_message("", log_file)
        log_message("=" * 70, log_file)
        log_message("RESULTS SUMMARY — SST Static Alpha Sweep (v2)", log_file)
        log_message("=" * 70, log_file)
        log_message(f"{'Alpha':>7s} {'Branch':>11s} {'C_L':>9s} {'C_D':>9s} "
                    f"{'Iters':>6s} {'Status'}", log_file)
        log_message("-" * 70, log_file)

        for r in results:
            log_message(
                f"{r['alpha_deg']:7.1f} {r['branch']:>11s} "
                f"{r['C_L']:9.5f} {r['C_D']:9.6f} "
                f"{r['iterations']:6d} {r['converged']}",
                log_file
            )

        # =====================================================================
        # 9. SANITY CHECKS
        # =====================================================================
        log_message("", log_file)
        log_message("=" * 70, log_file)
        log_message("SANITY CHECKS", log_file)
        log_message("=" * 70, log_file)

        # Check 1: Lift curve slope in linear region (0-8 deg)
        linear_results = [(r["alpha_deg"], r["C_L"]) for r in results
                          if r["branch"] == "upstroke" and 2.0 <= r["alpha_deg"] <= 8.0]
        if len(linear_results) >= 2:
            alphas = [x[0] for x in linear_results]
            cls = [x[1] for x in linear_results]
            # Simple linear fit
            n = len(alphas)
            sum_a = sum(alphas)
            sum_cl = sum(cls)
            sum_a2 = sum(a**2 for a in alphas)
            sum_acl = sum(a*c for a, c in zip(alphas, cls))
            slope = (n * sum_acl - sum_a * sum_cl) / (n * sum_a2 - sum_a**2)

            log_message(f"  Lift slope (2-8 deg): dC_L/dalpha = {slope:.4f}/deg", log_file)
            log_message(f"  Expected (thin airfoil theory): ~0.110/deg", log_file)
            if 0.08 < slope < 0.13:
                log_message(f"  [OK] Within acceptable range", log_file)
            else:
                log_message(f"  [WARNING] Outside expected range — check convergence", log_file)

        # Check 2: Symmetry at alpha = 0
        alpha0_up = [r for r in results if r["alpha_deg"] == 0.0 and r["branch"] == "upstroke"]
        alpha0_down = [r for r in results if r["alpha_deg"] == 0.0 and r["branch"] == "downstroke"]
        if alpha0_up and alpha0_down:
            cl_diff = abs(alpha0_up[0]["C_L"] - alpha0_down[0]["C_L"])
            log_message(f"  C_L at alpha=0: upstroke={alpha0_up[0]['C_L']:.5f}, "
                        f"downstroke={alpha0_down[0]['C_L']:.5f}, "
                        f"difference={cl_diff:.5f}", log_file)
            if cl_diff < 0.01:
                log_message(f"  [OK] Near-zero lift at alpha=0 on both branches", log_file)
            else:
                log_message(f"  [WARNING] Hysteresis at alpha=0 is unphysical — "
                            f"indicates unconverged solution", log_file)

        # Check 3: No negative drag
        neg_drag = [r for r in results if r["C_D"] < 0]
        if neg_drag:
            log_message(f"  [WARNING] Negative drag at {len(neg_drag)} stations:", log_file)
            for r in neg_drag:
                log_message(f"    alpha={r['alpha_deg']:.1f} ({r['branch']}): "
                            f"C_D={r['C_D']:.6f}", log_file)
        else:
            log_message(f"  [OK] No negative drag values detected", log_file)

        # Check 4: Monotonic lift in linear region
        upstroke_linear = [(r["alpha_deg"], r["C_L"]) for r in results
                           if r["branch"] == "upstroke" and r["alpha_deg"] <= 10.0]
        upstroke_linear.sort()
        non_monotonic = False
        for i in range(1, len(upstroke_linear)):
            if upstroke_linear[i][1] < upstroke_linear[i-1][1]:
                non_monotonic = True
                log_message(f"  [WARNING] Non-monotonic lift: "
                            f"alpha={upstroke_linear[i][0]:.1f} "
                            f"(C_L={upstroke_linear[i][1]:.5f}) < "
                            f"alpha={upstroke_linear[i-1][0]:.1f} "
                            f"(C_L={upstroke_linear[i-1][1]:.5f})", log_file)
        if not non_monotonic:
            log_message(f"  [OK] Lift is monotonically increasing 0-10 deg", log_file)

        # =====================================================================
        # 10. BIFURCATION HYSTERESIS ANALYSIS
        # =====================================================================
        if config.include_downstroke:
            log_message("", log_file)
            log_message("=" * 70, log_file)
            log_message("BIFURCATION HYSTERESIS ANALYSIS", log_file)
            log_message("(NOT dynamic stall — k ≈ 0.0002 << 0.004 threshold)", log_file)
            log_message("=" * 70, log_file)

            upstroke_data = {r["alpha_deg"]: r for r in results
                            if r["branch"] == "upstroke"}
            downstroke_data = {r["alpha_deg"]: r for r in results
                              if r["branch"] == "downstroke"}

            common_alphas = sorted(
                set(upstroke_data.keys()) & set(downstroke_data.keys())
            )

            log_message(f"{'Alpha':>7s} {'CL_up':>9s} {'CL_down':>9s} "
                        f"{'Delta_CL':>10s} {'Hysteresis?':>12s}", log_file)
            log_message("-" * 55, log_file)

            hysteresis_detected = False
            hysteresis_range = []

            for alpha in common_alphas:
                cl_up = upstroke_data[alpha]["C_L"]
                cl_down = downstroke_data[alpha]["C_L"]
                delta = cl_down - cl_up
                is_hyst = abs(delta) > 0.05

                if is_hyst:
                    hysteresis_detected = True
                    hysteresis_range.append(alpha)

                flag = "  <<< YES" if is_hyst else ""
                log_message(
                    f"{alpha:7.1f} {cl_up:9.5f} {cl_down:9.5f} "
                    f"{delta:10.5f} {flag}",
                    log_file
                )

            log_message("", log_file)
            if hysteresis_detected:
                log_message("RESULT: Static bifurcation hysteresis DETECTED.", log_file)
                log_message(f"  Hysteresis range: alpha = "
                            f"{min(hysteresis_range):.0f}deg to "
                            f"{max(hysteresis_range):.0f}deg", log_file)
                log_message("", log_file)

                # Check if hysteresis is only in the stall region (physical)
                # or also at low alpha (numerical artefact)
                low_alpha_hyst = [a for a in hysteresis_range if a < 8.0]
                if low_alpha_hyst:
                    log_message("  [WARNING] Hysteresis detected at low alpha "
                                f"({min(low_alpha_hyst):.0f}-{max(low_alpha_hyst):.0f}deg)", log_file)
                    log_message("  This is likely a NUMERICAL ARTEFACT, not physical.", log_file)
                    log_message("  Fully attached flow has no mechanism for path-dependence.", log_file)
                    log_message("  Consider increasing iteration count or tightening tolerance.", log_file)
                else:
                    log_message("  [OK] Hysteresis confined to stall region — physically plausible.", log_file)
                    log_message("  Path-dependent switching between attached/separated attractors.", log_file)
                    log_message("  (Sereez et al. 2021, J. Aircraft; 2024, Aerospace)", log_file)
            else:
                log_message("RESULT: No significant hysteresis detected.", log_file)

        # =====================================================================
        # 11. REDUCED FREQUENCY VERIFICATION
        # =====================================================================
        log_message("", log_file)
        log_message("=" * 70, log_file)
        log_message("REDUCED FREQUENCY VERIFICATION", log_file)
        log_message("=" * 70, log_file)

        alpha_dot = 2.0
        alpha_dot_rad = alpha_dot * math.pi / 180.0
        k_reduced = (alpha_dot_rad * config.chord) / (2.0 * config.U_inf)

        log_message(f"  Pitch rate:  {alpha_dot} deg/s = {alpha_dot_rad:.4f} rad/s",
                    log_file)
        log_message(f"  k = (alpha_dot * c) / (2 * V_inf) = {k_reduced:.6f}", log_file)
        log_message(f"  Thresholds (McAlister et al., NASA TM-78446):", log_file)
        log_message(f"    k < 0.004       Quasi-steady   <-- YOU ARE HERE", log_file)
        log_message(f"    k = 0.004-0.05  Mildly unsteady", log_file)
        log_message(f"    k = 0.05-0.25   Dynamic stall regime", log_file)
        log_message(f"  Your pitch rate is {0.004/k_reduced:.0f}x BELOW the "
                    f"quasi-steady threshold.", log_file)

        # =====================================================================
        # FINAL SUMMARY
        # =====================================================================
        total_elapsed = time.time() - start_time
        log_message("", log_file)
        log_message("=" * 70, log_file)
        log_message("SIMULATION COMPLETE", log_file)
        log_message("=" * 70, log_file)
        log_message(f"Total alpha stations: {len(results)}", log_file)
        log_message(f"Total wall time: {total_elapsed/3600:.2f} hours", log_file)
        log_message(f"Results CSV:        {csv_path}", log_file)
        log_message(f"Convergence CSV:    {convergence_csv}", log_file)
        log_message(f"Case files:         {cases_dir}", log_file)
        log_message("", log_file)
        log_message("CORRECT TERMINOLOGY FOR REPORT:", log_file)
        log_message("  USE:    'quasi-static hysteresis', 'bifurcation hysteresis',", log_file)
        log_message("          'static stall hysteresis', 'path-dependent stall'", log_file)
        log_message("  AVOID:  'dynamic stall', 'dynamic stall delay',", log_file)
        log_message("          'dynamic hysteresis' (at this pitch rate)", log_file)

    except Exception as e:
        log_message(f"ERROR: {str(e)}", log_file)
        raise

    finally:
        log_message("Closing Fluent session...", log_file)
        solver.exit()


if __name__ == "__main__":
    main()
