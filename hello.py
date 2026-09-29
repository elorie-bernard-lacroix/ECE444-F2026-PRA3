from flask import Flask, flash, render_template
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)
app.config['SECRET_KEY'] = 'hard to guess string'

class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    email = StringField(
        'What is your UofT Email address?',
        validators=[DataRequired()],
        render_kw={'type': 'email'},
    )
    submit = SubmitField('Submit')

@app.route('/', methods=['GET', 'POST'])
def index():
    name = None
    email = None
    form = NameForm()
    if form.validate_on_submit():
        if 'utoronto' in form.email.data.lower():
            name = form.name.data
            email = form.email.data
            form.name.data = ''
            form.email.data = ''
        else:
            flash('Please use your UofT email.')
    return render_template(
        'index.html',
        current_time=datetime.utcnow(),
        form=form,
        name=name,
        email=email,
    )

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name, current_time=datetime.utcnow())

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500