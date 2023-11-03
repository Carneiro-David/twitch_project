from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)
url_api = "http://127.0.0.1:5000"

@app.route('/')
def accueil():
    return render_template('accueil.html')

@app.route('/comment', methods=['GET'])
def comment_vue():
    return render_template('comment.html')

@app.route('/check_commentaire', methods=['POST'])
def check_commentaire():
    commentaire = request.form['comment']
    data = {'comment': commentaire}
    response = requests.post(url_api, json=data)

    if response.status_code == 200:
        reponse_api = response.json()
        validation = reponse_api['validation']

        if validation:
            resultat = "Le commentaire est positif !"
        else:
            resultat = "Le commentaire est négatif."
    else:
        resultat = "Erreur lors de la requête à l'API."

    return jsonify({'resultat': resultat})

if __name__ == '__main__':
    app.run(debug=True)
