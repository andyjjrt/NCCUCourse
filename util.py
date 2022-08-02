from base64 import b64encode
from pyDes import des, ECB, PAD_PKCS5
from constant import PERSON_API, TRACE_API, KEY

def des_ecb_encode(source, key):
    des_obj = des("........", ECB, IV=None, pad=None, padmode=PAD_PKCS5)
    des_obj.setKey(key)
    des_result = des_obj.encrypt(source)
    return b64encode(des_result).decode()

def get_login_url(username, password):
    source = "aNgu1ar%!" + username + "X_X" + password + "!%ASjjLInGH:lkjhdsa:)_l0OK"
    return PERSON_API + str(des_ecb_encode(source, KEY)) + "/"

def get_addtrack_url(encstu, courseid):
    source = "aNgu1ar%!" + courseid + "!%ASjjLInGH:lkjhdsa"
    return TRACE_API + "C/zh-TW/3" + str(des_ecb_encode(source, KEY)) + "-" + encstu + "/"

def get_deltrack_url(encstu, courseid):
    source = "aNgu1ar%!" + courseid + "!%ASjjLInGH:lkjhdsa"
    return TRACE_API + "D/zh-TW/" + str(des_ecb_encode(source, KEY)) + "-" + encstu + "/"

def get_track_url(encstu):
    return TRACE_API + "zh-TW/" + encstu + "/"

def get_updatetrack_url(encstu, courseid):
    source = "aNgu1ar%!" + courseid + "!%ASjjLInGH:lkjhdsa"
    return TRACE_API + "U/zh-TW/1" + str(des_ecb_encode(source, KEY)) + "-" + encstu + "/"
