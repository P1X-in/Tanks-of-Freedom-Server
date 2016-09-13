"""Module for validating if map data is correct"""
import hashlib, json
from tof_server import config
from tof_server.utils import randcoder

def validate(map_data, cursor):
    """Method for validating if map data is correct"""

    sql = "SELECT download_code FROM maps WHERE map_hash = %s"
    md5_hash = hashlib.md5(json.dumps(map_data).encode()).hexdigest()

    cursor.execute(sql, (md5_hash,))
    previous_code = cursor.fetchone()

    if previous_code:
        return get_result(previous_code[0], md5_hash, True)

    sql = "SELECT download_code FROM maps WHERE download_code = %s"

    size_increase = 0
    while True:
        code = randcoder.get_random_code(config.MAP_CODE_LENGTH + size_increase)
        cursor.execute(sql, (code,))
        previous_code = cursor.fetchone()
        if previous_code:
            if size_increase == config.MAP_CODE_LENGTH:
                return get_error(500)
            size_increase = size_increase + 1
        else:
            break

    return get_result(code, md5_hash, False)

def get_result(code, md5_hash, found):
    """Method for creating ok response"""
    return {
        'status' : 'ok',
        'code' : code,
        'found' : found,
        'hash' : md5_hash
    }

def get_error(code):
    """Method for generating error response"""
    return {
        'status' : 'error',
        'code' : code
    }