from mdk.resources.animation import Animation, Frame
from source.includes.constants import ANIMSEARCH_BASE

# create 'empty' animations at the top of AIR for use in animsearch
for idx in range(1001):
    Animation(id = ANIMSEARCH_BASE + idx, frames = [Frame(-1, 0)])