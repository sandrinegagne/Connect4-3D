# Sandrine Gagne, February 1st 2023

import sys
import cv2
import pyzbar.pyzbar as pyzbar
import time
import os
try:
    from MotorControl import MotorMove
except:
    pass
from PyQt5 import QtWidgets

import os
from streak_counter import streak_counter
from UserInterface import userInterface

class gameboard(QtWidgets.QMainWindow):
    row_total = 4
    column_total = 4
    floor_total = 6
    board = []
    LastList = [0 for _ in range(16)]
    var = 0
    
    def __init__(self):
        # Function used to display the user interface (UI) and let the user use inputs to move the robot
        # to a certain position or tell the program he's done playing. 

        self.init_board()
        super().__init__()
        userInterface(self)    
        return
    
    def init_board(self):
        # Uses the global variables to generate the gameboard matrix

        x = self.row_total
        y = self.column_total
        z = self.floor_total
        self.board = [[[0 for k in range(x)] for j in range(y)] for i in range(z)]
        return

    def print_board(self):
        # Generate a visual representation of the gameboard to see what the robot / program knows of the game status.

        i = 1
        usermatrix = ('')
        for row in self.board:
            stringmatrix = ("\n\n                         A  B  C  D    floor = " + str(i) + "\n\n" + "1    " + str(row[0]) + "\n" + "2    " + str(
                row[1]) + "\n" + "3    " + str(row[2]) + "\n" + "4    " + str(row[3]))
            usermatrix = usermatrix + stringmatrix
            i += 1
        return usermatrix

    def add_piece(self, position_list):
        # Display the piece played on the UI to refresh the gameboard.

        row = int(position_list[0])
        column = int(position_list[1])
        player_id = str(position_list[2])
        player_id = str(position_list[2])
        limit_board = self.row_or_column_limit(row, column)
        if limit_board == 1:
            floor = self.determine_floor(row, column)
            if floor != None and limit_board == 1:
                self.board[floor - 1][row - 1][column - 1] = player_id
        return

    def delete_piece(self, row, column, floor):
        # Delete the piece played on the UI to refresh the gameboard.

        self.board[floor - 1][row - 1][column - 1] = 0
        return

    def row_or_column_limit(self, row, column):
        # Returns an error if the player is trying to play out of the gameboard range limit. 
        # Asks the player to play at another position. 

        row = int(row)
        column = int(column)
        if row > 4 or column > 4:
            print('This case is not reachable. Try again.')
            self.add_piece(self.player_played())
            return 0
        return 1

    def determine_floor(self, row, column):
        # Calculate the actual floor of the piece, knowing the previous pieces played at this exact position. 

        floor = 1
        row = int(row)
        column = int(column)
        for i in range(1, 7):
            if self.board[i - 1][row - 1][column - 1] != 0:
                floor = floor + 1   
        if floor > 6:
            print('This case is not reachable. Try again.')
            self.add_piece(self.player_played())
            return None
        else:
            print('floor value is : ', floor)               
        return floor

    def detect_win(self,play):
        streak_list = streak_counter(play,self.board,self.row_total,self.column_total,self.floor_total)
        for streak in streak_list:
            if streak == 4:
                return True
        return False

    def player_played(self):
        # Actualize the gameboard status with the new inputs

        player, column, row = self.take_picture()
        vision_list = [str(row), str(column), str(player)]
        print('vision list : ', vision_list)
        self.add_piece(vision_list)

        if self.push_button1.isChecked():
            #user_input = self.line_edit1.text()    # Uncomment thoses lines to use the player's input
            #entries = user_input.split()           # Comment thoses lines to use the vision input
            #self.add_piece(entries)                # " "  
            #self.line_edit1.clear()                # " "
            self.push_button1.setChecked(False)

        elif self.push_button2.isChecked():
            #user_input = self.line_edit2.text()    # Uncomment thoses lines to use the player's input
            #entries = user_input.split()           # Comment thoses lines to use the vision input
            #self.add_piece(entries)                # " "
            #self.line_edit2.clear()                # " "
            self.push_button2.setChecked(False)
        
        self.label.setText(self.print_board())
        return vision_list

    def submit_inputs_xyz(self):
        # Send the xyz coordinates entered from the UI to the motor control program, to move the robot to desired position. 

        xPosition = self.line_edit3.text()
        yPosition = self.line_edit4.text()
        zPosition = self.line_edit5.text()
        MotorMove.moveCart(MotorMove, int(xPosition), int(yPosition), int(zPosition))
        print(str(int(xPosition)) + str(int(yPosition)) + str(int(zPosition)))
        return # int(xPosition), int(yPosition), int(zPosition)

    def actual_position_xyz(self):
        # Receives the xyz coordinates from the motor control program and uses it to display it on the UI. 

        # Link with UI
        xActualPos = 1
        yActualPos = 2
        zActualPos = 2
        return xActualPos, yActualPos, zActualPos

    def submit_inputs_joints(self):
        # Send the joints coordinates entered from the UI to the motor control program, to move the robot to desired position.

        joint1Position = self.line_edit6.text()
        joint2Position = self.line_edit7.text()
        MotorMove.moveJoint(MotorMove, joint1Position, joint2Position)
        return int(joint1Position), int(joint2Position)

    def actual_position_joints(self):
        # Receives the joints coordinates from the motor control program and uses it to display it on the UI.

        # Link with UI
        joint1ActualPos = 1
        joint2ActualPos = 2
        return joint1ActualPos, joint2ActualPos

    def on_toggled(self, checked):
        if checked:
            self.toggle_button.setText("Automatic Mode")
        else:
            self.toggle_button.setText("Manual Mode")

        return


    def submit_auto_startSequence(self):
        # Starts the state machine to make the robot play

        return

    def submit_auto_resetSequence(self):
        # The robot stops its sequence and goes back home

        return

    def submit_man_goToHome(self):
        # Move the robot to his home position registered

        return

    def submit_man_goToPick45deg(self):
        # Move the robot to his pick position registered, where the pieces dispenser is placed at 45 deg

        return 

    def submit_man_goToPick0deg(self):
        # Move the robot to his pick position registered, where the pieces dispenser is placed at 0 deg

        return 
    
    def submit_man_goDown(self):
        # Move the z coordinate of the robot to its lower position

        return

    def submit_man_goToLS(self):
        # Move the z coordinate of the robot to its limit switch
        return 

    def submit_man_grip(self):
        # Activate the electromagnet

        return

    def submit_man_drop(self):
        # Disable the electromagnet

        return

    def update_selected_btn(self, btn):
        # When a position button is selected on the UI, selected_btn is updated here. 

        self.selected_btn = btn

    def update_selected_floor(self, floor):
        # When a floor button is selected on the UI, selected_floor is updated here. 

        self.selected_floor = floor

    def submit_gameboard_pos(self):
        # Once a position and a floor is selected, the gameboard position is updated and the robot can move to this position. 

        if self.selected_btn and self.selected_floor:
            self.button_played(self.selected_btn, self.selected_floor)

    def button_played(self, btn, floor):
        # Returns the xyz coordinates of the position where the robot has to move to. 
        # The xyz values are hard coded based on experimental moves. The values may changes according to the robot environment. 
        # The reference position is A1 and then the other positinos are automatically generated. 

        height_constant = 200
        height_init = 70
        gameboardPosition = [btn.text(), floor.text()]
        xA1Position = 1
        yA1Position = 1
        xgap = 5
        ygap = -5            # Use a negative value since the A1 position is at the top left

        match btn.text():
            case 'A1':
                xPosition = xA1Position
                yPosition = yA1Position
            case 'A2':
                xPosition = xA1Position
                yPosition = yA1Position + ygap
            case 'A3':
                xPosition = xA1Position
                yPosition = yA1Position + 2*ygap
            case 'A4':
                xPosition = xA1Position
                yPosition = yA1Position + 3*ygap

            case 'B1':
                xPosition = xA1Position + xgap
                yPosition = yA1Position
            case 'B2':
                xPosition = xA1Position + xgap
                yPosition = yA1Position + ygap
            case 'B3':
                xPosition = xA1Position + xgap
                yPosition = yA1Position + 2*ygap
            case 'B4':
                xPosition = xA1Position + xgap
                yPosition = yA1Position + 3*ygap

            case 'C1':
                xPosition = xA1Position + 2*xgap 
                yPosition = yA1Position 
            case 'C2':
                xPosition = xA1Position + 2*xgap 
                yPosition = yA1Position + ygap
            case 'C3':
                xPosition = xA1Position + 2*xgap 
                yPosition = yA1Position + 2*ygap
            case 'C4':
                xPosition = xA1Position + 2*xgap 
                yPosition = yA1Position + 3*ygap
            
            case 'D1':
                xPosition = xA1Position + 3*xgap 
                yPosition = yA1Position 
            case 'D2':
                xPosition = xA1Position + 3*xgap
                yPosition = yA1Position + ygap
            case 'D3':
                xPosition = xA1Position + 3*xgap
                yPosition = yA1Position + 2*ygap
            case 'D4':
                xPosition = xA1Position + 3*xgap
                yPosition = yA1Position + 3*ygap

        zPosition = int((floor.text())[5]) * height_constant + height_init
        #print("gameboardposition : ", gameboardPosition)
        #print("x  ", xPosition, "    y  ", yPosition)
        return xPosition, yPosition, zPosition

    def take_picture(self):
        # Take picture of the gameboard when the played button is press. Actualize the UI by comparing the actual status gameboard
        # and the previous status gameboard. 

        start_time = time.time()
        list = self.LastList[:]

        cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)        # Create a VideoCapture object 
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)         # Set the focus distance
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)        # Set the focus distance

        while list == self.LastList:
            i=0
            ret, img = cap.read()                       # Capture a frame from the webcam
            cv2.imshow("Webcam", img)                   # Show the frame

            if cv2.waitKey(1) & 0xFF == ord('q'):       # Exit the loop if the 'q' key is pressed
                break

            center = (img.shape[1]//2, img.shape[0]//2) # Crop the image and divise it into 16 squares
            size = (1080, 1080)
            img = cv2.getRectSubPix(img, size, center)

            height, width, _ = img.shape
            square_size = (height//4, width//4)

            for row in range(4):                        # Iterate through the rows and columns of the image
                for col in range(4):
                    square = img[row*square_size[0]:(row+1)*square_size[0], col*square_size[1]:(col+1)*square_size[1]]  # Extract each square of the image
                    gray_img = cv2.cvtColor(square, cv2.COLOR_BGR2GRAY)
                    
                    qr_codes = pyzbar.decode(gray_img)  # Detect QR codes
                    for qr_code in qr_codes:            # Add QR code to the list
                        data = qr_code.data.decode()    # Get QR code data
                        list[i]=(int(data))                
                    i+=1
                    
            os.system('cls' if os.name == 'nt' else 'clear')    # Print the game board
            for i in range(0, 16, 4):
                print(list[i:i+4])
            
            time.sleep(0.2)                             # Wait 0.2 seconds
        
        for i, (a, b) in enumerate(zip(list, self.LastList)):
            if a != b:
                x = i%4+1
                y = i//4+1
                if (a < 47):
                    Player = 'R'
                else:
                    Player = 'U'

        self.LastList = list
        #print("--- %s seconds ---" % (time.time() - start_time))
        cap.release()                                   # Release the VideoCapture object and Close all the windows
        cv2.destroyAllWindows()
        return Player, x, y

if __name__ == "__main__":
    gm = gameboard
    app = QtWidgets.QApplication(sys.argv)
    window = gameboard()
    window.show()
    sys.exit(app.exec_())