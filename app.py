from flask import Flask, render_template, url_for, redirect, request, flash

app = Flask(__name__, static_folder='static')

app.config['SECRET_KEY'] = '3e44bf25ddddcbdf3f0c476982c4f5b5'


@app.route('/', methods = ['POST', 'GET'])
def hello_world():
    if request.method == 'POST':
        form = request.form
        name = form.get('name')
        sid = form.get('student_id_number')
        eml = form.get('email_address')
        passw = form.get('Password')
        print(form)
        if sid != None and name != None and passw != None and eml != None:
             return redirect(url_for('dashboard', id=sid))
        return "Please verify"
        #sid = request.form['student_id_number']
        #return redirect(url_for('dashboard', id=sid))
    else:
        return render_template('Project1.html')

@app.route('/dashboard/')
def dashboard():
    sid = request.args['id']
    return render_template('Student_Dashboard.html', id=sid)

if __name__ == '__main__':
    app.run()
