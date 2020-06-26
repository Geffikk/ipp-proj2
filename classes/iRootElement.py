"""
Title - IPP <interpret.py>
Author - Maroš Geffert
Login - <xgeffe00>
"""

import xml.etree.ElementTree as ET
from classes.iArgsErrors import *

class Root_Element(Arg_Error_Checker):
    def __init__(self, FILE_PATH):
        self.FILE_PATH = FILE_PATH

    def make_Root_Tree(self):
        try:
            tree = ET.parse(self.FILE_PATH)
            self.root = tree.getroot()
        except FileNotFoundError:
            self.exit_program(E_OPENING_INPUT_ERROR)
        except Exception as e:
            self.exit_program(E_BAD_XML_ERROR)
        return self.root