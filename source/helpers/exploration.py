from mdk.compiler import statedef
from mdk.types import SCOPE_HELPER, HitType, HitAttr, HelperType, AssertType, MoveType, StateType, HitFlagType, VariableExpression, SCOPE_PLAYER, BoolVar, Expression, AnyType, TeamType
from mdk.stdlib import (
    SelfState, NotHitBy, AssertSpecial, ChangeAnim2, Helper, StateTypeSet, PosSet, HitDef,
    NumHelper, HitPauseTime, GetHitVar,
    helperID, enemy, enemyID, rescope
)

from source.includes.types import ExplorerActionType
from source.includes.variables import (
    Exploration_CurrentState, Exploration_ActionType,
    ExplorerStorage_SavedMoveTypeH_Low, ExplorerStorage_SavedMoveTypeH_High,
    ExplorerStorage_SavedHitByState,
    ExplorerStorage_SavedHitDefState
)
from source.includes.shared import SendToSafeStates, ReadStorageVar_Enemy, SetStorageVar_Enemy
from source.includes.constants import SPY_HELPER_ID, EXPLORER_HELPER_ID, EXPLORER_BUFFER_ID, PAUSETIME_MAX, PASSIVE_ANIM

creirwy = enemyID(enemy.Name != "M-Creirwy")
"""A custom redirect to the correct enemy index for Creirwy."""
spy = helperID(SPY_HELPER_ID)
"""Redirect targeting the Spy helper."""

ATTACK_ANIM = 10001
"""Used by the Exploration helper when it needs to gain HitPauseTime."""
GETHIT_ANIM = 10000
"""Used by the Exploration helper when it needs to check for HitBy overrides."""

HITBY_DETECTION = EXPLORER_BUFFER_ID
"""Used during HitBy detection; if the Explorer has a fall amplitude of this value in its HitVar, then a hit made contact."""

def ReadBufferHelperVar(variable: VariableExpression):
    """Helper function to provide access to Buffer helper's internal variables to Conds inside Variable Storage."""
    return rescope(enemy, SCOPE_PLAYER).Cond(NumHelper(EXPLORER_BUFFER_ID) != 0, getattr(helperID(EXPLORER_BUFFER_ID), variable.exprn), -1)

@statedef(stateno = EXPLORER_BUFFER_ID, movetype = MoveType.I, scope = SCOPE_HELPER(EXPLORER_BUFFER_ID))
def ExplorationBuffer_Base():
    """
    Entry point for the Exploration buffer.

    This is only responsible for spawning additional Exploration helpers and tracking the next state to enter.

    This is done here instead of in Spy because exploration target states can invoke ParentVarSet and corrupt the parent's variables, this buffer helper keeps the Spy's variables reliable.
    """
    SendToSafeStates()

    local_isFrozenSearch = BoolVar()
    if (ReadStorageVar_Enemy(ExplorerStorage_SavedMoveTypeH_Low) != 0 and ReadStorageVar_Enemy(ExplorerStorage_SavedMoveTypeH_High) != 0) or Exploration_CurrentState > 999:
        local_isFrozenSearch.set(True)

    ## spy should be untouchable/invisible.
    NotHitBy(value = (HitType.SCA, HitAttr.AA, HitAttr.AT, HitAttr.AP))
    PosSet(x = creirwy.Pos.x, y = creirwy.Pos.y)
    AssertSpecial(flag = AssertType.Invisible, flag2 = AssertType.NoShadow)
    ChangeAnim2(value = PASSIVE_ANIM)

    ## if the current Explorer state is CheckHitBy, then in the previous frame we attempted to attack.
    ## try to detect the HITBY_DETECTION value and progress to Ready.
    if Exploration_ActionType == ExplorerActionType.CheckHitBy:
        if helperID(EXPLORER_HELPER_ID).GetHitVar("fall.envshake.ampl") == HITBY_DETECTION:
            SetStorageVar_Enemy(ExplorerStorage_SavedHitByState, ReadBufferHelperVar(Exploration_CurrentState))
        Exploration_ActionType.set(ExplorerActionType.Ready)

    ## if the current Explorer state is EnterState and there has not been a HitBy state detected,
    ## we need to pause investigation and give a chance to detect HitBy.
    if Exploration_ActionType == ExplorerActionType.EnterState and ReadStorageVar_Enemy(ExplorerStorage_SavedHitByState) == 0:
        ## the Buffer helper will attempt to attack the Exploration helper to see if HitBy has been applied.
        StateTypeSet(statetype = StateType.S, movetype = MoveType.A)
        ChangeAnim2(value = ATTACK_ANIM)
        HitDef(attr = (HitType.SCA, HitAttr.AA, HitAttr.AT, HitAttr.AP), hitflag = HitFlagType.HLAFD, sparkno = -1, guard_sparkno = -1, fall_envshake_ampl = HITBY_DETECTION, affectteam = TeamType.F)
        Exploration_ActionType.set(ExplorerActionType.CheckHitBy)

    ## otherwise, progress the investigation back to Ready to enter the next state.
    if Exploration_ActionType == ExplorerActionType.EnterState:
        Exploration_ActionType.set(ExplorerActionType.Ready)

    ## if the Explorer exists and Ayuayu + HitDef is already detected, then we need to make sure to gain HPT.
    ## this allows the Explorer to detect Alive-change, Palno-change, etc. states and reduces crash risk.
    ## also use an arbitrary cutoff: if the explorer reaches state 999 and still has not swapped to frozen,
    ## assume no Ayuayu/HitDef exist and start using frozen. (this is for crash avoidance).
    if NumHelper(EXPLORER_HELPER_ID) != 0 and helperID(EXPLORER_HELPER_ID).HitPauseTime == 0 and Exploration_ActionType == ExplorerActionType.Ready:
        if local_isFrozenSearch:
            Exploration_ActionType.set(ExplorerActionType.WaitForHitPause)

    ## if HPT was gained, return to a Ready state so it can continue to investigate.
    if NumHelper(EXPLORER_HELPER_ID) != 0 and helperID(EXPLORER_HELPER_ID).HitPauseTime > 0 and Exploration_ActionType == ExplorerActionType.WaitForHitPause:
        Exploration_ActionType.set(ExplorerActionType.Ready)

    ## check if the Explorer exists and if the current action type is Ready
    if NumHelper(EXPLORER_HELPER_ID) != 0 and Exploration_ActionType == ExplorerActionType.Ready:
        ## increment the target state for exploration.
        Exploration_CurrentState.add(1)
        ## we must skip over all guard states.
        if Exploration_CurrentState >= 120 and Exploration_CurrentState < 160:
            Exploration_CurrentState.set(161)
        ## set ActionType to EnterState to instruct the helper to progress
        Exploration_ActionType.set(ExplorerActionType.EnterState)

    if NumHelper(EXPLORER_HELPER_ID) == 0:
        Exploration_ActionType.set(ExplorerActionType.Ready)
        Helper(
            id = EXPLORER_HELPER_ID,
            name = "Creirwy's Exploration Helper",
            stateno = EXPLORER_HELPER_ID,
            helpertype = HelperType.Normal,
            supermovetime = PAUSETIME_MAX,
            pausemovetime = PAUSETIME_MAX
        )

    print(f"Using frozen exploration? {local_isFrozenSearch}")

