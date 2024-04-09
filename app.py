from flask import Flask, render_template, request, redirect, url_for, session
from functions import run_tests
import re
import os
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import time



app = Flask(__name__)
app.secret_key = '!jirhf!456__f24r'  # Secret key for sessions

#Home page of the webapp
@app.route('/')
def index():
    return render_template('index.html')

#Request when the form is submitted
@app.route('/run_tests', methods=['POST'])
def run_tests_route():

    #Retrieve the data from the request
    container_name = request.form['container_name'].strip()
    delete_after_execution = 'delete_container' in request.form
    tests = request.form.getlist('tests')
    providers = request.form.getlist('providers')

    validDockerName = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9_.-]*$') #Regex for valid Docker container name

    #Backend check on the provided data
    if not tests or not providers or len(container_name)<2 or not validDockerName.match(container_name):
        return redirect(url_for('error', type='form'))

    #Run the tests (imported function from functions.py)
    results = run_tests(container_name=container_name, tests=tests, providers=providers, remove_container=delete_after_execution) 
    
    if results is False: #Result is set to false when there is something wrong with Docker
        return redirect(url_for('error', type='docker'))

    #If we got to the results, render the template with the results and add them to the session
    session['results'] = results
    return render_template('results.html', results=results)

#Request for the error page
@app.route('/error', defaults={'type': None}) #Also possible to not specify the type of error, the template will then provide a generic message
@app.route('/error/<type>')
def error(type):
    return render_template('error.html', type=type)


# Definisci gli scopes
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Definisci l'ID e il range del foglio di calcolo
SPREADSHEET_ID = "1kPkhk67xB-buh6V4EsR9-M2-cub_SreJ56ivTYjCRgk"
RANGE_NAME = "data!A1:E"
# Metrics form page
@app.route('/metrics_form', methods=['GET', 'POST'])
def metrics_form():
    if request.method == 'POST':
        location = request.form['location']
        company = request.form['company']
        date = request.form['date']
        avg_response_time = request.form['avgResponseTime']
        peak_response_time = request.form['peakResponseTime']
        error_rate = request.form['errorRate']
        avg_concurrency = request.form['avgConcurrency']
        peak_concurrency = request.form['peakConcurrency']

        # Write data to Google Sheet
        data = [location, company, date, avg_response_time, peak_response_time, error_rate, avg_concurrency, peak_concurrency]
        write_to_sheet(data)

        return 'Dati inviati con successo al foglio di lavoro Google Sheet.'
    # Else if the method is get compile the metrics form
    results = session.get('results', [])
    return render_template('metrics_form.html', results=results)
    # Logic for the metrics form page...
    #return render_template('metrics_form.html')
def write_to_sheet(data):
    # Carica le credenziali dal file del service account
    creds = Credentials.from_service_account_file(
        "credentials.json", scopes=SCOPES)

    # Costruisci il client per l'API di Google Sheets
    service = build("sheets", "v4", credentials=creds)

    try:
        # Chiama l'API di Google Sheets per scrivere i dati
        sheet = service.spreadsheets()
        # Calcola la prossima riga vuota nel foglio di lavoro
        next_row = len(sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                           range=RANGE_NAME).execute().get("values", [])) + 1
        # Scrivi i dati nella prossima riga vuota del foglio di lavoro
        sheet.values().update(spreadsheetId=SPREADSHEET_ID, 
                              range=f"data!A{next_row}",
                              valueInputOption="USER_ENTERED",
                              body={"values": [data]}).execute()
    except HttpError as err:
        print(err)



@app.route('/submit_metrics', methods=['POST'])
def submit_metrics():
    # Recupera i dati dal form
    location = request.form['location']
    company = request.form['company']
    date = request.form['date']
    avg_response_time = request.form['avgResponseTime']
    peak_response_time = request.form['peakResponseTime']
    error_rate = request.form['errorRate']
    avg_concurrency = request.form['avgConcurrency']
    peak_concurrency = request.form['peakConcurrency']

    # Scrivi i dati nel Google Sheet
    data = [location, company,date, avg_response_time, peak_response_time, error_rate, avg_concurrency, peak_concurrency]
    write_to_sheet(data)

    # Non necessario poiché la scrittura dei dati è gestita all'interno della route 'metrics_form'
    return 'Data successfully sent to the Google Sheet.'



@app.route('/results', methods=['GET', 'POST'])
def results():
    results = session.get('results', [])
    return render_template('results.html', results=results)



@app.route('/history', methods=['GET', 'POST'])
def history():
    sheet_id = '1kPkhk67xB-buh6V4EsR9-M2-cub_SreJ56ivTYjCRgk'
    df = pd.read_csv(f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv')
    results = df.to_dict(orient='records')
    if session.get('success', False):
        session["success"] = False
        return render_template('history.html', results=results, success=True)
    return render_template('history.html', results=results, success=False)


#FOR DEVELOPMENT REASONS, CAN BE REMOVED BEFORE DEPLOYMENT
#@app.route('/results', methods=['GET', 'POST'])
#def results():
 #   return render_template('results.html')


if __name__ == '__main__':
    app.run(debug=True)#Set to false before deployment
