import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import pandas as pd
from flask_mysqldb import MySQL

def get_years(mysql):
    cur = mysql.connection.cursor()
    cur.execute("SELECT DISTINCT year FROM global_data ORDER BY year ASC")
    years = cur.fetchall()
    cur.close()
    return [year[0] for year in years]

def get_hrswatchd_graph(mysql):
    cur = mysql.connection.cursor()
    cur.execute("SELECT year, SUM(hours_watched) AS total_hours FROM global_data GROUP BY year ORDER BY year ASC")
    data = cur.fetchall()
    cur.close()

    df = pd.DataFrame(data, columns=['Annee', 'Heures_Vues'])

    plt.figure(figsize=(10, 6))
    plt.plot(df['Annee'], df['Heures_Vues'], marker='o', linestyle='-')
    plt.title('Heures de stream vues par année')
    plt.xlabel('Année')
    plt.ylabel('Heures vues (en milliard)')
    plt.grid(True)

    # Format personnalisée pour l'axe des ordonnées
    def billions(x, pos):
        return f'{x / 1e9:.0f} Md'
    formatter = FuncFormatter(billions)
    plt.gca().yaxis.set_major_formatter(formatter)
    plt.yticks(range(0, int(max(df['Heures_Vues']) + 2000000001), 2000000000))

    
    graph_filename = 'static/global_hrswatchd_graph.png'
    plt.savefig(graph_filename)

    return graph_filename

def get_avgviewers_graph(mysql):
    cur = mysql.connection.cursor()
    cur.execute("SELECT year, AVG(avg_viewers) AS average_viewers FROM global_data GROUP BY year ORDER BY year ASC")
    data = cur.fetchall()
    cur.close()

    df = pd.DataFrame(data, columns=['Annee', 'Moyenne_Viewers'])

    plt.figure(figsize=(10, 6))
    plt.plot(df['Annee'], df['Moyenne_Viewers'], marker='o', linestyle='-')
    plt.title('Moyenne de viewers par an')
    plt.xlabel('Année')
    plt.ylabel('Moyenne des viewers (en milliers)')
    plt.grid(True)

    # Format personnalisée pour l'axe des ordonnées
    def format_thousands(x, pos):
        return f'{x / 1000:.0f} K'

    formatter = FuncFormatter(format_thousands)
    plt.gca().yaxis.set_major_formatter(formatter)
    plt.yticks(range(0, int(max(df['Moyenne_Viewers']) + 400001), 400000))

    graph_filename = 'static/global_avg_viewers_graph.png'
    plt.savefig(graph_filename)

    return graph_filename

def get_records(mysql):
    cur = mysql.connection.cursor()
    records = {}
    stat_translation = {
        'hours_watched': 'Heures vues',
        'avg_viewers': 'Moyenne de viewers',
        'peak_viewers': 'Pic de viewers',
        'streams': 'Nombre de streams',
        'avg_channels': 'Moyenne de chaînes',
        'games_streamed': 'Nb de jeux streamés'
    }
    month_translation = {
        1: 'Janvier',
        2: 'Février',
        3: 'Mars',
        4: 'Avril',
        5: 'Mai',
        6: 'Juin',
        7: 'Juillet',
        8: 'Août',
        9: 'Septembre',
        10: 'Octobre',
        11: 'Novembre',
        12: 'Décembre'
    }
    stats = ['hours_watched', 'avg_viewers', 'peak_viewers', 'streams', 'avg_channels', 'games_streamed']

    for stat in stats:
        cur.execute(f"""
            SELECT
                year, month, {stat} AS record
            FROM
                global_data
            WHERE
                (year, {stat}) = (
                    SELECT year, MAX({stat})
                    FROM global_data
                    GROUP BY year
                    ORDER BY MAX({stat}) DESC
                    LIMIT 1
                )
        """)
        data = cur.fetchall()
        df = pd.DataFrame(data, columns=['year', 'month', 'record'])

        records[stat_translation[stat]] = {
            'date': f"{month_translation[df['month'][0]]} {df['year'][0]}",
            'record': df['record'][0]
        }

    cur.close()

    return records