from mdk.compiler import build
from mdk.types.context import CompilerContext
from mdk.utils.shared import convert

## apply ignorehitpause/persistent by default to all states.
CompilerContext.instance().default_state = (convert(True), convert(256))

from source import brain, action, image, crosstalk # type: ignore

if __name__ == "__main__":
    build("M-Creirwy.def", "States/Creirwy-States.mtl", preserve_ir = True, target_folder = "M-Creirwy.CNS")