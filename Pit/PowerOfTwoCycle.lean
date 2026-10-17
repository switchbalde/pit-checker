import Mathlib

namespace Pit.PowerOfTwoCycle

/-- Erdős problem #64 (Erdős–Gyárfás). Taken from google-deepmind/formal-conjectures `erdos_64`; `Type*` became `Type` so `Statement` carries no universe parameter (every finite graph is isomorphic to one on a `Type`). Source: https://www.erdosproblems.com/64 -/
def Statement : Prop :=
  ∀ (V : Type) (G : SimpleGraph V) [Fintype V] [DecidableRel G.Adj],
    G.minDegree ≥ 3 → ∃ (k : ℕ) (v : V) (c : G.Walk v v),
      k ≥ 2 ∧ c.IsCycle ∧ c.length = 2 ^ k

end Pit.PowerOfTwoCycle
