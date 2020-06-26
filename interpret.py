#!/usr/bin/env python3.8
"""
Title - IPP <interpret.py>
Author - Maroš Geffert
Login - <xgeffe00>
"""

from classes.iInstructionList import *
from classes.iXmlParser import *
from classes.iDataStack import *
from classes.iRootElement import *

def Main():
    # <Class> for arguments
    argument_checker = Arg_Error_Checker()
    # Control arguments
    argument_checker.check()
    # Input file for READ function
    iInputFile = argument_checker.get_input_path()
    try:
        iInputFile = open(iInputFile, 'r')
    except:
        pass
    # Generate instruction list
    instList = InstructionList()
    # <Class> Root Tree
    root = Root_Element(argument_checker.get_file_path())
    # Make a root tree
    root = root.make_Root_Tree()
    # <Class> XML strucutre
    xmlParser = XmlParser(root, instList)
    # Parse XML and check XML structure
    xmlParser.parse()
    # <Class> Generate data stack
    dataStack = DataStack()

    cnt = 0
    function_flag = False
    function_flag2 = False

    while True:
        # Load actual instruction
        actual_inst = instList.get_next_instruction()
        # If actual instruction is none end program
        if actual_inst is None:
            exit(0)

        # <Class> Make interpret class
        interpret = Instruction(actual_inst, dataStack, instList, function_flag, function_flag2, iInputFile)
        # process instructions (interpret)
        interpret.choose_operation()

        # Flags for functions (poping frames)
        function_flag = interpret.function_flag
        function_flag2 = interpret.function_flag2
        cnt += 1


