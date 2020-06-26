"""
Title - IPP <interpret.py>
Author - Maroš Geffert
Login - <xgeffe00>
"""

from classes.iArgsErrors import *

class InstructionList(Arg_Error_Checker):

    def __init__(self):
        super().__init__()
        self.iInstructions = {}
        self.iInstructions_in_file = 0
        self.iInstructionsCounter = 1
        self.iInstructionsDoneNumber = 0
        self.iLabels = {}

    def insert_instruction(self, instruction):
        self.iInstructions_in_file += 1
        self.iInstructions[self.iInstructions_in_file] = instruction

        if instruction.opcode == 'LABEL':
            label_name = instruction.arg1['text']
            if label_name in self.iLabels:
                self.exit_program(52, 'ERROR: Label \'{}\' already exist !'.format(label_name))
            else:
                self.iLabels[label_name] = self.iInstructions_in_file

    def get_next_instruction(self):

        if self.iInstructionsCounter <= self.iInstructions_in_file:
            self.iInstructionsDoneNumber += 1
            self.iInstructionsCounter += 1
            return self.iInstructions[self.iInstructionsCounter - 1]
        else:
            return None

    def jump_to_label(self, i_arg_label, iReturn=False):

        if iReturn == False:
            label = i_arg_label['text']
        else:
            label = i_arg_label

        if label in self.iLabels:
            self.iInstructionsCounter = self.iLabels[label] + 1
        elif iReturn == True:
            self.iInstructionsCounter = label
        else:
            self.exit_program(52, 'ERROR: Label doesnt exist')

    def check_label(self, i_arg_label, iReturn=False):
        if iReturn == False:
            label = i_arg_label['text']
        else:
            label = i_arg_label

        if label in self.iLabels:
            pass
        else:
            self.exit_program(52, 'ERROR: Label doesnt exist')

    def get_instruction_counter(self):
        return self.iInstructionsCounter - 1

    def get_instruction_done_number(self):
        return self.iInstructionsDoneNumber - 1