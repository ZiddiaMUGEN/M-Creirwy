from mdk.compiler import statedef
from mdk.stdlib import Null
from mdk.types import SCOPE_TARGET

from .includes.constants import MC_DEVILS_TARGET_STATE

@statedef(stateno = MC_DEVILS_TARGET_STATE, scope = SCOPE_TARGET)
def TargetLandingState():
    """
    Initial target state for enemies after they pass through Devil's Eye Killer states.
    This will redirect targets further based on what attack the character is attempting.
    """
    Null()