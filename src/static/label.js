var canvas = new fabric.Canvas('canvas');
var img = new Image();
var scale_factor;
var selected_uuid = "";
img.onload = function() {
    var img_h = this.height;
    var img_w = this.width;
    var canvas_width = document.getElementById('canvas_container').clientWidth;
    canvas.setWidth(canvas_width);
    scale_factor = canvas_width / img_w;
    canvas.setHeight(scale_factor * img_h);
    canvas.setBackgroundImage(image_path, canvas.renderAll.bind(canvas),{
        scaleX: scale_factor,
        scaleY: scale_factor,
        originX: 'left',
        originY: 'top'
    });
    for (var i = 0; i < existing_labels.length; i++) {
        loadExistingLabel(
            existing_labels[i]['object_id'],
            existing_labels[i]['object_type'],
            existing_labels[i]['box_left'] * scale_factor,
            existing_labels[i]['box_top'] * scale_factor,
            existing_labels[i]['box_right'] * scale_factor,
            existing_labels[i]['box_bottom'] * scale_factor);
    }
};
img.src = image_path;

canvas.selection = false;
var rect, ellipse, line, triangle, isDown, origX, origY, textVal, activeObj;

canvas.on('mouse:down', function(o) {
    isDown = true;
    var pointer = canvas.getPointer(o.e);
    origX = pointer.x;
    origY = pointer.y;
    rect = new fabric.Rect({
        left: origX,
        top: origY,
        width: pointer.x-origX,
        height: pointer.y-origY,
        fill: '',
        stroke: 'red',
        type: 'rect',
        uuid: generateUUID(),
        strokeWidth: 1,
        selectable: false
    });
    canvas.add(rect);
    activeObj = rect;
});

canvas.on('mouse:move', function(o) {
    if (isDown) {
        var pointer = canvas.getPointer(o.e);
        var box_x = Math.max(Math.min(pointer.x, canvas.width-2), 0);
        var box_y = Math.max(Math.min(pointer.y, canvas.height-2), 0);

        if(origX>box_x){
            rect.set({ left: Math.abs(box_x) });
        }
        if(origY>box_y){
            rect.set({ top: Math.abs(box_y) });
        }
        
        rect.set({ width: Math.abs(origX - box_x) });
        rect.set({ height: Math.abs(origY - box_y) });
        canvas.renderAll();
    }
});

canvas.on('mouse:up', function(o) {
    isDown = false;
    if (activeObj.height < 4 || activeObj.width < 4) {
        canvas.remove(activeObj);
        return;
    }
    textVal = activeObj.uuid.slice(0, 4);
    //add text to the canvas.
    var _text = new fabric.Text(textVal, {
        fontSize: 10,
        fontFamily: 'Arial',
        fill : 'orange',
        type : 'text',
        selectable : false,
        left : activeObj.left + 2,
        top : activeObj.top,
        uuid : activeObj.uuid,
        type : 'text'
    });
    canvas.add(_text);
    //set coordinates for proper mouse interaction
    var objs = canvas.getObjects();
    for (var i = 0; i < objs.length; i++) {
        objs[i].setCoords();
    }
    activeObj.lockMovementX = false;
    activeObj.lockMovementY = false;
    activeObj.lockScalingX = false;
    activeObj.lockScalingY = false;
    addFormRowFromUUID(activeObj.uuid, "", "", activeObj.left, activeObj.top, activeObj.width, activeObj.height);
});

function generateUUID(){
    var d = new Date().getTime();
    if(window.performance && typeof window.performance.now === "function"){
        d += performance.now(); //use high-precision timer if available
    }
    var uuid = 'xxxxxxxxxxxxxxxxyxxxxxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (d + Math.random()*16)%16 | 0;
        d = Math.floor(d/16);
        return (c=='x' ? r : (r&0x3|0x8)).toString(16);
    });
    return uuid;
}
    canvas.on("object:modified", function (e) {
        try {
            var obj = e.target;
                //find text with the same UUID
                var currUUID = obj.uuid;
                var objs = canvas.getObjects();
                var currObjWithSameUUID = null;
                for (var i = 0; i < objs.length; i++) {
                    if (objs[i].uuid === currUUID && 
                            objs[i].type === 'text') {
                        currObjWithSameUUID = objs[i];
                        break;
                    }
                }
                if (currObjWithSameUUID) {
                    currObjWithSameUUID.left = obj.left;
                    currObjWithSameUUID.top = obj.top - 30;
                    currObjWithSameUUID.opacity = 1;
                }
            } catch (E) {
            }
    });

var _hideText = function (e) {
    try {
        var obj = e.target;
//        	 	console.log(obj);
            //find text with the same UUID
            var currUUID = obj.uuid;
            var objs = canvas.getObjects();
            var currObjWithSameUUID = null;
            for (var i = 0; i < objs.length; i++) {
                if (objs[i].uuid === currUUID && objs[i].type === 'text') {
                    currObjWithSameUUID = objs[i];
                    break;
                }
            }
            if (currObjWithSameUUID) {
                currObjWithSameUUID.opacity = 0;
            }
        } catch (E) {
        }
}

canvas.on("object:moving", function (e) {
    _hideText(e);
});
canvas.on("object:scaling", function (e) {
    _hideText(e);
});
canvas.renderAll();


