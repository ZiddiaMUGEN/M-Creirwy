from mdk.compiler import statefunc, trigger
from mdk.stdlib import Name, IsHelper, root, ChangeState, SelfState, Random, Cond
from mdk.types import Expression, IntType

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

@statefunc
def SelfState_TimeReset(target_state: Expression):
    """
    Performs a SelfState, while also resetting the value of TrackedTime to 0.
    """
    if (TrackedTime := 0) or True: # type: ignore
        SelfState(value = target_state, ignorehitpause = True, persistent = 256)

@statefunc
def SelfState_TimeIncrease(target_state: Expression):
    """
    Performs a SelfState, while also increasing the value of TrackedTime by 1.
    """
    if (TrackedTime := TrackedTime + 1) or True: # type: ignore
        SelfState(value = target_state, ignorehitpause = True, persistent = 256)

@trigger(inputs = [IntType, IntType], result = IntType, library = "States/Creirwy-SharedFunc.inc")
def RandRange(min: Expression, max: Expression) -> Expression:
    return min + (Random % (max - min))

@trigger(inputs = [IntType, IntType], result = IntType, library = "States/Creirwy-SharedFunc.inc")
def RandPick(val1: Expression, val2: Expression) -> Expression:
    return Cond(Random % 2 == 1, val1, val2)