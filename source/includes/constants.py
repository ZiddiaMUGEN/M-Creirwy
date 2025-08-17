MC_DEVILS_TARGET_STATE = 2694491
"""Target state for Devil's Eye Killer. Should be the state number used for `TargetLandingState`."""

######################################################
## Helper IDs for quick reference
######################################################
IMAGEREPRO_HELPER_ID = 10000
"""ID of the ImageRepro helper, declared here to avoid having bare numbers in code."""

CROSSTALK_HELPER_ID = 11000
"""ID of the Crosstalk helpers."""

CROSSTALK_TARGET_ID = 12000
"""ID of the Crosstalk target helpers (used during CT setup)."""

CROSSTALK_HELPER_COUNT = 27
"""Total number of crosstalk helpers to spawn. Double this should be equal to 56, less the number of other helpers we use."""

OCCUPANCY_HELPER_ID = 19000
"""ID of the Occupancy helpers (which fill space if CT count leaves an uneven count, or in specific situations)."""

LAST_HELPER_ID = 20000
"""ID of the Last helper (which always runs its code last)."""

## some constants to make code more readable.
PAUSETIME_MAX = (2 ** 31) - 1