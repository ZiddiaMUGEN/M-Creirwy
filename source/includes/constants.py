MC_DEVILS_TARGET_STATE = 2694491
"""Target state for Devil's Eye Killer. Should be the state number used for `TargetLandingState`."""

PASSIVE_ANIM = 10002
"""ID of an animation with no Clsn1/Clsn2; used by various Helpers when they don't need to be doing anything."""

######################################################
## Helper IDs for quick reference
######################################################
SPY_HELPER_ID = MC_DEVILS_TARGET_STATE + 1
"""ID of the Spy helper, which is a normal-type Helper spawned in the enemy context."""

EXPLORER_BUFFER_ID = MC_DEVILS_TARGET_STATE + 2
"""ID of the Exploration buffer, which is spawned by the Spy helper to create Explorers (and buffer any parent variable tampering)."""

EXPLORER_HELPER_ID = MC_DEVILS_TARGET_STATE + 3
"""ID of the Exploration helper, which is spawned by the buffer helper to handle state exploration."""

IMAGEREPRO_HELPER_ID = 10000
"""ID of the ImageRepro helper, declared here to avoid having bare numbers in code."""

MOONJUMP_HELPER_ID = 10001
"""ID of a Helper used for display during ImageRepro's MoonJump attack."""

CROSSTALK_HELPER_ID = 11000
"""ID of the Crosstalk helpers."""

CROSSTALK_TARGET_ID = 12000
"""ID of the Crosstalk target helpers (used during CT setup)."""

CROSSTALK_HELPER_COUNT = 24
"""Total number of crosstalk helpers to spawn. Double this should be equal to 56, less the number of other helpers we use."""

MARKING_HELPER_ID = 13000
"""ID of the Marking helper."""

INFILTRATION_HELPER_ID = 14000
"""ID of the Infiltration helper."""

INFILTRATION_CONTROLLER_ID = 14001
"""
ID of the Infiltration Controller helper. This helper doesn't need to do anything, it exists to prevent
the Infiltration helper from doing ParentVarSet while it explores the enemy's states.
"""

RECEIVER_HELPER_ID = 15000
"""ID of the Callback Receiver helper."""

STORAGE_HELPER_ID = 16000
"""ID of the Storage helper."""

OCCUPANCY_HELPER_ID = 18000
"""ID of the Occupancy helpers (which fill space if CT count leaves an uneven count, or in specific situations)."""

FIRST_HELPER_ID = 19000
"""ID of the First helper (which always runs its code first)."""

LAST_HELPER_ID = 20000
"""ID of the Last helper (which always runs its code last)."""

## some constants to make code more readable.
PAUSETIME_MAX = (2 ** 31) - 1
ANIMSEARCH_BASE = 11100000