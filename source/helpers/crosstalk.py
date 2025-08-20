### States for Crosstalk helper.
### This helper retains permanent targets on all Helpers. This allows us to use the enemy's Helpers to do more interesting things
### (for example, variable tampering and state callback).
from mdk.compiler import statedef
from mdk.types import (
    SCOPE_HELPER,
    StateType, MoveType, PhysicsType, HitAttr, HitType, TeamType,
    IntVar
)
from mdk.stdlib import (
    DestroySelf, ChangeAnim, PosSet, HitDef, ReversalDef, ScreenBound, PlayerPush, DisplayToClipboard,
    IsHelper, Const, ID, NumTarget, TeamSide,
    playerID, helperID, parent, target
)

from source.includes.constants import CROSSTALK_HELPER_ID, CROSSTALK_TARGET_ID
from source.includes.variables import CrossTalkTarget_TargetObtained
from source.includes.shared import SendToDevilsEye, TargetVarSet

CT_GROUP_INDEX = Const("size.shadowoffset")

CT_GETHIT_ANIM = 10000
CT_ATTACK_ANIM = 10001
CT_PASSIVE_ANIM = 10002

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
        ChangeAnim(value = CT_PASSIVE_ANIM)
        ReversalDef(reversal_attr = (HitType.SCA, HitAttr.AA, HitAttr.AT, HitAttr.AP))
        PosSet(x = parent.Pos.x, y = parent.Pos.y)

    ## setup: gain a target if not already gained
    if not NumTarget():
        ChangeAnim(value = CT_ATTACK_ANIM)
        PosSet(x = -500, y = -15 * CT_GROUP_INDEX)
        HitDef(
            attr = (HitType.SCA, HitAttr.AA, HitAttr.AT, HitAttr.AP),
            affectteam = TeamType.F
        )

    ## once we have a target on the initial CT Target helper, prompt it to delete itself
    if NumTarget() and target.TeamSide == TeamSide and target.Const("size.shadowoffset") == CT_GROUP_INDEX:
        ## we want to rescope `target` to `helper(CROSSTALK_TARGET_ID)` to get access to the `CrossTalkTarget_TargetObtained` variable.
        TargetVarSet(CrossTalkTarget_TargetObtained, True, helperID(CROSSTALK_TARGET_ID))

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