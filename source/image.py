### States for ImageRepro helper.
### This helper provides visuals for the character (while the root does more interesting things).
from mdk.compiler import statedef, statefunc
from mdk.types import (
    SCOPE_HELPER, ConvertibleExpression, VariableExpression, TupleExpression,
    BoolVar, IntVar, FloatVar, ByteVar,
    StateType, MoveType, PhysicsType, PosType, AssertType, SpaceType, TransType
)
from mdk.stdlib import (
    SprPriority, Turn, Explod, VelSet, PosSet, ChangeState, AssertSpecial, ChangeAnim, PlaySnd,
    EnvShake, ModifyExplod, BGPalFX, AllPalFX, PlayerPush, StateTypeSet, VelAdd,
    Facing, Pos, Anim, RoundState, AnimTime, Random, NumExplod, AnimElemTime, GameTime, Cond, Vel,
    FrontEdgeDist, Const, Sin, Cos, StateType as ST, AnimElemNo, Floor,
    enemy
)

from .includes.variables import (
    SavedState, 
    TrackedTime, # type: ignore
    ImageRepro_HasRunIntro, ImageRepro_MotionState, ImageRepro_LastSelection
)
from .includes.types import ImageReproActionType
from .includes.constants import IMAGEREPRO_HELPER_ID, PAUSETIME_MAX
from .includes.shared import SendToDevilsEye, RandRange, RandPick, InRange

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

@statefunc
def SpawnEnergyAnim(scale: VariableExpression, pos: TupleExpression, postype: ConvertibleExpression):
    """
    Spawns some Explods with anims 30020 and 30021; these are used in several attacks in the same way.

    Pos and PosType are modifiable if needed.
    """
    for _ in range(2):
        scale.set(Random % 360)
        for idx in range(2):
            Explod(
                anim = 30020 + idx,
                postype = postype,
                pos = pos,
                vel = (15 * Cos(scale), 15 * Sin(scale)),
                scale = (0.35 - 0.1 * idx, 0.35 - 0.1 * idx),
                ontop = True,
                ownpal = True,
                pausemovetime = PAUSETIME_MAX,
                supermovetime = PAUSETIME_MAX
            )


@statedef(stateno = IMAGEREPRO_HELPER_ID, scope = SCOPE_HELPER(IMAGEREPRO_HELPER_ID), type = StateType.S, movetype = MoveType.I, physics = PhysicsType.U)
def ImageRepro_Base():
    """
    Base state for the ImageRepro helper. From here it will decide which action it wants to display.
    """
    SendToDevilsEye()

    local_selectAttackState = IntVar()

    SprPriority(value = 100)
    if (Facing == 1 and enemy.Pos.x < Pos.x) or (Facing == -1 and enemy.Pos.x > Pos.x):
        Turn()

    if ImageRepro_MotionState != ImageReproActionType.Attacking:
        VelSet(y = 0)
        PosSet(y = 0)

    if not ImageRepro_HasRunIntro:
        ResetTimeAndSetState(ImageRepro_IntroIdle)
        ImageRepro_HasRunIntro.set(True)

    ## select a move to use.
    if RoundState == 2:
        ## if we are currently idle, she should dash towards the enemy before making any action
        if ImageRepro_MotionState == ImageReproActionType.Idle:
            ResetTimeAndSetState(ImageRepro_DashToEnemy)
            ImageRepro_MotionState.set(ImageReproActionType.DashForward)

        ## if we have just finished dashing, we should go to an attack state;
        ## attack states will carry her out of range and she will try to dash again on completion.
        if ImageRepro_MotionState == ImageReproActionType.DashFinished:
            local_selectAttackState.set(Random)
            ## make sure we always pick a new move
            if Floor(local_selectAttackState / 120) == ImageRepro_LastSelection:
                local_selectAttackState.set((local_selectAttackState + 120) % 1000)
            ImageRepro_LastSelection.set(Floor(local_selectAttackState / 120))
            if InRange(local_selectAttackState, 0, 120):
                ResetTimeAndSetState(ImageRepro_Attack_SlashDash)
            if InRange(local_selectAttackState, 120, 240):
                ResetTimeAndSetState(ImageRepro_Attack_JumpSuper)
            if InRange(local_selectAttackState, 240, 360):
                ResetTimeAndSetState(ImageRepro_Attack_SlamFloor)
            if InRange(local_selectAttackState, 360, 480):
                ResetTimeAndSetState(ImageRepro_Attack_ThrowSpikes)
            if InRange(local_selectAttackState, 480, 600):
                ResetTimeAndSetState(ImageRepro_Attack_SlashDash)
            if InRange(local_selectAttackState, 600, 720):
                ResetTimeAndSetState(ImageRepro_Attack_SlashDash)
            if InRange(local_selectAttackState, 720, 840):
                ResetTimeAndSetState(ImageRepro_Attack_SlashDash)
            if local_selectAttackState >= 840:
                ResetTimeAndSetState(ImageRepro_Attack_SlashDash)
            ImageRepro_MotionState.set(ImageReproActionType.Attacking)
    
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

    if AnimTime == 0 and (ImageRepro_MotionState := ImageReproActionType.DashFinished): 
        ResetTimeAndSetState(ImageRepro_Base)

