from mdk.resources.animation import Animation, Frame
from source.includes.constants import ANIMSEARCH_BASE

# create 'empty' animations at the top of AIR for use in animsearch
for idx in range(1001):
    Animation(id = ANIMSEARCH_BASE + idx, frames = [Frame(-1, 0)])

# these are externally-linked animations (to improve readability)
CALLBACK_RECEIVER_ANIM = Animation(id = 2694500, external = True)
"""Animation with a large Clsn2, used by Callback Receiver as a target for Projectile callback."""

SMALL_GETHIT_ANIM = Animation(id = 10000, external = True)
"""Animation with a small Clsn2, used by Crosstalk (and other Helpers) during target acquisition."""
SMALL_ATTACK_ANIM = Animation(id = 10001, external = True)
"""Animation with a small Clsn1, used by Crosstalk (and other Helpers) during target acquisition."""

PASSIVE_ANIM = Animation(id = 10002, external = True)
"""Infinite-looptime Animation with no Clsn1/Clsn2; used by various Helpers when they don't need to be doing anything."""

MARKING_ATTACK_ANIM = Animation(id = 2694501, external = True)
"""Animation with a Clsn1 which is sized to a normal player size, used by Marking during target acquisition."""

