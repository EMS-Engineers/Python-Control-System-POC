import pygame, sys, threading, queue, numpy, functools
pygame.init()

# Event class for linking events to functions using decorators
class event:
    registry = {}

    def __init__(self, objectName, eventName):
        self.objectName = objectName
        self.eventName = eventName

    def __call__(self, func):
        events = []
        if type(self.objectName) is list:
            if type(self.eventName) is list:
                for objName in self.objectName:
                    for evName in self.eventName:
                        events.append((objName,evName))
            else:
                for objName in self.objectName:
                    events.append((objName,self.eventName))
        else:
            if type(self.eventName) is list:
                for evName in self.eventName:
                    events.append((self.objectName,evName))
            else:
                events.append((self.objectName,self.eventName))
        events = list(dict.fromkeys(events))

        for key in events:
            self.registry.update({key:func})

        @functools.wraps(func)
        def wrapper(*args,**kwargs):
            return func(*args,**kwargs)
        return wrapper

# Display Loop for running touchpanel with buttons in a thread
def displayLoop():
    clicked = False
    while True:
        screen.blit(backdrop,(0,0))
        buttons = [screen.blit(buttonCategories[idx][buttonStates[idx]],buttonPositions[idx]) for idx in range(len(buttonStates))]
        for idx in range(len(buttons)):
            text = font.render(buttonLabels[idx][0],True,buttonLabels[idx][1][buttonStates[idx]])
            button = buttons[idx]
            screen.blit(text,(button.left + (button.width - text.get_width())//2,button.top + (button.height - text.get_height())//2))

        pygame.event.get()
        if not clicked and pygame.mouse.get_pressed()[0]:
            clicked = True
            pos = pygame.mouse.get_pos()
            for idx in range(len(buttons)):
                if buttons[idx].collidepoint(pos):
                    eventQueue.put((idx,'Pressed'))
                    break
        elif clicked and not pygame.mouse.get_pressed()[0]:
            clicked = False
            pos = pygame.mouse.get_pos()
            for idx in range(len(buttons)):
                if buttons[idx].collidepoint(pos):
                    eventQueue.put((idx,'Released'))
                    break

        pygame.display.flip()

# Main Program Loop
def programLoop():
    eventFunctions = event.registry
    
    while True:
        nextEvent = eventQueue.get()
        button = nextEvent[0]
        state = nextEvent[1]

        try:
            eventFunctions[nextEvent](button,state)
        except KeyError as e:
            print('Unbound TouchPanel Event: ', e)

# System Setup
width = 1024
height = 600
screen = pygame.display.set_mode((width,height))
pygame.display.set_caption('TouchPanel')
backdrop = pygame.image.load('700_BlueGrey_Main_1024x600.jpg')
buttonBlack = [pygame.image.load('130x85_black.png'), pygame.image.load('130x85_sel.png')]
buttonBlue = [pygame.image.load('130x85_blue.png'), pygame.image.load('130x85_sel.png')]
buttonRed = [pygame.image.load('130x85_red.png'), pygame.image.load('130x85_sel.png')]
font = pygame.font.SysFont(None, 24)
eventQueue = queue.SimpleQueue()

# Buttons
buttonStates = [0, 0, 0, 0]
buttonPositions = [(35, 160),(35, 280),(35,400), (865,480)]
buttonCategories = [buttonBlack, buttonBlack, buttonBlack, buttonRed]
buttonLabels = [('Sources',((255,255,255),(0,0,0))), ('Volume',((255,255,255),(0,0,0))), ('Displays',((255,255,255),(0,0,0))), ('System Off',((255,255,255),(0,0,0)))]

# Run Display
displayThread = threading.Thread(target=displayLoop)
displayThread.start()

# Run Program
programThread = threading.Thread(target=programLoop)
programThread.start()

@event([0,1,2],'Pressed')
def subpageSelect(button, state):
    buttonStates[button] ^= 1
    for idx in range(len(buttonStates)):
        if idx != button:
            buttonStates[idx] = 0

@event(3,['Pressed','Released'])
def momentaryFB(button, state):
    buttonStates[button] ^= 1
