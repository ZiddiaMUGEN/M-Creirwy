### States for Storage helper.
### This Helper does nothing, but exposes all its variables for free use via Condbug.
### Therefore Helpers which have unreliable variables due to tampering (Spy, Infiltration, Exploration) can use this for storing
### investigation results.
from mdk.compiler import statedef
from mdk.types import SCOPE_HELPER, HitAttr, HitType, AssertType
from mdk.stdlib import NotHitBy, AssertSpecial, ChangeAnim

from source.includes.constants import STORAGE_HELPER_ID, PASSIVE_ANIM
from source.includes.shared import SendToDevilsEye
from source.includes.variables import (
    SpyStorage_SavedClsn1, SpyStorage_SavedClsn2, ExplorerStorage_SavedMoveTypeH_Low, ExplorerStorage_SavedMoveTypeH_High
)

@statedef(stateno = STORAGE_HELPER_ID, scope = SCOPE_HELPER(STORAGE_HELPER_ID))
def StorageHelper_Actions():
    SendToDevilsEye()

    NotHitBy(value = (HitType.SCA, HitAttr.AA, HitAttr.AT, HitAttr.AP))
    AssertSpecial(flag = AssertType.Invisible, flag2 = AssertType.NoShadow)
    ChangeAnim(value = PASSIVE_ANIM)

    print(f"CLSN1 = {SpyStorage_SavedClsn1} CLSN2 = {SpyStorage_SavedClsn2} Low AyuAyu = {ExplorerStorage_SavedMoveTypeH_Low} High AyuAyu = {ExplorerStorage_SavedMoveTypeH_High}")