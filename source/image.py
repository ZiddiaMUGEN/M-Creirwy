### States for ImageRepro helper.
### This helper provides visuals for the character (while the root does more interesting things).
from mdk.compiler import statedef, statefunc
from mdk.types import (
    SCOPE_HELPER, ConvertibleExpression, VariableExpression, TupleExpression,
    BoolVar, IntVar, FloatVar, ByteVar,
    StateType, MoveType, PhysicsType, PosType, AssertType, SpaceType, TransType,
    HelperType
)
from mdk.stdlib import (
    SprPriority, Turn, Explod, VelSet, PosSet, ChangeState, AssertSpecial, ChangeAnim, PlaySnd,
    EnvShake, ModifyExplod, BGPalFX, AllPalFX, PlayerPush, StateTypeSet, VelAdd, EnvColor, PalFX,
    ScreenBound, RemoveExplod, Trans, Helper, AngleDraw, DestroySelf,
    Facing, Pos, Anim, RoundState, AnimTime, Random, NumExplod, AnimElemTime, GameTime, Cond, Vel,
    FrontEdgeDist, Const, Sin, Cos, StateType as ST, AnimElemNo, Floor, BackEdgeBodyDist,
    enemy
)

from .includes.variables import (
    SavedState, 
    TrackedTime, # type: ignore
    ImageRepro_HasRunIntro, ImageRepro_MotionState, ImageRepro_LastSelection
)
from .includes.types import ImageReproActionType
from .includes.constants import IMAGEREPRO_HELPER_ID, MOONJUMP_HELPER_ID, PAUSETIME_MAX
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
                ResetTimeAndSetState(ImageRepro_Attack_MoonJump)
            if InRange(local_selectAttackState, 600, 720):
                ResetTimeAndSetState(ImageRepro_Attack_SlashDash)
            if InRange(local_selectAttackState, 720, 840):
                ResetTimeAndSetState(ImageRepro_Attack_SlashDash)
            if local_selectAttackState >= 840:
                ResetTimeAndSetState(ImageRepro_Attack_SlashDash)
            ImageRepro_MotionState.set(ImageReproActionType.Attacking)

    for index in [13020, 13021, 13022, 13023, 13024]:
        if SavedState != ImageRepro_MoonJump_CrossMoon and NumExplod(index):
            RemoveExplod(id = index)
    
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

@statedef(scope = SCOPE_HELPER(IMAGEREPRO_HELPER_ID), type = StateType.S, movetype = MoveType.I, physics = PhysicsType.S)
def ImageRepro_Attack_MoonJump():
    """
    
    """
    SendToDevilsEye()

    if Anim != 3000: ChangeAnim(value = 3000)
    if Anim == 3000: VelSet(x = 0, y = 0)
    if InRange(AnimElemTime(1), 0, 11): VelSet(x = -(BackEdgeBodyDist - 120) / 2.5)

    if AnimElemTime(4) == 0:
        Explod(
            anim = 30051,
            ontop = True,
            postype = PosType.Back,
            scale = (2, 2),
            trans = TransType.add,
            pausemovetime = PAUSETIME_MAX,
            supermovetime = PAUSETIME_MAX
        )

        Explod(
            anim = 30048,
            ontop = True,
            postype = PosType.Left,
            scale = (0.5, 0.5),
            trans = TransType.add,
            pausemovetime = PAUSETIME_MAX,
            supermovetime = PAUSETIME_MAX
        )

        PlaySnd(value = (10, 32))
        PlaySnd(value = (2400, 0))


    if AnimElemTime(4) > 0:
        BGPalFX(time = 1, add = (-128, -128, -128))

    if AnimElemTime(14) == 0:
        PlaySnd(value = (255, 1))

    if AnimElemTime(15) == 0:
        EnvShake(time = 20, ampl = 15)
        Explod(
            anim = 30040,
            ontop = True,
            facing = -1,
            postype = PosType.P1,
            scale = (3, 3),
            pausemovetime = PAUSETIME_MAX,
            supermovetime = PAUSETIME_MAX
        )

    if AnimElemTime(17) == 0:
        EnvColor(time = 4, value = (0, 0, 255))
        Explod(
            anim = 30032,
            facing = -1,
            postype = PosType.P2,
            pos = (0, -60),
            ontop = True,
            ownpal = True,
            scale = (0.8, 0.8),
            pausemovetime = PAUSETIME_MAX,
            supermovetime = PAUSETIME_MAX
        )
        for idx in range(2):
            Explod(
                anim = 30045 + idx * 2,
                facing = -1,
                postype = PosType.P2,
                pos = (0, -70),
                ontop = True,
                ownpal = True,
                scale = (1.2 + 0.1 * idx, 1.2 + 0.1 * idx),
                pausemovetime = PAUSETIME_MAX,
                supermovetime = PAUSETIME_MAX
            )
        PlaySnd(value = (10, 30), freqmul = 1.2)
        ## this Explod was previously a Helper as `angle` did not exist pre-1.1.
        Explod(
            anim = 3010,
            pos = (70, 50),
            postype = PosType.P1,
            ownpal = True,
            sprpriority = 300,
            scale = (0.38, 0.38),
            angle = 33,
            pausemovetime = PAUSETIME_MAX,
            supermovetime = PAUSETIME_MAX
        )

    if AnimTime == 0:
        #ImageRepro_MotionState.set(ImageReproActionType.Idle)
        ResetTimeAndChangeState(ImageRepro_MoonJump_CrossMoon)

