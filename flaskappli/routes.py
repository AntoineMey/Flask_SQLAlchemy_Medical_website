from flask import render_template, flash, redirect, url_for, request, abort
from flaskappli import app, db, bcrypt
from flaskappli.register import RegistrationForm, LoginForm, UpdateAccountForm, ArticleForm
from flaskappli.models import User, Article
from flask_login import login_user, LoginManager, UserMixin, current_user, logout_user, login_required
from werkzeug import secure_filename
import os


@app.route('/')
@app.route('/home')
def home():
    posts = Article.query.all()
    return render_template('home.html', posts=posts)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Compte créé pour {form.username.data} !', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Vous êtes loggé!', 'success')
            return redirect (next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Vous n\' êtes pas loggé', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/compte', methods=['GET', 'POST'])
@login_required
def compte():
    posts = Article.query.all()
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Votre compte a été mis à jour', 'success')
        return redirect(url_for('compte'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('compte.html', title='compte', form=form, posts=posts)


@app.route('/article/nouveau', methods=['GET', 'POST'])
@login_required
def new_post():
    form = ArticleForm()
    if form.validate_on_submit():
        post = Article(title=form.title.data, content=form.content.data, author=current_user, category=form.category.data) ##image=form.image.data)
        db.session.add(post)
        db.session.commit()
        flash('Votre appareil a bien été ajouté ! ', 'success')
        return redirect(url_for('home'))
    return render_template('new_post.html', title='Ajouter un appareil', form=form)

"""
def upload_image():
    if request.method =='POST':
            file = request.files['file[]']
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))

def upload_image():
    if request.method == 'POST':
        f = request.files['file']
        sfname = './templates/images/'+str(secure_filename(f.filename))
        f.save(f.sfname)
"""

@app.route("/article/<int:post_id>")
def post(post_id):
    post = Article.query.get_or_404(post_id)
    return render_template('article.html', title=post.title, post=post)

@app.route("/article/<post_id>/update", methods=['GET', 'POST'])
def update_post(post_id):
    post = Article.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = ArticleForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Vous avez modifié la fiche de l\'appareil', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('update.html', title='Update Article', form=form)


@app.route("/article/<post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Article.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Vous avez supprimé cet appareil', 'success')
    return redirect(url_for('compte', post_id=post.id))


@app.route("/irm", methods=['GET', 'POST'])
def IRM():
    posts = Article.query.all()
    return render_template('irm.html', posts=posts)

@app.route("/scanner", methods=['GET', 'POST'])
def scanner():
    posts = Article.query.all()
    return render_template('scanner.html', posts=posts)

@app.route("/radiographie", methods=['GET', 'POST'])
def radiographie():
    posts = Article.query.all()
    return render_template('radiographie.html', posts=posts)

@app.route("/echographie", methods=['GET', 'POST'])
def echographie():
    posts = Article.query.all()
    return render_template('echographie.html', posts=posts)
