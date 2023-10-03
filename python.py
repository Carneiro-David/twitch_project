import pandas as pd
from flask import Flask, request, render_template
from flask_mysqldb import MySQL

app = Flask(__name__)

# Configure MySQL connection
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'twitch'

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('Home/index.html')

@app.route('/<jeu>', methods=['GET'])
def filter_data(jeu):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM game_data WHERE id=%s", (jeu))
    executed_data = cursor.fetchall()
    cursor.close()

    if executed_data:
        return str(executed_data[0])
    else:
        return "Le jeu n'existe pas"

if __name__ == '__main__':
    app.run(debug=True)
