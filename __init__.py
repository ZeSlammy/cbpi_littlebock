# LittleBock craftbeerpi3 plugin
# Log iSpindel temperature, SG and Battery data from CraftBeerPi 3.0 to
# LittleBock
from modules import cbpi
import requests
import json


# Parameters
littleBock_base_url = None
littleBock_iSpindel_xRef = None


def log(s):
    s = "LittleBock_iSpindel: " + s
    cbpi.app.logger.info(s)


@cbpi.initalizer(order=9000)
def init(cbpi):
    cbpi.app.logger.info("LittleBock_iSpindel plugin Initialize")
    log("LittleBock_iSpindel params")
# The Base URL Value for your iSpindel
# On the iSpindle page on LittleBock, in Server URL you'll see
# /api/log/ispindle/XXX/YYY
# base_url is XXX
    global littleBock_base_url

    littleBock_base_url = cbpi.get_config_parameter(
        "littleBock_base_url", None)
    log("LittleBock littleBock_base_url %s" % littleBock_base_url)

    if littleBock_base_url is None:
        log("Init littleBock_base_url config URL")
    try:
        cbpi.add_config_parameter(
            "littleBock_base_url", "", "text", "LittleBock base URL /api/log/ispindel/XXX")
    except:
        cbpi.notify("LittleBock_iSpindel Error",
                    "Unable to update LittleBock_iSpindel base_url parameter", type="danger")

    global littleBock_iSpindel_xRef

    littleBock_iSpindel_xRef = cbpi.get_config_parameter(
        "littleBock_iSpindel_xRef", None)
    log("littleBock_iSpindel_xRef %s" % littleBock_iSpindel_xRef)

    if littleBock_iSpindel_xRef is None:
        log("Init littleBock_iSpindel_xRef XRef Table")
    try:
        cbpi.add_config_parameter(
            "littleBock_iSpindel_xRef", "", "text", "LittleBock/iSpindel XRef Table. /api/log/ispindel/XXX/YYY. Must be list of iSpindel/YYY separated by , ")
    except:
        cbpi.notify("LittleBock_iSpindel Error",
                    "Unable to update LittleBock_iSpindel xRef parameter", type="danger")

    log("LittleBock_iSpindel params ends")

# interval=900 is 900 seconds, 15 minutes
# if you try to reduce this, LittleBock will throw "ignored" status back at you
@cbpi.backgroundtask(key="LittleBock_iSpindel_task", interval=900)
def LittleBock_iSpindel_background_task(api):
    global littleBock_base_url
    log("LittleBock_iSpindel background task")
    if littleBock_base_url is None:
        return False
    if littleBock_iSpindel_xRef is None:
        return False

    # Potentially multiple iSpindels
    # Build a list with iSpindel / Temperature / Gravity / Battery
    multi_payload = {}
    for key, value in cbpi.cache.get("sensors").iteritems():
        log("key %s value.name %s value.instance.last_value %s value.type %s" %
            (key, value.name, value.instance.last_value, value.type))

        if (value.type == "iSpindel"):
            log("sensorType %s value.instance.last_value %s " %
                (value.instance.sensorType,    value.instance.last_value))
            iSpindel_name = value.instance.key
            if not(iSpindel_name in multi_payload):
                multi_payload[iSpindel_name] = {}
            # multi_payload[iSpindel_name]['iSpindel_name'] = iSpindel_name
            if (value.instance.sensorType == "Temperature"):
                temp = value.instance.last_value
                multi_payload[iSpindel_name]['temperature'] = temp
                # payload['name'] = value.instance.key
            if (value.instance.sensorType == "Battery"):
                multi_payload[iSpindel_name]['battery'] = value.instance.last_value
            if (value.instance.sensorType == "Gravity") and (value.instance.last_value > 0):
                multi_payload[iSpindel_name]['gravity'] = value.instance.last_value
    log("LittleBock_iSpindel Parsing done")
    for iSpindel, payload in multi_payload.iteritems():
        log("LittleBock_iSpindel %s" % (iSpindel))
#        payload = {}
        littleBock_base_url = cbpi.get_config_parameter(
            "littleBock_base_url", None)
        Xref = get_Xref_iSpindel(iSpindel)
        url = "http://www.littlebock.fr/api/log/ispindle/" + \
            littleBock_base_url + "/" + Xref
        headers = {}
        '''
        payload['temperature'] = multi_payload[iSpindel]['temperature']
        payload['battery'] = multi_payload[iSpindel]['battery']
        payload['gravity'] = iSpindel['gravity']
        '''
        log("Payload %s" %
            (json.dumps(payload)))
        r = requests.request("POST", url, data=payload,
                             headers=headers)
        log("LittleBock_iSpindel Result %s" % r.text)
        log("LittleBock_iSpindel  done")


def get_Xref_iSpindel(iSpindel_name):
    littleBock_iSpindel_xRef = cbpi.get_config_parameter(
        "littleBock_iSpindel_xRef", None)
    my_list = littleBock_iSpindel_xRef.split(",")
    for el in my_list:
        spin_name, Xref_tmp = el.split("/")
        if spin_name == iSpindel_name:
            return Xref_tmp
    XRef = None
    return XRef
