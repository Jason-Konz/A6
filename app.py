from flask import (
    abort, Flask, jsonify, redirect, render_template, request,
    session, url_for
)
from flask_sqlalchemy import SQLAlchemy
import os 
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = b'REPLACE_ME_x#pi*CO0@^z_beep_beep_boop_boop'

sqlite_uri = 'sqlite:///' + os.path.abspath(os.path.curdir) + '/test.db'
app.config['SQLALCHEMY_DATABASE_URI'] = sqlite_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import Profile, Post, Like

from pathlib import Path

IMAGE_DIR = 'static/img/profilephotos'


def get_username():
    if 'username' in session:
        return session['username']

    return None

def authenticate(username, password):
    user = Profile.query.filter_by(username=username).first()
    
    if user and username == user.username and password == user.password:
        session['username'] = username
        return True

    return False

def is_secure_route(request):
    if request.method == 'GET':
        if request.path in ['/profile/', '/', '/main/', '/api/posts/']:
            # these are secure paths
            return True
        else:
            return False
    
    elif request.method == 'POST':
        if request.path in ['/api/posts/']:
            # these are secure paths
            return True
        else:
            return False
        
    elif request.path.startswith('/static/'):
        return True

@app.before_request
def login_redirect():
    if get_username() == None and is_secure_route(request):
        return redirect(url_for('login_form'))

@app.before_first_request
def app_init():
  imgdir = Path(IMAGE_DIR)
  if not imgdir.exists():
      imgdir.mkdir(parents=True)

  try:
      Profile.query.all()
  except:
      db.create_all()

@app.route('/')
def index():
    return redirect(url_for('main'))

@app.route('/main/')
def main():
    return render_template('main.html', username=get_username())

@app.route('/login/', methods=['GET'])
def login_form():
    return render_template('login_form.html')

@app.route('/login/', methods=['POST'])
def login():
    if authenticate(request.form['username'], request.form['password']):
        return redirect(url_for('main'))
    else:
        return render_template('login_form.html', \
                messages=['Invalid username/password combination'])

@app.route('/logout/', methods=['GET'])
def logout():
    if 'username' in session:
        del session['username']
    return render_template('login_form.html', \
            messages=['Logged out. Thanks for visiting this site.'])

@app.route('/profile/new/', methods=["GET"])
def new_profile_form():
    return render_template('new_profile_form.html')

@app.route('/profile/', methods=["POST"])
def profile():
    new_username = request.form["username"]
    new_password = request.form["password"]
    new_email = request.form["email"]
    infile = request.files["img"]
    if '' in [new_username, new_password, new_email] or not infile:
        return render_template("new_profile_form.html", \
            messages=['Please fill in all fields'])
    infile.filename = new_username + "-" + infile.filename
    filename = secure_filename(infile.filename)
    filepath = os.path.join(IMAGE_DIR, filename)
    print(infile)


    user = Profile.query.filter_by(username=new_username).first()

    if user:
        return render_template("new_profile_form.html", \
            messages=[f'{new_username} is already taken'])

    infile.save(filepath)
    newprofile = Profile(username=new_username, password=new_password, \
                        email=new_email, photofn=filename, posts=[])

    db.session.add(newprofile)
    db.session.commit()

    return redirect(url_for("login_form"))
    
@app.route('/profile/', methods=["GET"])
def get_profile():
    user = Profile.query.filter_by(username=get_username()).first()
    return render_template("profile_page.html",user=user)

@app.route('/profile/<int:profile_id>/', methods=["GET"])
def get_profile_by_id(profile_id):
    user = Profile.query.get(profile_id)
    return render_template("profile_page.html",user=user)

@app.route('/api/posts/', methods=['GET'])
def get_posts():
    user = Profile.query.filter_by(username=get_username()).first()
    posts = user.posts
    posts = list(map(lambda p: p.serialize(), posts))

    return jsonify(posts)

@app.route('/api/posts/', methods=['POST'])
def create_post():
    post_text = request.form['post-text']
    user = Profile.query.filter_by(username=get_username()).first()
    newpost = Post(content=post_text, profile_id=user.id)

    db.session.add(newpost)
    db.session.commit()

    return redirect(url_for('main'))

@app.route('/api/posts/?profile_id=<PROFILE_ID>', methods=['GET'])
def get_posts_by_profile_id(profile_id):
    user = Profile.query.get(profile_id)
    if user:
        posts = user.posts
        return jsonify(posts.serialize())
    
    else:
        return []

@app.route('/api/posts/<int:post_id>', methods=['GET'])
def get_post_by_post_id(post_id):
    post = Post.query.get(post_id)

    return jsonify(post.serialize())

@app.route('/api/posts/<int:post_id>/like/', methods=['POST'])
def like_post(current_post_id):
    likedUser = Profile.query.filter_by(username=get_username()).first()
    post = Post.query.get(current_post_id)
    postUser = post.profile_id
    like = Like(profile_id=likedUser.id, post_id=current_post_id, profile=postUser)

    db.session.add(like)
    db.session.commit()

    return 'ok'

@app.route('/api/posts/<int:post_id>/unlike/', methods=['POST'])
def unlike_post(current_post_id):
    unLikedUser = Profile.query.filter_by(username=get_username()).first()
    post = Post.query.get(current_post_id)
    like = Like.query.query.filter_by(profile_id=unLikedUser.id, post_id=post.id)

    db.session.delete(like)
    db.session.commit()

    return 'ok'

@app.route('/api/posts/<int:post_id>/likes/', methods=['GET'])
def get_likes(current_post_id):
    post = Post.query.filter_by(post_id=current_post_id)
    likes=post.likes

    return jsonify(likes.serialize())