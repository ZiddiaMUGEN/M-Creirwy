from mdk.compiler import statedef, statefunc
from mdk.stdlib import Null, Helper, NumHelper, IsHelper, PlayerPush, ScreenBound, RoundState, AfterImage, SelfState, VarSet
from mdk.types import HelperType

from .includes.constants import IMAGEREPRO_HELPER_ID, IMAGEREPRO_HELPER_STATE, PAUSETIME_MAX
from .includes.variables import TrackedTime

@statedef(stateno = -2)
def Think():
    Think_ImageRepro()

@statedef(stateno = -3)
def PreThink():
    Null()

@statedef(stateno = -1)
def Act():
    Null()

##########################################################################################
# just separating out some steps to make the code more readable.
# these need to use the @statefunc decorator to make sure triggers are translated.
##########################################################################################
@statefunc
def Think_ImageRepro():
    """
    Responsible for spawning the ImageRepro helper and applying its assert/screenbound properties.
    """
    if NumHelper(IMAGEREPRO_HELPER_ID) == 0:
        Helper(
            helpertype = HelperType.Player,
            name = "Image Reproduction",
            id = IMAGEREPRO_HELPER_ID,
            stateno = IMAGEREPRO_HELPER_STATE,
            supermovetime = PAUSETIME_MAX,
            pausemovetime = PAUSETIME_MAX,
            ignorehitpause = True
        )

    if IsHelper(IMAGEREPRO_HELPER_ID):
        PlayerPush(value = False, ignorehitpause = True)
        ScreenBound(value = True, movecamera = (True, True), ignorehitpause = True)
        if RoundState < 2: AfterImage(time = -1, length = 8, framegap = 2, ignorehitpause = 1)

        VarSet(var = TrackedTime, value = TrackedTime + 1)
        SelfState(value = IMAGEREPRO_HELPER_STATE)