@statefunc
def ImageRepro_MoonJump_DashFrames(id: int, postype: ConvertibleExpression, basepos: tuple[int, int]):
    angle = -45
    vel = (32, 8)
    if id in [13002, 13004]: 
        angle = -170
        vel = (-6, 24)
    if id == 13003: 
        angle = -30
        vel = (18, -8)
    if id == 13005: 
        angle = 35
        vel = (15, -10)

    Explod(
        anim = 3011 + (3 if id == 13001 else 0) + (4 if id in [13002, 13004] else 0) + (1 if id == 13005 else 0),
        ownpal = True,
        postype = postype,
        pos = basepos,
        sprpriority = 300000,
        vel = vel,
        angle = angle,
        facing = -1 if id == 13004 else 1,
        scale = (0.5, 0.5),
        pausemovetime = PAUSETIME_MAX,
        supermovetime = PAUSETIME_MAX
    )

    EnvShake(time = 15, ampl = 10)
    Explod(
        anim = 30056,
        pos = basepos,
        postype = postype,
        random = (50, 50),
        bindtime = 1,
        scale = (0.75, 0.75),
        ontop = True,
        facing = -1 if id == 13004 else 1,
        pausemovetime = PAUSETIME_MAX,
        supermovetime = PAUSETIME_MAX
    )
    PlaySnd(value = (3100, 4))
    PlaySnd(value = (255, 1))

    Explod(
        anim = 30032,
        ownpal = True,
        postype = PosType.P2,
        pos = (10, -80 + (60 if id == 13003 else 0)),
        vel = (-3, 0),
        scale = (0.55, 0.55),
        ontop = True,
        pausemovetime = PAUSETIME_MAX,
        supermovetime = PAUSETIME_MAX
    )
    Explod(
        anim = 30035,
        ownpal = True,
        facing = -1,
        postype = PosType.P2,
        pos = (10, -80 + (60 if id == 13003 else 0)),
        scale = (1.5, 1.5),
        ontop = True,
        pausemovetime = PAUSETIME_MAX,
        supermovetime = PAUSETIME_MAX
    )
    Explod(
        anim = 30036,
        ownpal = True,
        facing = -1,
        postype = PosType.P2,
        pos = (10, -80 + (60 if id == 13003 else 0)),
        scale = (1.125, 1.125),
        trans = TransType.sub,
        ontop = True,
        pausemovetime = PAUSETIME_MAX,
        supermovetime = PAUSETIME_MAX
    )

    PlaySnd(value = (10, 30))

