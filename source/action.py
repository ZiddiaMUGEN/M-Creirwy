from mdk.compiler import statedef, statefunc, ControllerProps
from mdk.stdlib import (
    Null, Helper, NumHelper, IsHelper, PlayerPush, ScreenBound, RoundState, 
    AfterImage, SelfState, VarSet, AssertSpecial, TargetDrop, NotHitBy,
    DestroySelf
)
from mdk.types import HelperType, AssertType, HitType, HitAttr

from .includes.constants import IMAGEREPRO_HELPER_ID, IMAGEREPRO_HELPER_STATE, PAUSETIME_MAX
from .includes.variables import TrackedTime, SavedState
from .includes.shared import SelfState_TimeIncrease

@statedef(stateno = -2)
def Think():
    """
    Essentially the entry point for P1-sided work, all helpers are spawned and dispatched from here.
    """
    with ControllerProps(ignorehitpause = True, persistent = 256):
        Think_SpawnBaseHelpers()
        Think_Root()
        Think_ImageRepro()

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
    Spawns base (i.e. non-crosstalk, non-occupancy) helpers.
    Crosstalk is handled separately.
    """
    if NumHelper(IMAGEREPRO_HELPER_ID) == 0:
        Helper(
            helpertype = HelperType.Player,
            name = "Image Reproduction",
            id = IMAGEREPRO_HELPER_ID,
            stateno = IMAGEREPRO_HELPER_STATE,
            supermovetime = PAUSETIME_MAX,
            pausemovetime = PAUSETIME_MAX
        )

@statefunc
def Think_Root():
    """
    Functions for the root which need to run on every frame.
    """
    if not IsHelper():
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
    if IsHelper(IMAGEREPRO_HELPER_ID):
        PlayerPush(value = False)
        ScreenBound(value = True, movecamera = (True, True))
        if RoundState < 2: AfterImage(time = -1, length = 8, framegap = 2)

        SelfState_TimeIncrease(IMAGEREPRO_HELPER_STATE)