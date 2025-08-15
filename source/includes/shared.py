from mdk.compiler import statefunc
from mdk.stdlib import Name, IsHelper, root, ChangeState
from mdk.types import Expression

from source.brain import TargetLandingState

from .variables import TrackedTime # type: ignore

@statefunc
def SendToDevilsEye():
    """
    Checks if an enemy landed in this state, and redirects to TargetLandingState.
    This needs to be applied at the start of every player state!
    """
    if Name != "M-Creirwy" or (IsHelper() and root.Name != "M-Creirwy"): 
        TargetLandingState(ignorehitpause = True, persistent = 256)

@statefunc
def ChangeState_TimeReset(target_state: Expression):
    """
    Performs a ChangeState, while also resetting the value of TrackedTime to 0.
    """
    if (TrackedTime := 0) or True: # type: ignore
        ChangeState(value = target_state, ignorehitpause = True, persistent = 256)