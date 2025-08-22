from mdk.compiler import statedef
from mdk.types import SCOPE_PLAYER

from source.includes.shared import SendToDevilsEye

@statedef(scope = SCOPE_PLAYER)
def TempPlayerState():
    SendToDevilsEye()