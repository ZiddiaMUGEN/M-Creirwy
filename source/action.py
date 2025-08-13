from mdk.compiler import statedef
from mdk.stdlib import Null

from source.includes.shared import SendToDevilsEye
from source.brain import TargetLandingState

@statedef()
def TempTestCustomState():
    SendToDevilsEye(target_state = TargetLandingState)
    Null()