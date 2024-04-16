import os
import uuid
import flask
import urllib
from PIL import Image
from tensorflow.keras.models import load_model
from flask import Flask, render_template, request, send_file
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import numpy as np

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model = load_model(os.path.join(BASE_DIR, 'model.hdf5'))

ALLOWED_EXT = set(['jpg', 'jpeg', 'png', 'jfif'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXT

classes = ['Brecha', 'Arcilla', 'Conglomerado', 'Arenisca', 'Limolita']

def predict(filename, model):
    img = load_img(filename, target_size=(150, 150))
    img = img_to_array(img)
    img = np.expand_dims(img, axis=0)
    img = np.vstack([img])
    result = model.predict(img)

    dict_result = {}
    for i in range(5):
        dict_result[result[0][i]] = classes[i]

    res = result[0]
    res.sort()
    res = res[::-1]
    prob = res[:3]

    prob_result = []
    class_result = []
    for i in range(3):
        prob_result.append((prob[i] * 100).round(2))
        class_result.append(dict_result[prob[i]])

    return class_result, prob_result


@app.route('/')
def home():
    return render_template("index.html")

@app.route('/tools')
def tools():
    return render_template("tools.html")

@app.route('/success', methods=['GET', 'POST'])
def success():
    error = ''
    target_img = os.path.join(os.getcwd(), 'static/images')
    if request.method == 'POST':
        if (request.form):
            link = request.form.get('link')
            try:
                resource = urllib.request.urlopen(link)
                unique_filename = str(uuid.uuid4())
                filename = unique_filename + ".jpg"
                img_path = os.path.join(target_img, filename)
                output = open(img_path, "wb")
                output.write(resource.read())
                output.close()
                img = filename

                class_result, prob_result = predict(img_path, model)

                predictions = {
                    "class1": class_result[0],
                    "class2": class_result[1],
                    "class3": class_result[2],
                    "prob1": prob_result[0],
                    "prob2": prob_result[1],
                    "prob3": prob_result[2],
                }

                if predictions == "Brecha":
                    desctription = "Brecha"
                elif predictions == "Arcilla":
                    desctription =  "Claystone"
                elif predictions == "Conglomerado":
                    desctription = "Conglomerate"
                elif predictions == "Arenisca":
                    desctription = "Sandstone"
                else:
                    desctription = "Limolita"

            except Exception as e:
                print(str(e))
                error = 'Esta imagen no es accesible'

            if (len(error) == 0):
                return render_template('success.html', img=img, predictions=predictions, desctription=desctription)
            else:
                return render_template('tools.html', error=error)


        elif (request.files):
            file = request.files['file']
            if file and allowed_file(file.filename):
                file.save(os.path.join(target_img, file.filename))
                img_path = os.path.join(target_img, file.filename)
                img = file.filename

                class_result, prob_result = predict(img_path, model)

                predictions = {
                    "class1": class_result[0],
                    "class2": class_result[1],
                    "class3": class_result[2],
                    "prob1": prob_result[0],
                    "prob2": prob_result[1],
                    "prob3": prob_result[2],
                }

                if predictions['class1']  == "Brecha":
                    color = "Verde amarillento o marrón blanquecino."
                    tamaño = "> 2 milímetros "
                    empaque = "Abierto"
                    forma = "Angular"
                    porosity = "10 - 30% "
                    permeability = "Moderada"
                elif predictions['class1']  == "Arcilla":
                    color = "Amarillo-marrón fresco, marrón oscuro apagado."
                    tamaño = "> 2 milímetros "
                    empaque = "Abierto"
                    forma = "Redondeada"
                    porosity = "10 - 30%"
                    permeability = "Moderada"
                elif predictions['class1']  == "Conglomerado":
                    color = "Marrón claro, marrón, amarillo, rojo, gris y blanco."
                    tamaño = "1/16 a 2 milímetros"
                    empaque = "Cerrado"
                    forma = "Redondeada"
                    porosity = "14 - 49%"
                    permeability = "Moderada"
                elif predictions['class1']   == "Arenisca":
                    color = "Gris, marrón, o marrón rojizo. A veces también es blanco, amarillo, verde, rojo, púrpura, naranja, negro y otros."
                    tamaño = "1/256 a 1/16 milímetros"
                    empaque = "Cerrado"
                    forma = "Redondeada"
                    porosity = "21 - 41%"
                    permeability = "Moderada"
                elif predictions['class1']   == "Limolita":
                    color = "Gris fresco, gris marrón apagado."
                    tamaño = "< 1/256 milímetros"
                    empaque = "Cerrado"
                    forma = "Redondeada"
                    porosity = "41 - 45%"
                    permeability = "Moderada"
                else:
                    color = "-"
                    tamaño = "-"
                    empaque = "-"
                    forma = "-"
                    porosity = "-"
                    permeability = "-"

            else:
                error = "Por favor suba un archivo con extensión jpg , jpeg o png"

            if (len(error) == 0):
                return render_template('success.html', img=img, predictions=predictions, color=color, tamaño=tamaño, empaque=empaque, forma=forma, porosity=porosity, permeability=permeability)
            else:
                return render_template('tools.html', error=error)

    else:
        return render_template('tools.html')


if __name__ == "__main__":
    app.run(debug=True)

