import Mathlib
import Pit.BarGauss

-- The house's own proof that the warm-up is provable: induction on n.
theorem solution : Pit.BarGauss.Statement := by
  intro n
  induction n with
  | zero => simp
  | succ k ih =>
    rw [Finset.sum_range_succ, mul_add 2, ih]
    show k * (k + 1) + 2 * (k + 1) = (k + 1) * (k + 1 + 1)
    ring
