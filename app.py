from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, jsonify, request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_login import LoginManager, current_user, login_user, logout_user, login_required, UserMixin
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema


app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)
ma = Marshmallow(app)
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return f"User('{self.username}','{self.email}')"

    def set_password(self,password):
        self.password_hash = generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password_hash, password)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    author = db.relationship('User', backref = db.backref('posts',lazy=True))

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"



class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_relationships = True
        load_instance = True


class PostSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Post
        include_relationships = True
        load_instance = True


user_schema = UserSchema()
users_schema = UserSchema(many=True)
post_schema = PostSchema()
posts_schema = PostSchema(many=True)


# User Authentication
@app.route('/register', methods=['POST'])
def register():

    username = request.json.get('username')
    email = request.json.get('email')
    password = request.json.get('password')
    
    if User.query.filter_by(username=username).first():
        return make_response(jsonify({'error': 'Username already exists.'}), 400)

    if User.query.filter_by(email=email).first():
        return make_response(jsonify({'error': 'Email already exists.'}), 400)

    # Create new user
    user = User(username=username, email=email)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    # Dump the user object to a JSON response
    user_schema = UserSchema()
    result = user_schema.dump(user)

    return jsonify({'user': result}), 201


@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    # remember_me = request.json.get('remember_me')

    # check if username exists
    user = User.query.filter_by(username=username).first()
    if not user:
        return make_response(jsonify({'error': 'Invalid username or password.'}),400)
            
    # check if password is correct
    if not user.check_password(password):
        return make_response(jsonify({'error' : 'Invalid username or password'}), 400)

    # log user in 
    login_user(user)

    return make_response(jsonify({'message': 'User logged in successfully'}))


@app.route('/logout')
def logout():
    # logout user
    logout_user()
    return jsonify({'message':'User logged out successfully!'})

@app.route('/users')
def get_users():
    users = User.query.all()
    result = users_schema.dump(users)
    return jsonify(result)

@app.route('/users/<int:user_id>')
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return make_response(jsonify({'error': 'User not found.'}),404)
    return jsonify(user_schema.dump(user))

# CRUD
@app.route('/posts', methods=['GET'])
def get_posts():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=per_page)
    result = posts_schema.dump(posts.items)
    return jsonify({'posts': result, 'total_pages': posts.pages, 'total_items': posts.total})


@app.route('/posts', methods=['POST'])
@login_required
def add_post():
    title = request.json.get('title')
    content = request.json.get('content')
    post = Post(title=title, content=content, author=current_user)
    db.session.add(post)
    db.session.commit()
    
    return jsonify(post_schema.dump(post))


@app.route('/posts/<int:post_id>', methods=['PUT'])
@login_required
def update_post(post_id):
    post = Post.query.get(post_id)
    if not post:
        return make_response(jsonify({'error': 'Post not found.'}), 404)
    
    if post.author != current_user:
        return make_response(jsonify({'error': 'You are not authorized to update this post.'}), 403)
    
    post.title = request.json.get('title')
    post.content = request.json.get('content')
    
    db.session.commit()
    return jsonify(post_schema.dump(post))


@app.route('/posts/<int:post_id>', methods=['DELETE'])
@login_required
def delete_post(post_id):
    post = Post.query.get(post_id)
    if not post:
        return make_response(jsonify({'error': 'Post not found.'}), 404)
    
    if post.author != current_user:
        return make_response(jsonify({'error': 'You are not authorized to delete this post.'}), 403)
    
    db.session.delete(post)
    db.session.commit()
    return jsonify({'message': 'Post delete successfully.'})


if __name__ == '__main__':
    app.run(debug=True)
