import copy

from mdk.compiler import create_statedef, build
from mdk.stdlib import Name, IsHelper, root, ChangeState

def _devils():
    if Name != "M-Creirwy" or (IsHelper() and root.Name != "M-Creirwy"): 
        ChangeState(value = "TargetLandingState", ignorehitpause = True)

if __name__ == "__main__":

    ## states from 0 to 1k, all
    for idx in range(1000):
        next_state = copy.deepcopy(_devils)
        next_state.__name__ = f"DevilsEye{idx}"
        create_statedef(next_state, stateno = idx)

    ## states from 1k to 100k, every 1k
    for idx in range(1000, 100000, 1000):
        next_state = copy.deepcopy(_devils)
        next_state.__name__ = f"DevilsEye{idx}"
        create_statedef(next_state, stateno = idx)

    build("M-Creirwy.def", "States/Creirwy-Devil.mtl", run_mtl=False, locations=False, compress=True)