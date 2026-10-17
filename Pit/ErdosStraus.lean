import Mathlib

namespace Pit.ErdosStraus

/-- Erdős problem #242 (Erdős–Straus). Taken from google-deepmind/formal-conjectures `erdos_242`, with the hypotheses moved under the quantifier. Source: https://www.erdosproblems.com/242 -/
def Statement : Prop :=
  ∀ n : ℕ, 2 < n → ∃ x y z : ℕ, 1 ≤ x ∧ x < y ∧ y < z ∧
    (4 / n : ℚ) = 1 / x + 1 / y + 1 / z

end Pit.ErdosStraus
