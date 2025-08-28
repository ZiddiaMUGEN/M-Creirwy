## Diary

This is a log of any work I do on the character so I remember what I worked on.

### 2025-08-28

- fix a couple mtl bracketing issues
- fix a bug in variable compilation method for else blocks
- introduce exploration/explorer buffer helpers
- add a storage helper to store exploration results
- add skeleton for occupancy helpers
- move Spy critical vars into Storage helper (CLSN1/CLSN2/AnimationSearchState)
    - this also required a bunch of helper functions for reading/writing storage helper variables.
- implement MTL rescope into mdk-python
- update most or all manually-built `Expression("...")` in Creirwy code to use Python expressions
    - there are a few holdouts for variable assignment in `shared.py`, mostly just because Condbug is terrible to work with. normal characters would not need to deal with this.
- skeleton for Explorer state changes

### 2025-08-26

- work on enum/flag typing in mdk
- fix typecheck issues in source files
- convert ImageReproActionType and AnimationSearchStateType to Enum-backed types
- work on an alternate compilation method (for mutating variables inside blocks)

### 2025-08-25

- finish implementing Structure types in MTL

### 2025-08-22

- implement basic TargetState on crosstalk+marking to spawn spy helper
- add skeletons for Callback Receiver and Infiltration
- implement fast clsn1/clsn2 search in Spy helper
- add support for sysvar usage to mdk/MTL

### 2025-08-20

- pass an ID to each crosstalk helper/target in size.shadowoffset
- implement crosstalk permanent target + CT target deletion
- move helper code to a separate folder
- add skeleton for first/last helpers, marking helper
- implement hitdefs/reversaldef for marking helper
- implement display/append clipboard in mdk-python
- implement automatic print-to-clipboard for statedef, statefunc, template
- swap to use prints instead of clipboard controllers

### 2025-08-19

- work on a couple more super anims, move some code into helper statefuncs for clarity
- ensure MDK can convert partials into stateno expressions

### 2025-08-17

- allow arbitrary scope changes out of negative states (this is important for e.g. Helper SelfState out of -2)
- implement idle explods for imagerepro, start working on imagerepro attacks
- allow implicit use of int types (int, short, byte) in triggers (in MDK)
- set up a variable to track the substate machine for ImageRepro attack selection
- converted substate variable to an Enum, added type definition emits to mdk, work on basic enum operators in MTL
- ensure MTL can output integer values for user-defined enums

### 2025-08-16

- start working on adding Crosstalk
- add a helper for setting bool vars on root via Condbug
- work on testing mtldbg under helper occupancy
- set up a variable for crosstalk init under root
- set up a temp state with PLAYER scope for root
- dramatically improve mtldbg performance by implementing custom ASM processing inside MUGEN process

### 2025-08-15

- work on ImageRepro intro
- set up shared globals for state/time tracking
- set up helper-scoped global flag for imagerepro intro run
- add a couple statefuncs for state/time updates
- add a trigger for random range (`includes.shared.RandRange`)
- fix for signed variable display in mtldbg
- add a trigger to pick between 2 values at random (`includes.shared.RandPick`)
- add break by state name in mtldbg

### 2025-08-14

- update MDK to support scoped output
- add `target` scope to all DEK states and to landing state
- fix some bugs in MDK related to ConvertibleExpressions
- implement global forward declarations into MTL/MDK
- start working on ImageRepro helper spawn/states

### 2025-08-13

- Initial commit, pull in system files from the previous Creirwy
- Work on MDK/MTL to improve compilation performance for characters with large DEK common
- Implement DEK common statefile in MDK (separate build step)
- Implement a stub for the target state for DEK