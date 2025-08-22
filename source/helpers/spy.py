from mdk.compiler import statedef
from mdk.types import SCOPE_HELPER, HitType, HitAttr
from mdk.stdlib import (
    SelfState, ChangeAnim2, NotHitBy,
    Name, IsHelper,
    root
)

from source.includes.constants import SPY_HELPER_ID, PASSIVE_ANIM
from source.includes.variables import SavedState

@statedef(stateno = SPY_HELPER_ID, scope = SCOPE_HELPER(SPY_HELPER_ID))
def SpyHelper_Base():
    """
    Entry point for the Spy helper.
    """
    if Name == "M-Creirwy":
        SelfState(value = SavedState)
    if IsHelper() and root.Name == "M-Creirwy":
        SelfState(value = SavedState)

    ## spy should be untouchable/invisible.
    NotHitBy(value = (HitType.SCA, HitAttr.AA, HitAttr.AT, HitAttr.AP))
    ChangeAnim2(value = PASSIVE_ANIM)