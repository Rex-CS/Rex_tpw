from enum import unique
import os
from PIL import Image
from flask import Flask, render_template, url_for, redirect, request, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import exc
from werkzeug.utils import secure_filename
from sqlalchemy.orm import backref
import pytesseract
import time

pytesseract.pytesseract.tesseract_cmd = './.apt/usr/share/tesseract-ocr/4.00/tessdata'

app = Flask(__name__, static_folder='static')
UPLOAD_FOLDER = 'certificates'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['SECRET_KEY'] = '3e44bf25ddddcbdf3f0c476982c4f5b5'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    institute = db.Column(db.String(100),nullable=False)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    pAcademic = db.Column(db.Integer, default=0)
    pCultural = db.Column(db.Integer, default=0)
    pSocial = db.Column(db.Integer, default=0)
    records = db.relationship('Rec', backref='User', lazy=True)

    def __repr__(self) -> str:
        return f"User('{self.name}', '{self.email}','{self.student_id}','{self.pAcademic}','{self.pCultural}','{self.pSocial}','{self.records}','{self.institute}','{self.id}')"

class Rec(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.Integer, nullable=False)
    organisation = db.Column(db.String(100), nullable=False)
    certificate_uri = db.Column(db.String(20), nullable=False)
    certificate_text = db.Column(db.Text)
    verified = db.Column(db.Boolean, default=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self) -> str:
        return f"Rec('{self.id}','{self.organisation}','{self.category}','{self.user_id}','{self.certificate_uri}','{self.certificate_text}','{self.date}')"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods = ['POST', 'GET'])
def hello_world():
    if request.method == 'POST':
        form = request.form
        name = form.get('name')
        sid = form.get('student_id_number')
        eml = form.get('email_address')
        passw = form.get('Password')
        institute = form.get('institution_name')
        print(form)
        if sid != None and name != None and passw != None and eml != None and institute != None:
            us=User(name=name, email=eml, password=passw, student_id=sid, institute=institute)
            try:
                print('trying')
                db.session.add(us)
                db.session.commit()
                print('commited')
                return redirect(url_for('dashboard', id=us.id))
            except exc.IntegrityError as err:
                return "email is already used please SignIn"
        else:
            return "Please verify"
        #sid = request.form['student_id_number']
        #return redirect(url_for('dashboard', id=sid))
    else:
        return render_template('Project1.html')

@app.route('/dashboard/')
def dashboard():
    id = request.args['id']
    user = User.query.filter_by(id=id).first()
    print(id)
    if(user != None):
        return render_template('Student_Dashboard.html', id=id, user=user)
    else:
        return render_template('plsSignIn.html')

@app.route('/signIn', methods=['POST', 'GET'])
def signIn():
    return render_template('Student_login.html')

@app.route('/addRecord', methods=['POST', 'GET'])
def addRecord():
     form = request.form
     org = form.get('institute')
     cat = form.get('category')
     userId = form.get('id')
     print(userId)
     user = User.query.filter_by(id=userId).first()
     if request.method == 'POST':
        print(request.form.get('category'))
        if 'file' not in request.files:
            print('No file part')
            return "Verify Selected Image"
        file = request.files['file']
        if file.filename == '':
            print('No File')
            return "No File Selected"
        if file and allowed_file(file.filename):
            print('No image prob')
            print(org)
            if user:
                print('start upload')
                cText = pytesseract.image_to_string(Image.open(file))
                imgName = f"{userId}_{len(user.records)+1}.jpg"
                print(imgName)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], imgName))
                #time.sleep(2)
                text = "Certificate Text"
                time.sleep(2)
                rec = Rec(category=cat, organisation=org, user_id=userId, certificate_uri=f"/certificates/{imgName}", certificate_text=cText)
                try:
                    db.session.rollback()
                    print('trying')
                    db.session.add(rec)
                    print('added')
                    print(rec)
                    db.session.commit()
                    print('commited')
                    return redirect(url_for('viewRec', recid=rec.id))
                except exc.IntegrityError as err:
                    return "error occured"
                print(text)
                
            else:
                return "Check values"
        else:
            return "Problem with image"
     else:
        print('get')
        id = request.args.get('id')
        print(id)
        if(User.query.filter_by(id=id)):
            return render_template('addrecord.html', id=id)
        else:
            return render_template('plsSignIn.html')

@app.route('/viewRec')
def viewRec():
    recid = request.args['recid']
    rec = Rec.query.filter_by(id=recid).first()
    if rec:
        return render_template('viewRec.html', rec=rec)
    return "No Records", 404
    


if __name__ == '__main__':
    app.run()
