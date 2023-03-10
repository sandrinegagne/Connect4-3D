# Jacob Lambert, January 17th 2023

from GameBoardRepresentation import gameboard
import random
import sys
from PyQt5 import QtWidgets
import os
from streak_counter import streak_counter

class AI():
    def __init__(self, gb):
        self.gb = gb
        self.AI_id = 2
        self.opponent_id = 4

        return
    

    def detect_win(self,play,player_id):
        for streak in streak_counter(play,self.gb.board,self.gb.row_total,self.gb.column_total,self.gb.floor_total,player_id):
            if streak == 4:
                return True
        return False
    #This function returns a list of all possible positions on the board
    def get_positions(self):
        possible_positions = []
        for i in range(self.gb.row_total):
            for j in range(self.gb.column_total):
                for k in range(self.gb.column_total):
                    if self.gb.board[i][j][k] == 0:  
                        possible_positions.append([i+1,j+1,k+1])
                        break

        return possible_positions

    #This function rates a play based on the number of pieces in a row
    def rate_play(self,play):
        strength=0
        #This rates the offensive strength of the play
        for streak in streak_counter(play,self.gb.board,self.gb.row_total,self.gb.column_total,self.gb.floor_total):
            if streak == 1:
                strength=strength+11
            elif streak == 2:
                strength=strength+101
            elif streak == 3:
                strength=strength+1001
            elif streak == 4:
                strength=strength+10001

        opponent_play = [play[0],play[1],self.opponent_id]
        #This rates the defensive strength of the play
        for streak in streak_counter(opponent_play,self.gb.board,self.gb.row_total,self.gb.column_total,self.gb.floor_total):
            if streak == 1:
                strength=strength+10
            elif streak == 2:
                strength=strength+100
            elif streak == 3:
                strength=strength+1000
            elif streak == 4:
                strength=strength+10000
    
        return strength

    #This function chooses the best play
    def choose_play(self):
        possible_positions = self.get_positions()
        max_strength = 0
        best_plays = []
        for position in possible_positions:
            play = [position[0]]+[position[1]]+[position[2]]+[self.AI_id]
            strength = self.rate_play(play)
            if strength > max_strength:
                max_strength = strength
                best_plays = [play]
            elif strength == max_strength:
                best_plays.append(play)
        best_play = random.choice(best_plays)

        return best_play
 

