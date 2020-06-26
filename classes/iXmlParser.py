"""
Title - IPP <interpret.py>
Author - Maroš Geffert
Login - <xgeffe00>
"""

import xml.etree.ElementTree as ET
import re
from classes.iArgsErrors import *

ZERO_ADDRESS = ['CREATEFRAME', 'PUSHFRAME', 'POPFRAME', 'RETURN', 'BREAK']
ONE_ADDRESS = ['LABEL', 'JUMP', 'EXIT', 'DPRINT', 'WRITE', 'POPS', 'PUSHS', 'CALL', 'VAR', 'DEFVAR']
TWO_ADDRESS = ['MOVE', 'INT2CHAR', 'READ', 'STRLEN', 'TYPE', 'NOT']
THREE_ADDRESS = ['ADD', 'SUB', 'MUL', 'IDIV', 'LT', 'GT', 'EQ', 'OR', 'NOT', 'STRI2INT', 'CONCAT', 'GETCHAR', 'SETCHAR',
                 'JUMPIFEQ', 'JUMPIFNEQ', 'AND']
VAR_SYMBOL_SYMBOL = ['ADD', 'SUB', 'MUL', 'IDIV', 'LT', 'GT', 'EQ', 'OR',
                     'STRI2INT', 'CONCAT', 'GETCHAR', 'SETCHAR', 'AND']


