from mdk.compiler import build
from mdk.types.context import CompilerContext
from mdk.utils.shared import convert

## apply ignorehitpause/persistent by default to all states.
CompilerContext.instance().default_state = (convert(True), convert(256))

## source.anims MUST be the first import as we need animsearch at the top of the generated AIR.
from source import anims
## we only need to import these as `action` already imports all the Helper states individually.
from source import brain, action, target # type: ignore
from source.helpers import spy, exploration # type: ignore

if __name__ == "__main__":
    build("M-Creirwy.def", "States/Creirwy-States.mtl", preserve_ir = True, target_folder = "M-Creirwy.CNS", debug_build = True)