### States for ImageRepro helper.
### This helper provides visuals for the character (while the root does more interesting things).
from mdk.compiler import statedef, statefunc
from mdk.types import (
    SCOPE_HELPER, ConvertibleExpression,
    BoolVar, IntVar, FloatVar,
    StateType, MoveType, PhysicsType, PosType, AssertType
)
from mdk.stdlib import (
    SprPriority, Turn, Explod, VelSet, PosSet, ChangeState, AssertSpecial, ChangeAnim, PlaySnd,
    Facing, Pos, Anim, RoundState, AnimTime, Random, NumExplod, AnimElemTime, GameTime,
    enemy
)

from .includes.variables import (
    SavedState, 
    TrackedTime # type: ignore
)
from .includes.constants import IMAGEREPRO_HELPER_ID, PAUSETIME_MAX
from .includes.shared import SendToDevilsEye, RandRange, RandPick

ImageRepro_HasRunIntro = BoolVar(scope = SCOPE_HELPER(IMAGEREPRO_HELPER_ID))
"""Flag indicating whether ImageRepro has gone through its into animation + returned to idle already."""

@statefunc
def ResetTimeAndSetState(value: ConvertibleExpression):
    """
    Resets the value of TrackedTime to 0 and updates SavedState, but does not trigger a state change.
    """
    if (TrackedTime := 0) or True: # type: ignore
        SavedState.set(value)

@statefunc
def ResetTimeAndChangeState(value: ConvertibleExpression):
    """
    Resets the value of TrackedTime to 0 and updates SavedState, then performs a state change.
    """
    if (TrackedTime := 0) or True: # type: ignore
        if (SavedState := value) or True:
            ChangeState(value = SavedState)

@statedef(stateno = IMAGEREPRO_HELPER_ID, scope = SCOPE_HELPER(IMAGEREPRO_HELPER_ID), type = StateType.S, movetype = MoveType.I, physics = PhysicsType.U)
def ImageRepro_Base():
    """
    Base state for the ImageRepro helper. From here it will decide which action it wants to display.
    """
    SendToDevilsEye()

    SprPriority(value = 100)
    if (Facing == 1 and enemy.Pos.x < Pos.x) or (Facing == -1 and enemy.Pos.x > Pos.x):
        Turn()

    VelSet(y = 0)
    PosSet(y = 0)

    if not ImageRepro_HasRunIntro:
        ResetTimeAndSetState(ImageRepro_IntroIdle)
        ImageRepro_HasRunIntro.set(True)
    
    ChangeState(value = SavedState)

@statedef(scope = SCOPE_HELPER(IMAGEREPRO_HELPER_ID), type = StateType.S, movetype = MoveType.I, physics = PhysicsType.U)
def ImageRepro_Idle():
    """
    Idle/standing animation.
    """
    local_xOffs = IntVar()
    local_yOffs = IntVar()
    local_scale = FloatVar()

    SendToDevilsEye()
    if Anim != 0: ChangeAnim(value = 0)

    if TrackedTime >= 6 and GameTime % 3 == 0:
        local_xOffs.set(RandRange(-55, -35))
        local_yOffs.set(RandRange(-125, -25))
        local_scale.set(RandPick(1, -1) * (0.25 + 0.01 * (Random % 5)))


@statedef(scope = SCOPE_HELPER(IMAGEREPRO_HELPER_ID), type = StateType.S, movetype = MoveType.I, physics = PhysicsType.U)
def ImageRepro_IntroIdle():
    """
    Display introduction phase 1.
    """
    SendToDevilsEye()
    AssertSpecial(flag = AssertType.Intro)
    if Anim != 190: ChangeAnim(value = 190)
    if TrackedTime >= 180:
        ResetTimeAndChangeState(ImageRepro_IntroAnim)

@statedef(scope = SCOPE_HELPER(IMAGEREPRO_HELPER_ID), type = StateType.S, movetype = MoveType.I, physics = PhysicsType.U)
def ImageRepro_IntroAnim():
    """
    Display introduction phase 2.
    """
    SendToDevilsEye()
    AssertSpecial(flag = AssertType.Intro)
    if RoundState == 1 and Anim != 193: ChangeAnim(value = 193)
    if RoundState == 1 and TrackedTime == 0: PlaySnd(value = (180, Random % 3))

    # explods for the sword image
    ## TODO: the sword glow is displayed twice here, need to figure out why.
    for idx in range(2):
        if NumExplod(191 + idx) == 0 and AnimElemTime(4) == 0 and Anim == 193:
            Explod(
                id = 191 + idx,
                anim = 191 + idx,
                scale = (0.25, 0.25),
                postype = PosType.P1,
                pos = (0, 0),
                sprpriority = 23 - idx,
                supermovetime = PAUSETIME_MAX,
                pausemovetime = PAUSETIME_MAX
            )

    if AnimTime == 0:
        ResetTimeAndChangeState(ImageRepro_Idle)