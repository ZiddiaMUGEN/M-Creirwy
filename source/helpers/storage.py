### States for Storage helper.
### This Helper does nothing, but exposes all its variables for free use via Condbug.
### Therefore Helpers which have unreliable variables due to tampering (Spy, Infiltration, Exploration) can use this for storing
### investigation results.
from mdk.compiler import statedef
from mdk.types import SCOPE_HELPER, HitAttr, HitType, AssertType
from mdk.stdlib import NotHitBy, AssertSpecial, ChangeAnim

from source.includes.constants import STORAGE_HELPER_ID, PASSIVE_ANIM
from source.includes.shared import SendToDevilsEye

@statedef(stateno = STORAGE_HELPER_ID, scope = SCOPE_HELPER(STORAGE_HELPER_ID))
def StorageHelper_Actions():
    SendToDevilsEye()

    NotHitBy(value = (HitType.SCA, HitAttr.AA, HitAttr.AT, HitAttr.AP))
    AssertSpecial(flag = AssertType.Invisible, flag2 = AssertType.NoShadow)
    ChangeAnim(value = PASSIVE_ANIM)