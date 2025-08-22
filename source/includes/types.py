from mdk.types import EnumType

ImageReproActionType = EnumType("ImageReproActionType", [
    "Idle", 
    "DashForward",
    "DashFinished",
    "Attacking"
], library = "States/Creirwy-Types.inc")
"""
Used to track the current action ImageRepro is performing (e.g. attacking, moving towards enemy, etc).
"""

AnimationSearchStateType = EnumType("AnimationSearchStateType", [
    "NotStarted",
    "ReadyClsn1",
    "TestClsn1",
    "FinishedClsn1",
    "ReadyClsn2",
    "TestClsn2",
    "Finished",
    "NotFoundClsn1",
    "NotFoundClsn2"
], library = "States/Creirwy-Types.inc")
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