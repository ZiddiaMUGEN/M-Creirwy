from mdk.compiler import statedef
from mdk.types import SCOPE_HELPER, HitType, HitAttr, HelperType, AssertType, MoveType
from mdk.stdlib import (
    SelfState, NotHitBy, AssertSpecial, ChangeAnim2, Helper, StateTypeSet,
    NumHelper,
    helperID, enemy, enemyID
)

from source.includes.variables import Exploration_CurrentState
from source.includes.shared import SendToSafeStates
from source.includes.constants import SPY_HELPER_ID, EXPLORER_HELPER_ID, EXPLORER_BUFFER_ID, PAUSETIME_MAX, PASSIVE_ANIM

creirwy = enemyID(enemy.Name != "M-Creirwy")
"""A custom redirect to the correct enemy index for Creirwy."""
spy = helperID(SPY_HELPER_ID)
"""Redirect targeting the Spy helper."""

@statedef(stateno = EXPLORER_BUFFER_ID, movetype = MoveType.I, scope = SCOPE_HELPER(EXPLORER_BUFFER_ID))
def ExplorationBuffer_Base():
    """
    Entry point for the Exploration buffer.

    This is only responsible for spawning additional Exploration helpers and tracking the next state to enter.

    This is done here instead of in Spy because exploration target states can invoke ParentVarSet and corrupt the parent's variables, this buffer helper keeps the Spy's variables reliable.
    """
    SendToSafeStates()

    ## spy should be untouchable/invisible.
    NotHitBy(value = (HitType.SCA, HitAttr.AA, HitAttr.AT, HitAttr.AP))
    AssertSpecial(flag = AssertType.Invisible, flag2 = AssertType.NoShadow)
    ChangeAnim2(value = PASSIVE_ANIM)

    if NumHelper(EXPLORER_HELPER_ID) != 0:
        ## increment the target state for exploration.
        Exploration_CurrentState.add(1)
        ## we must skip over all guard states.
        if Exploration_CurrentState >= 120 and Exploration_CurrentState < 160:
            Exploration_CurrentState.set(161)

    if NumHelper(EXPLORER_HELPER_ID) == 0:
        Helper(
            id = EXPLORER_HELPER_ID,
            name = "Creirwy's Exploration Helper",
            stateno = EXPLORER_HELPER_ID,
            helpertype = HelperType.Normal,
            supermovetime = PAUSETIME_MAX,
            pausemovetime = PAUSETIME_MAX
        )

@statedef(stateno = EXPLORER_HELPER_ID, movetype = MoveType.U, scope = SCOPE_HELPER(EXPLORER_HELPER_ID))
def ExplorationHelper_Base():
    """
    Entry point for the Exploration helper.
    """
    SendToSafeStates()

    ## spy should be untouchable/invisible.
    NotHitBy(value = (HitType.SCA, HitAttr.AA, HitAttr.AT, HitAttr.AP))
    AssertSpecial(flag = AssertType.Invisible, flag2 = AssertType.NoShadow)
    ChangeAnim2(value = PASSIVE_ANIM)

    ## set MoveType=H for Ayuayu detection
    StateTypeSet(movetype = MoveType.H)

    ## enter the next state for exploration.
    SelfState(value = helperID(EXPLORER_BUFFER_ID).Exploration_CurrentState, ctrl = True)