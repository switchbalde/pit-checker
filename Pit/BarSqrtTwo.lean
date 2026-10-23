import Mathlib

namespace Pit.BarSqrtTwo

/-- A warm-up for the Bar: the square root of 2 is irrational. Not an open problem; an evening's proof. -/
def Statement : Prop := Irrational (Real.sqrt 2)

end Pit.BarSqrtTwo
