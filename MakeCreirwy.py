from mdk.compiler import build

from source import brain, action, image # type: ignore

if __name__ == "__main__":
    build("M-Creirwy.def", "States/Creirwy-States.mtl", preserve_ir = True, target_folder = "M-Creirwy.CNS")