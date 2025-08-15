from mdk.types import IntVar, StateNoType, VariableExpression

TrackedTime = IntVar()
"""
Tracks the amount of time which has been spent in the current state.

This is used over the `Time` trigger due to the amount of `SelfState` usage in the character.
"""

SavedState = VariableExpression(StateNoType)
"""
Used as part of pseudo-statechange. Tracks which state the actor is supposed to enter from negative states.
"""