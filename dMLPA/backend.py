import os
import zipfile
from datetime import datetime

img_versioned = os.getenv(
    "IMG_VERSIONED"
)  # Automatically set in the Dockerfile when deployed - can be added to reports for audit traceability


def run_backend(single_file, array_of_files, output_directory):
    # Ensure the output directory exists, if not, create it
    os.makedirs(output_directory, exist_ok=True)

    # Create a name for the zipped folder containing backend output
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    zip_name = os.path.join(output_directory, f"output_files_{timestamp}.zip")

    # Ensure all paths are absolute
    single_file = os.path.abspath(single_file)
    array_of_files = [os.path.abspath(file) for file in array_of_files]

    # Prepare the files to be zipped
    files_to_zip: list[str] = [single_file] + array_of_files

    # USER WARNINGS: Anything added to the list 'input_errors' will be passed from the backend to
    # the frontend and displayed in a warning to the user. Used to give immediate feedback to the
    # user about errors such as incorrect formatting of input files etc.
    input_errors: list[str] = []
    input_ok_flag: bool = True

    # TODO: Add any relevant data validation here.  Currently only checks if the file has "error_test"
    # in the name, and if so, sends warning to frontend.  This is just a placeholder for now.
    for file_name in files_to_zip:
        if "error_test" in file_name:
            input_errors, input_ok_flag = [
                "TEST ERROR: File passed to trigger this warning for testing purposes"
            ], False
            break

    # TODO: Add any relevant data processing here.  Currently just copies the input files to the
    # output directory.  This is just a placeholder for now.

    # Create a new Zip file
    with zipfile.ZipFile(zip_name, "w") as myzip:
        for file in files_to_zip:
            if os.path.isfile(file):
                myzip.write(
                    file, arcname=os.path.basename(file)
                )  # add file to the zip using its basename
            else:
                print(
                    f"File {file} does not exist."
                )  # Consider replacing with proper logging

    return zip_name, input_errors, input_ok_flag
