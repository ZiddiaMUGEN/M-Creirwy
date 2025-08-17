from mdk.types import EnumType

ImageReproActionType = EnumType("ImageReproActionType", [
    "Idle", 
    "DashForward",
    "DashFinished",
    "Attacking"
], library = "States/Creirwy-Types.inc")