from mdk.compiler import statedef, statefunc
from mdk.types import SCOPE_HELPER, SCOPE_PLAYER, HitType, HitAttr, AssertType, HitFlagType, PosType, TeamType, Expression, HelperType, VariableExpression, IntType
from mdk.stdlib.redirects import RedirectTarget
from mdk.stdlib import (
    ChangeAnim2, ChangeAnim, NotHitBy, HitBy, AssertSpecial, Projectile, PosSet, Helper,
    Anim, NumHelper,
    enemy, enemyID, root, helperID, rescope
)

from source.includes.shared import SendToSafeStates, ReadStorageVar_Enemy, SetStorageVar_Enemy
from source.includes.constants import SPY_HELPER_ID, EXPLORER_BUFFER_ID, PASSIVE_ANIM, PAUSETIME_MAX
from source.includes.variables import (
    Spy_AnimTestNumber, SpyStorage_AnimationSearchState, SpyStorage_SavedClsn1, SpyStorage_SavedClsn2, Spy_LastAnimChecked
)
from source.includes.types import AnimationSearchStateType, AnimationSearchStateTypeT

creirwy = enemyID(enemy.Name != "M-Creirwy")
"""A custom redirect to the correct enemy index for Creirwy."""

def RootNumProjID(exprn: Expression) -> Expression:
    """A helper to get NumProjID (which only works on the root) while retaining access to Spy's variables."""
    return rescope(root, SCOPE_HELPER(SPY_HELPER_ID)).NumProjID(exprn)

def ReadAnimationSearchState(): 
    """Helper function to read the value of AnimationSearchState, which is stored in Variable Storage."""
    return ReadStorageVar_Enemy(SpyStorage_AnimationSearchState)

def ReadSpyHelperVar(variable: VariableExpression):
    """Helper function to provide access to Spy helper's internal variables to Conds inside Variable Storage."""
    return rescope(enemy, SCOPE_PLAYER).Cond(NumHelper(SPY_HELPER_ID) != 0, getattr(helperID(SPY_HELPER_ID), variable.exprn), -1)

@statedef(stateno = SPY_HELPER_ID, scope = SCOPE_HELPER(SPY_HELPER_ID))
def SpyHelper_Base():
    """
    Entry point for the Spy helper.
    """
    SendToSafeStates()

    ## for debugging.
    #print(f"State = {ReadAnimationSearchState()} CLSN1 = {ReadStorageVar_Enemy(SpyStorage_SavedClsn1)} CLSN2 = {ReadStorageVar_Enemy(SpyStorage_SavedClsn2)} Last = {Spy_LastAnimChecked} Test = {Spy_AnimTestNumber}")

    ## spy should be untouchable/invisible.
    NotHitBy(value = (HitType.SCA, HitAttr.AA, HitAttr.AT, HitAttr.AP))
    AssertSpecial(flag = AssertType.Invisible, flag2 = AssertType.NoShadow)
    ChangeAnim2(value = PASSIVE_ANIM)

    ## spawn another Helper to run state exploration.
    ## this goes into a separate Helper as we don't want the Spy's variables to get interfered with.
    if NumHelper(EXPLORER_BUFFER_ID) == 0:
        Helper(
            id = EXPLORER_BUFFER_ID,
            name = "Exploration Buffer",
            stateno = EXPLORER_BUFFER_ID,
            helpertype = HelperType.Normal,
            supermovetime = PAUSETIME_MAX,
            pausemovetime = PAUSETIME_MAX
        )

    ## the first step for animation investigation will always be animation search.
    ## we can't achieve much until we have at least a Clsn1 anim (and ideally a Clsn2 anim).
    if ReadAnimationSearchState() == AnimationSearchStateType.NotStarted or ReadAnimationSearchState() == AnimationSearchStateType.ReadyClsn1:
        ## start performing animation search
        SpyHelper_Clsn1Search()

    if ReadAnimationSearchState() == AnimationSearchStateType.ReadyClsn2:
        ## start performing animation search
        SpyHelper_Clsn2Search()

    if ReadAnimationSearchState() == AnimationSearchStateType.TestClsn1:
        ## check if projectile made contact
        ## if it did, store the animation into SavedClsn1 and progress to Clsn2 search.
        if Spy_AnimTestNumber > 0 and RootNumProjID(Spy_AnimTestNumber + 11100000) == 0:
            SetStorageVar_Enemy(SpyStorage_SavedClsn1, ReadSpyHelperVar(Spy_LastAnimChecked))
            SetStorageVar_Enemy(SpyStorage_AnimationSearchState, AnimationSearchStateType.FinishedClsn1)
        ## if it did not, go back to ReadyClsn1 status for the next animation to test.
        if Spy_AnimTestNumber > 0 and RootNumProjID(Spy_AnimTestNumber + 11100000) != 0:
            SetStorageVar_Enemy(SpyStorage_AnimationSearchState, AnimationSearchStateType.ReadyClsn1)

    if ReadAnimationSearchState() == AnimationSearchStateType.TestClsn2:
        ## check if projectile made contact
        ## if it did, store the animation into SavedClsn2 and complete the search.
        if Spy_AnimTestNumber > 0 and RootNumProjID(Spy_AnimTestNumber + 11100000) == 0:
            SetStorageVar_Enemy(SpyStorage_SavedClsn2, ReadSpyHelperVar(Spy_LastAnimChecked))
            SetStorageVar_Enemy(SpyStorage_AnimationSearchState, AnimationSearchStateType.Finished)
        ## if it did not, go back to ReadyClsn2 status for the next animation to test.
        if Spy_AnimTestNumber > 0 and RootNumProjID(Spy_AnimTestNumber + 11100000) != 0:
            SetStorageVar_Enemy(SpyStorage_AnimationSearchState, AnimationSearchStateType.ReadyClsn2)

    ## if we just finished Clsn1 search, reset variables before moving to Clsn2 search
    if ReadAnimationSearchState() == AnimationSearchStateType.FinishedClsn1:
        Spy_AnimTestNumber.set(0)
        Spy_LastAnimChecked.set(0)
        SetStorageVar_Enemy(SpyStorage_AnimationSearchState, AnimationSearchStateType.ReadyClsn2)

    ## if we've reached a NotFound state, we need to attempt slow anim search.
    ## this is because fast anim search 'only' checks 1k animations.
    ### TODO: implement slow animation search

