### States for Last helper.
### This helper is the last helper spawned during opening occupancy/crosstalk setup,
### and permanently retains MoveType = H.
### This means it will always act last out of all the Helpers and Players.
from mdk.compiler import statedef
from mdk.types import SCOPE_HELPER, MoveType
from mdk.stdlib import Null

from source.includes.constants import LAST_HELPER_ID
from source.includes.shared import SendToDevilsEye

@statedef(stateno = LAST_HELPER_ID, movetype = MoveType.H, scope = SCOPE_HELPER(LAST_HELPER_ID))
def LastHelper_Actions():
    SendToDevilsEye()