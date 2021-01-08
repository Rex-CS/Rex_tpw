from enum import unique
from flask import Flask, render_template, url_for, redirect, request, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import exc

from sqlalchemy.orm import backref

app = Flask(__name__, static_folder='static')

app.config['SECRET_KEY'] = '3e44bf25ddddcbdf3f0c476982c4f5b5'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

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
    records = db.relationship('Record', backref='User', lazy=True)

    def __repr__(self) -> str:
        return f"User('{self.name}', '{self.email}','{self.student_id}','{self.pAcademic}','{self.pCultural}','{self.pSocial}','{self.records}','{self.institute}','{self.id}')"

class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.Integer, nullable=False)
    organisation = db.Column(db.String(100), nullable=False)
    certificate_uri = db.Column(db.String(20), unique=True, nullable=False)
    certificate_text = db.Column(db.Text)
    verified = db.Column(db.Boolean)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self) -> str:
        return super().__repr__()



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
                return "email is already used"
        else:
            return "Please verify"
        #sid = request.form['student_id_number']
        #return redirect(url_for('dashboard', id=sid))
    else:
        return render_template('Project1.html')

@app.route('/dashboard/')
def dashboard():
    sid = request.args['id']
    user=User.query.filter_by(id=sid).first()
    print(user)
    return render_template('Student_Dashboard.html', id=sid, user=user)

if __name__ == '__main__':
    app.run()