@statefunc()
def Spy_GetNextAnim(fail_state: Expression) -> None:
    ## ChangeAnim2 to one of Creirwy's pre-prepared animations
    ChangeAnim2(value = Spy_AnimTestNumber + 11100000)
    ## then ChangeAnim to a (hopefully) invalid animation
    ChangeAnim(value = 2694491)
    ## check if this is the same as the last animation we tested
    ## if it is, it means we exhausted all the available enemy animations and should quit.
    if Anim == Spy_LastAnimChecked and Spy_AnimTestNumber > 0:
        SetStorageVar_Enemy(SpyStorage_AnimationSearchState, fail_state)
    ## save the current anim ID and increment the current anim index
    Spy_LastAnimChecked.set(Anim)
    Spy_AnimTestNumber.add(1)

    ## if we tested more than 1k animations, we've run out of room in Creirwy's animations.
    ## this means fast anim search didn't work and we should fall back to slow search.
    if Spy_AnimTestNumber > 1000:
        SetStorageVar_Enemy(SpyStorage_AnimationSearchState, fail_state)

    ## switch to a known good anim to avoid potential crashes.
    ChangeAnim2(value = PASSIVE_ANIM)

@statedef(scope = SCOPE_HELPER(SPY_HELPER_ID))
def SpyHelper_Clsn2Search():
    """
    Use fast animation search to look for an animation with a hitbox.
    """
    SendToSafeStates()

    ## run animation search
    SetStorageVar_Enemy(SpyStorage_AnimationSearchState, AnimationSearchStateType.ReadyClsn2)
    Spy_GetNextAnim(AnimationSearchStateType.NotFoundClsn2)
    ## change to the selected animation
    ChangeAnim(value = Spy_LastAnimChecked)

    ## if we are still in `ReadyClsn2` state (i.e no early exit criteria was met),
    ## set our Anim to the testable Anim,
    ## and fire a projectile with the known Clsn1 anim to see if we get hit.
    ## we use (C, HT) here so that we don't hit the Callback-Receiver helper.
    ## (as is this probably has false positives anyway...)
    if ReadAnimationSearchState() == AnimationSearchStateType.ReadyClsn2:
        HitBy(value = (HitType.C, HitAttr.HT))
        PosSet(x = creirwy.Pos.x, y = creirwy.Pos.y)
        Projectile(
            projid = Spy_AnimTestNumber + 11100000,
            hitflag = HitFlagType.HLAFD,
            attr = (HitType.C, HitAttr.HT),
            affectteam = TeamType.F,
            sparkno = -1,
            guard_sparkno = -1,
            projscale = (0, 0),
            projanim = ReadStorageVar_Enemy(SpyStorage_SavedClsn1),
            projremovetime = 3,
            projhits = 1,
            projpriority = 99999999,
            postype = PosType.P2,
            offset = (0, 0),
            supermovetime = PAUSETIME_MAX,
            pausemovetime = PAUSETIME_MAX
        )
        SetStorageVar_Enemy(SpyStorage_AnimationSearchState, AnimationSearchStateType.TestClsn2)

@statedef(scope = SCOPE_HELPER(SPY_HELPER_ID))
def SpyHelper_Clsn1Search():
    """
    Use fast animation search to look for an animation with a hurtbox.
    """
    SendToSafeStates()

    ## run animation search
    SetStorageVar_Enemy(SpyStorage_AnimationSearchState, AnimationSearchStateType.ReadyClsn1)
    Spy_GetNextAnim(AnimationSearchStateType.NotFoundClsn1)

    ## if we are still in `ReadyClsn1` state (i.e no early exit criteria was met),
    ## fire a Projectile.
    if ReadAnimationSearchState() == AnimationSearchStateType.ReadyClsn1:
        Projectile(
            projid = Spy_AnimTestNumber + 11100000,
            hitflag = HitFlagType.HLAFD,
            attr = (HitType.C, HitAttr.HP),
            sparkno = -1,
            guard_sparkno = -1,
            projscale = (0, 0),
            projanim = Spy_LastAnimChecked,
            projremovetime = 3,
            projhits = 1,
            projpriority = 99999999,
            postype = PosType.P2,
            offset = (0, 0),
            supermovetime = PAUSETIME_MAX,
            pausemovetime = PAUSETIME_MAX
        )
        SetStorageVar_Enemy(SpyStorage_AnimationSearchState, AnimationSearchStateType.TestClsn1)