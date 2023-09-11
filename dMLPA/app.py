from argparse import Namespace
from datetime import datetime
from backend import run_backend
from flask import (
    Flask,
    render_template,
    Response,
    send_file,
    jsonify,
    request,
    session,
    Blueprint,
)
from flask_wtf import FlaskForm
from flask_session import Session
from flask_cors import CORS, cross_origin
from io import BytesIO
import os
import time
import random
import tempfile
from wtforms import (
    FileField,
    SubmitField,
    MultipleFileField,
    ValidationError,
)
from werkzeug.utils import secure_filename
import zipfile


import logging

log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logger = logging.getLogger("dMLPA_logger")

# To override the default severity of logging
logger.setLevel("DEBUG")


app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = os.environ["UPLOAD_FOLDER"]
app.config["SECRET_KEY"] = "catchmeifyoucan"
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_FILE_DIR"] = os.environ["SESSION_FILE_DIR"]
app.config["UPLOAD_EXTENSIONS"] = [
    ".xlsx",
    ".xlsx",
]  # TODO: If multiple file types, add to list i.e. [".txt", ".csv", ".xlsm", ".xlsx"]
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # File has to be less than 2MB
app.config["APPLICATION_ROOT"] = "/dMLPA"
app.config["WTF_CSRF_ENABLED"] = True

app.config.from_object(__name__)
webapp_bp = Blueprint(
    "dMLPA",
    __name__,
    url_prefix="/dMLPA",
)
Session(app)
CORS(app, supports_credentials=True)


def validate_input_file(form, field):
    allowed_extensions = [
        "xlsx"
    ]  # TODO: If multiple file types, add to list i.e. ["xlsm", "xlsx"]
    file = field.data
    if not file:
        raise ValidationError("No file provided.")
    if not file.filename:
        raise ValidationError("No file selected.")
    if not (
        "." in file.filename
        and file.filename.rsplit(".", 1)[1].lower() in allowed_extensions
    ):
        raise ValidationError(
            f"Invalid file type for input file '{file.filename}'. Allowed types are: xlsx"  # TODO: Ammend file types as appropriate i.e. "xlsm, xlsx"
        )


def validate_input_files_array(form, field):
    allowed_extensions = [
        "xlsx"
    ]  # TODO: Ammend file types as appropriate i.e. ["xlsm", "xlsx"]
    files = field.data
    if not files:
        raise ValidationError("No files provided.")
    for file in files:
        if not file.filename:
            raise ValidationError("No files selected.")
        if not (
            "." in file.filename
            and file.filename.rsplit(".", 1)[1].lower() in allowed_extensions
        ):
            raise ValidationError(
                f"Invalid file type for input files '{file.filename}'. Allowed types are: xlsx"  # TODO: Ammend file types as appropriate i.e. "xlsm, xlsx"
            )


class ChangeForm(FlaskForm):
    single_file = FileField(
        "Input file:",
        validators=[validate_input_file],
        render_kw={
            "accept": ".xlsx",
            "id": "single_file",
        },  # TODO: If multiple file types, add to list i.e. [".xlsm, .xlsx"]
    )
    multiple_array_of_files = MultipleFileField(
        "Multiple Input Files:",
        validators=[validate_input_files_array],
        render_kw={
            "accept": ".xlsx",
            "multiple": "True",
            "id": "multiple_array_of_files",
        },  # TODO: If multiple file types, add to list i.e. [".xlsm, .xlsx"]
    )
    submit = SubmitField("Run dMLPA")


