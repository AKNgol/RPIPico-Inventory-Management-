from mfrc522 import MFRC522
from machine import Pin
from time import sleep
import time


def readCardScanner(reader, isLoaded, cardID):
    """Reads an RFID card and outputs a boolean stating if a card was read and the card's ID

    Args:
        reader (MFRC522): MFRC522 object that represents a RFID reader   
        isLoaded (bool): Boolean that determines if a reader is currently reading a card
        cardID (int): int that holds the scanned card's ID

    Returns:
        isLoaded (bool): Boolean that determines if a reader is currently reading a card
        cardID (int): int that holds the scanned card's ID
    """
    (stat, tag_type) = reader.request(reader.REQIDL)
    if stat == reader.OK and not isLoaded:
        (stat, uid) = reader.SelectTagSN()
        if stat == reader.OK:
            card = int.from_bytes(bytes(uid),"little",False)
            print("READER CARD ID: "+str(card))
            isLoaded = True
            cardID = card
    #if isLoaded is true but the scanner isn't reading any card, set it to false
    if isLoaded and stat != 0:
        isLoaded = False
        cardID = None
    return isLoaded, cardID

def openDoor(doorNum):
    """Takes in an int doorNum that will spin the motor 90 degrees counter-clockwise (open left gate)
    if doorNum == 0 and clockwise (open right gate) if doorNum == 1

    Args:
        doorNum (int): int that determines the direction the motor will spin. 
    """

    IN1 = Pin(18,Pin.OUT) 
    IN2 = Pin(19,Pin.OUT)
    IN3 = Pin(16,Pin.OUT)
    IN4 = Pin(17,Pin.OUT)
    sensor = Pin(27, Pin.IN, Pin.PULL_UP) #.value() returns 0 when it detects an obj in between
    
    pins = [IN1, IN2, IN3, IN4]
    sequence = [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]
    revSequence = [[0,0,0,1],[0,0,1,0],[0,1,0,0],[1,0,0,0]]
    
    #sequence array will cause the motor to rotate clockwise 
    #revSequence will cause the motor to rotate counter-clockwise 
    def rotate(arr):
        for i in range(128):
            #128 steps for 90 deg?
            for step in arr:
                for i in range(len(pins)):
                    pins[i].value(step[i])
                    sleep(0.001)
                    
    if doorNum == 0:
        rotate(revSequence)  
        #Sleep for 3 seconds to avoid closing the gate immediately and wait for the motor to completely turn
        time.sleep(3)
        #While the sensor still detects the user's hand, sleep for a second
        while sensor.value() == 0:
            time.sleep(1)      
        time.sleep(1)
        rotate(sequence)
    else:
        rotate(sequence)
        time.sleep(3)
        while sensor.value() == 0:
            time.sleep(1)      
        time.sleep(1)
        rotate(revSequence)


if __name__ == "__main__":
    #Initialize variables for card reading
    isLeftLoaded = False 
    isRightLoaded = False
    leftCardID = None
    rightCardID = None
    #Initialize variables for opening the gate
    #Change the pin values depending on your wiring
    LEFT_BUTTON_PIN = 20
    RIGHT_BUTTON_PIN = 21
    blueButton = Pin(LEFT_BUTTON_PIN, Pin.IN) 
    blackButton = Pin(RIGHT_BUTTON_PIN, Pin.IN)
    #These values change depending on the RFID card
    #These two IDs were used for our use case.  
    blueID = 335783353
    blackID = 461520631
    
    while True:
        #Initialize and read card scanners to see if the bins are loaded
        reader = MFRC522(spi_id=0,sck=2,miso=4,mosi=3,cs=1,rst=0) #Values correspond to the GPIO pins being used
        reader.init()
        isLeftLoaded, leftCardID = readCardScanner(reader, isLeftLoaded, leftCardID)
        reader2 = MFRC522(spi_id=1,sck=10,miso=12,mosi=11,cs=9,rst=8)
        reader2.init()
        isRightLoaded, rightCardID = readCardScanner(reader2, isRightLoaded, rightCardID)
        
        #blue ID:  335783353
        #black ID: 461520631
        if blueButton.value() == 0:
            if blueID == leftCardID and isLeftLoaded:   
                print("left gate open")
                openDoor(0)
            elif blueID == rightCardID and isRightLoaded:
                print("right gate open")
                openDoor(1)
            
        if blackButton.value() == 0:
            if blackID == leftCardID and isLeftLoaded:   
                print("left gate open")
                openDoor(0)
            elif blackID == rightCardID and isRightLoaded:
                print("right gate open")
                openDoor(1)