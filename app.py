from flask import Flask, request, render_template, send_from_directory
import os
import subprocess
import imageio
import numpy as np
from tkinter import colorchooser

# Initialiser l'application Flask
app = Flask(__name__)
if __name__ == '__main__':
    app.run(debug=True, port=5002)  # Vous pouvez remplacer 5001 par le port que vous souhaitez

# Fonction pour ouvrir le sélecteur de couleur
def select_color():
    color_code = colorchooser.askcolor(title="Choisir la couleur à supprimer")[0]
    if color_code:
        return tuple(map(int, color_code))  # Retourne la couleur sous forme de tuple (R, G, B)
    return None

# Fonction pour enlever les pixels d'une couleur spécifique et convertir en DXT
def remove_color_pixels(image_path, output_path, color):
    img = imageio.imread(image_path)
    if img.shape[2] == 3:  # RGB
        img = np.dstack([img, np.ones((img.shape[0], img.shape[1]), dtype=np.uint8) * 255])  # Ajouter un canal alpha complet

    for y in range(img.shape[0]):
        for x in range(img.shape[1]):
            r, g, b, a = img[y, x]  # Récupérer les valeurs des pixels (RGBA)
            if r == color[0] and g == color[1] and b == color[2]:
                img[y, x] = [0, 0, 0, 0]  # Rendre le pixel transparent

    # Sauvegarder l'image temporaire
    temp_image_path = output_path.replace('.dxt', '_temp.png')
    imageio.imwrite(temp_image_path, img)

    # Utiliser Crunch pour convertir l'image en DXT
    subprocess.run(['crunch', '-dxt5', temp_image_path, '-o', output_path], check=True)

    # Renommer le fichier en .dxt après la conversion
    os.rename(output_path, output_path.replace('.dds', '.dxt'))

# Page d'accueil
@app.route('/')
def index():
    return render_template('index.html')

# Fonction pour gérer le téléchargement du fichier et le traitement
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'Aucun fichier sélectionné.'
    
    file = request.files['file']
    if file.filename == '':
        return 'Aucun fichier sélectionné.'

    # Sauvegarder le fichier téléchargé
    file_path = os.path.join('static/uploads', file.filename)
    file.save(file_path)

    # Choisir la couleur à supprimer
    color = select_color()
    if color:
        output_image_path = os.path.join('static/uploads', f"{os.path.splitext(file.filename)[0]}_dxt.dxt")
        remove_color_pixels(file_path, output_image_path, color)
        return send_from_directory('static/uploads', os.path.basename(output_image_path))

    return 'Couleur non sélectionnée, le processus a été annulé.'

if __name__ == '__main__':
    app.run(debug=True)
