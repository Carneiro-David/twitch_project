from controllers.global_controller import GlobalController
import pandas as pd
from flask import Flask, request, render_template, jsonify
from flask_mysqldb import MySQL
import json
import matplotlib.pyplot as plt
import io
import base64
import matplotlib
import datetime
import pandas as pd
from raceplotly.plots import barplot
import plotly.graph_objects as go
import plotly
from random import sample
import random

app = Flask(__name__)
app.secret_key = 'mIlTkQ6kFlKVJ1ANl3vR7jSioF6PVhTv'

# Configure MySQL connection
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'twitch'

mysql = MySQL(app)
matplotlib.use('Agg')

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


@app.route('/jeu')
def allGames():
    cursor = mysql.connection.cursor()
    
    query = "SELECT game, sum(hours_watched) as sumHours FROM `game_data` group by game ORDER BY `sumHours` DESC"
    cursor.execute(query)
    
    data_df = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])
    
    cursor.close()
    
    data_dict = data_df.to_dict(orient='records')
    
    return render_template('listJeu.html', table=data_dict)


@app.route('/jeu/<jeu>', methods=['GET', 'POST'])
def jeu_vue(jeu):
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

            month_mapping = {1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Avr', 5: 'Mai', 6: 'Jun',
                            7: 'Jul', 8: 'Aou', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
            dataFrameAnnee['month'] = dataFrameAnnee['month'].replace(month_mapping)

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

    query ="SELECT game, sum(hours_streamed) as hours_streamed FROM `game_data` where game =%s ORDER BY `game_data`.`game` DESC"
    cursor.execute(query, (jeu,))
    hour_streamed = cursor.fetchall()

    query ="SELECT game, sum(hours_watched), year FROM `game_data` where game =%s group by year ORDER BY `game_data`.`game` DESC"
    cursor.execute(query, (jeu,))
    hours_watched = cursor.fetchall()
    
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

    return render_template('jeu.html', hours_watched = hours_watched, hours_streamed= hour_streamed, table = table_data, graphAnne = chart_image_annee, chart_image_by_year=chart_image, years=years, dataAnnee = data_json2, annee = selected_year, current_year = current_year)

@app.route('/timeline/', methods=['GET'])
def annee_vue():
    cursor = mysql.connection.cursor()

    query = """
    SELECT
        year,
        month,
        game,
        ROW_NUMBER() OVER (PARTITION BY year, month ORDER BY hours_watched DESC) AS game_rank,
        hours_watched,
        hours_streamed,
        peak_viewers
    FROM
        game_data
    WHERE
        game_data.rank <= 10
    ORDER BY
        year ASC,
        month ASC,
        game_data.rank ASC;
    """

    cursor.execute(query)
    top_games = cursor.fetchall()

    grouped_data = {}

    for year, month, game, game_rank, hours_streamed, peak_viewers, hours_watched in top_games:
        if year not in grouped_data:
            grouped_data[year] = {}
        if month not in grouped_data[year]:
            grouped_data[year][month] = []

        grouped_data[year][month].append({
            'game': game,
            'game_rank': game_rank,
            'hours_streamed': hours_streamed,
            'hours_watched': hours_watched,
            'peak_viewers': peak_viewers
        })

    data_df = pd.DataFrame(top_games, columns=[desc[0] for desc in cursor.description])
    
    my_raceplot = barplot(data_df, item_column="game", value_column="peak_viewers", time_column="year")
    my_raceplot.plot(title = 'Top 10 best game from 2015 to 2023', item_label = 'Top 10 jeux', value_label = 'Peek de viewers', frame_duration = 800)

    fig = {
        "data": [],
        "layout": {},
        "frames": []
    }
    
    unique_games = data_df['game'].unique()
    game_colors = {game: 'rgb({}, {}, {})'.format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for game in unique_games}
    data_df['color'] = data_df['game'].map(game_colors)

    frame1 = data_df[data_df['year'] == data_df['year'].min()]

    top_entries = 10
    frame1 = frame1.iloc[:top_entries, :]
    frame1 = frame1.sort_values('game_rank', ascending = False).iloc[:top_entries, :]
    fig['data'] = go.Bar(
        x = frame1['hours_watched'],
        y = frame1['game'],
        marker_color = frame1['color'],
        hoverinfo = 'all',
        textposition = 'outside',
        # texttemplate = '%{y}',
        texttemplate = '%{y}<br>%{x:.4s}',
        orientation = 'h',
        textfont = {'size': 20}
    )

    fig['layout'] = go.Layout(
        font = {'size' : 14},
        plot_bgcolor = 'white',
        xaxis = {
            'showline': True,
            'visible': True,
            'range': (0, data_df['hours_watched'].max()),
            'title_text': 'Heures visionnées' # title of the x axis,
        },
        yaxis = {
            'showline': False, 
            'visible': True, # to show the title
            'showticklabels': False, # to avoid displaying the names
            'title_text': 'Top 10 des jeux'
        }, # title of the y axis
        bargap = 0.15, # number btwn 0 and 1, sets gap between adjacent bars (as plot fraction)
        title = 'Jeux les plus regardés', # sets title for default plot
        height = 650
    )

    sliders_dict = {
        "active": 0,
        "yanchor": "top",
        "xanchor": "left",
        "currentvalue": {
            "font": {"size": 20},
            "prefix": "Year:",
            "visible": True,
            "xanchor": "right"
        },
        "transition": {"duration": 1500, "easing": "cubic-in-out"},
        "pad": {"b": 10, "t": 50},
        "len": 0.9,
        "x": 0.1,
        "y": 0,
        "steps": []
    }

    for year in range(data_df['year'].min(), data_df['year'].max()+1):
        snap_data = data_df[data_df['year'] == year]
        snap_data = snap_data.iloc[:top_entries,:]
        snap_data = snap_data.sort_values('game_rank', ascending=False).iloc[:top_entries,:]

        frame = go.Frame(
            data=[
                go.Bar(
                    x=snap_data['hours_watched'],
                    y=snap_data['game'],
                    marker_color=snap_data['color'],
                    hoverinfo='all',
                    textposition='outside',
                    texttemplate= '%{y}',
                    # texttemplate= '%{y}<br>%{x:.4s}',
                    orientation = 'h'
                )
            ],
            layout=go.Layout(
                font={'size': 14},
                plot_bgcolor = 'white',
                xaxis={
                    'showline': True,
                    'visible': True,
                    'range': (0, data_df['hours_watched'].max())
                },
                yaxis={
                    'showline': False,
                    'visible': False
                },
                bargap= 0.15,
                title= 'Top 10 Crops across time'
            ),
            name = year
        )
        fig['frames'].append(frame)

        slider_step = {"args": [
            [year],
            {"frame": {"duration": 300, "redraw": False},
            "mode": "immediate",
            "transition": {"duration": 300}}
        ],
        "label": year,
        "method": "animate"}
        sliders_dict["steps"].append(slider_step)

        fig['layout']['sliders'] = [sliders_dict]

    figSchema = go.Figure(fig)
    figChart64 = json.dumps(figSchema, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('timeline.html', fig=figChart64)

if __name__ == '__main__':
    app.run(debug=True)
 