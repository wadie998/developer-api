*** Settings ***
Library    BuiltIn
Library    String

*** Test Cases ***
Sanity Check – Robot Framework CI
    [Documentation]    Verifies that Robot Framework is installed and CI is working.
    ${message}=    Set Variable    Hello from Robot Framework!
    Log    ${message}
    Should Contain    ${message}    Robot Framework