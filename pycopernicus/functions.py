
import zipfile
import os
import uuid

# check file allowed to upload
def allowed_file(app, filename):
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
    os.rmdir(path)

# create download files
def create_download_folder(app, product):

    pathFiles = os.path.abspath(
            os.getcwd()) + '/' + app.config['DOWNLOAD_FOLDER'] + '/' + str(uuid.uuid4())

    if (not os.path.isdir(pathFiles)):
        os.mkdir(pathFiles)

    pathFiles += "/" + product

    if (not os.path.isdir(pathFiles)):
        os.mkdir(pathFiles)

    print('--- create download path: ', pathFiles)

    return pathFiles