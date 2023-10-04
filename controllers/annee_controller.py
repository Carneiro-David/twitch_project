from flask import render_template, request, redirect, url_for

class AnneeController:
    def index(self):
        selected_year = request.args.get('year')
        
        if selected_year and 2016 <= int(selected_year) <= 2023:
            return render_template('annee.html', year=selected_year)
        else:
            return render_template('annee.html')