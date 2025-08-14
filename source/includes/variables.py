from mdk.types import IntVar

TrackedTime = IntVar()
"""
Tracks the amount of time which has been spent in the current state.

This is used over the `Time` trigger due to the amount of `SelfState` usage in the character.
"""