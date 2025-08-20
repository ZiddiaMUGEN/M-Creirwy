### States for Marking helper.
### This helper attempts to obtain a permanent target on the enemy root.
### It will attempt both Hit and Reversal marking.
from mdk.compiler import statedef
from mdk.types import (
    SCOPE_HELPER, 
    MoveType, HitType, HitAttr, TeamType, HitFlagType,
    IntVar
)
from mdk.stdlib import (
    ChangeAnim, ReversalDef, HitDef, PosSet, TargetDrop, DisplayToClipboard,
    NumTarget, GameTime,
    enemy, parent, target
)

from source.includes.constants import MARKING_HELPER_ID
from source.includes.shared import SendToDevilsEye, InRange

MARKING_ATTACK_ANIM = 2694501
MARKING_PASSIVE_ANIM = 10002

@statedef(stateno = MARKING_HELPER_ID, movetype = MoveType.A, scope = SCOPE_HELPER(MARKING_HELPER_ID))
def MarkingHelper_Actions():
    SendToDevilsEye()

    local_lastTargetID = IntVar()

    ## retain the target once it's been obtained
    if NumTarget():
        ChangeAnim(value = MARKING_PASSIVE_ANIM)
        ReversalDef(reversal_attr = (HitType.SCA, HitAttr.AA, HitAttr.AT, HitAttr.AP))
        PosSet(x = parent.Pos.x, y = parent.Pos.y)

    ## setup: gain a target if not already gained
    if not NumTarget():
        ChangeAnim(value = MARKING_ATTACK_ANIM)
        PosSet(x = enemy.Pos.x, y = enemy.Pos.y)

        ## we want to alternate between HitDef-based and ReversalDef-based marking.
        ## HitDef-based marking should also apply once for each HitDef/HitAttr combo.
        ## (this is because certain characters use HitOverride and can only be marked
        ## in specific ways)
        ## each HitDef gets 2 frames, and ReversalDef is interleaved on alternate 2 frames.
        index = 0
        for hittype in [HitType.S, HitType.C, HitType.A]:
            for hitattr in [
                HitAttr.NA, HitAttr.SA, HitAttr.HA,
                HitAttr.NT, HitAttr.ST, HitAttr.HT,
                HitAttr.NP, HitAttr.SP, HitAttr.HP
            ]:
                if GameTime % 108 == index or GameTime % 108 == index + 1:
                    HitDef(
                        attr = (hittype, hitattr),
                        hitflag = HitFlagType.HLAFD,
                        sparkno = -1,
                        guard_sparkno = -1,
                        hitsound = (-1, 0),
                        guardsound = (-1, 0),
                        affectteam = TeamType.E
                    )
                index += 4
        
        if GameTime % 4 == 2 or GameTime % 4 == 3:
            ReversalDef(
                reversal_attr = (HitType.SCA, HitAttr.AA, HitAttr.AT, HitAttr.AP),
                hitflag = HitFlagType.HLAFD,
                sparkno = -1,
                guard_sparkno = -1,
                hitsound = (-1, 0),
                guardsound = (-1, 0)
            )

    ## if this helper manages to capture multiple targets, drop all but one.
    ## then inspect the remaining target and drop it as well if it is not the enemy root.
    if NumTarget() > 1:
        TargetDrop(keepone = True)
    if NumTarget() == 1 and target.IsHelper():
        TargetDrop()
        
    ## last step in this state: update the target ID local to make sure we identify when
    ## a new target is captured.
    if NumTarget():
        local_lastTargetID.set(target.ID)

    ## technically we can get this info from mtldbg but this is easier as an overview.
    print(f"Target: {local_lastTargetID}")