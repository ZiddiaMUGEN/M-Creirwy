### States for Crosstalk helper.
### This helper retains permanent targets on all Helpers. This allows us to use the enemy's Helpers to do more interesting things
### (for example, variable tampering and state callback).
from mdk.compiler import statedef
from mdk.types import (
    SCOPE_HELPER, SCOPE_PLAYER,
    StateType, MoveType, PhysicsType, HitAttr, HitType, TeamType, Expression,
    IntVar
)
from mdk.stdlib import (
    DestroySelf, ChangeAnim, PosSet, HitDef, ReversalDef, ScreenBound, PlayerPush,
    TargetState,
    IsHelper, Const, NumTarget, TeamSide, NumHelper,
    helperID, parent, target, root, enemy, rescope
)

from source.includes.constants import CROSSTALK_HELPER_ID, CROSSTALK_TARGET_ID, SPY_HELPER_ID, EXPLORER_BUFFER_ID, EXPLORER_HELPER_ID, STORAGE_HELPER_ID
from source.includes.variables import (
    CrossTalkTarget_TargetObtained, 
    ExplorerStorage_SavedMoveTypeH_Low, ExplorerStorage_SavedMoveTypeH_High, ## ayuayu
    ExplorerStorage_SavedAttackState, ExplorerStorage_SavedHitDefState, ## OTHK
)
from source.includes.shared import SendToDevilsEye, TargetVarSet, SetStorageVar_Self
#from source.includes.types import ExplorerActionTypeT, ExplorerActionType

from source.anims import SMALL_ATTACK_ANIM, PASSIVE_ANIM

CT_GROUP_INDEX = Const("size.shadowoffset")

def GetExplorationStateNo() -> Expression:
    """
    Use this as a Trigger. Returns a Condbug statement to retrieve the value of the Explorer's target state.
    """
    return rescope(enemy, SCOPE_PLAYER).Cond(NumHelper(EXPLORER_BUFFER_ID) != 0, helperID(EXPLORER_BUFFER_ID).Exploration_CurrentState, -1)

