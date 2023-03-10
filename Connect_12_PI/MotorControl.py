#Alexandre Baril: Created: january 16 2023, Sherbrooke
#Alexandre Baril: Modified: february 8 2023, Sherbrooke

import struct
import numpy as np
import serial
import time
import sys
import serial.tools.list_ports
from PyQt5 import QtWidgets
app = QtWidgets.QApplication(sys.argv)
#from GameBoardRepresentation import gameboard
#game = gameboard()

theta = 0.001
phi = 0.001

class MotorMove:
    ### Math variable
    BicepLen:float = 0.1425
    ForearmLen:float = 0.1425
    J1Offset:int = 0
    J2Offset:int = 0

    ## Communication variables
    mssg1:str = "0000"
    mssg2:str = "0000"
    mssg3:str = "0000"
    mssg4:str = "0"             #default is manual
    mssg5:str = "0"             #default is Home
    mssg:str = "000000000000"

    Zpos:int = 0 #zposition

    ## Motor control
    
    vari:int = 1
    vari2:int = 1
    

    #serOpenCR = serial.Serial('/dev/ttyUSB0', 9600)

    #serOpenCR = serial.tools.list_ports.comports(include_links=False)
    serOpenCR = serial.Serial('COM5', baudrate= 9600, timeout=2.0)

    ## Methods
    def __init__(self):
        self.init_motor(self)

    def sendMsg(self, Shouldermessage:int, Elbowmessage:int):
        '''
        communication order:    [j1 j1 j1 j1  --> int 0-9 times 4
                                j2 j2 j2 j2   --> int 0-9 times 4
                                z z z z       --> int 0-9 times 4
                                mode          --> int 0 = manual, 1 = automatic
                                state          --> int 0-9: 0 = state no1, 1 = state no2, [...], 9 = state no10
                                ]
        ex: 01230123012300
        '''
        
        ### First Joint Position
        Shoulderlength = len(str(Shouldermessage))
        if Shoulderlength == 1:
            mssg1 =  "000" + str(Shouldermessage)
        elif Shoulderlength == 2:
            mssg1 =  "00" + str(Shouldermessage)
        elif Shoulderlength == 3:
            mssg1 =  '0' + str(Shouldermessage)
        elif Shoulderlength == 4:
            mssg1 = str(Shouldermessage)
        if mssg1 == "":
            mssg1 = "0000"

        ### Second Joint Position
        Elbowlength = len(str(Elbowmessage))
        if Elbowlength == 1:
            mssg2 =  "000" + str(Elbowmessage)# + '|'
        elif Elbowlength == 2:
            mssg2 =  "00" + str(Elbowmessage)# + '|'
        elif Elbowlength == 3:
            mssg2 =  '0' + str(Elbowmessage)# + '|'
        elif Elbowlength == 4:
            mssg2 = str(Elbowmessage)# + '|'
        if mssg2 == "":
            mssg2 = "0000"
        
        ### Z Position
        '''
        floor0 = 2750
        floor1 = 2450
        floor2 = 2150
        floor3 = 1850
        floor4 = 1550
        floor5 = 1250
        '''
        Zlength = len(str(self.Zpos))
        if Zlength == 1:
            mssg3 =  "000" + str(self.Zpos)# + '|'
        elif Zlength == 2:
            mssg3 =  "00" + str(self.Zpos)# + '|'
        elif Zlength == 3:
            mssg3 =  '0' + str(self.Zpos)# + '|'
        elif Zlength == 4:
            mssg3 = str(self.Zpos)# + '|'
        if mssg3 == "":
            mssg3 = "0000"

        ### Mode, Automatic (1) or Manual (0)
        mssg4 = "1"

        ### States:
        '''
        fromPi_Idle                 = 0
        fromPi_auto_startSequence   = 1
        fromPi_auto_resetSequence   = 2

        fromPi_man_Idle             = 0
        fromPi_man_goToHome         = 1
        fromPi_man_goToPick         = 2
        fromPi_man_goToPlace        = 3
        fromPi_man_goDownPlace      = 4
        fromPi_man_goDownPick       = 5
        fromPi_man_goToLS           = 6
        fromPi_man_grip             = 7
        fromPi_man_drop             = 8
        '''
        
        self.mssg5 = "1"

        mssg = mssg1 + mssg2 + mssg3 + self.mssg4 + self.mssg5
        print(mssg)
        if self.serOpenCR.isOpen():
            self.serOpenCR.write(mssg.encode().rstrip())
            print("msg Sent: " + mssg)
        
        self.mssg5 = "0"
        return

    def readMsg(self):
        answer:str = ""
        if self.serOpenCR.isOpen():
            StartTime = time.time()
            while self.serOpenCR.inWaiting()==0:
                #TimeElapsed = time.time() - StartTime
                '''if (time.time() - StartTime) >= 2:     ##timeout after 2sec
                    print("timeout achieved")
                    break
                else:
                    #print(round(2.0 - (time.time() - StartTime), 1))
                    pass'''
                pass
            while  self.serOpenCR.inWaiting() > 0:
                answer = self.serOpenCR.readline().decode()
                print("Answer is : " + answer)
                self.serOpenCR.flushInput()
        return int(answer)

    def rad2Servo(self, angleRad:float):
        angleServo = angleRad * 4095 / (2*np.pi)
        return angleServo

    def lawOfCos(self, a, b, c):
        modulus = np.power(a, 2) + np.power(b, 2) - np.power(c, 2)
        return np.arccos(modulus / (2*a*b))

    def cart2cyl(self, cartX:float, cartY:float):
        '''
        C2:float = (cartX**2 + cartY**2 - self.BicepLen**2 - self.ForearmLen**2) / (2 * self.BicepLen * self.ForearmLen)
        S2:float = 1-C2**(0.5)  
        theta = np.arccos(C2)     ###cos-1
        phiX = (self.ForearmLen * S2 * cartX) + ((self.BicepLen + self.ForearmLen*C2)*cartY)
        phiY = ((self.BicepLen + self.ForearmLen*C2)*cartX)-(self.ForearmLen * S2 * cartY)
        phi = np.arctan2(((self.ForearmLen * S2 * cartX) + ((self.BicepLen + self.ForearmLen*C2)*cartY)), (((self.BicepLen + self.ForearmLen*C2)*cartX)-(self.ForearmLen * S2 * cartY)))
        '''
        '''
        distance = np.sqrt(cartX*cartX + cartY*cartY)
        theta1 = np.arctan2(cartX, cartY)
        theta2 = self.lawOfCos(self, distance, self.BicepLen, self.ForearmLen)
        theta = theta1 + theta2

        phi = self.lawOfCos(self, self.BicepLen, self.ForearmLen, distance)
        '''

        t2:float = (cartX**2 + cartY**2 - self.BicepLen**2 - self.ForearmLen**2) / (2 * self.BicepLen * self.ForearmLen)
        theta2:float = np.arccos(t2)
        t1 = (self.ForearmLen*np.sin(theta2)) / (self.BicepLen*np.cos(theta2))
        theta1:float = np.arctan(cartX/cartY) + np.arctan(t1)

        theta = theta1
        phi = theta2

        J1:int = round(self.rad2Servo(self, theta) * 2) + self.J1Offset
        J2:int = round(self.rad2Servo(self, phi)) + self.J2Offset

        if J1 > 4095:
            J1 = 4095
        if J2 > 4095:
            J2 = 4095

        print("phi: " + str(J1))
        print("theta: " + str(J2))

        return J1, J2

    def Interpolation(self, posXStart: int, posYStart: int, posXEnd: int, posYEnd: int):
        jointAngles = self.cart2cyl(self, posXStart, posYStart)
        increment = 100
        posx = posXStart
        posy = posYStart
        diffX = posXEnd - posXStart
        diffY = posYEnd - posYStart
        #print(str(diffX) + "\t" + str(diffY))
        stepX = diffX / increment
        stepY = diffY / increment
        
        positionsX = list()
        positionsY = list()
        jointAngles = list()
        for i in range(increment):
            positionsX.append(posXStart + (i+1)*stepX)
            positionsY.append(posYStart + (i+1)*stepY)
            #print("i: " + str(i) + "\tpositionX: " + str(positionsX[i]) + "  \tpositionY: " + str(positionsY[i]))
            jointAngles.append(self.cart2cyl(self, positionsX[i], positionsY[i]))
            #print("angle: " + str(jointAngles[i]))
        
        return positionsX, positionsY

    def moveZ(self, height):
        motorEncoder = 0
        while motorEncoder < height:
            #motor.movedown
            #serOpenCR.read()
            #print(motorEncoder)
            motorEncoder += 5
        while motorEncoder > 0:
            #motor.moveup
            #serOpenCR.read()
            #print(motorEncoder)
            motorEncoder -= 10
        
        return

    def pos2cart(self, letterPos: str, numberPos: str, floorLevel: str):
        match letterPos:
            case 'A':
                posx = -75
            case 'B':
                posx = -25
            case 'C':
                posx = 25
            case 'D':
                posx = 75

        match numberPos:
            case '1':
                posy = 0
            case '2':
                posy = 50
            case '3':
                posy = 100
            case '4':
                posy = 150

        match floorLevel:
            case 'f0':
                ztarget = 300
            case 'f1':
                ztarget = 250
            case 'f2':
                ztarget = 200
            case 'f3':
                ztarget = 150
            case 'f4':
                ztarget = 100
            case 'f5':
                ztarget = 50
        
        #print(str(posx) + "\t" + str(posy))
        return posx, posy, ztarget

    def moveCart(self, gameXpos, gameYpos, gameZpos):

        servoShoulderAngle, servoElbowAngle = self.cart2cyl(self, gameXpos, gameYpos)
        self.sendMsg(self, servoShoulderAngle, servoElbowAngle)
    
    def moveJoint(self, J1, J2):
        self.sendMsg(self, J1, J2)
        #msgReceived = self.readMsg(self)

'''while(True):
    vari = 1000
    vari2 = 500
    servoShoulderAngle, servoElbowAngle = MotorMove.cart2cyl(MotorMove, vari, vari2)
    MotorMove.sendMsg(MotorMove, vari, vari2)
    msgReceived = MotorMove.readMsg(MotorMove)
    time.sleep(2)

    vari = 2000
    vari2 = 1500
    servoShoulderAngle, servoElbowAngle = MotorMove.cart2cyl(MotorMove, vari, vari2)
    MotorMove.sendMsg(MotorMove, vari, vari2)
    msgReceived = MotorMove.readMsg(MotorMove)
    time.sleep(2)'''


