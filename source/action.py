from mdk.compiler import statedef, statefunc
from mdk.stdlib import (
    Null, Helper, NumHelper, IsHelper, PlayerPush, ScreenBound, RoundState, 
    AfterImage, SelfState, VarSet, AssertSpecial, TargetDrop, NotHitBy,
    DestroySelf,
    root
)
from mdk.types import HelperType, AssertType, HitType, HitAttr, BoolVar, SCOPE_PLAYER

from .includes.constants import (
    IMAGEREPRO_HELPER_ID, MOONJUMP_HELPER_ID,
    PAUSETIME_MAX,
    CROSSTALK_HELPER_ID, CROSSTALK_TARGET_ID, CROSSTALK_HELPER_COUNT,
    MARKING_HELPER_ID,
    OCCUPANCY_HELPER_ID,
    FIRST_HELPER_ID,
    LAST_HELPER_ID
)
from source.includes.variables import TrackedTime, SavedState, Root_CrosstalkInitialized
from source.includes.shared import SelfState_TimeIncrease, RootVarSet

from source.brain import TempPlayerState
from source.helpers.image import ImageRepro_Base, ImageRepro_MoonJump_MoonHelper
from source.helpers.crosstalk import CrossTalk_Base, CrossTalk_Target
from source.helpers.first import FirstHelper_Actions
from source.helpers.last import LastHelper_Actions
from source.helpers.marking import MarkingHelper_Actions

@statedef(stateno = -2, scope = SCOPE_PLAYER)
def Think():
    """
    Essentially the entry point for P1-sided work, all helpers are spawned and dispatched from here.
    Note this state is scoped to SCOPE_PLAYER, which is technically wrong but lets root access its variables
    cleanly.
    """
    if not IsHelper(): 
        Think_SpawnBaseHelpers()
        Think_Root()
    if IsHelper(IMAGEREPRO_HELPER_ID): Think_ImageRepro()
    if IsHelper(CROSSTALK_HELPER_ID): Think_CrossTalk()
    if IsHelper(CROSSTALK_TARGET_ID): SelfState(value = CrossTalk_Target)
    if IsHelper(MOONJUMP_HELPER_ID): SelfState(value = ImageRepro_MoonJump_MoonHelper)
    if IsHelper(FIRST_HELPER_ID): SelfState(value = FirstHelper_Actions)
    if IsHelper(LAST_HELPER_ID): SelfState(value = LastHelper_Actions)
    if IsHelper(MARKING_HELPER_ID): SelfState(value = MarkingHelper_Actions)

    ## this is a failsafe.
    ## the only way a helper ever reaches here is if I screw up,
    ## or if infiltration spawns a helper.
    if IsHelper(): DestroySelf()

@statedef(stateno = -3)
def PreThink():
    """
    -3 is not executed during custom stating, so this is only important for custom state detection.
    """
    Null()

@statedef(stateno = -1)
def Act():
    """
    Unneeded?
    """
    Null()

##########################################################################################
# just separating out some steps to make the code more readable.
# these need to use the @statefunc decorator to make sure triggers are translated.
##########################################################################################
@statefunc
def Think_SpawnBaseHelpers():
    """
    Spawns all helpers used by the root (excluding special cases like end-of-round occupancy).
    """
    if NumHelper(FIRST_HELPER_ID) == 0:
        Helper(
            helpertype = HelperType.Player,
            name = "First Action Helper",
            id = FIRST_HELPER_ID,
            stateno = FirstHelper_Actions,
            supermovetime = PAUSETIME_MAX,
            pausemovetime = PAUSETIME_MAX
        )

    if NumHelper(MARKING_HELPER_ID) == 0:
        Helper(
            helpertype = HelperType.Player,
            name = "Enemy Marking",
            id = MARKING_HELPER_ID,
            stateno = MarkingHelper_Actions,
            supermovetime = PAUSETIME_MAX,
            pausemovetime = PAUSETIME_MAX
        )

    if NumHelper(IMAGEREPRO_HELPER_ID) == 0:
        Helper(
            helpertype = HelperType.Player,
            name = "Image Reproduction",
            id = IMAGEREPRO_HELPER_ID,
            stateno = ImageRepro_Base,
            supermovetime = PAUSETIME_MAX,
            pausemovetime = PAUSETIME_MAX
        )

    ## spawn Crosstalk helpers and targets to fill Helper occupancy.
    for idx in range(CROSSTALK_HELPER_COUNT):
        if NumHelper(CROSSTALK_HELPER_ID) < CROSSTALK_HELPER_COUNT and not Root_CrosstalkInitialized:
            Helper(
                helpertype = HelperType.Player,
                name = f"Crosstalk Helper {idx + 1}",
                id = CROSSTALK_HELPER_ID,
                stateno = CrossTalk_Base,
                size_shadowoffset = idx,
                supermovetime = PAUSETIME_MAX,
                pausemovetime = PAUSETIME_MAX
            )
        if NumHelper(CROSSTALK_TARGET_ID) < CROSSTALK_HELPER_COUNT and not Root_CrosstalkInitialized:
            Helper(
                helpertype = HelperType.Player,
                name = f"Crosstalk Target {idx + 1}",
                id = CROSSTALK_TARGET_ID,
                stateno = CrossTalk_Target,
                size_shadowoffset = idx,
                supermovetime = PAUSETIME_MAX,
                pausemovetime = PAUSETIME_MAX
            )

    if NumHelper(LAST_HELPER_ID) == 0:
        Helper(
            helpertype = HelperType.Player,
            name = "Last Action Helper",
            id = LAST_HELPER_ID,
            stateno = LastHelper_Actions,
            supermovetime = PAUSETIME_MAX,
            pausemovetime = PAUSETIME_MAX
        )

@statefunc
def Think_Root():
    """
    Functions for the root which need to run on every frame.
    """
    if SavedState == 0: SavedState.set(TempPlayerState)
    TargetDrop(keepone = True) ## keep only one target, certain redirects break with multiple targets
    AssertSpecial(flag = AssertType.Invisible, flag2 = AssertType.NoShadow, flag3 = AssertType.TimerFreeze) ## display
    PlayerPush(value = False) ## uninteractable
    ScreenBound(value = False, movecamera = (False, False)) ## uninteractable
    NotHitBy(value = (HitType.SCA, HitAttr.AA, HitAttr.AP, HitAttr.AT)) ## uninteractable

    SelfState_TimeIncrease(SavedState) ## goto the saved state, and increase TrackedTime by 1 as well.

@statefunc
def Think_ImageRepro():
    """
    Responsible for spawning the ImageRepro helper and applying its assert/screenbound properties.
    """
    PlayerPush(value = False)
    ScreenBound(value = True, movecamera = (True, True))
    if RoundState < 2: AfterImage(time = -1, length = 8, framegap = 2)

    SelfState_TimeIncrease(ImageRepro_Base)

@statefunc
def Think_CrossTalk():
    """
    Responsible for dispatching CT helpers to their main state.
    """
    AssertSpecial(flag = AssertType.Invisible, flag2 = AssertType.NoShadow) ## display
    if root.Root_CrosstalkInitialized == False: RootVarSet(Root_CrosstalkInitialized, True)

    SelfState(value = CrossTalk_Base)