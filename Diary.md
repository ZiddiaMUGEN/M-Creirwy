## Diary

This is a log of any work I do on the character so I remember what I worked on.

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