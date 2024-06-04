import os
from glob import glob
from urllib.parse import quote
from pdfrw import PdfReader
import zipfile

# import aiohttp_jinja2
# from aiohttp import web
from io import BytesIO
from flask import (
    Blueprint,
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
        page_height=height, name=in_data["pdf_name"], to_front=True
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
        certificate_id=certificate_id
    )
    
    
@router.route("/tpdf/generate_and_download/<string:certificate_id>", methods=["GET"])
def generate_and_download(certificate_id):
    # TODO : логика обработки данных
    # TODO : Выбор csv-файла
    # пример полученных данных
    json_data = {
        "data": [
            {
                "name": "Вася Пупкин",
                "nickname": "MusicalDisaster",
                "discipline": "Dota 2" ,
                "event_period": "12.02.2004 - 13.02.2004",
                "chairman": "Ф. И. Васильев",
                "team": "IDMAN",
                "winner_tournament": "КИПУ Dota 2" 
            },
            {
                "name": "Вася Пупкин",
                "nickname": "MusicalDisaster",
                "discipline": "Dota 2" ,
                "event_period": "12.02.2004 - 13.02.2004",
                "chairman": "Ф. И. Васильев",
                "team": "IDMAN",
                "winner_tournament": "КИПУ Dota 2" 
            }
        ]
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
    if request.method == "POST":
        if "file" not in request.files:
            return jsonify("error: No file"), 400
        file = request.files["file"]
        if file.filename == "":
            return jsonify("error: No selected file"), 400
        if file and allowed_file(file.filename):
            filename = secure_filename("form.pdf")
            directory = os.path.join("libs", "tpdf_templates", certificate_id)
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=False)
                file.save(os.path.join(directory, filename))
                with open(os.path.join(directory, "fields.json"), "w") as json:
                    pass
                return jsonify("message: Upload seccessfully"), 200
            else:
                return jsonify("error: dir exist"), 400
        else:
            return jsonify({"error: File type not allowed"}), 400


@router.route("/tpdf/example", methods=["GET"])
def example():

    data = {
        "data": {
            "last_name": "Иванова",
            "first_name": "Мария",
            "middle_name": "Иванова",
            "gender": "Ж",
            "birth_date": "01.01.2000",
            "birth_place": "г.Москва",
            "registration": "г.Москва, ул. Полковника Исаева, дом 17, кв 43",
            "phone": "+7978010000",
            "Telephone": 1234,
            "1_work": "Радистка 3 категории, в/ч 89031",
            "2_work": "Радистка 1 категорvalues/ч 17043",
            "3_work": "Командир отделения радистов, в/ч 17043 главного управления разведки комитета государственной безопасности республики Беларусь.",
        },
        "complete": [
            ["409f05934Rtyh", 1],
            ["ZayavlenieNaZagranpasport", 1],
        ],
    }

    # перечень документов в комплекте
    complete = data["complete"]
    # набор данных для генерации комплекта документов
    user_data = data["data"]
    # загружаем данные в основной класс и получаем комплект документов в pdf
    tpdf = TPdf(**user_data)
    # можно сгенерировать один файл или комплект документов
    # file = tpdf.get_pdf('ZayavlenieNaZagranpasport', b64='False')

    file = tpdf.get_complete(complete=complete, b64="False")

    with open(file="static/done/save.pdf", mode="wb") as f:
        f.write(file)

    return ResponseFile.create_response(f"{list(user_data.values())[0]}.pdf", file)
