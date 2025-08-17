from mdk.compiler import statefunc, trigger
from mdk.stdlib import Name, IsHelper, root, ChangeState, SelfState, Random, Cond, Null
from mdk.types import Expression, IntType, BoolType

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
    """Use the Random trigger to select a random (integer) value from within the provided range."""
    return min + (Random % (max - min))

@trigger(inputs = [IntType, IntType], result = IntType, library = "States/Creirwy-SharedFunc.inc")
def RandPick(val1: Expression, val2: Expression) -> Expression:
    """Use the Random trigger to select a random value from the two provided values."""
    return Cond(Random % 2 == 1, val1, val2)

@statefunc
def RootFlagSet(var_name: Expression, value: Expression):
    """Use Cond-bug with a Null controller to set a value on the root. 
    This will not work as expected if executed from a non-Helper context."""
    if RootFlagSet_Cond(var_name, value):
        Null()

@trigger(inputs = [BoolType, BoolType], result = BoolType, library = "States/Creirwy-SharedFunc.inc")
def RootFlagSet_Cond(var_name: Expression, value: Expression) -> Expression:
    """Use Cond-bug to set a bool value on the root. This will not work as expected if executed from a non-Helper context."""
    return Expression(f"root,Cond({var_name.exprn} := {value.exprn}, true, true)", BoolType)