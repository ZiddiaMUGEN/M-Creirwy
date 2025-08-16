MC_DEVILS_TARGET_STATE = 2694491
"""Target state for Devil's Eye Killer. Should be the state number used for `TargetLandingState`."""

## all static helper IDs can go here.
IMAGEREPRO_HELPER_ID = 10000
"""ID of the ImageRepro helper, declared here to avoid having bare numbers in code."""
IMAGEREPRO_HELPER_STATE = IMAGEREPRO_HELPER_ID

CROSSTALK_HELPER_ID = 11000
"""ID of the Crosstalk helpers."""
CROSSTALK_HELPER_STATE = CROSSTALK_HELPER_ID

CROSSTALK_TARGET_ID = 12000
"""ID of the Crosstalk target helpers (used during CT setup)."""
CROSSTALK_TARGET_STATE = CROSSTALK_TARGET_ID

CROSSTALK_HELPER_COUNT = 27
"""Total number of crosstalk helpers to spawn. Double this should be equal to 56, less the number of other helpers we use."""

OCCUPANCY_HELPER_ID = 19000
"""ID of the Occupancy helpers (which fill space if CT count leaves an uneven count, or in specific situations)."""
OCCUPANCY_HELPER_STATE = OCCUPANCY_HELPER_ID

LAST_HELPER_ID = 20000
"""ID of the Last helper (which always runs its code last)."""
LAST_HELPER_STATE = LAST_HELPER_ID

## some constants to make code more readable.
PAUSETIME_MAX = (2 ** 31) - 1