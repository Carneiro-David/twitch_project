import pandas as pd
from flask import Flask, request, render_template, jsonify
from flask_mysqldb import MySQL
import json
import matplotlib.pyplot as plt
import io
import base64
import matplotlib
import datetime
import re



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

@app.route('/jeu/<jeu>', methods=['GET', 'POST'])
def filter_data(jeu):
    cursor = mysql.connection.cursor()

    selected_year = None
    data_json2 = None 
    dataFrameAnnee = pd.DataFrame()

    if request.method == 'POST':
        selected_year = request.form.get('year')
        if selected_year:
            query = "SELECT * FROM game_data WHERE game=%s AND year=%s"
            cursor.execute(query, (jeu, selected_year))
            dataFrameAnnee = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])

            # Remplacer les numéros des mois par leurs abréviations
            month_mapping = {1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Avr', 5: 'Mai', 6: 'Jun',
                            7: 'Jul', 8: 'Aou', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
            dataFrameAnnee['month'] = dataFrameAnnee['month'].replace(month_mapping)

            # Convertir les mois en catégorie et spécifier l'ordre des catégories
            months_order = ['Jan', 'Fev', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aou', 'Sep', 'Oct', 'Nov', 'Dec']
            dataFrameAnnee['month'] = pd.Categorical(dataFrameAnnee['month'], categories=months_order, ordered=True)

            data_json2 = json.dumps(dataFrameAnnee.to_dict(orient='records'))



    query = "SELECT DISTINCT year FROM game_data WHERE game=%s" 
    cursor.execute(query, (jeu,)) 
    years = [row[0] for row in cursor.fetchall()]

    query = "SELECT * FROM game_data WHERE game=%s"
    cursor.execute(query, (jeu,))
    data_df = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])

    query = "SELECT game, MAX(peak_viewers) as peak_viewer, year FROM game_data WHERE game =%s GROUP BY year ORDER BY year ASC;"
    cursor.execute(query, (jeu,))
    data_df_peak_viewer = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])
    data_json3 = json.dumps(data_df_peak_viewer.to_dict(orient='records'))
    table_data = json.loads(data_json3)



    cursor.close()

    myDatetime = datetime.datetime.now()
    current_year = myDatetime.year

    avg_viewers_by_year = data_df.groupby('year')['avg_viewers'].mean()
    avg_viewers_by_year.plot(kind='bar')
    ax = avg_viewers_by_year.plot(kind='bar') 

    ax.grid(True, linestyle='-', linewidth=0.5, color='lightgrey') 
    ax.set_axisbelow(True)
    plt.xlabel('Année') 
    plt.xticks(rotation=0)
    plt.ylabel('Nombre moyen de spectateurs')
    plt.title('Nombre moyen de spectateurs par année')

    image_buffer = io.BytesIO()
    plt.savefig(image_buffer, format='png')
    image_buffer.seek(0)

    chart_image = base64.b64encode(image_buffer.read()).decode('utf-8')

    chart_image_annee = None
    if not dataFrameAnnee.empty:
        avg_viewers_by_month = dataFrameAnnee.groupby('month')['avg_viewers'].mean().sort_index()
        ax = avg_viewers_by_month.plot(kind='bar')

        plt.xlabel('Mois')
        plt.xticks(rotation=0)
        ax.grid(True, linestyle='-', linewidth=0.5, color='lightgrey') 
        ax.set_axisbelow(True)

        plt.ylabel('Nombre moyen de spectateurs')
        plt.title("Nombre moyen de spectateurs par mois pour l'année " + selected_year)

        image_buffer = io.BytesIO()
        plt.savefig(image_buffer, format='png')
        image_buffer.seek(0)
        chart_image_annee = base64.b64encode(image_buffer.read()).decode('utf-8')
        plt.clf()

    return render_template('Home/index.html',table = table_data, graphAnne = chart_image_annee, chart_image_by_year=chart_image, years=years, dataAnnee = data_json2, annee = selected_year, current_year = current_year)

if __name__ == '__main__':
    app.run(debug=True)
