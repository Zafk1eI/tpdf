import os
from glob import glob
from urllib.parse import quote
from pdfrw import PdfReader
import zipfile
import json
import csv

from io import BytesIO
from flask import (
    Blueprint,
    session,
    request,
    render_template,
    jsonify,
    send_file,
)
from werkzeug.utils import secure_filename

from libs.tpdf import TPdf

router = Blueprint("handlers", __name__)


def get_pdf_page_size(file_path):
    pdf = PdfReader(file_path)
    first_page = pdf.pages[0]
    width = float(first_page.MediaBox[2])
    height = float(first_page.MediaBox[3])
    return height, width


class ResponseFile:
    @staticmethod
    def create_response(file_name, file_body):
        # headers = {
        #     "Content-Type": 'application/pdf; charset="utf-8"',
        #     "Content-Disposition": f'inline; filename="{file_name}"',
        # }
        return send_file(
            BytesIO(file_body),
            mimetype="application/pdf",
            download_name=file_name,
            as_attachment=False,
        )


@router.before_request
def make_session():
    session.permanent = True


@router.route("/tpdf/positioning/<string:certificate_id>", methods=["GET"])
def positioning(certificate_id):

    height, width = get_pdf_page_size(
        os.path.join("libs", "tpdf_templates", certificate_id, "form.pdf")
    )

    if height > width:
        orientation = "portrait"
    else:
        orientation = "landscape"

    tpdf = TPdf(page_orientation=orientation)
    # дефолтные параметры

    page_num = request.args.get("page_num")

    in_data = {
        "pdf_name": f"{certificate_id}",
        "page_num": f"{page_num}",
    }

    # Ограничение страниц
    fields = tpdf.load_fields_from_file(
        height, name=in_data["pdf_name"], to_front=True
    )

    # if str(int(page_num) - 1) not in list(fields.keys()):
    #     in_data["page_num"] = "1"
    # else:
    #     in_data.update(request.args.to_dict())

    fonts = [
        os.path.basename(filename)[:-4]
        for filename in glob(os.path.join(tpdf.FONTS, "*.ttf"))
    ]
    in_data.update({"fields": fields, "fonts": fonts})
    return render_template(
        "positioning.html", **in_data, 
        page_height=height, 
        page_width=width, 
        certificate_id=certificate_id,
    )
    
@router.route("/tpdf/update_font", methods=["POST"])
def update_font():
    data = request.json
    json_path = os.path.join('libs', 'tpdf_templates', data['pdf_name'], 'fields.json')
    try:
        with open(file=json_path, mode="r", encoding='utf-8') as json_file:
            fields = json.load(json_file)
    except FileNotFoundError:
        return jsonify({"status": "error", "message": "File not found"}), 404
    except json.JSONDecodeError:
        return jsonify({"status": "error", "message": "Invalid JSON format"}), 400
    
    updated = False
    
    for page, field_list in fields.items():
        if str(page) == str(data['page_num']):
            for field in field_list:
                field_name = field[2]
                if field_name in data['font_sizes']:
                    field_font_size = data['font_sizes'][field_name]
                    field[4] = int(field_font_size)
                    field[6] = bool(data['visibility'][field_name])
                    updated = True
        else:
            continue

    if not updated:
        return jsonify({"status": "error", "message": "Field not found"}), 404
    
    # Сохранение обновленного JSON-файла
    with open(json_path, "w", encoding='utf-8') as json_file:
        json.dump(fields, json_file, ensure_ascii=False, indent=4)

    return jsonify({"status": "success"}), 200

    
@router.route('/tpdf/upload_csv', methods=['POST'])
def upload_csv():
    if request.method != "POST":
        return jsonify({"error": "unsupported method"}), 400
    
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    csv_content = file.read().decode('utf-8')
    session['csv_data'] = csv_content
    
    return jsonify({"message": "CSV uploaded seccessfully"}), 200


@router.route("/tpdf/generate_and_download/<string:certificate_id>", methods=["GET"])
def generate_and_download(certificate_id):
    # TODO : логика обработки данных
    # TODO : Выбор csv-файла
    # пример полученных данных
    json_data = {
        "data":
            {
                
            }
    }
    user_data = json_data["data"][0]
    print(user_data)
    
    zip_data = BytesIO()
    
    with zipfile.ZipFile(zip_data, mode='w') as z:
        for index, user_data in enumerate(json_data["data"]):
            tpdf = TPdf(**user_data)
            file = tpdf.get_pdf(certificate_id, b64='False')
            z.writestr(f"{certificate_id}_{index}_{user_data["name"]}.pdf", file)
            del tpdf
    zip_data.seek(0)
    
    return send_file(
        zip_data,
        mimetype="application/zip",
        as_attachment=True,
        download_name=f"{certificate_id}_certificates.zip"
    )

