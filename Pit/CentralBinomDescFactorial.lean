import Mathlib

namespace Pit.CentralBinomDescFactorial

/-- Erdős problem #396. Taken from google-deepmind/formal-conjectures `erdos_396`. Source: https://www.erdosproblems.com/396 -/
def Statement : Prop :=
  ∀ k : ℕ, ∃ n : ℕ, Nat.descFactorial n (k + 1) ∣ Nat.centralBinom n

end Pit.CentralBinomDescFactorial
