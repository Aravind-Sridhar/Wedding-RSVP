from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_wtf import FlaskForm
from wtforms import StringField, RadioField
import qrcode
from io import BytesIO
import os

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

# Generate QR code function
def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white")
    img_buffer = BytesIO()
    qr_img.save(img_buffer)
    img_buffer.seek(0)
    return img_buffer

# Save QR code to file
def save_qr_code(filename, data):
    qr_img = generate_qr_code(data)
    with open(filename, 'wb') as f:
        f.write(qr_img.read())

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

@app.route('/generate_qr_code')
def generate_qr():
    base_url = request.url_root.rstrip('/')
    website_url = f"{base_url}/"
    qr_code_filename = 'rsvp_qr_code.png'
    save_qr_code(qr_code_filename, website_url)
    return f'QR code saved to {qr_code_filename}'

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    # Use the host and port provided by PythonAnywhere
    port = int(os.environ.get('PORT', 0000))
    app.run(host='0.0.0.0', port=port)
