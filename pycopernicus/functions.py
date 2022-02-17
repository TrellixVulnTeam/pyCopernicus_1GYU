
import zipfile
import os

# check file allowed to upload
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def unZip(filezip, path):
    with zipfile.ZipFile(filezip, 'r') as zip_ref:
        extracted = zip_ref.namelist()
        zip_ref.extractall(path)
    return os.path.join(path, extracted[0])

# delete file downloaded
def delete_folder(path):
    for file in path:
        os.remove(file)