class XmlParser(Arg_Error_Checker):

    def __init__(self, ROOT, instruction_List):
        super().__init__()
        self.ROOT = ROOT
        self.instruction_List = instruction_List

    def parse(self):
        self.check_XML_struct()
        self.check_Syntax()

    ########################################################################################################################

    def check_XML_struct(self):

        # Control if root tag is 'program'
        if self.ROOT.tag != 'program':
            self.exit_program(32, 'ERROR: XML file is in bad format')

        # Control if attribut is 'language'
        if 'language' in self.ROOT.attrib:
            if str(self.ROOT.attrib['language']).lower() == 'ippcode20':
                pass
            else:
                self.exit_program(32, 'ERROR: Bad name of XMLheader')
        else:
            self.exit_program(32, 'ERROR: Missing atributte language')

        # Control instructions if
        instruction_order_numbers = []
        inst_opcode_order = ['instruction', 'opcode', 'order']

        for instruction in self.ROOT:
            if ((inst_opcode_order[0] not in instruction.tag) or
                    (inst_opcode_order[1] not in instruction.attrib) or
                    (inst_opcode_order[2] not in instruction.attrib)):
                self.exit_program(32, 'ERROR: Missing attribute')
            else:
                instruction_order_numbers.append(instruction.attrib['order'])

            for argument in instruction:
                # Nazov elementu
                if re.match('^(arg)\d+$', argument.tag) is None:
                    self.exit_program(32, 'ERROR: Bad name of element')
                if 'type' not in argument.attrib:
                    self.exit_program(31, 'ERROR: Missing attribute')
                if argument.attrib['type'] not in ['int', 'string', 'label', 'bool', 'type', 'var', 'nil']:
                    self.exit_program(32, 'ERROR: Not allowed value (type)')

        if len(instruction_order_numbers) != len(set(instruction_order_numbers)):
            self.exit_program(32, 'ERROR: Instruction with duplicit value attribute order')
        for x in instruction_order_numbers:
            try:
                if int(x) <= 0:
                    self.exit_program(32, 'ERROR: Argument order not allowed ')
            except:
                self.exit_program(32, 'ERROR: Argument order cant be -> {} '.format(type(x)))

    #######################################################################################################################

    def check_Syntax(self):
        COUNT = 0
        for instruction in self.ROOT:
            COUNT += 1
            count_Of_Instructions = len(list(instruction))
            attr_opcode = instruction.attrib['opcode']

            # ZERO ADDRESS INSTRUCTION
            if attr_opcode.upper() in ZERO_ADDRESS and count_Of_Instructions == 0:
                INSTRUCTION_OBJECT = self.instruction(attr_opcode, count_Of_Instructions)
                self.instruction_List.insert_instruction(INSTRUCTION_OBJECT)

            # ONE ADDRESS INSTRUCTION
            elif attr_opcode.upper() in ONE_ADDRESS and count_Of_Instructions == 1:
                # INSTRUCTION (<var>)
                if attr_opcode.upper() in ['DEFVAR', 'POPS']:
                    var = instruction[0]
                    self.checkVar(var)
                    INSTRUCTION_OBJECT = self.instruction(attr_opcode, count_Of_Instructions, arg1=instruction[0])
                    self.instruction_List.insert_instruction(INSTRUCTION_OBJECT)
                # INSTRUCTION (<label>)
                elif attr_opcode.upper() in ['CALL', 'JUMP', 'LABEL']:
                    label = instruction[0]
                    self.checkLabel(label)
                    INSTRUCTION_OBJECT = self.instruction(attr_opcode, count_Of_Instructions, arg1=label)
                    self.instruction_List.insert_instruction(INSTRUCTION_OBJECT)
                # INSTRUCTION (<symbol>)
                elif attr_opcode.upper() in ['PUSHS', 'WRITE', 'EXIT', 'DPRINT']:
                    symbol = instruction[0]
                    self.checkSymb(symbol)
                    INSTRUCTION_OBJECT = self.instruction(attr_opcode, count_Of_Instructions, arg1=symbol)
                    self.instruction_List.insert_instruction(INSTRUCTION_OBJECT)

            # TWO ADDRESS INSTRUCTION
            elif attr_opcode.upper() in TWO_ADDRESS and count_Of_Instructions == 2:

                # Rotate args, if are in bad order
                iArgument1 = instruction[0].tag[3:]
                iArgument2 = instruction[1].tag[3:]
                if int(iArgument1) > int(iArgument2):
                    tmp = instruction[1]
                    instruction[1] = instruction[0]
                    instruction[0] = tmp
                else:
                    pass

                # INSTRUCTION (<var> <symbol>)
                if attr_opcode.upper() in ['MOVE', 'INT2CHAR', 'STRLEN', 'TYPE', 'NOT']:
                    var = instruction[0]
                    symbol = instruction[1]
                    self.checkVar(var)
                    self.checkSymb(symbol)
                    INSTRUCTION_OBJECT = self.instruction(attr_opcode, count_Of_Instructions,
                                                          arg1=var, arg2=symbol)
                    self.instruction_List.insert_instruction(INSTRUCTION_OBJECT)
                # INSTRUCTION (<var> <type>)
                if attr_opcode.upper() in ['READ']:
                    var = instruction[0]
                    types = instruction[1]
                    self.checkVar(var)
                    self.checkType(types)
                    INSTRUCTION_OBJECT = self.instruction(attr_opcode, count_Of_Instructions,
                                                          arg1=var, arg2=types)
                    self.instruction_List.insert_instruction(INSTRUCTION_OBJECT)

            # THREE ADDRESS INSTRUCTION
            elif attr_opcode.upper() in THREE_ADDRESS and count_Of_Instructions == 3:

                # Rotate args, if are in bad order
                iArgument1 = instruction[0].tag[3:]
                iArgument2 = instruction[2].tag[3:]
                if int(iArgument1) > int(iArgument2):
                    tmp = instruction[2]
                    instruction[2] = instruction[0]
                    instruction[0] = tmp
                else:
                    pass

                # INSTRUCTION (<var> <symbol> <symbol>)
                if attr_opcode.upper() in VAR_SYMBOL_SYMBOL:
                    var = instruction[0]
                    symbol = instruction[1]
                    symbol_symbol = instruction[2]
                    self.checkVar(var)
                    self.checkSymb(symbol)
                    self.checkSymb(symbol_symbol)
                    INSTRUCTION_OBJECT = self.instruction(attr_opcode, count_Of_Instructions, arg1=var,
                                                          arg2=symbol, arg3=symbol_symbol)
                    self.instruction_List.insert_instruction(INSTRUCTION_OBJECT)
                # INSTRUCTION (<label> <symbol> <symbol>)
                elif attr_opcode.upper() in ['JUMPIFEQ', 'JUMPIFNEQ']:
                    label = instruction[0]
                    symbol = instruction[1]
                    symbol_symbol = instruction[2]
                    self.checkLabel(label)
                    self.checkSymb(symbol)
                    self.checkSymb(symbol_symbol)
                    INSTRUCTION_OBJECT = self.instruction(attr_opcode, count_Of_Instructions,
                                                          arg1=label, arg2=symbol, arg3=symbol_symbol)
                    self.instruction_List.insert_instruction(INSTRUCTION_OBJECT)
            else:
                self.exit_program(32, 'ERROR: Bad or missing opcode of instruction')

    ########################################################################################################################

    def checkVar(self, instruction):
        if instruction.attrib['type'] != 'var':
            self.exit_program(52, 'ERROR: Bad atributte type in label')
        if instruction.text is None or not re.match('^(GF|LF|TF)@(_|-|\$|&|%|\*|[a-zA-Z])(_|-|\$|&|%|\*|[a-zA-Z0-9])*$',
                                                    instruction.text):
            self.exit_program(32, 'ERROR: Bad label')

    def checkLabel(self, instruction):
        if instruction.attrib['type'] != 'label':
            self.exit_program(52, 'ERROR: Bad attribute type in variable')
        if instruction.text is None or not re.match('^(_|-|\$|&|%|\*|[a-zA-Z])(_|-|\$|&|%|\*|[a-zA-Z0-9])*$',
                                                    instruction.text):
            self.exit_program(32, 'ERROR: Bad name of variable')

    def checkSymb(self, instruction):
        if instruction.attrib['type'] == 'int':
            if instruction.text is None or not re.match('^([+-]?[1-9][0-9]*|[+-]?[0-9])$', instruction.text):
                self.exit_program(32, 'ERROR: Bad value of int')

        elif instruction.attrib['type'] == 'bool':
            if instruction.text is None or not re.match('^(true|false)$', instruction.text):
                self.exit_program(32, 'ERROR: Bad value of bool')

        elif instruction.attrib['type'] == 'string':
            if instruction.text is None:
                instruction.text = ''
            elif not re.search('^(\\\\[0-9]{3}|[^\s\\\\#])*$', instruction.text):
                self.exit_program(32, 'ERROR: Bad value of string')
            else:
                instruction.text = re.sub(r'\\([0-9]{3})', lambda x: chr(int(x.group(1))), instruction.text)

        elif instruction.attrib['type'] == 'var':
            self.checkVar(instruction)

        elif instruction.attrib['type'] == 'nil':
            pass
        else:
            self.exit_program(32, 'ERROR: Bad value of nil')

    def checkType(self, instruction):
        if instruction.attrib['type'] != 'type':
            self.exit_program(52, 'ERROR: Bad atributte of type')
        if instruction.text is None or not re.match('^(int|bool|string)$', instruction.text):
            self.exit_program(32, 'ERROR: Bad type')

    ########################################################################################################################

    class instruction():
        def __init__(self, opcode, howmuch, arg1=None, arg2=None, arg3=None):
            self.opcode = opcode
            self.arg_count = 0
            if howmuch >= 1:
                self.arg1 = {'type': arg1.attrib['type'], 'text': arg1.text}
                self.arg_count = 1
                if howmuch >= 2:
                    self.arg2 = {'type': arg2.attrib['type'], 'text': arg2.text}
                    self.arg_count = 2
                    if howmuch >= 3:
                        self.arg3 = {'type': arg3.attrib['type'], 'text': arg3.text}
                        self.arg_count = 3
