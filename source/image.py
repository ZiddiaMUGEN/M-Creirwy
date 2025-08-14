### States for ImageRepro helper.
### This helper provides visuals for the character (while the root does more interesting things).
from mdk.compiler import statedef
from mdk.types import SCOPE_HELPER

from .includes.constants import IMAGEREPRO_HELPER_ID
from .includes.shared import SendToDevilsEye

@statedef(stateno = IMAGEREPRO_HELPER_ID, scope = SCOPE_HELPER(IMAGEREPRO_HELPER_ID))
def ImageRepro_Base():
    SendToDevilsEye()