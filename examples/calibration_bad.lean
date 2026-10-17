import Mathlib
import Pit.Calibration

-- A planted bad proof: it passes the screen, but `Nat.zero_add n : 0 + n = n` is a different statement,
-- and Lean refuses to accept it as a proof of `n + 0 = n`.
theorem solution : Pit.Calibration.Statement := fun n => Nat.zero_add n
