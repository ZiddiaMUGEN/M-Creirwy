from mdk.types import IntVar, StateNoType, VariableExpression, BoolVar, SCOPE_PLAYER, SCOPE_HELPER, IntType

from source.includes.constants import IMAGEREPRO_HELPER_ID, CROSSTALK_TARGET_ID, SPY_HELPER_ID, STORAGE_HELPER_ID, EXPLORER_BUFFER_ID
from source.includes.types import ImageReproActionTypeT, AnimationSearchStateTypeT

######################################################
## Global unscoped - used by root + helpers
######################################################

TrackedTime = IntVar()
"""
Tracks the amount of time which has been spent in the current state.

This is used over the `Time` trigger due to the amount of `SelfState` usage in the character.
"""

TrackedGameTime = IntVar()
"""
Tracks the value of GameTime. This gets set in -3 (which is not executed during custom states). Therefore it can be used to detect when
an actor enters a custom state.
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

Root_SpyIsSpawned = BoolVar(scope = SCOPE_PLAYER)
"""
Used by the root, set by enemy root or Helper after TargetState. Indicates if the Spy helper has already been spawned.
"""

######################################################
## Global helper-scoped - used by ImageRepro
######################################################

ImageRepro_HasRunIntro = BoolVar(scope = SCOPE_HELPER(IMAGEREPRO_HELPER_ID))
"""
Flag indicating whether ImageRepro has gone through its into animation + returned to idle already.
"""

ImageRepro_MotionState = VariableExpression(ImageReproActionTypeT, scope = SCOPE_HELPER(IMAGEREPRO_HELPER_ID))
"""
Indicates which phase of move display the ImageRepro helper is in (e.g. dashing, attacking, etc).

Each phase of move display receives one entry in the ImageReproActionType user-defined enum.
"""

ImageRepro_LastSelection = VariableExpression(IntType, scope = SCOPE_HELPER(IMAGEREPRO_HELPER_ID))
"""
Tracks the last move selected by the ImageRepro helper. If a new move selection matches the most recent move selection,
ImageRepro will pick a different move.
"""

######################################################
## Global helper-scoped - used by Crosstalk targets
######################################################

CrossTalkTarget_TargetObtained = BoolVar(scope = SCOPE_HELPER(CROSSTALK_TARGET_ID))
"""
Flag indicating whether the owner of this CT target has successfully obtained its target.
"""

######################################################
## Global helper-scoped - used by the Spy helper
######################################################
Spy_AnimTestNumber = IntVar(scope = SCOPE_HELPER(SPY_HELPER_ID))
"""
Tracks the last animation index which the Spy helper has tested.
"""

Spy_LastAnimChecked = IntVar(scope = SCOPE_HELPER(SPY_HELPER_ID))
"""
Tracks the last animation ID which the Spy helper has tested.
"""

############################################################################################
## Global helper-scoped - used by the Exploration controller.
## these MUST be sysvars, as Exploration controller can be hit by ParentVarSet.
############################################################################################
Exploration_CurrentState = IntVar(scope = SCOPE_HELPER(EXPLORER_BUFFER_ID), system = True)
"""
Tracks the last state which was entered and tested by the Exploration helper.
"""

############################################################################################
## Global helper-scoped - used by various characters, but stored in the Storage helper
############################################################################################
SpyStorage_AnimationSearchState = VariableExpression(AnimationSearchStateTypeT, scope = SCOPE_HELPER(STORAGE_HELPER_ID))
"""
Indicates the progress the Spy helper has made towards finding Clsn1/2 animations.
"""

SpyStorage_SavedClsn1 = IntVar(scope = SCOPE_HELPER(STORAGE_HELPER_ID))
"""
Saves the animation number of a Clsn1-containing animation for the enemy.
"""

SpyStorage_SavedClsn2 = IntVar(scope = SCOPE_HELPER(STORAGE_HELPER_ID))
"""
Saves the animation number of a Clsn2-containing animation for the enemy.
"""