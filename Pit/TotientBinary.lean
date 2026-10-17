import Mathlib

namespace Pit.TotientBinary

/-- Erdős problem #249. Taken from google-deepmind/formal-conjectures `erdos_249`, with the φ notation spelled out as `Nat.totient` and the cast to ℝ made explicit. Source: https://www.erdosproblems.com/249 -/
def Statement : Prop :=
  Irrational (∑' n : ℕ, (Nat.totient n : ℝ) / 2 ^ n)

end Pit.TotientBinary
