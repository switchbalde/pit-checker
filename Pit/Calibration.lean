import Mathlib

namespace Pit.Calibration

/-- The calibration round: adding zero to a natural number changes nothing. Not an open problem; it exists so anyone can watch the checker go GREEN on a real proof and RED on a bad one. -/
def Statement : Prop := ∀ n : ℕ, n + 0 = n

end Pit.Calibration