@statedef(scope = SCOPE_HELPER(IMAGEREPRO_HELPER_ID), type = StateType.S, movetype = MoveType.I, physics = PhysicsType.S)
def ImageRepro_Attack_SlashDash():
    """
    
    """
    SendToDevilsEye()

    EXPLOSION_FX_ID = 32072
    local_velScale = FloatVar()

    PlayerPush(value = False)
    if Anim != 3500: ChangeAnim(value = 3500)
    if TrackedTime == 0:
        PlaySnd(value = (10, 32), freqmul = 1)
        PlaySnd(value = (2300, 0), freqmul = 1)
        EnvShake(time = 20, ampl = 10)
        Explod(
            id = EXPLOSION_FX_ID, 
            anim = EXPLOSION_FX_ID, 
            ownpal = True, 
            removetime = 15, 
            pausemovetime = PAUSETIME_MAX, 
            supermovetime = PAUSETIME_MAX
        )

    if NumExplod(EXPLOSION_FX_ID) and TrackedTime <= 15:
        scale = 0.5 + (0.12 * TrackedTime)
        ModifyExplod(
            id = EXPLOSION_FX_ID,
            scale = (scale, scale),
            trans = TransType.addalpha,
            alpha = (255 - 16 * (TrackedTime - 15), 255)
        )

    ## background flashes
    BGPalFX(add = (-128, -128, -128), time = 2)
    if InRange(TrackedTime, 30, 33):
        color = 255 - (25 * (TrackedTime - 30))
        AllPalFX(add = (color, color, color), time = 2)

    if TrackedTime == 30:
        EnvShake(time = 30, freq = 120, ampl = 20)

    if InRange(TrackedTime, 0, 31):
        VelSet(x = 3)

    ## burst explosion behind the player and the enemy
    if AnimElemTime(7) == 0:
        for idx in range(2):
            scale = 400 if idx == 0 else Const("size.xscale")
            Explod(
                anim = 3004 + idx * 2,
                id = 3004 + idx * 2,
                pos = (0, 0),
                postype = PosType.P2 if idx == 0 else PosType.P1,
                facing = 1,
                bindtime = 1,
                removetime = -2,
                scale = (scale, scale),
                sprpriority = 4,
                removeongethit = True,
                ontop = True if idx == 0 else False,
                ownpal = False
            )
            
    if TrackedTime == 32:
        VelSet(x = 14)
        for snd in [27, 30, 37, 49]:
            PlaySnd(value = (10, snd), freqmul = 0.8)
        for facing in [1, -1]:
            if Facing == facing:
                Explod(
                    anim = 31061,
                    pos = (0, 0),
                    facing = facing,
                    bindtime = -1,
                    sprpriority = 99,
                    ownpal = True,
                    postype = PosType.Right if facing == 1 else PosType.Left
                )

    if TrackedTime == 33:
        PlaySnd(value = (10, 26))

    if TrackedTime == 34:
        for anim in [30026, 30090, 30065]:
            Explod(
                anim = anim,
                postype = PosType.P2,
                pos = (0, -60),
                ownpal = True,
                ontop = False if anim == 30026 else True,
                facing = -1 if anim == 30065 else 1,
                scale = (0.6, 0.6) if anim == 30065 else (1.2, 1.2),
                sprpriority = 99
            )
        for facing in [-1, 1]:
            Explod(
                anim = 30040,
                postype = PosType.P2,
                pos = (0, -10),
                facing = facing,
                ownpal = True,
                ontop = True,
                scale = (1.3, 0.7) if facing == -1 else (1.8, 1),
                sprpriority = 99
            )
    
    if InRange(TrackedTime, 34, 38):
        SpawnEnergyAnim(local_velScale, (0, -50), PosType.P2)

    if AnimTime == 0:
        ImageRepro_MotionState.set(ImageReproActionType.Idle)
        ResetTimeAndSetState(ImageRepro_Base)

