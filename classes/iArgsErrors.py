"""
Title - IPP <interpret.py>
Author - Maroš Geffert
Login - <xgeffe00>
"""

import getopt
import sys

""" ERRORS """
E_MISSING_PARAMETER_ERROR = 10  # Chybajuci parameter skriptov
E_OPENING_INPUT_ERROR = 11  # Chyba pri otvarani vstupnych suborov
E_OPENINT_OUTPUT_ERROR = 12  # Chyba pri otvarani vystupnych suborov pre zapis
E_INTERNAL_ERROR = 99  # Iterna chyba
E_BAD_XML_ERROR = 31  # XML error - zly format
E_LEX_SYN_ERROR = 32  # Lexikalna alebo synakticka chyba

def print_to_stderr(msg):
    print(msg, file=sys.stderr)

class Arg_Error_Checker():
    def __init__(self):
        self.source = None
        self.input = None

    @staticmethod
    def exit_program(error=None, msg=None):
        print(error, msg, file=sys.stderr)
        exit(error)

    def get_file_path(self):
        return self.source

    def get_input_path(self):
        return  self.input

    def check(self):
        option2 = ''
        file2 = ''

        try:
            options, args = getopt.getopt(sys.argv[1:], '', ['help', 'source=', 'input='])
        except  getopt.GetoptError as error:
            self.exit_program(10, 'ERROR: Bad choice options')

        if len(options) > 2 or len(options) < 1:
            self.exit_program(10, 'ERROR: Missing or bad parameter')

        option1 = options[0]
        try:
            option2 = options[1]
            option2, file2 = option2
        except:
            pass
        option1, file1 = option1
        iInput = False

        if option1 == '--help':
            print('''Program načíta XML kontent zo zadaného suboru a tento pogram intepretuje. 
            Vstupný XML súbor je generovaný napríklad skriptom parse.php
            
            Parametre skriptu:
            \t --source=file (vstupný XML súbor)
            \t --input=file (vstupný súbor)''')
            exit(0)
        elif option1 == '--source':
            self.source = file1
        elif option1 == '--input':
            iInput = True
            self.input = file1
        else:
            self.exit_program(10, 'ERROR: Missing or bad parameter')

        if option2 == '--input':
            self.input = file2
        elif option2 == '--source':
            self.source = file2
        elif iInput is True:
            self.source = sys.stdin
        elif option2 == '':
            pass
        else:
            self.exit_program(10, 'ERROR: Missing or bad parameter')
