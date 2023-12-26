from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, RadioField

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key_for_form_security'

# Define a simple RSVP form using WTForms
class RSVPForm(FlaskForm):
    name = StringField('Name')
    attendance = RadioField('Attendance', choices=[('yes', 'Yes, I will attend'), ('no', 'No, I cannot attend')])

# SQLite Database setup
from flask_sqlalchemy import SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rsvp.db'
db = SQLAlchemy(app)

class RSVP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    attendance = db.Column(db.String(10), nullable=False)

# Routes
@app.route('/', methods=['GET', 'POST'])
def index():
    form = RSVPForm()

    if request.method == 'POST' and form.validate_on_submit():
        name = form.name.data
        attendance = form.attendance.data

        new_rsvp = RSVP(name=name, attendance=attendance)
        db.session.add(new_rsvp)
        db.session.commit()

        flash('RSVP submitted successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('index.html', form=form)

@app.route('/guests')
def guests():
    guests_list = RSVP.query.all()
    return render_template('guests.html', guests=guests_list)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
