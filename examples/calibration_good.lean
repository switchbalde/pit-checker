import Mathlib
import Pit.Calibration

-- A real proof: `n + 0` reduces to `n` by the definition of addition on ℕ.
theorem solution : Pit.Calibration.Statement := fun n => rfl
