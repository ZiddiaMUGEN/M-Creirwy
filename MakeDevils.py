import copy

from mdk.compiler import statedef, build
from mdk.stdlib import Name, IsHelper, root, ChangeState
from mdk.types import SCOPE_TARGET

def _devils():
    if Name != "M-Creirwy" or (IsHelper() and root.Name != "M-Creirwy"):
        ChangeState(value = "TargetLandingState", ignorehitpause = True)

if __name__ == "__main__":

    ## states from 0 to 1k, all
    for idx in range(1000):
        next_state = copy.deepcopy(_devils)
        next_state.__name__ = f"DevilsEye{idx}"
        statedef(stateno = idx, scope = SCOPE_TARGET)(next_state)

    ## states from 1k to 1m, every 1k
    for idx in range(1000, 1000000, 1000):
        next_state = copy.deepcopy(_devils)
        next_state.__name__ = f"DevilsEye{idx}"
        statedef(stateno = idx, scope = SCOPE_TARGET)(next_state)

    build("M-Creirwy.def", "States/Creirwy-Devil.mtl", run_mtl=False, locations=False, compress=True, preserve_ir=True)