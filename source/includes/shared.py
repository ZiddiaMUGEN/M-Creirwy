from mdk.compiler import statefunc, trigger
from mdk.stdlib import Name, IsHelper, root, ChangeState, SelfState, Random, Cond, Null
from mdk.types import Expression, ConvertibleExpression, VariableExpression, TypeSpecifier, IntType, BoolType

from mdk.stdlib.redirects import RedirectTarget
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
def RootVarSet(var_name: ConvertibleExpression, value: ConvertibleExpression):
    """
    Use Cond-bug with a Null controller to set a value on the root. 
    This will not work as expected if executed from a non-Helper context.
    """
    if not isinstance(var_name, Expression): var_name = convert(var_name)
    if not isinstance(value, Expression): value = convert(value)

    if Expression(f"root,Cond({var_name.exprn} := {value.exprn}, true, true)", BoolType):
        Null()

@statefunc()
def TargetVarSet(var_name: ConvertibleExpression, value: ConvertibleExpression, scope: RedirectTarget):
    """
    Use Cond-bug with a Null controller to set a value on a target.
    You must provide a concrete scope for the target as well.
    This will not work as expected if the current context has no target.
    """
    if not isinstance(var_name, Expression): var_name = convert(var_name)
    if not isinstance(value, Expression): value = convert(value)

    if Expression(f"rescope(target, {scope.__repr__()}),Cond({var_name.exprn} := {value.exprn}, true, true)", BoolType):
        Null()

@statefunc()
def CreirwyVarSet(var_name: ConvertibleExpression, value: ConvertibleExpression):
    """
    Use Cond-bug with a Null controller to set a value on Creirwy's root.
    This is expected to be run from the enemy's context so that captured enemies can set Creirwy's progress flags.
    """
    if not isinstance(var_name, Expression): var_name = convert(var_name)
    if not isinstance(value, Expression): value = convert(value)

    ## because this is executed from a TARGET scope, no `rescope` operator is required.
    ## `enemy(xyz)` on TARGET scope is resolved to PLAYER scope.
    if Expression(f"enemy(enemy,Name != \"M-Creirwy\"),Cond({var_name.exprn} := {value.exprn}, true, true)", BoolType):
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

def ReadStorageVar_Enemy(var_name: VariableExpression, type: TypeSpecifier = IntType) -> Expression:
    """
    Use this as a Trigger. Returns a Condbug statement to read the value of a variable in the Storage helper.
    """
    return Expression(f"enemy(enemy,Name != \"M-Creirwy\"),Cond(NumHelper({STORAGE_HELPER_ID}), Helper({STORAGE_HELPER_ID}),{var_name.exprn}, 0)", type)

@statefunc()
def SetStorageVar_Enemy(var_name: ConvertibleExpression, value: ConvertibleExpression):
    """
    Use Cond-bug with a Null controller to set a value on Creirwy's Storage helper.
    This is expected to be run from the enemy's context so that captured enemies can set Creirwy's progress flags.
    """
    if not isinstance(var_name, Expression): var_name = convert(var_name)
    if not isinstance(value, Expression): value = convert(value)

    ## because this is executed from a TARGET scope, no `rescope` operator is required.
    ## `enemy(xyz)` on TARGET scope is resolved to PLAYER scope.
    if Expression(f"enemy(enemy,Name != \"M-Creirwy\"),Cond(Helper({STORAGE_HELPER_ID}),Cond({var_name.exprn} := {value.exprn}, true, true)), true, true)", BoolType):
        Null()

@statefunc()
def SetStorageVar_Self(var_name: ConvertibleExpression, value: ConvertibleExpression):
    """
    Use Cond-bug with a Null controller to set a value on Creirwy's Storage helper.
    This is expected to be run from Creirwy's team's context so that helpers can set progress flags.
    """
    if not isinstance(var_name, Expression): var_name = convert(var_name)
    if not isinstance(value, Expression): value = convert(value)

    if Expression(f"Helper({STORAGE_HELPER_ID}),Cond({var_name.exprn} := {value.exprn}, true, true)", BoolType):
        Null()