@statedef(stateno = EXPLORER_HELPER_ID, movetype = MoveType.U, scope = SCOPE_HELPER(EXPLORER_HELPER_ID), hitdefpersist = True)
def ExplorationHelper_Base():
    """
    Entry point for the Exploration helper.
    """
    SendToSafeStates()

    ## spy should be untouchable/invisible.
    PosSet(x = creirwy.Pos.x, y = creirwy.Pos.y)
    AssertSpecial(flag = AssertType.Invisible, flag2 = AssertType.NoShadow)
    ChangeAnim2(value = PASSIVE_ANIM)

    ## if the current action type is CheckHitBy we cannot overwrite the HitBy status and we need to take a hittable anim.
    if helperID(EXPLORER_BUFFER_ID).Exploration_ActionType == ExplorerActionType.CheckHitBy:
        ChangeAnim2(value = GETHIT_ANIM)
        NotHitBy(value = (HitType.SCA, HitAttr.AA, HitAttr.AT, HitAttr.AP))
        SelfState(value = helperID(EXPLORER_BUFFER_ID).Exploration_CurrentState, ctrl = True)
    ## otherwise this Helper needs to always be unhittable.
    if helperID(EXPLORER_BUFFER_ID).Exploration_ActionType != ExplorerActionType.CheckHitBy:
        NotHitBy(value = (HitType.SCA, HitAttr.AA, HitAttr.AT, HitAttr.AP))

    print(f"Pausetime = {HitPauseTime}, State = {helperID(EXPLORER_BUFFER_ID).Exploration_ActionType}, Hitvar= {GetHitVar('fall.envshake.ampl')}")

    ## we only progress to the next detection state if the action type is EnterState (meaning bookkeeping in Buffer is done).
    if helperID(EXPLORER_BUFFER_ID).Exploration_ActionType == ExplorerActionType.EnterState:
        ## during Frozen search, we need to retain MoveType=A and remove our own HitDefAttr.
        if HitPauseTime != 0:
            StateTypeSet(statetype = StateType.S, movetype = MoveType.A)
            HitDef(attr = (Expression("", AnyType), ))

        ## set MoveType=H for Ayuayu detection
        if HitPauseTime == 0:
            StateTypeSet(movetype = MoveType.H)

        ## enter the next state for exploration.
        SelfState(value = helperID(EXPLORER_BUFFER_ID).Exploration_CurrentState, ctrl = True)

    ## if the current action type is WaitForHitPause this Helper needs to gain HPT for frozen exploration.
    ## (this implies 2 Ayuayu states have been detected already).
    if helperID(EXPLORER_BUFFER_ID).Exploration_ActionType == ExplorerActionType.WaitForHitPause:
        ## hit the Callback Receiver helper.
        ChangeAnim2(value = ATTACK_ANIM)
        StateTypeSet(statetype = StateType.C, movetype = MoveType.A)
        HitDef(attr = (HitType.C, HitAttr.HP), hitflag = HitFlagType.HLAFD, sparkno = -1, guard_sparkno = -1, pausetime = (PAUSETIME_MAX, 0))