@router.route("/tpdf/generate/<certificate_id>", methods=["POST"])
def generate_one(certificate_id):
    data = request.json
    
    if not data:
        return jsonify({"error": "invalid data"}), 400
    
    user_data = data['data'][0]
    
    if not data['data']:
        return jsonify({"error": "missing data key"}), 400
    
    json_path = os.path.join('libs', 'tpdf_templates', certificate_id, 'fields.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        fileds_data = json.load(f)
    
    for key in fileds_data:
        elements = fileds_data[key]
        
        for element in elements:
            fields_name = element[2]
            is_true = element[6]
            
            if is_true:
                if fields_name not in user_data:
                    return jsonify({"error": "missing fields", "fields": fields_name}), 400
            
    tpdf = TPdf(**user_data)
    file = tpdf.get_pdf(certificate_id, b64='False')
    pdf_buffer = BytesIO(file)
    
    return send_file(
        pdf_buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"test.pdf"
    )

@router.route("/tpdf/save_form_fields", methods=["POST"])
def save_form_fields():
    rq = request.json
    page_height = rq["page_height"]
    TPdf.save_fields_to_file(rq["pos"], page_height=page_height)
    return jsonify({"status": "success"})


mime = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "bmp": "image/bmp",
    "gif": "image/gif",
    "pdf": "application/pdf",
    "xls": "application/vnd.ms-excel",
    "xlsx": "application/vnd.ms-excel",
    "xlsm": "application/vnd.ms-excel",
    "doc": "application/msword",
    "docx": "application/msword",
    "rtf": "application/rtf",
    "ppt": "application/powerpoint",
    "pptx": "application/powerpoint",
}


@router.route("/tpdf/get_file", methods=["GET"])
def get_file():
    pdf_name = request.args.get("pdf_name")
    print(pdf_name)
    tpdf = TPdf()
    file = tpdf.get_pdf(pdf_name, b64="False", fill_x=True)

    return ResponseFile.create_response(pdf_name, file)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() == "pdf"


@router.route("/tpdf/create_directory/<string:certificate_id>", methods=["POST"])
def upload_file(certificate_id):
    data = {
    "0": [
        [323.25, 427.45, "full_name", "DejaVuSans", 12, 134, True],
        [321.75, 392.95, "event_title", "DejaVuSans", 24, 259, True],
        [485.25, 229.45, "stage", "DejaVuSans", 12, 119, True],
        [154.5, 225.7, "end_date", "DejaVuSans", 12, 88, True],
        [154.5, 225.7, "organization_name", "DejaVuSans", 12, 88, True],
        [154.5, 225.7, "team_name", "DejaVuSans", 12, 88, True],
    ]
}
    if request.method == "POST":
        if "file" not in request.files:
            return jsonify({"error": "No file"}), 400
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400
        if file and allowed_file(file.filename):
            filename = secure_filename("form.pdf")
            directory = os.path.join("libs", "tpdf_templates", certificate_id)
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=False)
                file.save(os.path.join(directory, filename))
                with open(os.path.join(directory, "fields.json"), "w") as json_file:
                    json.dump(data, json_file, ensure_ascii=False, indent=4)
                return jsonify({"message": "Upload seccessfully"}), 200
            else:
                return jsonify({"error": "dir exist"}), 400
        else:
            return jsonify({"error": "File type not allowed"}), 400


@router.route("/tpdf/example/<certificate_id>", methods=["GET"])
def example(certificate_id):

    data = {
        "data": {
            "full_name": "Иван Иванов",
            "event_title": "Чемпионат по программированию",
            "stage": "Финал",
            "team_name": "Команда А",
            "organization_name": "ООО Программирование",
            "end_date": "2024-12-31"
        }
    }
    # набор данных для генерации комплекта документов
    user_data = data["data"]
    # загружаем данные в основной класс и получаем комплект документов в pdf
    tpdf = TPdf(**user_data)
    # можно сгенерировать один файл или комплект документов
    file = tpdf.get_pdf(f'{certificate_id}', b64='False')

    return ResponseFile.create_response(f"{list(user_data.values())[0]}.pdf", file)
