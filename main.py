import logging
import os
from datetime import timedelta

# import aiohttp_jinja2
# import jinja2
# from aiohttp import web
from handlers.tpdf import router
from flask import Flask

from handlers import tpdf

app = Flask(__name__)
app.secret_key = "c01ae1a5f122f25ce5675f86028b536a"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

app.register_blueprint(blueprint=router)


# logging.basicConfig(level=logging.ERROR)

# app.add_routes(
#     [
#         web.get("/tpdf/positioning", tpdf.positioning),
#         web.post("/tpdf/save_form_fields", tpdf.save_form_fields),
#         web.get("/tpdf/get_file", tpdf.get_file),
#         web.get("/tpdf/example", tpdf.example),
#         web.static("/static", "static", show_index=True),
#     ]
# )


if __name__ == "__main__":
    app.run(port=8001, debug=True)
    