@statedef(scope = SCOPE_HELPER(IMAGEREPRO_HELPER_ID), type = StateType.U, movetype = MoveType.I, physics = PhysicsType.N)
def ImageRepro_Attack_JumpSuper():
    """
    
    """
    SendToDevilsEye()

    local_velScale = FloatVar()

    if Anim != 1200: ChangeAnim(value = 1200)
    if Pos.y >= 0: StateTypeSet(statetype = StateType.S)
    if AnimElemTime(3) >= 0: StateTypeSet(statetype = StateType.A)
    if ST == StateType.S: VelSet(x = 0, y = 0)
    if ST == StateType.A and AnimElemTime(3) == 0: VelAdd(x = 7, y = -8.5)
    if ST == StateType.A: VelAdd(y = 0.45)

    if AnimElemTime(1) == 0:
        Explod(
            anim = 30065, 
            ownpal = True,
            postype = PosType.P1,
            pos = (-75, -30),
            sprpriority = 100,
            pausemovetime = PAUSETIME_MAX,
            supermovetime = PAUSETIME_MAX
        )
        PlaySnd(value = (901, 10))

    if AnimElemTime(3) == 0:
        for snd in [29, 12, 30, 27]:
            PlaySnd(value = (10, snd))

        for scale in [(1, 1), (1.8, 0.4)]:
            Explod(
                anim = 30040,
                ownpal = True,
                postype = PosType.P1,
                vfacing = -1,
                pos = (0, 0),
                sprpriority = 10000,
                scale = scale,
                pausemovetime = PAUSETIME_MAX,
                supermovetime = PAUSETIME_MAX
            )
        
        for anim in [30026, 30025, 30024, 31064]:
            Explod(
                anim = anim,
                ownpal = True,
                ontop = True,
                postype = PosType.P2,
                pos = (0, -60),
                sprpriority = 10000,
                pausemovetime = PAUSETIME_MAX,
                supermovetime = PAUSETIME_MAX
            )

        EnvShake(time = 15, ampl = 12)

    if AnimElemTime(3) < 0 and (GameTime % 2) == 0:
        Explod(
            anim = 30054,
            ownpal = True,
            postype = PosType.P1,
            pos = (-75, -30),
            random = (50, 10),
            sprpriority = 100,
            pausemovetime = PAUSETIME_MAX,
            supermovetime = PAUSETIME_MAX
        )

    if AnimElemTime(6) == 0:
        Explod(
            anim = 30038,
            ownpal = True,
            vfacing = -1,
            postype = PosType.P1,
            pos = (0, -60),
            sprpriority = 100,
            pausemovetime = PAUSETIME_MAX,
            supermovetime = PAUSETIME_MAX
        )

    if InRange(AnimElemTime(3), 1, 5):
        SpawnEnergyAnim(local_velScale, (0, -50), PosType.P2)

    ## this is an extra check to make sure we don't fall through floor
    if (Pos.y + Vel.y) >= 0: 
        VelSet(x = 0, y = 0)
        StateTypeSet(statetype = StateType.S)

    if AnimTime == 0:
        ImageRepro_MotionState.set(ImageReproActionType.Idle)
        ResetTimeAndSetState(ImageRepro_Base)

@statedef(scope = SCOPE_HELPER(IMAGEREPRO_HELPER_ID), type = StateType.A, movetype = MoveType.I, physics = PhysicsType.N)
def ImageRepro_Attack_SlamFloor():
    """
    
    """
    SendToDevilsEye()

    local_velScale = FloatVar()

    if Anim != 1500: ChangeAnim(value = 1500)
    if AnimElemTime(4) == 0: VelSet(x = 11.5, y = -18.5)

    if AnimElemNo(0) >= 4 and Pos.y < 0: VelAdd(y = 2)

    if (Pos.y + Vel.y) >= 0: VelSet(x = 0, y = 0)

    if AnimElemTime(4) == 0:
        for anim in [31064, 30095]:
            Explod(
                anim = anim,
                postype = PosType.P1,
                pos = (0, 0),
                facing = 1,
                sprpriority = 1300,
                ownpal = True,
                pausemovetime = PAUSETIME_MAX,
                supermovetime = PAUSETIME_MAX
            )
        EnvShake(time = 10, ampl = 12)

    if AnimElemTime(4) == 3:
        Explod(
            anim = 30095,
            postype = PosType.P1,
            pos = (0, 0),
            facing = 1,
            sprpriority = 1300,
            ownpal = True,
            scale = (1.5, 1),
            pausemovetime = PAUSETIME_MAX,
            supermovetime = PAUSETIME_MAX
        )

    if InRange(AnimElemTime(4), 1, 5):
        SpawnEnergyAnim(local_velScale, pos = (0, 0), postype = PosType.P1)

    if AnimElemTime(4) == 0 or AnimElemTime(4) == 10 or AnimElemTime(4) == 15 or AnimElemTime(4) == 20:
        Explod(
            anim = 30101, 
            postype = PosType.P2,
            pos = (0, -60),
            facing = 1,
            bindtime = 1,
            scale = (0.5, 0.5),
            ownpal = True,
            sprpriority = 10000,
            pausemovetime = PAUSETIME_MAX,
            supermovetime = PAUSETIME_MAX
        )
        PlaySnd(value = (10, 50))
        PlaySnd(value = (10, 49))
        EnvShake(time = 6, ampl = 5)

    if AnimTime == 0:
        ImageRepro_MotionState.set(ImageReproActionType.Idle)
        ResetTimeAndSetState(ImageRepro_Base)

