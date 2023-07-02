from flask import (
    Flask,
    render_template,
    request,
    make_response,
    redirect,
    session,
    url_for,
    flash,
    session
)
from flask_bootstrap import Bootstrap
import pickle
import numpy as np
import pandas as pd
from werkzeug.utils import secure_filename
import os
from tslearn.clustering import TimeSeriesKMeans
import plotly
import plotly.express as px
import json
from flask_wtf import Form
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired

from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired

'''
To use flask shell:
$ export FLASK_APP=index
$ flask shell
'''

UPLOAD_FOLDER = os.path.join('static', 'uploads')
# Define allowed files
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__)
bootstrap = Bootstrap(app)

app.secret_key = 'This is your secret key to utilize session in Flask'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# # Hardcoded stuff for now, should allow user to select these settings from a drop bar


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[InputRequired()])
    submit = SubmitField('Submit')

# class CSVForm(FlaskForm):
#     '''
#     See https://flask-wtf.readthedocs.io/en/1.0.x/form/#file-uploads
#     '''
#     csv_file = FileField(validators=FileRequired())
    

@app.route('/', methods=['GET', 'POST'])
def index():
    '''
    This scheme follows post, redirect, get
    '''
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            print("bingo bongo")
            flash('Looks like you have changed your name!')
        session['name'] = form.name.data
        print('name:', session['name'])
        print('session:', session)
        print('url: ', url_for('index'))
        form.name.data = ''
        return redirect(url_for('index'))
    return render_template("index.html", form=form, name=session.get('name'))




@app.route('/read_csv1', methods=['GET', 'POST'])
def read_csv1():
    if request.method == 'POST':
        # upload file flask
        f = request.files.get('file')
        # Extracting uploaded file name
        data_filename = secure_filename(f.filename)
        session['fname'] = data_filename
        f.save(os.path.join(app.config['UPLOAD_FOLDER'],
                            data_filename))
        session['uploaded_data_file_path'] = os.path.join(app.config['UPLOAD_FOLDER'], data_filename)
        return render_template('read_csv2.html')
    return render_template("read_csv1.html")


@app.route('/show_data')
def showData():
    # Uploaded File Path
    data_file_path = session.get('uploaded_data_file_path', None)
    # read csv
    uploaded_df = pd.read_csv(data_file_path, encoding='unicode_escape')
    # Converting to html Table
    uploaded_df_html = uploaded_df.to_html()
    
    return render_template('show_csv_data.html', fname=session['fname'], data_var=uploaded_df_html)

@app.route('/plot_data')
def plotData():
    # Uploaded File Path
    data_file_path = session.get('uploaded_data_file_path', None)
    # read csv
    uploaded_df = pd.read_csv(data_file_path, encoding='unicode_escape')
    # Converting to html Table
    fig = px.line(uploaded_df, x='time', y='NE', title='Muh plot')
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)    
    
    return render_template('plot_csv_data.html', fname=session['fname'],
                           data_var=uploaded_df, graphJSON=graphJSON)


@app.route('/user/<name>')
def user(name):
    '''
    NOTES:
    - render_template integrates Jinja2 template engine with app.
    - render_template automatically looks in the "templates/" directory
    
    PARAMETERS:
    arg1: file name of template
    name: argument for actual value for name variable
    '''
    return render_template('user.html', name=name)

@app.route('/form', methods=['GET', 'POST'])
def form():
    form = NameForm()
    name = None
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
    return render_template('form.html', form=form, name=name)

@app.errorhandler(404)
def page_not_found(e):
    # print(type(e)) # <class 'werkzeug.exceptions.NotFound'>
    # print(e)
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int("3000"), debug=True)
