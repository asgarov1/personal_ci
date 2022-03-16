# CUSTOM CI 

## Motivation behind it
For one of the projects I worked for I often needed to clone and run tests for the project to make sure 
there are no failed tests being committed. Of course there are better resources out there I found myself in  a
situation where those aren't easily available, and those minutes of checking out branches
and running tests manually started adding up. Hence the scripts.

Constants are missing - this is done because those are company specific (secrets). The logic is there.

Scripts use Gitlab REST API

### There are 3 CI scripts:
1. ng_ci
2. backend_ci
3. check_focus

### ng_ci
This one is front_end oriented, in this case front end folder was in the same repository as backend
so for the sake of efficiency this script clones only the front_end sub-directory

 - it first checks if any of the open merge requests have last comment with a specified command
 - then it clones and runs tests for those merge_request branches
 - comments the result of the test on a merge request

### backend_ci
This one is pretty simple backend oriented script:

- it clones the branch for the merge_request
- runs `mvn clean verify`
- comments back whether test was successful

It also only runs based on the command found in the last comment of the merge request (no command no run)

### check_focus
Often in our front end, jasmine specific keywords were forgotten and comitted (`fdescribe` and `fit`)
This script checks (without any command) whether any of the open merge request changes had those as added lines and if so
it commented on that.
