import Mathlib

namespace Pit.BarPrimes

/-- A warm-up for the Bar: there is no largest prime (above every n sits a prime). Not an open problem; an evening's proof. -/
def Statement : Prop := ∀ n : ℕ, ∃ p, n ≤ p ∧ Nat.Prime p

end Pit.BarPrimes
