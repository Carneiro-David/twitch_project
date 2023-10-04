import pandas as pd
from flask import Flask, request, render_template, jsonify
from flask_mysqldb import MySQL
import json
import matplotlib.pyplot as plt
import io
import base64
import matplotlib


app = Flask(__name__)

# Configure MySQL connection
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'twitch'

mysql = MySQL(app)

matplotlib.use('Agg')

@app.route('/')
def index():
    cursor = mysql.connection.cursor()
    
    query = "SELECT * FROM game_data"
    cursor.execute(query)
    
    data_df = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])
    
    cursor.close()
    
    data_json = json.dumps(data_df.to_dict(orient='records'))
    
    return render_template('index.html', data_json=data_json, chart_image_by_year=None)

@app.route('/<jeu>', methods=['GET'])
def filter_data(jeu):
    cursor = mysql.connection.cursor()

    query = "SELECT DISTINCT year FROM game_data WHERE game=%s" 
    cursor.execute(query, (jeu,))
    
    years = [row[0] for row in cursor.fetchall()]

    query = "SELECT * FROM game_data WHERE game=%s"
    cursor.execute(query, (jeu,))

    data_df = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])

    cursor.close()

    data_json = json.dumps(data_df.to_dict(orient='records'))

    avg_viewers_by_year = data_df.groupby('year')['avg_viewers'].mean()
    avg_viewers_by_year.plot(kind='bar')
    plt.xlabel('Année')
    plt.ylabel('Nombre moyen de spectateurs')
    plt.title('Nombre moyen de spectateurs par année')

    image_buffer = io.BytesIO()
    plt.savefig(image_buffer, format='png')
    image_buffer.seek(0)

    chart_image = base64.b64encode(image_buffer.read()).decode('utf-8')

    return render_template('Home/index.html', data_json=data_json, chart_image_by_year=chart_image, years=years, selected_year=None)

if __name__ == '__main__':
    app.run(debug=True)
