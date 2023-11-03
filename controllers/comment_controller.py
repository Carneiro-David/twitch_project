from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name)
url_api = "http://adresse_de_votre_api/endpoint"  # Remplacez ceci par l'URL réelle de votre API

@app.route('/global', methods=['GET'])
def comment_vue():
    return render_template('comment.html')

@app.route('/check_commentaire', methods=['POST'])
def check_commentaire():
    commentaire = request.form['commentaire']
    data = {'commentaire': commentaire}
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
