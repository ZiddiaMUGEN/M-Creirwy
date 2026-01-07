### States for First helper.
### This helper is the first helper spawned during opening occupancy/crosstalk setup,
### and permanently retains MoveType = A.
### This means it will always act first out of all the Helpers (and is likely to act before P2,
### if P2 is using MoveType = I or H).
from mdk.compiler import statedef
from mdk.types import SCOPE_HELPER, MoveType
from mdk.stdlib import ChangeAnim

from source.includes.constants import FIRST_HELPER_ID
from source.includes.shared import SendToDevilsEye

from source.anims import PASSIVE_ANIM

@statedef(stateno = FIRST_HELPER_ID, movetype = MoveType.A, scope = SCOPE_HELPER(FIRST_HELPER_ID))
def FirstHelper_Actions():
    SendToDevilsEye()

    ChangeAnim(value = PASSIVE_ANIM)