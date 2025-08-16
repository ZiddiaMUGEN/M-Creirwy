### States for ImageRepro helper.
### This helper provides visuals for the character (while the root does more interesting things).
from mdk.compiler import statedef, statefunc
from mdk.types import (
    SCOPE_HELPER,
    StateType, MoveType, PhysicsType
)
from mdk.stdlib import (
    Null
)

from .includes.constants import CROSSTALK_HELPER_ID, CROSSTALK_HELPER_STATE
from .includes.shared import SendToDevilsEye

@statedef(stateno = CROSSTALK_HELPER_STATE, scope = SCOPE_HELPER(CROSSTALK_HELPER_ID), type = StateType.S, movetype = MoveType.A, physics = PhysicsType.U)
def CrossTalk_Base():
    """
    Base state for the CrossTalk helper. Most of the CT attacks are co-ordinated from here.

    CT uses MoveType = A by default to make sure it moves before its target.
    """
    SendToDevilsEye()