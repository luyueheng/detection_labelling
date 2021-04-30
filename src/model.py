import json


class Image:
    def __init__(self, db_results: dict):
        self.image_id = db_results['image_id']
        self.image_path = db_results['image_path']
        self.room_type = db_results['room_type']
        self.style = db_results['style']
        self.objects = [Object(obj_dict) for obj_dict in db_results['objects']]
        self.labelled_by = db_results['labelled_by']
        self.label_memo = db_results['label_memo']
        self.label_time = db_results['label_time']
    
    def generate_existing_labels_json(self) -> str:
        return json.dumps([obj.generate_existing_label_dict() for obj in self.objects])


class Object:
    def __init__(self, obj_dict: dict):
        self.object_id = obj_dict['object_id']
        self.object_type = obj_dict.get('object_type', '') # In case object_type may not exist
        self.box_left = obj_dict['box_left'] # [x1,y1,x2,y2]
        self.box_top = obj_dict['box_top']
        self.box_right = obj_dict['box_right']
        self.box_bottom = obj_dict['box_bottom']
    
    def generate_existing_label_dict(self) -> dict:
        return {
            'object_id': self.object_id,
            'object_type': self.object_type,
            'box_left': self.box_left,
            'box_top': self.box_top,
            'box_right': self.box_right,
            'box_bottom': self.box_bottom
        }
