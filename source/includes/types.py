from mdk.types import EnumType
from enum import Enum

class ImageReproActionType(Enum):
    """
    Used to track the current action ImageRepro is performing (e.g. attacking, moving towards enemy, etc).
    """
    Idle = 0
    DashForward = 1
    DashFinished = 2
    Attacking = 3

ImageReproActionTypeT = EnumType("ImageReproActionType", ImageReproActionType, library = "States/Creirwy-Types.inc")

class AnimationSearchStateType(Enum):
    """
    Used to track the current status of animation search in Spy helper.

    Ready to start search: NotStarted -> ReadyClsn1

    Fired a projectile candidate: ReadyClsn1 -> TestClsn1

    Projectile did not make contact: TestClsn1 -> ReadyClsn1

    Projectile made contact: TestClsn1 -> ReadyClsn2

    Fired a projectile candidate: ReadyClsn2 -> TestClsn2

    Projectile did not make contact: TestClsn2 -> ReadyClsn2

    Projectile made contact: TestClsn2 -> Finished
    """
    NotStarted = 0
    ReadyClsn1 = 1
    TestClsn1 = 2
    FinishedClsn1 = 3
    ReadyClsn2 = 4
    TestClsn2 = 5
    Finished = 6
    NotFoundClsn1 = 7
    NotFoundClsn2 = 8

AnimationSearchStateTypeT = EnumType("AnimationSearchStateType", AnimationSearchStateType, library = "States/Creirwy-Types.inc")
