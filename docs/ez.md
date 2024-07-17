ez.js

The ez.js library provides a flexible and extendable framework for managing event handling, agent registration, and event broadcasting. It is designed to handle various events efficiently while allowing agents to act autonomously and extend the controller's functionality as needed.

# ActionEventController

The ActionEventController class is the core component of ez.js. It manages event handlers, registers agents, and broadcasts events to registered agents.

Constructor
```javascript
constructor()
```

Initializes the controller with default event handlers and an empty list of registered agents.

Methods
# registerAgent
Registers an agent with the controller. The agent must implement a handleEvent method.

    Parameters:
        agent (Object): The agent to be registered. Must implement a handleEvent method.

    Throws:
        Error if the agent does not implement the handleEvent method.

# handleEvent
```javascript
async handleEvent(eventType, eventData)
```
GPT

Certainly! Below is a verbose and detailed external documentation for ez.js, covering all aspects, including class methods, event handling, agent registration, and usage examples.
ez.js Documentation
Overview

The ez.js library provides a flexible and extendable framework for managing event handling, agent registration, and event broadcasting. It is designed to handle various events efficiently while allowing agents to act autonomously and extend the controller's functionality as needed.

# ActionEventController

The ActionEventController class is the core component of ez.js. It manages event handlers, registers agents, and broadcasts events to registered agents.
Constructor

```javascript
constructor()
```
Initializes the controller with default event handlers and an empty list of registered agents.

# registerAgent

```javascript
registerAgent(agent)
```
Registers an agent with the controller. The agent must implement a handleEvent method.

    Parameters:
        agent (Object): The agent to be registered. Must implement a handleEvent method.

    Throws:
        Error if the agent does not implement the handleEvent method.

# handleEvent

```javascript
async handleEvent(eventType, eventData)
```
Handles an event by delegating to the appropriate event handler and broadcasting to agents.

    Parameters:
        eventType (string): The type of the event.
        eventData (Object): The data associated with the event.

    Throws:
        Error if there is an issue handling the event.

# broadcastEventToAgents
```javascript
async broadcastEventToAgents(eventType, eventData)
```
Broadcasts an event to all registered agents.

    Parameters:
        eventType (string): The type of the event.
        eventData (Object): The data associated with the event

# onClick
```javascript
async onClick(data)
```
Default handler for submit events.

    Parameters:
        data (Object): The data associated with the submit event.

registerEventHandler
```javascript
registerEventHandler(eventType, handler)
```
Registers a custom event handler.

    Parameters:
        eventType (string): The type of the event.
        handler (function): The handler function for the event.

# AgentUsingEz

The AgentUsingEz class demonstrates how an agent can use ez.js as the controller
```javascript
constructor()
async onClick(data)
async onSubmit(data)
registerCustomEventHandler(eventType, handler)
```
Initializes the agent with an instance of ActionEventController and registers itself with the controller
Handles events broadcasted by the controller.

    Parameters:
        eventType (string): The type of the event
        eventData (Object): The data associated with the event

Handles click events.

    Parameters:
        data (Object): The data associated with the click event
Handles submit events

    Parameters:
        data (Object): The data associated with the submit event



# Setting Up Event Listeners

The following example demonstrates how to set up event listeners using AgentUsingEz and ActionEventController

```javascript
// main.js

import AgentUsingEz from './agentUsingEz';

document.addEventListener('DOMContentLoaded', () => {
    const agent = new AgentUsingEz();

    // Function to send event to the agent
    function sendEventToAgent(eventType, eventData) {
        agent.handleEvent(eventType, eventData);
    }

    // Set up event listeners
    const events = [
        'click', 'submit', 'change', 'focus', 'blur', 'mouseover', 'mouseout',
        'keydown', 'keyup', 'keypress', 'dblclick', 'resize', 'scroll',
        'contextmenu', 'drag', 'dragstart', 'dragend', 'dragover', 'dragenter',
        'dragleave', 'drop', 'input', 'wheel', 'copy', 'cut', 'paste'
    ];

    events.forEach(eventType => {
        document.body.addEventListener(eventType, (event) => {
            sendEventToAgent(eventType, { message: `${eventType} event occurred`, event });
        });
    });

    // Example of agent registering a custom event handler
    agent.registerCustomEventHandler('customEvent', (data) => {
        console.log('Custom event handled by agent with data:', data);
    });

    // Simulate a custom event
    sendEventToAgent('customEvent', { message: 'This is a custom event' });
});
```
# Simulating Events

The simulateEvents method in AgentUsingEz can be used to demonstrate event handling

The ez.js framework provides a robust, flexible, and extendable system for managing events and agent interactions. By leveraging the ActionEventController and AgentUsingEz classes, developers can easily create agents that autonomously handle and respond to a wide range of events. This modular approach ensures maintainability and scalability, making it suitable for various applications.

