import os
import requests
from flask import Flask, flash, request, redirect, url_for, render_template, session
from werkzeug.utils import secure_filename
import pydicom
import cv2
import numpy

UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']

app = Flask(__name__, template_folder='template')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "Neeraj123"

@app.route('/empty_page')
def empty_page():
    filename = session.get('filename', None)
    os.remove(os.path.join(UPLOAD_FOLDER, filename))
    return redirect(url_for('index'))

@app.route('/pred_page')
def pred_page():
    pred = session.get('pred_label', None)
    f_name = session.get('filename', None)
    print("debug6")
    return render_template('pred.html', pred=pred, f_name=f_name)

@app.route('/', methods=['POST', 'GET'])
def index():
    # try:
    if request.method == 'POST':
        f = request.files['bt_image']
        filename = str(f.filename)
        # if request.form['submit_button'] == 'Submit':
        #     pass
        if filename!='':
            ext = filename.split(".")  
            if len(ext) == 1 or ext[1] == 'dcm':
                if len(ext) == 1:
                    filename = filename + ".dcm"
                ds = pydicom.dcmread(request.files['bt_image'])

                # pixel_array_numpy = numpy.hstack((ds.pixel_array,ds.pixel_array,ds.pixel_array))
                # pixel_array_numpy = pixel_array_numpy.reshape(pixel_array_numpy.shape[1],pixel_array_numpy.shape[1],pixel_array_numpy.shape[0])
                # pixel_array_numpy = numpy.array(list(map(lambda x : numpy.array([x,x,x]),ds.pixel_array)))
                array = []
                for i in range(len(ds.pixel_array)):
                    array0 =[]
                    for j in range(len(ds.pixel_array[0])):
                        array0.append([ds.pixel_array[i][j],ds.pixel_array[i][j],ds.pixel_array[i][j]])
                    array.append(array0)
                array = numpy.array(array)
                print("ds.pixel_array",ds.pixel_array.shape)
                print("pixel_array_numpy",array.shape)
                filename = filename.replace('.dcm', '.jpg')
                cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'], filename), array)
                
            #ALLOWED_EXTENSIONS has direct image files, not dicom
            elif ext[1] in ALLOWED_EXTENSIONS:
                filename = secure_filename(f.filename)
                print("debug2")
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                print("debug3")
            else:
                print("Invalid Image Format. Please try again.")
            with open(os.path.join(app.config['UPLOAD_FOLDER'], filename),'rb') as img:
                predicted = requests.post("http://localhost:5000/predict", files={"file": img}).json()
            print("debug4")
            session['pred_label'] = predicted['class_name']
            session['filename'] = filename
            print("debug5")
            return redirect(url_for('pred_page'))

    # except Exception as e:
    #     print("Exception\n")
    #     print(e, '\n')

    return render_template('index.html')

if __name__=="__main__":
    app.run(port=3000,debug=True)
    