class Instruction(Arg_Error_Checker):

    def __init__(self, instruction, dataStack, instList, function_flag, function_flag2, iInputFile):
        """Initialization of internal strcture of XML <instruction> node"""
        super().__init__()
        self.dataStack = dataStack
        self.iList = instList
        self.instruction = instruction
        self.instruction_order = 0
        self.remeberLine = 0
        self.function_flag = function_flag
        self.function_flag2 = function_flag2
        self.iInputFile = iInputFile

    def choose_operation(self):
        """Choose opcode instruction"""
        if self.instruction.opcode.upper() == "BREAK":
            self.iBreak()
        elif self.instruction.opcode.upper() == "WRITE" or self.instruction.opcode == "DPRINT":
            self.iWrite()
        elif self.instruction.opcode.upper() == "CREATEFRAME":
            self.iCreateframe()
        elif self.instruction.opcode.upper() == "PUSHFRAME":
            self.iPushframe()
        elif self.instruction.opcode.upper() == "POPFRAME":
            self.iPopframe()
        elif self.instruction.opcode.upper() == "RETURN":
            self.iReturn()
        elif self.instruction.opcode.upper() == "DEFVAR":
            self.iDefvar()
        elif self.instruction.opcode.upper() == "CALL":
            self.iCall()
        elif self.instruction.opcode.upper() == "LABEL":
            self.iLabel()
        elif self.instruction.opcode.upper() == "JUMP":
            self.iJump()
        elif self.instruction.opcode.upper() == "EXIT":
            self.iExit()
        elif self.instruction.opcode.upper() == "INT2CHAR":
            self.iInt2Char()
        elif self.instruction.opcode.upper() == "READ":
            self.iRead()
        elif self.instruction.opcode.upper() == "TYPE":
            self.iType()
        elif self.instruction.opcode.upper() == "ADD":
            self.iAdd()
        elif self.instruction.opcode.upper() == "IDIV":
            self.iDiv()
        elif self.instruction.opcode.upper() == "SUB":
            self.iSub()
        elif self.instruction.opcode.upper() == "MUL":
            self.iMul()
        elif self.instruction.opcode.upper() == "LT" or self.instruction.opcode.upper() == "GT" or self.instruction.opcode.upper() == "EQ":
            self.iLtGtEq()
        elif self.instruction.opcode.upper() == "AND" or self.instruction.opcode.upper() == "OR":
            self.iAndOr()
        elif self.instruction.opcode.upper() == "NOT":
            self.iNot()
        elif self.instruction.opcode.upper() == "MOVE":
            self.iMove()
        elif self.instruction.opcode.upper() == "CONCAT":
            self.iConcat()
        elif self.instruction.opcode.upper() == "STRLEN":
            self.iStrlen()
        elif self.instruction.opcode.upper() == "GETCHAR":
            self.iGetchar()
        elif self.instruction.opcode.upper() == "SETCHAR":
            self.iSetchar()
        elif self.instruction.opcode.upper() == "JUMPIFEQ" or self.instruction.opcode.upper() == "JUMPIFNEQ":
            self.iJumpifeqJumpifneq()
        elif self.instruction.opcode.upper() == "STRI2INT":
            self.iStri2Int()
        elif self.instruction.opcode.upper() == "PUSHS":
            self.iPush()
        elif self.instruction.opcode.upper() == "POPS":
            self.iPop()

        else:
            self.exit_program(99, 'ERROR: Opcode of instruction doesn\'t exist')

    """ ZERO ADDRESS INSTRUCTIONS """
    def iBreak(self):
        # Just print information about interpret
        print_to_stderr('Pozicia v kode: {}'.format(self.iList.get_instruction_counter()))
        print_to_stderr('Pocet vykonanych instrukcii: {}'.format(self.iList.get_instruction_done_number()))
        print_to_stderr(
            'Datovy zasobnik: {} (SPOLU: {})'.format(self.dataStack.get_stack(), len(self.dataStack.get_stack())))

        if Frames.iGetAlsoEmptyFrame('LF') == {}:
            print_to_stderr('Lokalny ramec (LF): {}'.format(Frames.iGetAlsoEmptyFrame('LF')))
        else:
            print_to_stderr('Lokalny ramec (LF): {}'.format(Frames.iGet('LF'), len(Frames.iGet('LF'))))
        if Frames.iGetAlsoEmptyFrame('TF') == {}:
            print_to_stderr('Docasny ramec (TF): {}'.format(Frames.iGetAlsoEmptyFrame('GF')))
        else:
            print_to_stderr('Docasny ramec (TF): {} (SPOLU: {})'.format(Frames.iGet('TF'), len((Frames.iGet('TF')))))
        if Frames.iGetAlsoEmptyFrame('GF') == {}:
            print_to_stderr('Globalny ramec (GF): {}'.format(Frames.iGetAlsoEmptyFrame('GF')))
        else:
            print_to_stderr('Globalny ramec (GF): {} (SPOLU: {})'.format(Frames.iGet('GF'), len(Frames.iGet('GF'))))

    def iCreateframe(self):
        # Create a temporary frame
        self.iCheckCountOfArgs(0)
        Frames.temporaryFrame = {}

    def iPushframe(self):
        # Create a local frame
        self.iCheckCountOfArgs(0)
        if self.function_flag == True:
            self.function_flag2 = True

        if Frames.temporaryFrame == None:
            self.exit_program(55, 'ERROR: You didnt create a temporary frame !')

        Frames.stack.append(Frames.temporaryFrame)
        Frames.localFrame = Frames.stack[-1]
        Frames.temporaryFrame = None

    def iPopframe(self):
        # Destroy a local frame
        self.iCheckCountOfArgs(0)

        if Frames.localFrame == None:
            self.exit_program(55, 'ERROR: Frame is not initialized')

        if len(Frames.stack) < 1:
            self.exit_program(52, "ERROR: You cant pop empty stack !")

        if self.function_flag == True:
            if self.function_flag2 != True:
                self.exit_program(55, 'ERROR: Missing frame')

        self.function_flag = False
        self.function_flag2 = False

        # Store top value from stack
        topOfStack = Frames.stack[-1]

        if topOfStack is None:
            self.exit_program(55, 'ERROR: Local frame is empty !')
        Frames.stack.pop(-1)
        try:
            Frames.localFrame = Frames.stack[-1]
        except:
            pass

        # Push value to temporary frame
        Frames.temporaryFrame = topOfStack

    def iReturn(self):
        # Return from function
        self.iCheckCountOfArgs(0)
        self.instruction_order = self.dataStack.popValue() + 1
        self.iList.jump_to_label(self.instruction_order, True)

    """ ONE ADDRESS INSTRUCTION """
    def iDefvar(self):
        self.iCheckCountOfArgs(1)
        Frames.iAdd(self.instruction.arg1['text'])

    def iWrite(self):
        self.iCheckCountOfArgs(1)
        value = self.instruction.arg1['text']

        if self.instruction.arg1['type'] == 'var':
            value = Frames.iGet(self.instruction.arg1['text'])

        # If type is boolean convert it to string for print
        if type(value) == bool:
            if value == True:
                value = "true"
            else:
                value = "false"

        # Print to stderr
        if self.instruction.opcode == "DPRINT":
            result = str(value)
            print_to_stderr(result)
        # Normal print
        else:
            result = str(value)
            print(result, end='')

    def iCall(self):
        # Count of instructions
        instNumber = self.iList.get_instruction_counter()
        self.dataStack.pushValue(instNumber)
        self.iList.jump_to_label(self.instruction.arg1)
        # Function flag is True (Used CALL)
        self.function_flag = True

    def iJump(self):
        self.iCheckCountOfArgs(1)
        self.iList.jump_to_label(self.instruction.arg1)

    def iLabel(self):
        # This is done, because labels i needed earlier
        self.iCheckCountOfArgs(1)

    def iExit(self):
        self.iCheckCountOfArgs(1)
        iExitRange = range(0, 50)

        if self.instruction.arg1['type'] != 'int' and self.instruction.arg1['type'] != 'var':
            self.exit_program(53, 'ERROR: You cant exit program just with integer -> {}'.format(self.instruction.arg1['type']))

        if self.instruction.arg1['type'] == 'var':
            iExitNumber = Frames.iGet(self.instruction.arg1['text'])
            if type(iExitNumber) != int:
                self.exit_program(53, 'ERROR: bad type of instruction exit -> {}'.format(self.instruction.arg1['type']))
        else:
            iExitNumber = int(self.instruction.arg1['text'])

        if iExitNumber < 0:
            self.exit_program(57, 'ERROR: Exit number can be just positive number !')

        if iExitNumber not in iExitRange:
            self.exit_program(57,
                              'ERROR: Exit have to be in range <0, 50> -> {}'.format(self.instruction.arg1['text']))
        else:
            exit(iExitNumber)

    def iPush(self):
        self.iCheckCountOfArgs(1)
        value = self.instruction.arg1['text']

        if self.instruction.arg1['type'] == 'var':
            value = Frames.iGet(self.instruction.arg1['text'])
        elif self.instruction.arg1['type'] == 'int':
            value = int(value)
        elif self.instruction.arg1['type'] == 'bool':
            value = bool(value)
        else:
            pass

        self.dataStack.pushValue(value)

    def iPop(self):
        self.iCheckCountOfArgs(1)
        value = self.dataStack.popValue()

        if self.instruction.arg1['type'] != 'var':
            self.exit_program(54, 'ERROR: Bad type of instruction -> ({})'.format(self.instruction.arg1['text']))

        Frames.iSet(self.instruction.arg1['text'], value)

    """ TWO ADDRESS INSTRUCTIONS """

    def iInt2Char(self):
        self.iCheckCountOfArgs(2)

        if self.instruction.arg2['type'] != 'int' and self.instruction.arg2['type'] != 'var':
            self.exit_program(53, 'Error bad type ({})'.format(self.instruction.arg2['text']))

        if self.instruction.arg2['type'] == 'var':
            value = Frames.iGet(self.instruction.arg2['text'])
        else:
            value = self.instruction.arg2['text']

        if self.instruction.arg2['type'] != 'int' and type(value) != int:
            self.exit_program(53,'ERROR: Bad type of argument INT2CHAR -> {}'.format(value))
        value = int(value)

        try:
            if value < 1 or value > 1023:
                self.exit_program(58, 'Bad number to convert ({})'.format(value))
            elif type(value) == bool:
                self.exit_program(53, 'ERROR: Bad type of argument -> {}, required int'.format(type(value)))
            value = chr(int(value))
        except ValueError:
            self.exit_program(53, 'ERROR: Bad type of argument -> ({})'.format(value))

        if self.instruction.arg1['type'] != 'var':
            self.exit_program(53, 'ERROR: You cant store value just to variable -> {}'.format(self.instruction.arg1['type']))

        Frames.iSet(self.instruction.arg1['text'], value)

    def iRead(self):
        self.iCheckCountOfArgs(2)
        value = self.instruction.arg2['text']
        iVar = ''

        if self.iInputFile is not None:
            iInputLine = self.iInputFile.readline()
            usr_input = iInputLine
        else:
            usr_input = input()

        if usr_input == '':
            usr_input = 'nil'

        if self.instruction.arg1['type'] != 'var':
            self.exit_program(53, 'ERROR: You have to store value to variable -> {}!'.format(self.instruction.arg1['type']))
        else:
            Frames.iGet(self.instruction.arg1['text'], True)

        # Control if value is type like in XML
        if value == 'int':
            try:
                usr_input = int(usr_input)
            except:
                usr_input = 'nil'
            iVar = self.instruction.arg1['text']
        elif value == 'bool':
            if usr_input.lower() == 'true':
                usr_input = True
            else:
                usr_input = False
            iVar = self.instruction.arg1['text']
        elif value == 'string':
            try:
                usr_input = str(usr_input)
            except:
                usr_input = 'nil'
            iVar = self.instruction.arg1['text']

        Frames.iSet(iVar, usr_input)

    def iType(self):
        self.iCheckCountOfArgs(2)
        var_name = self.instruction.arg1['text']
        result_final = ''

        if self.instruction.arg1['type'] != 'var':
            self.exit_program(53, 'ERROR: You can store valu just to variable -> {}'.format(self.instruction.arg1['type']))
        else:
            Frames.iGet(self.instruction.arg1['text'], True)

        if self.instruction.arg2['type'] == 'var':
            value = Frames.iGet(self.instruction.arg2['text'], True)
        else:
            value = self.instruction.arg2['text']

        if value is None:
            result = ''
        else:
            result = value

        # Control type of second instruction
        if self.instruction.arg2['type'] == 'bool':
            result = bool(result)
        elif self.instruction.arg2['type'] == 'int':
            result = int(result)
        elif self.instruction.arg2['type'] == 'string':
            result = str(result)
        elif self.instruction.arg2['type'] == 'nil':
            result = 'nil'

        # Convert instruction to important type
        if type(result) == int:
            result_final = 'int'
        if type(result) == bool:
            result_final = 'bool'
        if type(result) == str:
            result_final = 'str'
        if result == 'nil':
            result_final = 'nil'
        if result == '':
            result_final = ''

        Frames.iSet(var_name, result_final)

    def iMove(self):
        self.iCheckCountOfArgs(2)
        iResult = ''

        if self.instruction.arg2['type'] == 'var':
            iSymb = Frames.iGet(self.instruction.arg2['text'])
        else:
            iSymb = self.instruction.arg2['text']

        if type(iSymb) == str:
            if self.instruction.arg2['type'] == 'bool':
                if iSymb.lower() == 'true' or iSymb.lower() == 'false':
                    iResult = bool(iSymb)
            elif re.match('^([+-]?[1-9][0-9]*|[+-]?[0-9])$', iSymb):
                iResult = int(iSymb)
            elif iSymb.lower() == 'nil' and self.instruction.arg2['type'] == 'nil':
                iResult = 'nil'
            else:
                iResult = iSymb

        Frames.iSet(self.instruction.arg1['text'], iResult)

    def iStrlen(self):
        self.iCheckCountOfArgs(2)

        if self.instruction.arg2['type'] == 'var':
            iSymb = Frames.iGet(self.instruction.arg2['text'])
        else:
            iSymb = self.instruction.arg2['text']

            if type(iSymb) != str:
                self.exit_program(53, 'ERROR: STRLEN use string no -> ({})'.format(iSymb))
            if iSymb == 'nil':
                self.exit_program(53, 'ERROR: STRLEN use string no -> ({})'.format(iSymb))

        if self.instruction.arg2['type'] != 'var' and self.instruction.arg2['type'] != 'string':
            self.exit_program(53, 'TypeError: object of type int has no len()')

        if type(iSymb) != str or iSymb == 'nil':
            self.exit_program(53, 'TypeError: object of type {} has no len'.format(type(iSymb)))

        result = len(iSymb)
        Frames.iSet(self.instruction.arg1['text'], result)

    """ THREE ADDRESS INSTRUCTION """

    def iAdd(self):
        self.iCheckCountOfArgs(3)
        # Function for control conditions for adding
        value1, value2 = self._iCheckConditions()
        value1 = int(value1)
        value2 = int(value2)
        result = value1 + value2
        Frames.iSet(self.instruction.arg1['text'], result)

    def iSub(self):
        self.iCheckCountOfArgs(3)
        value1, value2 = self._iCheckConditions()
        value1 = int(value1)
        value2 = int(value2)
        result = value1 - value2
        Frames.iSet(self.instruction.arg1['text'], result)

    def iMul(self):
        self.iCheckCountOfArgs(3)
        value1, value2 = self._iCheckConditions()
        value1 = int(value1)
        value2 = int(value2)
        result = value1 * value2
        Frames.iSet(self.instruction.arg1['text'], result)

    def iDiv(self):
        self.iCheckCountOfArgs(3)
        value1, value2 = self._iCheckConditions()
        value1 = int(value1)
        value2 = int(value2)
        if value2 == 0:
            self.exit_program(57, 'ERROR: Can not div with zero ! -> {} // {}'.format(value1, value2))
        result = value1 // value2
        Frames.iSet(self.instruction.arg1['text'], result)

    def iLtGtEq(self):
        self.iCheckCountOfArgs(3)
        # Control conditions and store informations to vars
        iSymb1, iSymb2, iVar = self._iCheckConditionsVSS('gt')

        if (iSymb1 == 'nil' or iSymb2 == 'nil') and self.instruction.opcode != 'EQ':
            self.exit_program(53, 'ERROR: With nill you can equate just EQ !')

        if self.instruction.opcode == 'GT':
            result = iSymb1 > iSymb2
        elif self.instruction.opcode == 'LT':
            result = iSymb1 < iSymb2
        else:
            if iSymb1 is None:
                if iSymb2 == bool:
                    result = iSymb2
                else:
                    result = False
            elif iSymb2 is None:
                if iSymb1 == bool:
                    result = iSymb1
                else:
                    result = False
            else:
                result = iSymb1 == iSymb2
        Frames.iSet(iVar, result)

    def iNot(self):
        self.iCheckCountOfArgs(2)
        value1 = (self.instruction.arg2['text'])
        type1 = (self.instruction.arg2['type'])
        result = ''

        if self.instruction.arg2['type'] == 'var':
            value1 = Frames.iGet(self.instruction.arg2['text'])

        if type1 != 'bool' and type(value1) != bool:
            self.exit_program(53, 'ERROR: Bad type of instruction ({})'.format(type1))

        if self.instruction.arg2['type'] == 'bool':
            if value1.lower() == 'false':
                value1 = False
            elif value1.lower() == 'true':
                value1 = True

        if self.instruction.arg2['type'] != 'var' and self.instruction.arg2['type'] != 'bool' and type(value1) != bool:
            self.exit_program(53, 'ERROR: NOT can be just bool value -> ({})'.format(self.instruction.arg2['type']))

        if value1:
            result = False
        elif not value1:
            result = True
        else:
            self.exit_program(53, 'ERROR: Bad argument of instruction -> {}'.format(self.instruction.arg2['type']))
        Frames.iSet(self.instruction.arg1['text'], result)

    def iConcat(self):
        self.iCheckCountOfArgs(3)
        iSymb1, iSymb2, iVar = self._iCheckConditionsVSS('concat')
        result = iSymb1 + iSymb2
        Frames.iSet(self.instruction.arg1['text'], result)

    def iGetchar(self):
        self.iCheckCountOfArgs(3)
        result = ''

        iSymb1 = self.instruction.arg2['text']
        iSymb2 = self.instruction.arg3['text']

        iType1 = self.instruction.arg2['type']
        iType2 = self.instruction.arg3['type']

        if self.instruction.arg2['type'] == 'var':
            iSymb1 = Frames.iGet(self.instruction.arg2['text'])
        if self.instruction.arg3['type'] == 'var':
            iSymb2 = Frames.iGet(self.instruction.arg3['text'])

        if (iType1 != 'string' and iType1 != 'var') or (iType2 != 'int' and iType2 != 'var'):
            self.exit_program(53, 'ERROR: You can concat just strings')

        iSymb2 = int(iSymb2)
        # Array dimension
        max_index = len(iSymb1)

        if iSymb2 < 0 or iSymb2 > max_index:
            self.exit_program(58, 'ERROR: Index is out of rane string -> [{}] => {} '.format(iSymb1, iSymb2))

        iSymb1 = list(iSymb1)

        try:
            result = iSymb1[iSymb2]
        except IndexError:
            self.exit_program(58, 'ERROR: Index or array is out of range [{}] index -> {}!'.format(self.instruction.arg2['text'], iSymb2))

        Frames.iSet(self.instruction.arg1['text'], result)

    def iSetchar(self):
        self.iCheckCountOfArgs(3)

        iSymb1 = self.instruction.arg2['text']
        iSymb2 = self.instruction.arg3['text']

        if self.instruction.arg2['type'] == 'var':
            iSymb1 = Frames.iGet(self.instruction.arg2['text'])
        if self.instruction.arg3['type'] == 'var':
            iSymb2 = Frames.iGet(self.instruction.arg3['text'])

        symbol2 = self.instruction.arg3['type']
        symbol1 = self.instruction.arg2['type']

        if (symbol1 != 'int' and symbol1 != 'var') or (symbol2 != 'string' and symbol2 != 'var'):
            self.exit_program(53, 'ERROR: Bad Values for SETCHAR {} -> ({})'.format(symbol1, symbol2))

        iVar = Frames.iGet(self.instruction.arg1['text'])

        if iVar == 'nil':
            self.exit_program(53, 'ERROR: variable -> ({}) is nil !'.format(self.instruction.arg1['type']))

        if type(iVar) != str:
            self.exit_program(53, 'ERROR: You can change char just in the strings, variable is -> ({})'.format(type(iVar)))

        max_index = len(iVar)
        iSymb1 = int(iSymb1)

        if iSymb1 not in range(0, max_index):
            self.exit_program(58, 'ERROR: Value is out of array index [{}] -> {}'.format(max_index-1, iSymb1))
        iVar = list(iVar)

        if len(str(iSymb2)) > 1:
            iSymb2 = iSymb2[0]
        elif len(str(iSymb2)) == 0:
            self.exit_program(58, 'ERROR: You can not change char on empty string !')

        iVar[iSymb1] = str(iSymb2)
        str1 = ""
        result = str1.join(iVar)
        Frames.iSet(self.instruction.arg1['text'], result)

    def iJumpifeqJumpifneq(self):
        self.iCheckCountOfArgs(3)

        iSymb1, iSymb2, iVar = self._iCheckConditionsVSS('jump')

        self.iList.check_label(self.instruction.arg1)
        if iSymb2 == iSymb1 and self.instruction.opcode == "JUMPIFEQ":
            self.iList.jump_to_label(self.instruction.arg1)
        if iSymb2 != iSymb1 and self.instruction.opcode == "JUMPIFNEQ":
            self.iList.jump_to_label(self.instruction.arg1)

    def iStri2Int(self):
        self.iCheckCountOfArgs(3)
        iSymb1, iSymb2, iVar = self._iCheckConditionsVSS('stri2int')

        if type(iSymb1) != str or type(iSymb2) != int:
            self.exit_program(53, 'ERROR: Bad type of STRI2INT instruction ({}) : ({})'.format(iSymb1, iSymb2))
        max_index = len(iSymb1)

        iSymb1 = list(iSymb1)
        iSymb2 = int(iSymb2)
        if iSymb2 not in range(0, max_index):
            self.exit_program(58, 'ERROR: Index is out of range')

        result = ord(iSymb1[iSymb2])
        Frames.iSet(iVar, result)

    def iAndOr(self):
        self.iCheckCountOfArgs(3)
        iSymb1, iSymb2, iVar = self._iCheckConditionsVSS('and')
        result = ''

        if type(iSymb1) is not bool:
            self.exit_program(53, 'You can equate just bool type!')

        if type(iSymb2) is not bool:
            self.exit_program(53, 'You can equate just bool type!')

        if self.instruction.opcode == "AND":
            result = iSymb1 and iSymb2
        elif self.instruction.opcode == "OR":
            result = iSymb1 or iSymb2

        Frames.iSet(iVar, result)

    def _iCheckConditions(self):
        type1 = self.instruction.arg2['type']
        type2 = self.instruction.arg3['type']
        iVI = ['var', 'int']

        value1 = self.instruction.arg2['text']
        value2 = self.instruction.arg3['text']

        if type1 not in iVI or type2 not in iVI:
            self.exit_program(53, 'ERROR: Arguments in ADD have to be same type (arg1-> {} arg2-> {})!'.format(type1,
                                                                                                               type2))
        if type1 == 'var':
            value1 = Frames.iGet(self.instruction.arg2['text'])
        if type2 == 'var':
            value2 = Frames.iGet(self.instruction.arg3['text'])

        return value1, value2

    def _iCheckConditionsVSS(self, instructions):
        iVar = self.instruction.arg1['text']
        iSymb1 = self.instruction.arg2['text']
        iSymb2 = self.instruction.arg3['text']
        iVB = ['var', 'bool', 'string', 'int']
        type1 = self.instruction.arg2['type']
        type2 = self.instruction.arg3['type']
        iVs1 = []
        iVs2 = []

        # Set important types
        if instructions == 'concat':
            iVB = ['var', 'string']
        if instructions == 'and':
            iVB = ['var', 'bool']
        if instructions == 'stri2int':
            iVs1 = ['var', 'string']
            iVs2 = ['var', 'int']
        if instructions == 'gt' or instructions == 'jump':
            iVB = ['var', 'bool', 'string', 'int', 'nil']

            if(type1 not in iVs1 or type2 not in iVs2) and instructions == 'stri2int':
                self.exit_program(53,
                                  'ERROR: Arguments have to be same type (arg1-> {} arg2-> {})!'.format(type1, type2))

        if type1 not in iVB or type2 not in iVB:
            self.exit_program(53, 'ERROR: Arguments have to be same type (arg1-> {} arg2-> {})!'.format(type1,type2))

        # Check argument type
        if self.instruction.arg2['type'] == 'var':
            iSymb1 = Frames.iGet(self.instruction.arg2['text'])
        else:
            if self.instruction.arg2['type'] == 'string':
                iSymb1 = str(iSymb1)
            elif self.instruction.arg2['type'] == 'int':
                iSymb1 = int(iSymb1)
            elif self.instruction.arg2['type'] == 'nil':
                iSymb1 = 'nil'
            elif self.instruction.arg2['type'] == 'bool':
                if self.instruction.arg2['text'] == 'true':
                    iSymb1 = True
                else:
                    iSymb1 = False

        if self.instruction.arg3['type'] == 'var':
            iSymb2 = Frames.iGet(self.instruction.arg3['text'])
        else:
            if self.instruction.arg3['type'] == 'string':
                iSymb2 = str(iSymb2)
            elif self.instruction.arg3['type'] == 'int':
                iSymb2 = int(iSymb2)
            elif self.instruction.arg3['type'] == 'nil':
                iSymb2 = 'nil'
            elif self.instruction.arg3['type'] == 'bool':
                if self.instruction.arg3['text'] == 'true':
                    iSymb2 = True
                else:
                    iSymb2 = False

        if iSymb1 == None:
            self.exit_program(55, 'ERROR: Undefined variable -> \'{}\' is not initialized'.format(
                self.instruction.arg2['text'][3:]))
        if iSymb2 == None:
            self.exit_program(55, 'ERROR: Undefined variable -> \'{}\' is not initialized'.format(
                self.instruction.arg2['text'][3:]))

        if (instructions == 'gt' or instructions == 'jump') and (iSymb1 != 'nil' and iSymb2 != 'nil'):
            if type(iSymb1) != type(iSymb2):
                self.exit_program(53, 'ERROR: You can just equate same type')

        return iSymb1, iSymb2, iVar

    def iCheckCountOfArgs(self, arg_count):
        """Checks if arguments have expected count"""
        if self.instruction.arg_count != arg_count:
            exit(0)

