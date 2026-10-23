import Mathlib

namespace Pit.BarGauss

/-- A warm-up for the Bar: twice 0 + 1 + ... + n is n(n + 1). Not an open problem; an evening's proof. -/
def Statement : Prop := ∀ n : ℕ, 2 * (Finset.range (n + 1)).sum id = n * (n + 1)

end Pit.BarGauss
