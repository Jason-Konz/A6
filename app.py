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

def get_logged_in_id():
    if 'login_id' in session:
        return session['login_id']
    
    return None

def authenticate(username, password):
    user = Profile.query.filter_by(username=username).first()
    
    if user and username == user.username and password == user.password:
        session['username'] = username
        session['login_id'] = user.id
        return True

    return False

def is_secure_route(request):
#    return request.path not in ['/login/', '/logout/', '/profile/new/', '/profile/',] and \
#            not request.path.startswith('/static/')
    if request.method == 'GET':

        if request.path in ['/profile/', '/', '/main/', '/api/posts/'] or request.path.startswith('/api/'):
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
       
    elif request.path.startswith('/static/') and request.path.startswith('/api/'):
        return True

@app.before_request
def login_redirect():
    if get_username() == None and is_secure_route(request):
        # return render_template('login_form.html')
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
    if user:
        return render_template("profile_page.html",user=user, activeUser = user)
    else:
        return redirect(url_for('main'))

@app.route('/profile/<int:profile_id>/', methods=["GET"])
def get_profile_by_id(profile_id):
    user = Profile.query.get(profile_id)
    activeUser = Profile.query.filter_by(username=get_username()).first()
    if user:
        return render_template("profile_page.html",user=user, activeUser = activeUser)
    else:
        return redirect(url_for('main'))

@app.route('/api/posts/', methods=['GET'])
def get_posts():
    prof_id = get_logged_in_id()
    if 'profile_id' in request.args:
        prof_id = request.args['profile_id']

    posts = Post.query.filter_by(profile_id=prof_id).all()

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


@app.route('/api/posts/<int:post_id>', methods=['GET'])
def get_post_by_post_id(post_id):
    post = Post.query.get(post_id)

    return jsonify(post.serialize())

@app.route('/api/posts/<int:post_id>/like/', methods=['POST'])
def like_post(post_id):
    likedUser = Profile.query.filter_by(username=get_username()).first()
    post = Post.query.get(post_id)
    like = Like(profile_id=likedUser.id, post_id=post_id)

    db.session.add(like)
    db.session.commit()

    return jsonify(post.serialize())

@app.route('/api/posts/<int:post_id>/unlike/', methods=['POST'])
def unlike_post(post_id):
    unLikedUser = Profile.query.filter_by(username=get_username()).first()
    post = Post.query.get(post_id)
    like = Like.query.filter_by(profile_id=unLikedUser.id, post_id=post_id).first()

    db.session.delete(like)
    db.session.commit()

    return jsonify(post.serialize())

@app.route('/api/posts/<int:post_id>/likes/', methods=['GET'])
def get_likes(post_id):
    post = Post.query.filter_by(id=post_id).first()
    likes=post.liked_by()
    print(likes)
    profiles = list(map(lambda p: Profile.query.get(p).serialize(), likes))

    return jsonify(profiles)

