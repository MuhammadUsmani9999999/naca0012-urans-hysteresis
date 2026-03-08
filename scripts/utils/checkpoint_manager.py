"""
checkpoint_manager.py
======================
JSON-based checkpointing system for automatic recovery from solver
interruptions during long-running angle-of-attack sweeps.

Saves the state (completed angles, coefficients) to a JSON file after each
angle completes, enabling the sweep to resume from the last successful point.
"""

import json
from pathlib import Path
from typing import Optional


class CheckpointManager:
    """
    Manages simulation checkpoints via a JSON file.

    Parameters
    ----------
    filepath : Path or str
        Path to the checkpoint JSON file.
    """

    def __init__(self, filepath):
        self.filepath = Path(filepath)
        self._state = self._load()

    def _load(self) -> dict:
        """Load existing checkpoint or create empty state."""
        if self.filepath.exists():
            with open(self.filepath, "r") as f:
                state = json.load(f)
            print(f"  Checkpoint loaded: {len(state.get('completed', []))} "
                  f"angles previously completed.")
            return state
        return {"completed": [], "results": {}}

    def _write(self):
        """Persist current state to disc."""
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(self.filepath, "w") as f:
            json.dump(self._state, f, indent=2)

    def is_completed(self, alpha: int, direction: str) -> bool:
        """
        Check if a given angle and direction have already been simulated.

        Parameters
        ----------
        alpha : int
            Angle of attack in degrees.
        direction : str
            'Pitch-Up' or 'Pitch-Down'.

        Returns
        -------
        bool
        """
        key = f"{alpha}_{direction}"
        return key in self._state.get("completed", [])

    def save(self, alpha: int, direction: str, cl: float, cd: float):
        """
        Record a completed simulation point.

        Parameters
        ----------
        alpha : int
            Angle of attack in degrees.
        direction : str
            'Pitch-Up' or 'Pitch-Down'.
        cl : float
            Lift coefficient.
        cd : float
            Drag coefficient.
        """
        key = f"{alpha}_{direction}"
        if key not in self._state["completed"]:
            self._state["completed"].append(key)
        self._state["results"][key] = {"C_L": cl, "C_D": cd}
        self._write()

    def get_result(self, alpha: int, direction: str) -> Optional[dict]:
        """
        Retrieve stored result for a given angle and direction.

        Returns
        -------
        dict or None
            {'C_L': float, 'C_D': float} if available, else None.
        """
        key = f"{alpha}_{direction}"
        return self._state["results"].get(key)

    def clear(self):
        """Delete the checkpoint file and reset state."""
        if self.filepath.exists():
            self.filepath.unlink()
        self._state = {"completed": [], "results": {}}
        print("  Checkpoint cleared.")
