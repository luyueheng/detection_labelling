import json

from flask import Flask, render_template, request
from backend import Backend
from utils import get_mysql_config, parse_label_result, read_object_type_from_config, get_env


app = Flask(__name__)
env = get_env()
backend = Backend(get_mysql_config(env))
label_status = {}
OBJECT_TYPE_LIST = json.dumps(read_object_type_from_config())


@app.route('/', methods=['GET'])
def start_job():
    return render_template('start.html')


@app.route('/label', methods=['GET', 'POST'])
def label():
    if request.method == 'POST':
        if not request.args:
            labelled_by = request.form['labelled_by']
            label_memo = request.form['label_memo']
            image_id_list = [int(image_id.strip()) for image_id in request.form['image_id_list'].strip().split('\n')]
            wrong_image_id_list = []
            for image_id in image_id_list:
                if backend.get_image_from_image_id(image_id) == None:
                    wrong_image_id_list.append(image_id)
            if wrong_image_id_list:
                return 'image id not in database or cannot find image path: <br>'+'<br>'.join(
                    [str(image_id) for image_id in wrong_image_id_list])
            label_status[labelled_by] = {
                'image_id_list': image_id_list,
                'label_memo': label_memo,
                'next_index': 1
            }
            img = backend.get_image_from_image_id(image_id_list[0])
            image_property = {
                'room_type': img.room_type,
                'style': img.style,
                'labelled_by': img.labelled_by,
                'label_memo': img.label_memo,
                'label_time': img.label_time
            }
            next_image_id = image_id_list[1] if len(image_id_list) > 1 else ''
            return render_template(
                'label.html',
                image_id=image_id_list[0],
                image_property=image_property,
                next_image_id=next_image_id,
                previous_image_id='',
                image_path=img.image_path,
                existing_labels_json=img.generate_existing_labels_json(),
                labelled_by=labelled_by,
                object_type_list=OBJECT_TYPE_LIST,
            )
        else:
            labelled_by = request.form['labelled_by']
            label_objects = parse_label_result(request.form)
            previous_image_id = int(request.form['image_id'])
            backend.update_image_labels(previous_image_id, label_objects)
            backend.update_image_labels(
                previous_image_id, labelled_by, label_status[labelled_by]['label_memo'])
            # print(request.form)
            current_index = label_status[labelled_by]['next_index']
            if current_index == len(label_status[labelled_by]['image_id_list']):
                return 'All Images Done!' # TODO: 狗狗
            label_status[labelled_by]['next_index'] += 1
            image_id = label_status[labelled_by]['image_id_list'][current_index]
            img = backend.get_image_from_image_id(image_id)
            image_property = {
                'room_type': img.room_type,
                'style': img.style,
                'labelled_by': img.labelled_by,
                'label_memo': img.label_memo,
                'label_time': img.label_time
            }
            if current_index + 1 == len(label_status[labelled_by]['image_id_list']):
                next_image_id = ''
            else:
                next_image_id = label_status[labelled_by]['image_id_list'][current_index+1]
            return render_template(
                'label.html', 
                image_id=image_id,
                image_property=image_property,
                next_image_id=next_image_id,
                previous_image_id=previous_image_id,
                image_path=img.image_path,
                existing_labels_json=img.generate_existing_labels_json(),
                labelled_by=labelled_by,
                object_type_list=OBJECT_TYPE_LIST,
            )
    else:
        labelled_by = request.args['labelled_by']
        image_id_list = label_status[labelled_by]['image_id_list']
        image_id = int(request.args['image_id'])
        if image_id not in image_id_list:
            return 'image_id: {} is not in your list.'.format(image_id)
        img = backend.get_image_from_image_id(image_id)
        image_property = {
                'room_type': img.room_type,
                'style': img.style,
                'labelled_by': img.labelled_by,
                'label_memo': img.label_memo,
                'label_time': img.label_time
        }
        current_index = image_id_list.index(image_id)
        label_status[labelled_by]['next_index'] = current_index + 1
        if current_index == len(image_id_list) - 1:
            next_image_id = ''
        else:
            next_image_id = image_id_list[current_index+1]
        if current_index == 0:
            previous_image_id = ''
        else:
            previous_image_id = image_id_list[current_index-1]
        return render_template(
            'label.html', 
            image_id=image_id,
            image_property=image_property,
            next_image_id=next_image_id,
            previous_image_id=previous_image_id,
            image_path=img.image_path,
            existing_labels_json=img.generate_existing_labels_json(),
            labelled_by=labelled_by,
            object_type_list=OBJECT_TYPE_LIST
        )


@app.route('/quit')
def quit():
    labelled_by = request.args['labelled_by']
    image_id_list = label_status[labelled_by]['image_id_list']
    next_index = label_status[labelled_by]['next_index']
    unfinished_image_id_list = image_id_list[next_index-1:]
    return '<br>'.join([str(image_id) for image_id in unfinished_image_id_list])