@statefunc
def ImageRepro_MoonJump_Trails(id: int, postype: ConvertibleExpression, basepos: tuple[int, int]):
    anim = 3002
    if (id % 2) == 0: anim = 3111

    if id == 13051:
        scale = (0.75, 0.75)
        angle = -105
    elif id in [13053, 13057]:
        scale = (0.75, 0.75)
        angle = 20
    elif id == 13055:
        scale = (0.75, 0.75)
        angle = 20
    elif id == 13059:
        scale = (0.75, 0.75)
        angle = 40
    elif id == 13052:
        scale = (0.3, 2)
        angle = -112
    elif id in [13054, 13058]:
        scale = (0.3, 4)
        angle = -15
    elif id == 13056:
        scale = (0.3, 4)
        angle = -70
    elif id == 13060:
        scale = (0.3, 4)
        angle = -50
    
    Explod(
        anim = anim,
        ownpal = True,
        postype = postype,
        pos = basepos,
        sprpriority = 300000,
        facing = -1 if id in [13055, 13056, 13057, 13058] else 1,
        scale = scale,
        angle = angle,
        trans = TransType.add,
        pausemovetime = PAUSETIME_MAX,
        supermovetime = PAUSETIME_MAX
    )

@statefunc
def ImageRepro_MoonJump_BackgroundAnim(id: int, basepos: tuple[int, int]):
    if id == 13020: 
        anim = 3018
        angle = 180
        scale = (0.25, 0.25)
    if id == 13021:
        anim = 3020
        angle = 82
        scale = (0.25, 0.25)
    if id == 13022:
        anim = 3020
        angle = 126
        scale = (0.325, 0.325)
    if id == 13023:
        anim = 3021
        angle = -75
        scale = (0.25, 0.25)
    if id == 13024:
        anim = 3017
        angle = -70
        scale = (0.325, 0.325)
    Explod(
        id = id,
        anim = anim,
        ownpal = True,
        pos = basepos,
        postype = PosType.P1,
        angle = angle,
        scale = scale,
        trans = TransType.add
    )

@statefunc
def ImageRepro_MoonHelper_Flames(pos: ConvertibleExpression):
    Explod(
        anim = 30054,
        ownpal = True,
        postype = PosType.P1,
        pos = pos,
        scale = (1.2, 1.2),
        trans = TransType.add,
        vel = (0, -1),
        sprpriority = 5,
        pausemovetime = PAUSETIME_MAX,
        supermovetime = PAUSETIME_MAX
    )

