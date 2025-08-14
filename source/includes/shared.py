from mdk.compiler import statefunc
from mdk.stdlib import Name, IsHelper, root

from source.brain import TargetLandingState

@statefunc
def SendToDevilsEye():
    """
    Checks if an enemy landed in this state, and redirects to TargetLandingState.
    This needs to be applied at the start of every player state!
    """
    if Name != "M-Creirwy" or (IsHelper() and root.Name != "M-Creirwy"): 
        TargetLandingState(ignorehitpause = True)