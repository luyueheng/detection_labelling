from collections import namedtuple, defaultdict
from typing import List
import json
import os
from model import Object


CONFIG_PATH_FORMAT = '../config/{}.json'
MySQLConfig = namedtuple('MySQLConfig', ['host', 'port', 'label_db', 'user', 'password', 'num_retry'])


def get_mysql_config(env: str) -> MySQLConfig:
    with open(CONFIG_PATH_FORMAT.format(env)) as f:
        mysql_config = json.load(f)['mysql']
    user = os.getenv('MYSQL_USER')
    password = os.getenv('MYSQL_PASSWORD')
    return MySQLConfig(
        mysql_config['host'],
        mysql_config['port'],
        mysql_config['label_db'],
        user,
        password,
        mysql_config['num_retry']
    )

def get_env():
    return os.getenv('ENVIRONMENT')

def parse_label_result(label_result: dict) -> List[Object]:
    label_objects_dict = defaultdict(dict)
    for key in label_result:
        for field in ['object_type', 'box_left', 'box_top', 'box_w', 'box_h']:
            if key.split('-')[0] == field:
                value = label_result[key]
                if field in ['box_left', 'box_top', 'box_w', 'box_h']:
                    value = round(float(label_result[key]), 0)
                label_objects_dict[key.split('-')[1]][field] = value
                break
    label_objects = []
    for object_id, obj_dict in label_objects_dict.items():
        obj = Object({
            'object_id': object_id,
            'object_type': obj_dict['object_type'],
            'box_left': obj_dict['box_left'],
            'box_top': obj_dict['box_top'],
            'box_right': obj_dict['box_left'] + obj_dict['box_w'],
            'box_bottom': obj_dict['box_top'] + obj_dict['box_h']
        })
        label_objects.append(obj)
    return label_objects

def read_object_type_from_config():
    with open('../config/object_type_list.txt', 'r') as f:
        return f.read().split('\n')
