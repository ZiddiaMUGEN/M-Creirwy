### States for Occupany helper.
### This Helper exists to fill space.
from mdk.compiler import statedef
from mdk.types import SCOPE_HELPER, HitAttr, HitType, AssertType
from mdk.stdlib import NotHitBy, AssertSpecial, ChangeAnim

from source.includes.constants import OCCUPANCY_HELPER_ID
from source.includes.shared import SendToDevilsEye

from source.anims import PASSIVE_ANIM

@statedef(stateno = OCCUPANCY_HELPER_ID, scope = SCOPE_HELPER(OCCUPANCY_HELPER_ID))
def OccupancyHelper_Actions():
    SendToDevilsEye()

    NotHitBy(value = (HitType.SCA, HitAttr.AA, HitAttr.AT, HitAttr.AP))
    AssertSpecial(flag = AssertType.Invisible, flag2 = AssertType.NoShadow)
    ChangeAnim(value = PASSIVE_ANIM)