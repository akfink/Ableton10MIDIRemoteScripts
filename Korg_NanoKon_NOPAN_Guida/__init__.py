from __future__ import absolute_import, print_function, unicode_literals, with_statement
from NanoKontrol_NoPan import NanoKontrol_NoPan

def create_instance(c_instance):
    """ Creates and returns the NanoKontrol script """
    return NanoKontrol_NoPan(c_instance)