class Frames(Arg_Error_Checker):
    """Class Frames (Global Frame, Local Frame and Temporary Frame)"""
    globalFrame = {}
    localFrame = None
    temporaryFrame = None
    stack = []

    @classmethod
    def iAdd(cls, instruction):
        """Create a new frame"""
        frame, name = instruction.split("@")
        frame = cls.iChooseFrame(frame)
        # --- Check for duplicity ---
        if name in frame:
            cls.exit_program(52, 'Error: Variable already exist')
        # --- Create var in frame ---
        frame[name] = None

    @classmethod
    def iSet(cls, name, value):
        """Set value to frame"""
        frame, name = name.split("@")
        # Identify frame
        frame = cls.iChooseFrame(frame)
        # Check if exists
        if name not in frame:
            cls.exit_program(54, 'Variable is not initialized -> ({})'.format(name))
        frame[name] = value

    @classmethod
    def iGetAlsoEmptyFrame(cls, name):
        """Return empty frames for instruction -> Break"""
        if name == 'GF':
            frame = cls.globalFrame
        elif name == 'LF':
            frame = cls.localFrame
        else:
            frame = cls.temporaryFrame

        if frame is None:
            frame = {}
            return frame

        return frame

    @classmethod
    def iGet(cls, instruction, type=False):
        """Return value, which is stored in frame"""
        frame, name = instruction.split("@")

        frame = cls.iChooseFrame(frame)
        if frame is None:
            return None

        if name not in frame:
            cls.exit_program(54, 'ERROR: Variable ({}) is not defined !'.format(name))

        result = frame[name]

        if type is True and result is None:
            return result

        if result is None:
            cls.exit_program(56, 'ERROR: Variable ({}) has no value !'.format(name))

        return result

    @classmethod
    def iChooseFrame(cls, frame):
        """Return specific frame"""
        if frame == 'GF':
            frame = cls.globalFrame
        elif frame == 'LF':
            frame = cls.localFrame
        elif frame == 'TF':
            frame = cls.temporaryFrame
        else:
            cls.exit_program(99, 'ERROR: Uknown type of frame')

        if frame is None:
            cls.exit_program(55, 'ERROR: Frame is not defined !')

        return frame


Main()