@webapp_bp.route("/", methods=["GET", "POST"])
@cross_origin(supports_credentials=True)
def form(backend_state="initial"):
    chgForm = ChangeForm()
    chgDetail = dict()

    if request.method == "POST" and chgForm.validate_on_submit():
        if chgForm.errors:
            return render_template(
                "index.html",
                form=chgForm,
                file_errors=chgForm.errors,
            )

        # Use FileHandler() to log to a file

        session["timestr"] = datetime.now().strftime("%Y%m%d-%H%M%S")
        os.mkdir(os.path.join(app.config["UPLOAD_FOLDER"], session["timestr"]))
        file_handler = logging.FileHandler(
            f"/var/local/dMLPA/logs/dMLPA_error.log"
        )
        formatter = logging.Formatter(log_format)
        file_handler.setFormatter(formatter)

        # Don't forget to add the file handler
        logger.addHandler(file_handler)

        input_file = chgForm.single_file.data
        single_file_uploader = SingleFileUpload()
        input_single_file = single_file_uploader.upload(input_file)

        chgDetail["input_file"] = input_single_file

        input_files_array = chgForm.multiple_array_of_files.data
        multi_file_uploader = MultiFileArrayUpload()
        input_files = multi_file_uploader.upload(input_files_array)

        chgDetail["input_files_array"] = input_files
        backend_state = "started"

        # Get the file names of the uploaded files
        input_single_file_basename = os.path.basename(input_single_file)
        input_files_basenames = [os.path.basename(file) for file in input_files]

        # Create the paths to the uploaded files
        input_single_file_tmp_path = os.path.join(
            app.config["UPLOAD_FOLDER"], session["timestr"], input_single_file_basename
        )

        input_files_tmp_paths = [
            os.path.join(app.config["UPLOAD_FOLDER"], session["timestr"], basename)
            for basename in input_files_basenames
        ]

        zipped_output, input_errors, input_ok_flag = run_backend(
            input_single_file_tmp_path,
            input_files_tmp_paths,
            app.config["UPLOAD_FOLDER"],
        )
        # Save the zipped output path to the session
        session["zipped_output"] = zipped_output

        if input_ok_flag == False:
            return render_template(
                "index.html",
                form=chgForm,
                backend_state="initial",
                errors=input_errors,  # Pass the errors to the template
                file_errors=chgForm.errors,
            )
        else:
            return render_template(
                "index.html",
                form=chgForm,
                backend_state=backend_state,
                single_file_name=input_file.filename,
                multiple_array_of_files_names=", ".join(
                    [x.filename for x in input_files_array]
                ),
                zipped_folder_name=zipped_output,
                file_errors=chgForm.errors,
            )

    return render_template(
        "index.html",
        form=chgForm,
        backend_state=backend_state,
        file_errors=chgForm.errors,
    )


class SingleFileUpload:
    def upload(self, file):
        file_name = file.filename
        if file_name == "":
            return "NULL"

        else:
            secure_file_name = secure_filename(file_name)
            file.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    session["timestr"],
                    secure_file_name,
                )
            )

            return str(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    session["timestr"],
                    secure_file_name,
                )
            )


class MultiFileArrayUpload:
    def upload(self, files):
        file_names = []

        # If 'files' is a single file object, wrap it in a list
        if not isinstance(files, (list, tuple)):
            files = [files]

        for file in files:
            file_name = file.filename
            if file_name == "":
                return "NULL"

            else:
                secure_file_name = secure_filename(file_name)
                file.save(
                    os.path.join(
                        app.config["UPLOAD_FOLDER"],
                        session["timestr"],
                        secure_file_name,
                    )
                )
                file_names.append(
                    str(
                        os.path.join(
                            app.config["UPLOAD_FOLDER"],
                            session["timestr"],
                            secure_file_name,
                        )
                    )
                )

        return file_names


@webapp_bp.route("/download", methods=["GET", "POST"])
@cross_origin(supports_credentials=True)
def download():
    # Retrieve the zipped output path from the session
    zipped_output_path = session.get("zipped_output", None)
    if zipped_output_path is None:
        # Handle the error, e.g., return a 404 error or a custom error message
        return "File not found", 404
    return send_file(
        zipped_output_path,
        download_name=session["zipped_output"],
        mimetype="application/zip",
        as_attachment=True,
    )


# Register the blueprint with your Flask application
app.register_blueprint(webapp_bp)

if __name__ == "__main__":
    app.run(debug=True)
