from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime

# Initialize Flask app and SQLAlchemy
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"

# Define Base class for SQLAlchemy
class Base(DeclarativeBase):
    pass

# Bind SQLAlchemy to the app and set model_class to Base
db = SQLAlchemy(app, model_class=Base)

# Define User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

# Define Review model
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('reviews', lazy=True))

    def __repr__(self):
        return '<Review %r>' % self.text

# Create all tables
with app.app_context():
    db.create_all()

# Create a review
@app.route('/create_review', methods=['POST'])
def create_review():
    username = request.form['username']
    email = request.form['email']
    text = request.form['text']

    user = User.query.filter_by(username=username, email=email).first()
    if user is None:
        user = User(username=username, email=email)
        db.session.add(user)
        db.session.commit()

    review = Review(text=text, user_id=user.id)
    db.session.add(review)
    db.session.commit()

    return redirect(url_for('index_page'))

# Read users and reviews
@app.route('/users')
def view_users():
    users = User.query.all()
    return render_template_string('''
        <html>
        <head><title>Users and Reviews</title></head>
        <body>
            <h1>Users and Reviews</h1>
            <ul>
            {% for user in users %}
                <li>{{ user.username }} - {{ user.email }}
                    <ul>
                    {% for review in user.reviews %}
                        <li>{{ review.text }} - {{ review.timestamp }}</li>
                    {% endfor %}
                    </ul>
                </li>
            {% endfor %}
            </ul>
            <a href="{{ url_for('index_page') }}">Home</a>
        </body>
        </html>
    ''', users=users)

# Home page
@app.route('/')
def index_page():
    return render_template_string('''
        <html>
        <head><title>Home</title></head>
        <body>
            <h1>Home Page</h1>
            <form action="{{ url_for('create_review') }}" method="POST">
                <label for="username">Username:</label>
                <input type="text" id="username" name="username" required><br><br>
                <label for="email">Email:</label>
                <input type="email" id="email" name="email" required><br><br>
                <label for="text">Review:</label>
                <textarea id="text" name="text" required></textarea><br><br>
                <input type="submit" value="Create Review">
            </form>
            <a href="{{ url_for('view_users') }}">View Users and Reviews</a>
        </body>
        </html>
    ''')

if __name__ == '__main__':
    app.run(debug=True)
