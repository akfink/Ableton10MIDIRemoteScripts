#Embedded file name: __init__.py
from BCRXL import BCRXL
from _Framework.Capabilities import controller_id, inport, outport, CONTROLLER_ID_KEY, PORTS_KEY, NOTES_CC, SCRIPT, AUTO_LOAD_KEY

def create_instance(c_instance):
    return BCRXL(c_instance)


def get_capabilities():
    return {CONTROLLER_ID_KEY: controller_id(vendor_id=7001, product_ids=[7101], model_name='BCR XL'),
     PORTS_KEY: [inport(props=[NOTES_CC, SCRIPT]), outport(props=[NOTES_CC, SCRIPT])],
     AUTO_LOAD_KEY: True}
