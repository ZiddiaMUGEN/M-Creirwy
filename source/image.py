### States for ImageRepro helper.
### This helper provides visuals for the character (while the root does more interesting things).
from mdk.compiler import statedef
from mdk.types import SCOPE_HELPER, StateType, MoveType, PhysicsType
from mdk.stdlib import SprPriority, Turn, Explod, VelSet, PosSet, ChangeState, Facing, enemy, Pos


from .includes.constants import IMAGEREPRO_HELPER_ID
from .includes.shared import SendToDevilsEye, ChangeState_TimeReset

@statedef(stateno = IMAGEREPRO_HELPER_ID, scope = SCOPE_HELPER(IMAGEREPRO_HELPER_ID), type = StateType.S, movetype = MoveType.I, physics = PhysicsType.U)
def ImageRepro_Base():
    """
    Base state for the ImageRepro helper. From here it will decide which action it wants to display.
    """
    SendToDevilsEye()

    SprPriority(value = 100, ignorehitpause = True, persistent = 256)
    if (Facing == 1 and enemy.Pos.x < Pos.x) or (Facing == -1 and enemy.Pos.x > Pos.x):
        Turn(ignorehitpause = True, persistent = 256)

    ChangeState_TimeReset(ImageRepro_Base)