@statedef(stateno = MOONJUMP_HELPER_ID, scope = SCOPE_HELPER(MOONJUMP_HELPER_ID), type = StateType.A, movetype = MoveType.I, physics = PhysicsType.N, sprpriority = PAUSETIME_MAX - 1)
def ImageRepro_MoonJump_MoonHelper():
    if Anim != 3016: ChangeAnim(value = 3016)
    if AnimElemTime(1) == 0:
        VelSet(x = 0, y = 1)
    if InRange(AnimElemTime(1) == 0, 0, 13):
        VelAdd(y = 0.08)
    if AnimElemTime(5) == 0:
        VelAdd(x = 7, y = -23)
        Explod(
            anim = 1551,
            ownpal = True,
            postype = PosType.P1,
            scale = (0.75, 0.75),
            pausemovetime = PAUSETIME_MAX,
            supermovetime = PAUSETIME_MAX
        )
    if InRange(AnimElemTime(5), 0, 21):
        AngleDraw(value = 35)

    if AnimElemTime(1) == 0: ImageRepro_MoonHelper_Flames((20, -105))
    if AnimElemTime(1) == 2: ImageRepro_MoonHelper_Flames((0, -125))
    if AnimElemTime(1) == 4: ImageRepro_MoonHelper_Flames((20, -105))
    if AnimElemTime(1) == 6: ImageRepro_MoonHelper_Flames((-20, -85))
    if AnimElemTime(1) == 8: ImageRepro_MoonHelper_Flames((-20, -55))

    if AnimElemTime(5) == 5:
        Explod(
            id = 30057,
            anim = 30057,
            postype = PosType.Left,
            ownpal = True,
            bindtime = -1,
            sprpriority = PAUSETIME_MAX - 2,
            pausemovetime = PAUSETIME_MAX,
            supermovetime = PAUSETIME_MAX
        )
    if AnimElemTime(5) >= 5 and NumExplod(30057):
        alpha = Cond(AnimElemTime(5) <= 15, 255 - 25 * (AnimElemTime(5) - 5), 0)
        prio = (PAUSETIME_MAX - 3) + Cond(AnimElemTime(5) <= 50, 3, 0)
        ModifyExplod(
            id = 30057,
            trans = TransType.addalpha,
            alpha = (255, alpha),
            sprpriority = prio
        )
    if AnimTime == 0: RemoveExplod(id = 30057)
    if AnimElemTime(5) == 0: PlaySnd(value = (41, 10), freqmul = 0.5)

    if AnimElemTime(6) == 0:
        PosSet(x = -(Facing * 120), y = -20)
        VelSet(x = 1, y = -0.5)

        Explod(
            id = 30059,
            anim = 30059,
            scale = (0.35, 0.35),
            postype = PosType.Back,
            pos = (120, 100),
            bindtime = -1,
            vel = (0.5, 0),
            ownpal = True,
            sprpriority = PAUSETIME_MAX - 2,
            pausemovetime = PAUSETIME_MAX,
            supermovetime = PAUSETIME_MAX
        )
        Explod(
            id = 30058,
            anim = 30058,
            scale = (0.35, 0.35),
            postype = PosType.Back,
            pos = (120, 100),
            bindtime = -1,
            vel = (0.5, 0),
            ownpal = True,
            sprpriority = PAUSETIME_MAX - 2,
            pausemovetime = PAUSETIME_MAX,
            supermovetime = PAUSETIME_MAX
        )

        PlaySnd(value = (2100, 0), abspan = False)

    if InRange(AnimElemTime(6), 0, 121):
        VelAdd(y = 0.005)
        PalFX(add = (-255, -255, -255), time = 1)
        AngleDraw(value = 130, scale = (0.65, 0.65))

    if AnimElemTime(6) == 0 and Facing == 1:
        Explod(
            anim = 30060,
            postype = PosType.Right,
            facing = -1,
            scale = (0, 1.3),
            bindtime = -1,
            trans = TransType.add,
            ownpal = True,
            sprpriority = PAUSETIME_MAX - 2,
            pausemovetime = PAUSETIME_MAX,
            supermovetime = PAUSETIME_MAX
        )

    if AnimElemTime(6) == 0 and Facing == -1:
        Explod(
            anim = 30060,
            postype = PosType.Left,
            facing = 1,
            scale = (0, 1.3),
            bindtime = -1,
            trans = TransType.add,
            ownpal = True,
            sprpriority = PAUSETIME_MAX - 2,
            pausemovetime = PAUSETIME_MAX,
            supermovetime = PAUSETIME_MAX
        )

    if AnimElemTime(6) == 30 and Facing == 1:
        Explod(
            anim = 30061,
            postype = PosType.Right,
            facing = 1,
            bindtime = -1,
            trans = TransType.add,
            ownpal = True,
            ontop = True,
            scale = (0.5, 0.5),
            sprpriority = PAUSETIME_MAX,
            pausemovetime = PAUSETIME_MAX,
            supermovetime = PAUSETIME_MAX
        )

    if AnimElemTime(6) == 30 and Facing == -1:
        Explod(
            anim = 30061,
            postype = PosType.Left,
            facing = -1,
            bindtime = -1,
            trans = TransType.add,
            ownpal = True,
            scale = (0.5, 0.5),
            sprpriority = PAUSETIME_MAX,
            pausemovetime = PAUSETIME_MAX,
            supermovetime = PAUSETIME_MAX
        )

    if AnimElemTime(6) == 40:
        Explod(
            anim = 30051,
            postype = PosType.P1,
            scale = (1, 1),
            trans = TransType.add,
            ownpal = True,
            sprpriority = PAUSETIME_MAX - 2,
            pausemovetime = PAUSETIME_MAX,
            supermovetime = PAUSETIME_MAX
        )

    if InRange(AnimElemTime(6), 60, 71):
        color = 25 * (AnimElemTime(6) - 40)
        EnvColor(time = 1, value = (color, color, color))
    
    if InRange(AnimElemTime(6), 0, 11):
        color = 255 - 25 * AnimElemTime(6)
        AllPalFX(time = 1, value = (color, color, color))

    if AnimElemTime(6) > 70:
        EnvColor(time = 1, color = (255, 255, 255))

    if AnimTime == 0:
        RemoveExplod(id = 30058)
        RemoveExplod(id = 30059)
        DestroySelf()

