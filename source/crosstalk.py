### States for ImageRepro helper.
### This helper provides visuals for the character (while the root does more interesting things).
from mdk.compiler import statedef
from mdk.types import (
    SCOPE_HELPER,
    StateType, MoveType, PhysicsType
)
from mdk.stdlib import (
    DestroySelf,
    IsHelper
)

from .includes.constants import CROSSTALK_HELPER_ID, CROSSTALK_TARGET_ID
from .includes.shared import SendToDevilsEye

@statedef(stateno = CROSSTALK_HELPER_ID, scope = SCOPE_HELPER(CROSSTALK_HELPER_ID), type = StateType.S, movetype = MoveType.A, physics = PhysicsType.U)
def CrossTalk_Base():
    """
    Base state for the CrossTalk helper. Most of the CT attacks are co-ordinated from here.

    CT uses MoveType = A by default to make sure it moves before its target.
    """
    SendToDevilsEye()

@statedef(stateno = CROSSTALK_TARGET_ID, scope = SCOPE_HELPER(CROSSTALK_TARGET_ID), type = StateType.S, movetype = MoveType.H, physics = PhysicsType.U)
def CrossTalk_Target():
    """
    Base state for the CrossTalk target. This helper exists only in the initial frames,
    to provide each CT helper with something to hit to obtain a permanent target.
    """
    SendToDevilsEye()

    ## TODO: get hit before destroying!
    if IsHelper(CROSSTALK_TARGET_ID): DestroySelf()