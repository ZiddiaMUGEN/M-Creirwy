from mdk.compiler import statefunc, trigger
from mdk.stdlib import Name, IsHelper, root, ChangeState, SelfState, Random, Cond, Null, rescope, target, enemy, enemyID, helperID, NumHelper
from mdk.types import Expression, ConvertibleExpression, VariableExpression, IntType, BoolType, StateScope, SCOPE_PLAYER

from mdk.utils.shared import convert

from source.includes.variables import TrackedTime, SavedState # type: ignore
from source.includes.constants import MC_DEVILS_TARGET_STATE, STORAGE_HELPER_ID

@statefunc()
def SendToDevilsEye():
    """
    Checks if an enemy landed in this state, and redirects to TargetLandingState.
    This needs to be applied at the start of every player state!
    """
    if Name != "M-Creirwy" or (IsHelper() and root.Name != "M-Creirwy"): 
        ChangeState(value = MC_DEVILS_TARGET_STATE, ignorehitpause = True, persistent = 256)

@statefunc()
def ChangeState_TimeReset(target_state: Expression):
    """
    Performs a ChangeState, while also resetting the value of TrackedTime to 0.
    """
    if (TrackedTime := 0) or True: # type: ignore
        ChangeState(value = target_state, ignorehitpause = True, persistent = 256)

@statefunc()
def SelfState_TimeReset(target_state: Expression):
    """
    Performs a SelfState, while also resetting the value of TrackedTime to 0.
    """
    if (TrackedTime := 0) or True: # type: ignore
        SelfState(value = target_state, ignorehitpause = True, persistent = 256)

@statefunc()
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

@statefunc()
def RootVarSet(variable: VariableExpression, value: ConvertibleExpression):
    """
    Use Cond-bug with a Null controller to set a value on the root. 
    This will not work as expected if executed from a non-Helper context.
    """
    if not isinstance(value, Expression): value = convert(value)

    _assign = Expression(f"{variable.exprn} := {value.exprn}", variable.type)
    if root.Cond(_assign, True, True): # type: ignore
        Null()

@statefunc()
def TargetVarSet(variable: VariableExpression, value: ConvertibleExpression, scope: StateScope):
    """
    Use Cond-bug with a Null controller to set a value on a target.
    You must provide a concrete scope for the target as well.
    This will not work as expected if the current context has no target.
    """
    if not isinstance(value, Expression): value = convert(value)

    _assign = Expression(f"{variable.exprn} := {value.exprn}", variable.type)
    if rescope(target, scope).Cond(_assign, True, True): # type: ignore
        Null()

@statefunc()
def CreirwyVarSet(variable: VariableExpression, value: ConvertibleExpression):
    """
    Use Cond-bug with a Null controller to set a value on Creirwy's root.
    This is expected to be run from the enemy's context so that captured enemies can set Creirwy's progress flags.
    """
    if not isinstance(value, Expression): value = convert(value)

    ## because this is executed from a TARGET scope, no `rescope` operator is required.
    ## `enemy(xyz)` on TARGET scope is resolved to PLAYER scope.
    _assign = Expression(f"{variable.exprn} := {value.exprn}", variable.type)
    if enemyID(enemy.Name != "M-Creirwy").Cond(_assign, True, True): # type: ignore
        Null()

@trigger(inputs = [IntType, IntType, IntType], result = BoolType, library = "States/Creirwy-SharedFunc.inc")
def InRange(test_value: Expression, min: Expression, max: Expression) -> Expression:
    """
    Tests if a variable or expression falls inside a range. 
    
    The range is tested inclusive on the lower end and exclusive on the upper end.
    """
    return test_value >= min and test_value < max

@statefunc()
def SendToSafeStates():
    """
    Execute this from states where we send enemies.

    If the executor belongs to Creirwy's team, selfstate back to their original state.
    """
    if Name == "M-Creirwy":
        SelfState(value = SavedState)
    if IsHelper() and root.Name == "M-Creirwy":
        SelfState(value = SavedState)

def ReadStorageVar_Enemy(variable: VariableExpression) -> Expression:
    """
    Use this as a Trigger. Returns a Condbug statement to read the value of a variable in the Storage helper.
    """
    _e = Expression("1", variable.type)
    return rescope(enemyID(enemy.Name != "M-Creirwy"), SCOPE_PLAYER).Cond(NumHelper(STORAGE_HELPER_ID) != 0, getattr(helperID(STORAGE_HELPER_ID), variable.exprn), _e)

@statefunc()
def SetStorageVar_Enemy(variable: VariableExpression, value: ConvertibleExpression):
    """
    Use Cond-bug with a Null controller to set a value on Creirwy's Storage helper.
    This is expected to be run from the enemy's context so that captured enemies can set Creirwy's progress flags.
    """
    if not isinstance(value, Expression): value = convert(value)

    ## because this is executed from a TARGET scope, no `rescope` operator is required.
    ## `enemy(xyz)` on TARGET scope is resolved to PLAYER scope.
    _e = Expression("1", value.type)
    _assign = Expression(f"{variable.exprn} := {value.exprn}", variable.type)
    if rescope(enemyID(enemy.Name != "M-Creirwy"), SCOPE_PLAYER).Cond(NumHelper(STORAGE_HELPER_ID) != 0, helperID(STORAGE_HELPER_ID).Cond(True, _assign, _e), _e): # type: ignore
        Null()

@statefunc()
def SetStorageVar_Self(variable: VariableExpression, value: ConvertibleExpression):
    """
    Use Cond-bug with a Null controller to set a value on Creirwy's Storage helper.
    This is expected to be run from Creirwy's team's context so that helpers can set progress flags.
    """
    if not isinstance(value, Expression): value = convert(value)

    _e = Expression("1", value.type)
    _assign = Expression(f"{variable.exprn} := {value.exprn}", variable.type)
    if helperID(STORAGE_HELPER_ID).Cond(True, _assign, _e): # type: ignore
        Null()