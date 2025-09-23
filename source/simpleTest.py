from state_machine.state_machine import StateMachine
from state_machine.state_hello_world import StateHelloWorld
from state_machine.state_hello_moon import StateHelloMoon

stateMachine = StateMachine()
firstState = StateHelloWorld()
secondState = StateHelloMoon()

stateMachine.setState(firstState)

frameCounter = 0 

def doubleFunc(number):
    return (number % 2 == 0), number / 5

while frameCounter < 100:
    #stateMachine.update()
    #if(frameCounter % 10 != 0):
    #    stateMachine.setState(firstState)
    #else:
    #    stateMachine.setState(secondState)

    didPass, value = doubleFunc(frameCounter)
    if(didPass):
        print(value)

    frameCounter += 1