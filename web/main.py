
from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
import os
from flask_bcrypt import generate_password_hash, check_password_hash

app = Flask(__name__)

# Set session lifetime
app.permanent_session_lifetime = timedelta(days=30)
app.config["SECRET_KEY"] = "abc1111111"

# Set the database URI
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cafe.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password_hash = db.Column(db.String(100))

    @property
    def password(self):
        raise AttributeError('password is not readable')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

@app.route('/')
def Home():
    return render_template('home.html')

@app.route('/Login', methods=['GET', 'POST'])
def Login():
    if request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('password')

        user = User.query.filter_by(name=name).first()
        if user:
            if user.verify_password(password):
                # Đăng nhập thành công
                session['user'] = user.name
                flash("You have logged in as %s" % user.name, "info")
                return redirect(url_for('user'))
            else:
                flash('Invalid password', 'error')
        else:
            flash('Invalid username', 'error')

    return render_template('Login.html')

@app.route('/user')
def user():
    if 'user' in session:
        name = session['user']
        user = User.query.filter_by(name=name).first()
        if user:
            email = user.email
            return render_template('user.html', name=name, email=email)

    flash("You are not logged in", "error")
    return redirect(url_for('Login'))

@app.route('/Logout')
def Logout():
    flash("You are now logged out", "info")
    session.pop('user', None)
    return redirect(url_for("Login"))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('password')
        email = request.form.get('email')

        user = User.query.filter_by(name=name).first()
        if user:
            flash('Username already exists', 'error')
            return redirect(url_for('register'))

        new_user = User(name=name, email=email)
        new_user.password = password  # Set the password
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful', 'success')
        return redirect(url_for('Login'))

    return render_template('register.html')

    
if __name__ == '__main__':
    if not os.path.exists("cafe.db"):
        with app.app_context():
            db.create_all()
    app.run(debug=True)