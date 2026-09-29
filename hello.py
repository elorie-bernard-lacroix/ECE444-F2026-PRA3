from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
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
            session['name'] = form.name.data
            session['email'] = form.email.data
            session['chat_memory'] = {}
            form.name.data = ''
            form.email.data = ''
            return redirect(url_for('chat_page'))
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

@app.route('/chat')
def chat_page():
    if 'name' not in session:
        return redirect(url_for('index'))
    return render_template('chat.html', name=session['name'], email=session['email'])

@app.route('/chat', methods=['POST'])
def chat():
    if 'name' not in session:
        return jsonify({'reply': 'Please submit your name and UofT email first.'}), 401

    message = request.json.get('message', '').strip()
    memory = session.setdefault('chat_memory', {})
    lower_message = message.lower()

    if lower_message.startswith('my name is '):
        remembered_name = message[11:].strip()
        memory['name'] = remembered_name
        reply = f'Nice to meet you, {remembered_name}!'
    elif 'what is my name' in lower_message:
        remembered_name = memory.get('name')
        if remembered_name:
            reply = f'Your name is {remembered_name}.'
        else:
            reply = 'You have not told me your name yet.'
    elif 'hello' or 'hi' or 'hey' in lower_message:
        reply = 'Hello!'
    else:
        reply = "I don't understand. Try telling me your name, then ask what your name is."

    session['chat_memory'] = memory
    return jsonify({'reply': reply})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500