@statedef(scope = SCOPE_HELPER(IMAGEREPRO_HELPER_ID), type = StateType.S, movetype = MoveType.I, physics = PhysicsType.S)
def ImageRepro_MoonJump_CrossMoon():
    """
    
    """
    SendToDevilsEye()

    local_xOffset = IntVar()
    local_yOffset = IntVar()
    local_scale = FloatVar()

    if Anim != 3001: ChangeAnim(value = 3001)
    if AnimElemTime(47) < 208: BGPalFX(time = 1, add = (-128, -128, -128))

    if AnimElemTime(13) == 0:
        PlaySnd(value = (3100, 0))
        Explod(
            anim = 30051,
            ontop = True,
            ownpal = True,
            postype = PosType.P1,
            pos = (100, -100),
            scale = (2, 2),
            trans = TransType.add,
            pausemovetime = PAUSETIME_MAX,
            supermovetime = PAUSETIME_MAX
        )

    if InRange(AnimElemTime(13), 0, 91) and (GameTime % 10) == 0:
        Explod(
            anim = 30054,
            ownpal = True,
            postype = PosType.P1,
            pos = (85, -95),
            random = (20, 20),
            scale = (1.2, 1.2),
            trans = TransType.add,
            vel = (0, -1),
            sprpriority = -5,
            pausemovetime = PAUSETIME_MAX,
            supermovetime = PAUSETIME_MAX
        )

    if InRange(AnimElemTime(13), 0, 91) and (GameTime % 5) == 0:
        for idx in range(2):
            pos = (75, -75) if idx == 0 else (115, -125)
            scale = (0.6, 0.6) if idx == 0 else (1.2, 1.2)
            Explod(
                anim = 30054,
                ownpal = True,
                postype = PosType.P1,
                pos = pos,
                random = (20, 20),
                scale = scale,
                trans = TransType.add,
                vel = (0, -1),
                sprpriority = -5,
                pausemovetime = PAUSETIME_MAX,
                supermovetime = PAUSETIME_MAX
            )
        for pos in [(110, -120), (90, -95), (80, -80)]:
            Explod(
                anim = 30055,
                ownpal = True,
                postype = PosType.P1,
                pos = pos,
                random = (8, 8),
                scale = (0.5, 0.5),
                trans = TransType.add,
                vel = (0, -1),
                sprpriority = -4,
                pausemovetime = PAUSETIME_MAX,
                supermovetime = PAUSETIME_MAX
            )
    
    if InRange(AnimElemTime(38), 0, 19):
        color = 14 * AnimElemTime(38)
        PalFX(add = (color, color, color), time = 1)

    if AnimElemTime(38) > 18 and AnimElemTime(46) < 0:
        PalFX(add = (255, 255, 255), time = 1)

    ## 3x helper
    ### 13101, 13102, 13102
    if AnimElemTime(44) == 4 or AnimElemTime(46) == 64: ImageRepro_MoonJump_DashFrames(13001, PosType.Back, (20, -60))
    if AnimElemTime(44) == 1 or AnimElemTime(46) == 61: ImageRepro_MoonJump_Trails(13051, PosType.Back, (10, -120))
    if AnimElemTime(44) == 4 or AnimElemTime(46) == 64: ImageRepro_MoonJump_Trails(13052, PosType.Back, (90, -90))

    if AnimElemTime(44) >= 0: ScreenBound(value = False, movecamera = (False, False))

    if AnimElemTime(13) == 0:
        Explod(
            id = 30049,
            anim = 30049,
            sprpriority = 30,
            postype = PosType.P1,
            pos = (40, 0),
            scale = (1.5, 0.5),
            ownpal = True,
            removetime = -1,
            bindtime = -1,
            pausemovetime = PAUSETIME_MAX,
            supermovetime = PAUSETIME_MAX
        )
    if NumExplod(30049) and AnimElemTime(44) == 0: RemoveExplod(id = 30049)

    if AnimElemTime(44) == 0: VelSet(x = 30, y = -25)

    if InRange(AnimElemTime(44), 0, 7): Trans(trans = TransType.addalpha, alpha = (255 - 40 * AnimElemTime(44), 255))
    if AnimElemTime(46) >= 0 and AnimElemTime(47) < 0: PosSet(x = 0, y = 0)

    ## 13x Helper
    if AnimElemTime(46) == 5 or AnimElemTime(46) == 38 or AnimElemTime(46) == 54:
        pos_x = 30 + Cond(AnimElemTime(46) == 38, 50, 0) + Cond(AnimElemTime(46) == 54, -110, 0)
        ImageRepro_MoonJump_DashFrames(13002, PosType.P1, (pos_x, -240))
    if AnimElemTime(46) == 2 or AnimElemTime(46) == 35 or AnimElemTime(46) == 51:
        pos_x = 30 + Cond(AnimElemTime(46) == 35, 50, 0) + Cond(AnimElemTime(46) == 51, -110, 0)
        ImageRepro_MoonJump_Trails(13053, PosType.P1, (pos_x, -180))
    if AnimElemTime(46) == 5 or AnimElemTime(46) == 38 or AnimElemTime(46) == 54:
        pos_x = 50 + Cond(AnimElemTime(46) == 38, 50, 0) + Cond(AnimElemTime(46) == 54, -110, 0)
        ImageRepro_MoonJump_Trails(13054, PosType.P1, (pos_x, -240))
    if AnimElemTime(46) == 12 or AnimElemTime(46) == 46 or AnimElemTime(46) == 72 or AnimElemTime(46) == 96:
        ImageRepro_MoonJump_DashFrames(13003, PosType.P1, (120, 30 - Cond(AnimElemTime(46) == 72, 50, 0)))
    if AnimElemTime(46) == 9 or AnimElemTime(46) == 43 or AnimElemTime(46) == 69 or AnimElemTime(46) == 93:
        ImageRepro_MoonJump_Trails(13055, PosType.P1, (120, 30 - Cond(AnimElemTime(46) == 69, 50, 0)))
    if AnimElemTime(46) == 12 or AnimElemTime(46) == 46 or AnimElemTime(46) == 72 or AnimElemTime(46) == 96:
        ImageRepro_MoonJump_Trails(13056, PosType.P1, (120, 30 - Cond(AnimElemTime(46) == 72, 50, 0)))
    if AnimElemTime(46) == 23 or AnimElemTime(46) == 88:
        ImageRepro_MoonJump_DashFrames(13004, PosType.P1, (-60 + Cond(AnimElemTime(46) == 88, 120, 0), -240))
    if AnimElemTime(46) == 20 or AnimElemTime(46) == 85:
        ImageRepro_MoonJump_Trails(13057, PosType.P1, (-60 + Cond(AnimElemTime(46) == 85, 120, 0), -180))
    if AnimElemTime(46) == 23 or AnimElemTime(46) == 88:
        ImageRepro_MoonJump_Trails(13058, PosType.P1, (-80 + Cond(AnimElemTime(46) == 88, 120, 0), -240))
    if AnimElemTime(46) == 28 or AnimElemTime(46) == 80:
        ImageRepro_MoonJump_DashFrames(13005, PosType.P1, (-100, 25))
    if AnimElemTime(46) == 25 or AnimElemTime(46) == 77:
        ImageRepro_MoonJump_Trails(13059, PosType.P1, (-110, 15))
    if AnimElemTime(46) == 28 or AnimElemTime(46) == 80:
        ImageRepro_MoonJump_Trails(13060, PosType.P1, (-110, 15))

    ## this block uses a Helper, it's too complicated to convert into regular states.
    if AnimElemTime(46) == 110:
        Helper(
            id = MOONJUMP_HELPER_ID,
            stateno = ImageRepro_MoonJump_MoonHelper,
            ownpal = True,
            helpertype = HelperType.Player,
            postype = PosType.P1,
            pos = (0, -10),
            pausemovetime = PAUSETIME_MAX,
            supermovetime = PAUSETIME_MAX
        )

    if AnimElemTime(47) >= 0: PosSet(x = Facing * 120, y = 0)
    if AnimElemTime(46) >= 0: VelSet(x = 0, y = 0)

    ## 5x Helper
    if AnimElemTime(47) == 0:
        ImageRepro_MoonJump_BackgroundAnim(13020, (-20, -60))
        ImageRepro_MoonJump_BackgroundAnim(13021, (-10, -70))
        ImageRepro_MoonJump_BackgroundAnim(13022, (-30, -90))
        ImageRepro_MoonJump_BackgroundAnim(13023, (-150, -30))
        ImageRepro_MoonJump_BackgroundAnim(13024, (-150, -30))

    if AnimElemTime(47) == 0:
        Explod(
            anim = 30062,
            sprpriority = -10000,
            ownpal = True,
            bindtime = -1,
            facing = -1,
            postype = PosType.P1,
            pos = (40, 0),
            scale = (1.3, 1),
            trans = TransType.sub,
            removetime = 210,
            pausemovetime = PAUSETIME_MAX,
            supermovetime = PAUSETIME_MAX
        )
        Explod(
            anim = 30062,
            sprpriority = 10000,
            ownpal = True,
            bindtime = -1,
            facing = -1,
            postype = PosType.P1,
            pos = (40, 0),
            scale = (1.3, 1),
            trans = TransType.addalpha,
            alpha = (-128, 255),
            removetime = 210,
            pausemovetime = PAUSETIME_MAX,
            supermovetime = PAUSETIME_MAX
        )

    if AnimElemTime(47) == 180 and Facing == 1:
        Explod(
            anim = 30063,
            ontop = True,
            facing = -1,
            ownpal = True,
            bindtime = -1,
            postype = PosType.Right,
            trans = TransType.sub,
            pausemovetime = PAUSETIME_MAX,
            supermovetime = PAUSETIME_MAX
        )

    if AnimElemTime(47) == 180 and Facing == -1:
        Explod(
            anim = 30063,
            ontop = True,
            facing = 1,
            ownpal = True,
            bindtime = -1,
            postype = PosType.Left,
            trans = TransType.sub,
            pausemovetime = PAUSETIME_MAX,
            supermovetime = PAUSETIME_MAX
        )

    if AnimElemTime(47) == 208:
        Explod(
            anim = 30064,
            ontop = True,
            facing = 1,
            ownpal = True,
            scale = (0.5, 0.5),
            bindtime = -1,
            postype = PosType.Left,
            trans = TransType.add,
            pausemovetime = PAUSETIME_MAX,
            supermovetime = PAUSETIME_MAX
        )

    if InRange(AnimElemTime(47), 35, 46):
        color = 255 - 25 * (AnimElemTime(47) - 35)
        AllPalFX(add = (color, color, color), time = 1)
    
    if AnimElemTime(47) == 0: EnvShake(time = 240, ampl = 4, freq = 150)
    if AnimElemTime(47) == 208: EnvShake(time = 60, ampl = 45, freq = 130)
    if AnimElemTime(47) == 253: EnvShake(time = 30, ampl = 20, freq = 130)

    if AnimElemTime(47) == 30:
        for snd in [(10, 33), (990, 0), (10, 36)]:
            PlaySnd(value = snd, freqmul = 0.5)
    
    if AnimElemTime(47) == 208:
        for snd in [(10, 34), (10, 34), (10, 37)]:
            PlaySnd(value = snd, freqmul = 0.9)

    if InRange(AnimElemTime(47), 208, 218):
        color = 255 - 25 * (AnimElemTime(47) - 208)
        AllPalFX(add = (color, color, color), time = 1)

    ## spawn 3 batches of 2 Explods with similar behaviour, but different randomized scale + offset.
    ## these display energy balls of varying size.
    for _ in range(3):
        if InRange(AnimElemTime(47), 0, 209):
            local_xOffset.set(RandRange(-280, 40))
            local_yOffset.set(RandRange(10, 90))
            local_scale.set(RandPick(1, -1) * (0.25 + 0.01 * (Random % 5)))
            ## spawn 2 Explods based on these variables.
            for idx in range(2):
                Explod(
                    anim = 30020 + idx,
                    vel = (0, -5),
                    pos = (local_xOffset, local_yOffset),
                    ownpal = True,
                    sprpriority = Cond(local_scale < 0, -7 + idx, 6 + idx),
                    scale = (abs(local_scale), abs(local_scale)),
                    pausemovetime = PAUSETIME_MAX,
                    supermovetime = PAUSETIME_MAX
                )

    if AnimTime == 0:
        ImageRepro_MotionState.set(ImageReproActionType.Idle)
        ResetTimeAndSetState(ImageRepro_Base)