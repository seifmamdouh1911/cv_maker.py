from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_weasyprint import render_pdf
from weasyprint import HTML
import os
from werkzeug.utils import secure_filename
import uuid  # For generating unique filenames

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['SECRET_KEY'] = 'your_secret_key'  # Needed for flash messages

db = SQLAlchemy(app)

# Ensure the upload directory exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    summary = db.Column(db.String(500))
    skills = db.Column(db.String(500))
    experience = db.Column(db.String(1000))
    education = db.Column(db.String(1000))
    projects = db.Column(db.String(1000))
    certificates = db.Column(db.String(1000))
    photo_url = db.Column(db.String(500))


with app.app_context():
    db.create_all()


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Extract form data
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        summary = request.form.get('summary')
        skills = request.form.get('skills')
        experience = request.form.get('experience')
        education = request.form.get('education')
        projects = request.form.get('projects')
        certificates = request.form.get('certificates')

        # Handle file upload
        photo = request.files.get('photo')
        photo_url = 'default.jpg'  # Default photo

        if photo and photo.filename:
            if allowed_file(photo.filename):
                filename = secure_filename(photo.filename)
                # Generate a unique filename
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

                try:
                    # Save the uploaded file
                    photo.save(file_path)
                    photo_url = unique_filename
                    flash("File uploaded successfully", 'success')
                except Exception as e:
                    flash(f"Error saving file: {e}", 'danger')
                    print(f"Error saving file: {e}")  # Debugging
            else:
                flash('Invalid file type. Only JPG, JPEG, and PNG files are allowed.', 'danger')
                return render_template('index.html')

        # Create new user in the database
        new_user = User(
            name=name,
            email=email,
            phone=phone,
            summary=summary,
            skills=skills,
            experience=experience,
            education=education,
            projects=projects,
            certificates=certificates,
            photo_url=photo_url
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('choose_template', user_id=new_user.id))

    return render_template('index.html')


@app.route('/choose-template/<int:user_id>')
def choose_template(user_id):
    return render_template('choose_template.html', user_id=user_id)


@app.route('/template/<int:template_id>/<int:user_id>')
def view_template(template_id, user_id):
    user = User.query.get(user_id)
    if not user:
        flash("User not found", 'danger')
        return redirect(url_for('index'))

    if template_id == 1:
        return render_template('template1.html', user=user)
    elif template_id == 2:
        return render_template('template2.html', user=user)
    elif template_id == 3:
        return render_template('template3.html', user=user)
    else:
        flash("Template not found", 'danger')
        return redirect(url_for('index'))


@app.route('/download-pdf/<int:template_id>/<int:user_id>')
def download_pdf(template_id, user_id):
    user = User.query.get(user_id)
    if not user:
        flash("User not found", 'danger')
        return redirect(url_for('index'))

    if template_id == 1:
        html_content = render_template('template1.html', user=user)
    elif template_id == 2:
        html_content = render_template('template2.html', user=user)
    elif template_id == 3:
        html_content = render_template('template3.html', user=user)
    else:
        flash("Template not found", 'danger')
        return redirect(url_for('index'))

    # Use HTML string and correct paths for images
    html = HTML(string=html_content, base_url=request.host_url)
    return render_pdf(html)

if __name__ == '__main__':
    app.run(debug=True)
