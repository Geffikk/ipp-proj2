"""
Title - IPP <interpret.py>
Author - Maroš Geffert
Login - <xgeffe00>
"""

from classes.iArgsErrors import *

class DataStack(Arg_Error_Checker):

    def __init__(self):
        self.stack = []

    def pushValue(self, value):
        self.stack.append(value)

    def popValue(self):
        if len(self.stack) > 0:
            return self.stack.pop()
        else:
            self.exit_program(56, 'Error: You cannot pop empty stack')

    def get_stack(self):
        return self.stack

