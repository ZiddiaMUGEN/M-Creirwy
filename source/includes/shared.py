from mdk.compiler import template
from mdk.stdlib import Name, IsHelper, root, ChangeState
from mdk.types import StateNoType, Expression

@template(inputs = [StateNoType], library = "States/Creirwy-Shared.inc")
def SendToDevilsEye(target_state: Expression):
    if Name != "M-Creirwy" or (IsHelper() and root.Name != "M-Creirwy"): 
        ChangeState(value = target_state, ignorehitpause = True)