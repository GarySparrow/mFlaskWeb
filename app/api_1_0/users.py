from flask import jsonify, request, current_app, url_for
from . import api, authentication
from .. import db
from ..models import User, Post
from ..email import send_email
from flask_login import login_user, logout_user




# @api.route('/users/')
# def get_users(id):
#     users = User.query.all()
#     return jsonify({'users': user.to_json() for user in users})

@api.route('/users/<int:id>')
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify({'user': user.to_json()})


@api.route('/users/<int:id>/posts/')
def get_user_posts(id):
    user = User.query.get_or_404(id)
    # page = request.args.get('page', 1, type=int)
    # pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
    #     page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
    #     error_out=False)
    # posts = pagination.items
    # prev = None
    # if pagination.has_prev:
    #     prev = url_for('api.get_user_posts', page=page-1, _external=True)
    # next = None
    # if pagination.has_next:
    #     next = url_for('api.get_user_posts', page=page+1, _external=True)
    posts = Post.query.filter_by(author_id = user.id)
    return jsonify({
        'posts': [post.to_json() for post in posts],
        # 'prev': prev,
        # 'next': next,
        # 'count': pagination.total
    })


@api.route('/users/<int:id>/isfollowed/', methods = ['GET'])
def is_followed(id):
    poster_id = request.args.get('poster_id')
    user = User.query.filter_by(id=id).first()
    poster = User.query.filter_by(id=poster_id).first()
    isfollowed = poster.is_followed_by(user)
    return jsonify({
        'followed': isfollowed,
        'code': True
    })

@api.route('/users/<int:id>/follow/', methods = ['POST'])
def follow(id):
    poster_id = request.form.get('poster_id')
    user = User.query.filter_by(id=id).first()
    poster = User.query.filter_by(id=poster_id).first()
    user.follow(poster)
    return jsonify({
        'followed': True,
        'code': True
    })

@api.route('/users/<int:id>/unfollow/', methods = ['POST'])
def unfollow(id):
    poster_id = request.form.get('poster_id')
    user = User.query.filter_by(id=id).first()
    poster = User.query.filter_by(id=poster_id).first()
    user.unfollow(poster)
    return jsonify({
        'followed': False,
        'code': True
    })

@api.route('/update_info/<int:id>/', methods = ['POST'])
def user_update(id):
    location = request.form['location']
    about_me = request.form['about_me']
    name = request.form['name']
    user = User.query.get_or_404(id)
    code = False
    if user is not None:
        user.about_me = about_me
        user.location = location
        user.name = name
        db.session.commit()
        code = True
    return jsonify({
        'code': code
    })
