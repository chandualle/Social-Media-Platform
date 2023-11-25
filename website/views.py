# views.py
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Post, User, Like, Follow, Saves
from . import db
from flask import send_file
from flask import jsonify
import io
from random import shuffle
from sqlalchemy import func

views = Blueprint("views", __name__)


@views.route("/")
@views.route("/home")
@login_required
def home():
    all_posts = Post.query.order_by(func.random()).limit(16).all()
    shuffle(all_posts)

    # Calculate likes count for each post
    post_likes_count = {post.id: len(post.likes) for post in all_posts}

    saved_post_ids = [saved.post_id for saved in current_user.saves]
    post_saved_info = {post.id: post.id in saved_post_ids for post in all_posts}  # Calculate saved info

    categories = ["Love", "Family", "Friends", "Horror", "Fantasy", "Travel", "Educational", "Thriller", "Other"]
    category_info = {category: [post for post in all_posts if post.category == category] for category in categories}

    # Calculate category-specific saved info for each category
    category_saved_info = {}
    for category, category_posts in category_info.items():
        category_post_ids = [category_post.id for category_post in category_posts]
        category_saved_info[category] = {post.id: post.id in saved_post_ids for post in all_posts}

    return render_template("home.html", user=current_user, posts=all_posts, post_likes_count=post_likes_count,
                           post_saved_info=post_saved_info, category_saved_info=category_saved_info)

