### States for Infiltration Controller helper.
### This Helper exists as a buffer between Infiltration and the root,
### since Infiltration can potentially trigger ParentVarSet controllers during exploration.
### (because of this, the vars on this helper are not trustworthy).
from mdk.compiler import statedef
from mdk.types import SCOPE_HELPER, MoveType, HelperType
from mdk.stdlib import ChangeAnim, PosSet, Helper, NumHelper, root

from source.includes.constants import INFILTRATION_HELPER_ID, INFILTRATION_CONTROLLER_ID, PASSIVE_ANIM, PAUSETIME_MAX
from source.includes.shared import SendToDevilsEye

@statedef(stateno = INFILTRATION_CONTROLLER_ID, movetype = MoveType.A, scope = SCOPE_HELPER(INFILTRATION_CONTROLLER_ID))
def InfiltrationController_Actions():
    SendToDevilsEye()

    ChangeAnim(value = PASSIVE_ANIM)
    PosSet(x = root.Pos.x, y = root.Pos.y)

    ## spawn the infiltration helper IF it is not already spawned, and if CT is already set up.
    if NumHelper(INFILTRATION_HELPER_ID) == 0 and root.Root_CrosstalkInitialized:
        Helper(
            helpertype = HelperType.Player,
            name = "Infiltration Helper",
            id = INFILTRATION_HELPER_ID,
            stateno = InfiltrationHelper_NoOp,
            supermovetime = PAUSETIME_MAX,
            pausemovetime = PAUSETIME_MAX
        )

@statedef(stateno = INFILTRATION_HELPER_ID, movetype = MoveType.I, scope = SCOPE_HELPER(INFILTRATION_HELPER_ID))
def InfiltrationHelper_NoOp():
    """This state does nothing, it's a placeholder for Infiltration to be spawned into.
    It should spend very little time here."""
    SendToDevilsEye()

    ChangeAnim(value = PASSIVE_ANIM)
    PosSet(x = root.Pos.x, y = root.Pos.y)