@statefunc
def ImageRepro_Attack_ThrowSpikes_SpikeDisplay(index: int):
    """
    Helper function for the ThrowSpikes attack, replacing a group of actual Helpers which we want to eliminate.
    """
    basepos_x = 80 + 45 * index ## each explod under the Helper should be offset by this.

    Explod(
        anim = 2202,
        pos = (basepos_x, 0),
        postype = PosType.P1,
        ownpal = True,
        sprpriority = 3,
        scale = (0.3, 0.3),
        pausemovetime = PAUSETIME_MAX,
        supermovetime = PAUSETIME_MAX
    )

    PlaySnd(value = ("S255", 1))
    Explod(
        anim = 2205,
        pos = (basepos_x - 30, 0),
        postype = PosType.P1,
        facing = 1,
        bindtime = 1,
        removetime = -2,
        scale = (0.425, 0.8),
        sprpriority = 5,
        ownpal = False,
        removeongethit = False,
        pausemovetime = PAUSETIME_MAX,
        supermovetime = PAUSETIME_MAX
    )

    for facing in [1, -1]:
        Explod(
            anim = 12640,
            pos = (basepos_x + 30, 0),
            postype = PosType.P1,
            facing = facing,
            bindtime = 1,
            removetime = -2,
            sprpriority = 3,
            scale = (0.5, 0.5),
            ownpal = True,
            removeongethit = False,
            pausemovetime = PAUSETIME_MAX,
            supermovetime = PAUSETIME_MAX
        )

    Explod(
        anim = 3005,
        pos = (basepos_x, 0),
        postype = PosType.P1,
        facing = 1,
        bindtime = 1,
        removetime = -2,
        scale = (0.35, 0.35),
        sprpriority = -3,
        ontop = False,
        ownpal = True,
        pausemovetime = PAUSETIME_MAX,
        supermovetime = PAUSETIME_MAX
    )

    Explod(
        anim = 10042,
        pos = (basepos_x, 0),
        postype = PosType.P1,
        removetime = -2,
        scale = (0.25, 0.25),
        sprpriority = 0,
        ontop = False,
        ownpal = True,
        pausemovetime = PAUSETIME_MAX,
        supermovetime = PAUSETIME_MAX
    )

    for subidx in range(2):
        Explod(
            anim = 30035 + subidx,
            facing = -1,
            pos = (10, -80),
            postype = PosType.P2,
            vel = (-3, 0),
            scale = (0.75 + 0.1 * subidx, 0.75 + 0.1 * subidx),
            ontop = True,
            ownpal = True,
            pausemovetime = PAUSETIME_MAX,
            supermovetime = PAUSETIME_MAX
        )
    

@statedef(scope = SCOPE_HELPER(IMAGEREPRO_HELPER_ID), type = StateType.S, movetype = MoveType.I, physics = PhysicsType.S)
def ImageRepro_Attack_ThrowSpikes():
    """
    
    """
    SendToDevilsEye()

    if Anim != 2200: ChangeAnim(value = 2200)
    if AnimElemTime(6) == 0: VelSet(x = -8.5)

    ## TODO: this spawns 7 Helpers with ID 12200, I need to convert these into Explods if possible.
    for index in range(7):
        if AnimElemTime(8) == 3 * index:
            ImageRepro_Attack_ThrowSpikes_SpikeDisplay(index)

    if AnimElemTime(8) == 0:
        Explod(
            anim = 1001,
            postype = PosType.P1,
            pos = (0, 0),
            facing = 1,
            sprpriority = 1300,
            scale = (0.3, 0.3),
            ownpal = True
        )

    if AnimTime == 0:
        ImageRepro_MotionState.set(ImageReproActionType.Idle)
        ResetTimeAndSetState(ImageRepro_Base)