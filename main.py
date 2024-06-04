import logging
import os

# import aiohttp_jinja2
# import jinja2
# from aiohttp import web
from handlers.tpdf import router
from flask import Flask

from handlers import tpdf

app = Flask(__name__)

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
