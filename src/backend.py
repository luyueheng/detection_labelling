import pymysql

from utils import MySQLConfig
from model import Image, Object
from typing import List


LABEL = 'label'


class Backend:
    def __init__(self, mysql_config: MySQLConfig):
        self.mysql_connection = {}
        self._mysql_config = mysql_config
        self._mysql_db_name = {
            LABEL: mysql_config.label_db,
        }
        self._connect_mysql(LABEL)

    def _connect_mysql(self, db: str):
        self.mysql_connection[db] = pymysql.connect(
            host=self._mysql_config.host,
            port=self._mysql_config.port,
            user=self._mysql_config.user,
            password=self._mysql_config.password,
            db=self._mysql_db_name[db],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

    def _query_mysql(self, db: str, query: str, variables: List[str]) -> dict:
        for i in range(self._mysql_config.num_retry):
            connection = self.mysql_connection[db]
            connection.ping(reconnect=True)
            try:
                with connection.cursor() as cursor:
                    cursor.execute(query, variables)
                    result = cursor.fetchall()
                    cursor.close()
                    return result
            except pymysql.OperationalError as e:
                if i == self._mysql_config.num_retry - 1:
                    raise e
                self._connect_mysql(db)

    def _get_value_from_mysql(self, db: str, table_name: str, image_id: int, onehot: bool, field: str = None) -> str:
        result = self._query_mysql(
            db=db,
            query="select * from {} where image_id = %s limit 1;".format(table_name),
            variables=[image_id])
        if not result:
            return ''
        return result[0][field]

    def get_image_from_image_id(self, image_id: int) -> Image:
        db_results = {}
        connection = self.mysql_connection[LABEL]
        connection.ping(reconnect=True)
        with connection.cursor() as cursor:
            cursor.execute("select * from image where image_id = %s", [image_id])
            image_result = cursor.fetchall()[0]
            cursor.close()
        db_results['image_id'] = image_id
        db_results['image_path'] = 'static/' + image_result.get('image_path', '')
        db_results['room_type'] = image_result.get('room_type', '')
        db_results['style'] = image_result.get('style', '')
        db_results['labelled_by'] = image_result.get('labelled_by', '')
        db_results['label_memo'] = image_result.get('label_memo', '')
        db_results['label_time'] = image_result.get('label_time', '')
        with connection.cursor() as cursor:
            cursor.execute("select * from object where image_id = %s", [image_id])
            object_result = cursor.fetchall()
            cursor.close()
        db_results['objects'] = []
        for obj in object_result:
            obj_dict = {}
            obj_dict['object_id'] = obj['object_id']
            obj_dict['object_type'] = obj.get('object_type', '')
            obj_dict['box_left'] = obj['box_left']
            obj_dict['box_top'] = obj['box_top']
            obj_dict['box_right'] = obj['box_right']
            obj_dict['box_bottom'] = obj['box_bottom']
            db_results['objects'].append(obj_dict)
        return Image(db_results)
    
    def update_image_labels(self, image_id: int, label_objects: List[Object]):
        connection = self.mysql_connection[LABEL]
        connection.ping(reconnect=True)
        with connection.cursor() as cursor:
            cursor.execute("select * from object where image_id = %s", [image_id])
            object_result = cursor.fetchall()
            old_object_id_list = [r['object_id'] for r in object_result]
            for label_obj in label_objects:
                # Update
                if label_obj.object_id in old_object_id_list:
                    cursor.execute("update object set object_type = %s, box_left = %s, box_top = %s, box_right = %s, box_bottom = %s, where object_id = %s;",
                        [label_obj.object_type, label_obj.box_left, label_obj.box_top, label_obj.box_right, label_obj.box_bottom, label_obj.object_id])
                # Add
                else:
                    cursor.execute("insert into object(object_id, image_id, object_type, box_left, box_top, box_right, box_bottom) value (%s, %s, %s, %s, %s, %s, %s);",
                        [label_obj.object_id, image_id, label_obj.object_type, label_obj.box_left, label_obj.box_top, label_obj.box_right, label_obj.box_bottom])
            for obj_id in old_object_id_list:
                if obj_id not in [obj.object_id for obj in label_objects]:
                    cursor.execute("delete from object where object_id = %s;"), [obj_id]
            connection.commit()
            cursor.close()
    
    def update_image_metadata(self, image_id: int, labelled_by: str, label_memo: str):
        connection = self.mysql_connection[LABEL]
        connection.ping(reconnect=True)
        with connection.cursor() as cursor:
            cursor.execute("select * from image where image_id = %s", [image_id])
            result = cursor.fetchall()
            cursor.execute("update image set labelled_by = %s, label_memo = %s, label_time = CURRENT_TIMESTAMP where image_id = %s;",
                [labelled_by, label_memo, image_id])
            connection.commit()
            cursor.close()