function htmlToElement(html) {
    var template = document.createElement('template');
    html = html.trim(); // Never return a text node of whitespace as the result
    template.innerHTML = html;
    return template.content.firstChild;
}


function addFormRowFromUUID(uuid, object_type, box_left, box_top, box_w, box_h) {
    var box_left_original = box_left / scale_factor;
    var box_top_original = box_top / scale_factor;
    var box_w_original = box_w / scale_factor;
    var box_h_original = box_h / scale_factor;
    var html = `<div class="form-row" id="${uuid}">
                    <div class="col-md-1"></div>
                    <div class="input-group mb-1 col-md-6">
                        <div class="input-group-prepend">
                            <button id="uuid-${uuid}" onclick="selectBox(this);" class="btn btn-outline-secondary btn-sm" type="button">${uuid.slice(0,4)}</button>
                        </div>
                    </div>
                    <div class="col-md-4 form-group" id="select_form_group-${uuid}" onclick="selectBox(this);">
                    </div>
                    <div class="col-md-1">
                        <button type="button" class="btn btn-danger btn-sm" onclick="deleteBoxAndTextByUUID('${uuid}');">
                            &#10005
                        </button>
                    </div>
                    <input type="hidden" name="box_left-${uuid}" value="${box_left_original}">
                    <input type="hidden" name="box_top-${uuid}" value="${box_top_original}">
                    <input type="hidden" name="box_w-${uuid}" value="${box_w_original}">
                    <input type="hidden" name="box_h-${uuid}" value="${box_h_original}">
                </div>`;
    var row = htmlToElement(html);
    document.getElementById("label_rows").appendChild(row);

    var select = htmlToElement(`
    <select id="object_type-${uuid}" name="object_type-${uuid}" class="form-control form-control-sm combobox" onclick="selectBox(this);">
    <option></option></select>`)
    for (i = 0; i < object_type_list.length; i++) {
        var option;
        if (object_type === object_type_list[i]) {
            option = htmlToElement(`<option value=${object_type_list[i]} selected>${object_type_list[i]}</option>`);
        }
        else {
            option = htmlToElement(`<option value=${object_type_list[i]}>${object_type_list[i]}</option>`);
        }
        select.appendChild(option);
    }
    document.getElementById(`select_form_group-${uuid}`).appendChild(select);
    $(`#object_type-${uuid}`).combobox();
}

function getBoxAndTextByUUID(uuid) {
    var box_list = [];
    var objs = canvas.getObjects();
    for (var i = 0; i < objs.length; i++) {
        if (objs[i].uuid === uuid) {
            box_list.push(objs[i]);
        }
    }
    return box_list;
}

function getBoxByUUID(uuid) {
    var objs = getBoxAndTextByUUID(uuid);
    if (objs.length === 0) {
        return false;
    }
    for (var i = 0; i < 2; i++) {
        if (objs[i].get('type') === 'rect') {
            return objs[i];
        }
    }
}

function fillBox(rect) {
    rect.set("fill", "orange");
    rect.set("opacity", 0.3);
    canvas.renderAll();
}

function unfillBox(rect) {
    rect.set("fill", "");
    rect.set("opacity", 1);
    canvas.renderAll();
}

function selectBox(element) {
    var current_uuid = element.id.split("-")[1];
    if (current_uuid === selected_uuid) {
        return;
    }
    var previous_box = getBoxByUUID(selected_uuid);
    if (selected_uuid !== "" && previous_box !== false) {
        unfillBox(previous_box);
    }
    fillBox(getBoxByUUID(current_uuid));
    selected_uuid = current_uuid;
}

function deleteBoxAndTextByUUID(uuid) {
    var objs_to_delete = getBoxAndTextByUUID(uuid);
    for (var i = 0; i < objs_to_delete.length; i++) {
        canvas.remove(objs_to_delete[i]);
    }
    document.getElementById(uuid).remove();
}

function generateRandomColor(){
    var red = Math.floor(Math.random()* 255);
    var green = Math.floor(Math.random() * 255);
    var blue = Math.floor(Math.random() * 255);
    return 'rgb('+red+','+green+',' +blue+')';  
  }

function loadExistingLabelRectangle(object_id, box_left, box_top, box_right, box_bottom) {
    var color = generateRandomColor();
    rect = new fabric.Rect({
        left: box_left,
        top: box_top,
        width: (box_right - box_left),
        height: (box_bottom - box_top),
        fill: '',
        stroke: color,
        type: 'rect',
        uuid: object_id,
        strokeWidth: 1,
        selectable: false
    });
    canvas.add(rect);
    // Add UUID (object_id) Label
    textVal = object_id.slice(0, 4);
    var _text = new fabric.Text(textVal, {
        fontSize: 10,
        fontFamily: 'Arial',
        fill : color,
        type : 'text',
        selectable : false,
        left : box[0] + 2,
        top : box[1],
        uuid : object_id,
        type : 'text'
    });
    canvas.add(_text);
}

function loadExistingLabel(object_id, object_type, box_left, box_top, box_right, box_bottom) {
    addFormRowFromUUID(object_id, object_type, box_left, box_top, box_right - box_left, box_bottom - box_top);
    loadExistingLabelRectangle(object_id, box_left, box_top, box_right, box_bottom);
}
