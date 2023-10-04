from flask import Flask, render_template
from flask_mysqldb import MySQL
from controllers.annee_controller import AnneeController
from controllers.global_controller import GlobalController

app = Flask(__name__)
app.secret_key = 'mIlTkQ6kFlKVJ1ANl3vR7jSioF6PVhTv'

# Configure MySQL connection
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'twitch'

mysql = MySQL(app)

@app.route('/')
def accueil():
    return render_template('accueil.html')

@app.route('/global', methods=['GET'])
def global_vue():
    global_controller = GlobalController()
    return global_controller.index(mysql)

@app.route('/toggle_graph', methods=['POST'])
def toggle_graph():
    global_controller = GlobalController()
    return global_controller.toggle_graph()

@app.route('/annee', methods=['GET', 'POST'])
def annee_vue():
    annee_controller = AnneeController()
    return annee_controller.index()
@app.route('/annee/<year>')
def annee_vue_id(year):
    return render_template('annee.html', year=year)

@app.route('/jeu', methods=['GET'])
def jeu_vue():
    return render_template('jeu.html')

if (__name__ == '__main__'):
    app.run(debug=True)