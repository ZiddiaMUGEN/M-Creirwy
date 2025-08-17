from mdk.types import IntVar, StateNoType, VariableExpression, BoolVar, SCOPE_PLAYER, SCOPE_HELPER, ByteVar

from .constants import IMAGEREPRO_HELPER_ID
from .types import ImageReproActionType

######################################################
## Global unscoped - used by root + helpers
######################################################

TrackedTime = IntVar()
"""
Tracks the amount of time which has been spent in the current state.

This is used over the `Time` trigger due to the amount of `SelfState` usage in the character.
"""

SavedState = VariableExpression(StateNoType)
"""
Used as part of pseudo-statechange. Tracks which state the actor is supposed to enter from negative states.
"""

######################################################
## Global player-scoped - used by root
######################################################

Root_CrosstalkInitialized = BoolVar(scope = SCOPE_PLAYER)
"""
Used by the root, but set by CT. Set to True when the crosstalk helpers have all been spawned (roughly frame 1).
"""

######################################################
## Global helper-scoped - used by ImageRepro
######################################################

ImageRepro_HasRunIntro = BoolVar(scope = SCOPE_HELPER(IMAGEREPRO_HELPER_ID))
"""
Flag indicating whether ImageRepro has gone through its into animation + returned to idle already.
"""

ImageRepro_SelectedMove = VariableExpression(ImageReproActionType, scope = SCOPE_HELPER(IMAGEREPRO_HELPER_ID))
"""
Indicates which phase of move display the ImageRepro helper is in (e.g. dashing, attacking, etc).
"""