@views.route("/create-post", methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == "POST":
        titletext = request.form.get('titletext')
        text = request.form.get('text')
        totaltext = request.form.get('totaltext')
        pic = request.files['pic']
        category = request.form.get('category')

        if not text:
            flash('Post cannot be empty', category='error')
        elif len(text) > 28:
            flash('Give Caption Using 28 Letters', category='error')
        elif not pic:
            flash('Please select an image for your post', category='error')
        elif not titletext:
            flash('Please give some title', category='error')
        elif not category:
            flash('Please select categoty', category='error')
        elif len(titletext) > 18:
            flash('Give Title Using 18 Letters', category='error')
        elif not totaltext:
            flash('Please give whole story', category='error')
        else:
            # Save the image data to the database
            new_post = Post(text=text, titletext=titletext, totaltext=totaltext, category=category, name=pic.filename, mimetype=pic.mimetype, author=current_user.id, img=pic.read())
            db.session.add(new_post)
            db.session.commit()

            flash('Post created!', category='success')
            return redirect(url_for('views.home'))

    return render_template('create_post.html', user=current_user)

@views.route('/serve-image/<int:post_id>')
def serve_image(post_id):
    post = Post.query.get_or_404(post_id)
    return send_file(io.BytesIO(post.img), mimetype=post.mimetype)


@views.route("/delete-post/<post_id>", methods=['GET'])
@login_required
def delete_post(post_id):
    post = Post.query.filter_by(id=post_id).first()

    if not post:
        return jsonify({'error': 'Post does not exist'})
    elif current_user.id != post.author and len(post.likes) < 2:
        return jsonify({'error': 'You do not have permission to delete this post or likes are more than 2'})

    db.session.delete(post)
    # Also delete associated likes when deleting the post
    likes = Like.query.filter_by(post_id=post.id).all()
    for like in likes:
        db.session.delete(like)
    db.session.commit()

    return jsonify({'message': 'Post deleted'})

@views.route('/profile-image/<int:user_id>')
def serve_profile_image(user_id):
    user = User.query.get_or_404(user_id)
    if user.profile_img:
        return send_file(io.BytesIO(user.profile_img), mimetype='image/jpeg')  # Adjust mimetype accordingly
    else:
        return 'Default image not found', 404

@views.route("/like-post/<post_id>", methods=['POST'])
@login_required
def like(post_id):
    post = Post.query.get_or_404(post_id)
    like = Like.query.filter_by(author=current_user.id, post_id=post_id).first()

    if not post:
        return jsonify({'error': 'Post does not exist'})
    elif like:
        db.session.delete(like)
        db.session.commit()
        return jsonify({'message': 'Post unliked', 'likes': post.likes.count()})
    else:
        like = Like(author=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()
        return jsonify({'likes': post.likes.count()})

@views.route("/posts/<username>")
@login_required
def posts(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        flash('No user with that username exists.', category='error')
        return redirect(url_for('views.home'))

    posts = Post.query.filter_by(author=user.id).all()

    # Calculate the count of posts for the user
    post_count = db.session.query(func.count(Post.id)).filter(Post.author == user.id).scalar()

    return render_template("posts.html", posts=posts, username=username, user=user, post_count=post_count)

@views.route("/toggle-follow/<int:user_id>", methods=['GET'])
@login_required
def toggle_follow(user_id):
    user_to_toggle = User.query.get(user_id)

    if user_to_toggle:
        if current_user.is_following(user_to_toggle):
            current_user.unfollow(user_to_toggle)
            following = False
        else:
            current_user.follow(user_to_toggle)
            following = True
        return jsonify({'success': True, 'following': following})
    else:
        return jsonify({'success': False})

@views.route("/following/<username>")
@login_required
def following(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        flash('No user with that username exists.', category='error')
        return redirect(url_for('views.home'))

    following = user.following.all()
    return render_template("followers.html", following=following, username=username, user=user)

@views.route("/followers/<username>")
@login_required
def followers(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        flash('No user with that username exists.', category='error')
        return redirect(url_for('views.home'))

    followers = user.followers.all()
    return render_template("following.html", followers=followers, username=username, user=user)

@views.route("/save-post/<int:post_id>", methods=['GET'])
@login_required
def save_post(post_id):
    post = Post.query.get(post_id)
    if not post:
        flash('Post does not exist', category='error')

    # Check if the post is already saved by the user
    saved_post = Saves.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    if saved_post:
        # Unsave the post if already saved
        db.session.delete(saved_post)
        db.session.commit()
    else:
        # Save the post for the user if not saved
        new_saved_post = Saves(user_id=current_user.id, post_id=post_id)
        db.session.add(new_saved_post)
        db.session.commit()

    return redirect(url_for('views.home'))


@views.route("/saved-posts")
@login_required
def saved_posts():
    saved_post_ids = [saved.post_id for saved in current_user.saves]
    saved_posts = Post.query.filter(Post.id.in_(saved_post_ids)).all()

    # Generate information about saved posts for the current user
    post_saved_info = {post.id: post.id in saved_post_ids for post in saved_posts}

    # Calculate likes count for each post
    post_likes_count = {post.id: len(post.likes) for post in saved_posts}

    return render_template("saved_posts.html", user=current_user, saved_posts=saved_posts, post_saved_info=post_saved_info, post_likes_count=post_likes_count)

@views.route("/category/<category_name>")
@login_required
def category_posts(category_name):
    # Fetch posts based on the selected category
    category_posts = Post.query.filter_by(category=category_name).all()

    # Calculate likes count for each post in the selected category
    post_likes_count = {post.id: len(post.likes) for post in category_posts}

    # Calculate saved info for all posts
    saved_post_ids = [saved.post_id for saved in current_user.saves]
    post_saved_info = {post.id: post.id in saved_post_ids for post in category_posts}

    # Fetch categories for posts
    categories = ["Love", "Family", "Friends", "Horror", "Fantasy", "Travel", "Educational", "Thriller", "Other"]
    category_info = {category: [post for post in category_posts if post.category == category] for category in categories}

    # Calculate category-specific saved info for each category in the selected category
    category_saved_info = {}
    for category, cat_posts in category_info.items():
        cat_post_ids = [cat_post.id for cat_post in cat_posts]
        category_saved_info[category] = {post.id: post.id in saved_post_ids for post in category_posts}

    # Render a template that displays posts filtered by the selected category
    return render_template("category_posts.html", user=current_user, category_name=category_name, posts=category_posts, post_likes_count=post_likes_count, post_saved_info=post_saved_info, category_saved_info=category_saved_info)