@statedef(stateno = CROSSTALK_HELPER_ID, scope = SCOPE_HELPER(CROSSTALK_HELPER_ID), type = StateType.S, movetype = MoveType.A, physics = PhysicsType.U)
def CrossTalk_Base():
    """
    Base state for the CrossTalk helper. Most of the CT attacks are co-ordinated from here.

    CT uses MoveType = A by default to make sure it moves before its target.
    """
    SendToDevilsEye()

    local_lastTargetID = IntVar()

    ScreenBound(value = False, movecamera = (False, False))
    PlayerPush(value = False)

    ## retain the target once it's been obtained
    if NumTarget():
        ChangeAnim(value = PASSIVE_ANIM)
        ReversalDef(reversal_attr = (HitType.SCA, HitAttr.AA, HitAttr.AT, HitAttr.AP))
        PosSet(x = parent.Pos.x, y = parent.Pos.y)

    ## setup: gain a target if not already gained
    if not NumTarget():
        ChangeAnim(value = SMALL_ATTACK_ANIM)
        PosSet(x = -500, y = -15 * CT_GROUP_INDEX)
        HitDef(
            attr = (HitType.SCA, HitAttr.AA, HitAttr.AT, HitAttr.AP),
            affectteam = TeamType.F
        )

    ## once we have a target on the initial CT Target helper, prompt it to delete itself
    if NumTarget() and target.TeamSide == TeamSide and target.Const("size.shadowoffset") == CT_GROUP_INDEX:
        ## we want to rescope `target` to `helper(CROSSTALK_TARGET_ID)` to get access to the `CrossTalkTarget_TargetObtained` variable.
        TargetVarSet(CrossTalkTarget_TargetObtained, True, helperID(CROSSTALK_TARGET_ID))

    ## if we have a target, and no spy has been spawned, try to steal the target
    ## we can use DEK here as a baseline for target stealing.
    if NumTarget() and target.TeamSide != TeamSide and not root.Root_SpyIsSpawned:
        TargetState(value = target.StateNo)

    ## if the target is the Spy helper or the Explorer buffer, always send it to the base state for that helper.
    if NumTarget() and target.TeamSide != TeamSide and target.IsHelper(SPY_HELPER_ID):
        TargetState(value = SPY_HELPER_ID)
    if NumTarget() and target.TeamSide != TeamSide and target.IsHelper(EXPLORER_BUFFER_ID):
        TargetState(value = EXPLORER_BUFFER_ID)

    ## if the target is the Explorer helper, we want to detect any states found by exploration before running TargetState
    ## this is done here instead of inside Explorer or buffer as the CT targeting Explorer is always guaranteed to move before it.
    if NumTarget() and target.TeamSide != TeamSide and target.IsHelper(EXPLORER_HELPER_ID):
        ## for state inspection, only check if the target is not in the explorer base state (i.e. our state file)
        if target.StateNo == GetExplorationStateNo():
            ## detect Ayuayu: if the Explorer's movetype is H, then the current state is a candidate for Ayuayu
            if target.MoveType == MoveType.H:
                if target.StateNo < 200 and helperID(STORAGE_HELPER_ID).ExplorerStorage_SavedMoveTypeH_Low == 0:
                    SetStorageVar_Self(ExplorerStorage_SavedMoveTypeH_Low, enemy.Cond(NumHelper(EXPLORER_HELPER_ID) != 0, helperID(EXPLORER_HELPER_ID).StateNo, -1))
                if target.StateNo >= 200 and helperID(STORAGE_HELPER_ID).ExplorerStorage_SavedMoveTypeH_High == 0:
                    SetStorageVar_Self(ExplorerStorage_SavedMoveTypeH_High, enemy.Cond(NumHelper(EXPLORER_HELPER_ID) != 0, helperID(EXPLORER_HELPER_ID).StateNo, -1))
            ## detect candidate Attack states: Explorer's movetype is A
            if target.MoveType == MoveType.A and helperID(STORAGE_HELPER_ID).ExplorerStorage_SavedAttackState == 0:
                SetStorageVar_Self(ExplorerStorage_SavedAttackState, enemy.Cond(NumHelper(EXPLORER_HELPER_ID) != 0, helperID(EXPLORER_HELPER_ID).StateNo, -1))
        ## this doesn't detect properly in the above conditional (maybe it is moving out of the target state for some reason...?)
        if target.StateNo != EXPLORER_HELPER_ID:
            if target.HitDefAttr == (HitType.SCA, HitAttr.AA, HitAttr.AT, HitAttr.AP) and helperID(STORAGE_HELPER_ID).ExplorerStorage_SavedHitDefState == 0:
                SetStorageVar_Self(ExplorerStorage_SavedHitDefState, enemy.Cond(NumHelper(EXPLORER_HELPER_ID) != 0, helperID(EXPLORER_HELPER_ID).StateNo, -1))

        TargetState(value = EXPLORER_HELPER_ID)

    ## last step in this state: update the target ID local to make sure we identify when
    ## a new target is captured.
    if NumTarget():
        local_lastTargetID.set(target.ID)

    print(f"Target: {local_lastTargetID}")

@statedef(stateno = CROSSTALK_TARGET_ID, scope = SCOPE_HELPER(CROSSTALK_TARGET_ID), type = StateType.S, movetype = MoveType.H, physics = PhysicsType.U)
def CrossTalk_Target():
    """
    Base state for the CrossTalk target. This helper exists only in the initial frames,
    to provide each CT helper with something to hit to obtain a permanent target.
    """
    SendToDevilsEye()

    # just make sure you're not disruptive
    ScreenBound(value = False, movecamera = (False, False))
    PlayerPush(value = False)

    ## set a small Clsn2 animation
    ChangeAnim(value = 10000)

    ## set position based on this helper's group index
    PosSet(x = -500, y = -15 * CT_GROUP_INDEX)

    ## this helper doesn't need to do much, just get hit and destroy self.
    if IsHelper(CROSSTALK_TARGET_ID) and CrossTalkTarget_TargetObtained: DestroySelf()