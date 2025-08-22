from mdk.compiler import statedef
from mdk.types import SCOPE_TARGET, HelperType
from mdk.stdlib import (
    SelfState, Helper,
    Name, NumHelper, IsHelper,
    root, enemy
)

from source.includes.constants import MC_DEVILS_TARGET_STATE, SPY_HELPER_ID, PAUSETIME_MAX
from source.includes.variables import SavedState, Root_SpyIsSpawned
from source.includes.shared import CreirwyVarSet

@statedef(stateno = MC_DEVILS_TARGET_STATE, scope = SCOPE_TARGET)
def TargetLandingState():
    """
    Entry point for P2-sided work after enemies pass through Devil's Eye Killer states.
    This will redirect targets further based on what attack the character is attempting.
    """
    if Name == "M-Creirwy":
        SelfState(value = 0)
    if IsHelper() and root.Name == "M-Creirwy":
        SelfState(value = 0)

    ## set a variable for Creirwy to indicate a spy has been spawned.
    if NumHelper(SPY_HELPER_ID) == 0:
        CreirwyVarSet(Root_SpyIsSpawned, True)
        Helper(
            id = SPY_HELPER_ID,
            name = "Creirwy's Spy Helper",
            stateno = SPY_HELPER_ID,
            helpertype = HelperType.Normal,
            supermovetime = PAUSETIME_MAX,
            pausemovetime = PAUSETIME_MAX
        )

    #print(f"Spies = {NumHelper(SPY_HELPER_ID)}, CreirwyVar = {enemy.Root_SpyIsSpawned}")