### States for ImageRepro helper.
### This helper provides visuals for the character (while the root does more interesting things).
from mdk.compiler import statedef, statefunc
from mdk.types import (
    SCOPE_HELPER, ConvertibleExpression,
    BoolVar, IntVar, FloatVar, ByteVar,
    StateType, MoveType, PhysicsType, PosType, AssertType, SpaceType
)
from mdk.stdlib import (
    SprPriority, Turn, Explod, VelSet, PosSet, ChangeState, AssertSpecial, ChangeAnim, PlaySnd,
    Facing, Pos, Anim, RoundState, AnimTime, Random, NumExplod, AnimElemTime, GameTime, Cond, Vel,
    FrontEdgeDist,
    enemy
)

from .includes.variables import (
    SavedState, 
    TrackedTime, # type: ignore
    ImageRepro_HasRunIntro, ImageRepro_SelectedMove
)
from .includes.types import ImageReproActionType
from .includes.constants import IMAGEREPRO_HELPER_ID, PAUSETIME_MAX
from .includes.shared import SendToDevilsEye, RandRange, RandPick

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

    ## select a move to use.
    if RoundState == 2:
        if ImageRepro_SelectedMove == ImageReproActionType.Idle:
            ResetTimeAndSetState(ImageRepro_DashToEnemy)
    
    ChangeState(value = SavedState)

@statedef(scope = SCOPE_HELPER(IMAGEREPRO_HELPER_ID), type = StateType.S, movetype = MoveType.I, physics = PhysicsType.U, sprpriority = 3)
def ImageRepro_Idle():
    """
    Idle/standing animation.
    """
    local_xOffs = IntVar()
    local_yOffs = IntVar()
    local_scale = FloatVar()

    SendToDevilsEye()
    if Anim != 0: ChangeAnim(value = 0)

    ## spawn 2 batches of 2 Explods with similar behaviour, but different randomized scale + offset.
    ## these display energy balls of varying size rising from the blade.
    for _ in range(2):
        if TrackedTime >= 6 and GameTime % 3 == 0:
            local_xOffs.set(RandRange(-125, -25))
            local_yOffs.set(RandRange(-55, -35))
            local_scale.set(RandPick(1, -1) * (0.25 + 0.01 * (Random % 5)))
            ## spawn 2 Explods based on these variables.
            for idx in range(2):
                Explod(
                    anim = 30020 + idx,
                    vel = (0, -3),
                    space = SpaceType.Stage,
                    facing = Facing,
                    postype = PosType.P1,
                    pos = (local_xOffs, local_yOffs),
                    ownpal = True,
                    sprpriority = Cond(local_scale < 0, -7 + idx, 6 + idx),
                    scale = (abs(local_scale), abs(local_scale)),
                    pausemovetime = PAUSETIME_MAX,
                    supermovetime = PAUSETIME_MAX
                )

    ## 1 additional Explod.
    ## this displays a halo-like energy effect around the blade.
    if TrackedTime >= 6 and (GameTime % 6) == 0:
        local_xOffs.set(RandRange(-125, -25))
        local_yOffs.set(RandRange(-65, -45))
        local_scale.set(0.05 + 0.01 * (Random % 5))
        Explod(
            anim = 30022,
            vel = (0, 0),
            space = SpaceType.Stage,
            facing = Facing,
            postype = PosType.P1,
            pos = (local_xOffs, local_yOffs),
            ownpal = True,
            sprpriority = RandPick(2, 4),
            scale = (abs(local_scale), abs(local_scale)),
            pausemovetime = PAUSETIME_MAX,
            supermovetime = PAUSETIME_MAX
        )


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

@statedef(scope = SCOPE_HELPER(IMAGEREPRO_HELPER_ID), type = StateType.S, movetype = MoveType.I, physics = PhysicsType.N)
def ImageRepro_DashToEnemy():
    """
    Move towards the enemy root prior to selecting any attack to use.
    """
    SendToDevilsEye()

    if Anim != 270: ChangeAnim(value = 270)

    ## move towards the opponent (ImageRepro_Base turns us towards the opponent)
    if TrackedTime == 0 or Vel.x == 0: VelSet(x = 6.8)
    
    ## transition to the dash-finished state once we are in close enough range
    if abs(Pos.x - enemy.Pos.x) <= 60 or FrontEdgeDist <= 70:
        ResetTimeAndChangeState(ImageRepro_DashToEnemy_Finished)

@statedef(scope = SCOPE_HELPER(IMAGEREPRO_HELPER_ID), type = StateType.S, movetype = MoveType.I, physics = PhysicsType.S)
def ImageRepro_DashToEnemy_Finished():
    """
    Displays an animation for dash completion before returning to the base state.
    """
    SendToDevilsEye()

    if Anim != 271: ChangeAnim(value = 271)
    if TrackedTime == 0: VelSet(x = 0) ## this is just for safety, really it's covered by ImageRepro_Base already

    if AnimTime == 0 and (ImageRepro_SelectedMove := ImageReproActionType.DashForward): 
        ResetTimeAndSetState(ImageRepro_Base)