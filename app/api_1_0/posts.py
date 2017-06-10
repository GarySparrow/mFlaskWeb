from flask import jsonify, request, g, abort, url_for, current_app, render_template
from .. import db
from ..models import Post, Permission, User
from . import api
from .decorators import permission_required
from sqlalchemy import func, distinct
from .errors import forbidden
import datetime
import zlib, pickle, json


@api.route('/posts/')
def get_posts():
    # page = request.args.get('page', 1, type=int)
    # pagination = Post.query.paginate(
    #     page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
    #     error_out=False)
    # posts = pagination.items
    # prev = None
    # if pagination.has_prev:
    #     prev = url_for('api.get_posts', page=page-1, _external=True)
    # next = None
    # if pagination.has_next:
    #     next = url_for('api.get_posts', page=page+1, _external=True)
    posts = Post.query.order_by(db.desc(Post.id)).all()
    return jsonify({
        'posts': [post.to_json() for post in posts],
        # 'prev': prev,
        # 'next': next,
        # 'count': pagination.total
    })


@api.route('/posts/<int:id>')
def get_post(id):
    post = Post.query.get_or_404(id)
    return jsonify(post.to_json())


# @api.route('/posts/', methods=['POST'])
# @permission_required(Permission.WRITE_ARTICLES)
# def new_post():
#     post = Post.from_json(request.json)
#     post.author = g.current_user
#     db.session.add(post)
#     db.session.commit()
#     return jsonify(post.to_json()), 201, \
#         {'Location': url_for('api.get_post', id=post.id, _external=True)}

@api.route('/posts/', methods=['POST'])
# @permission_required(Permission.WRITE_ARTICLES)
def new_post():
    body = request.form['body']
    author_id = request.form['author_id']
    user = User.query.filter_by(id=author_id).first()
    if user is None and not user.can(Permission.WRITE_ARTICLES):
        return jsonify({'code': False})
    img = ['img1', 'img2', 'img3', 'img4', 'img5', 'img6', 'img7', 'img8', 'img9']

    idx = 0
    imgs_root = '/static/'
    video_root = '/static/'
    imgs_path = []
    video_path = None
    for s in img:
        if s in request.files:
            last = user.posts.order_by(Post.timestamp.desc()).first()
            if last is not None:
                post_id = last.id + 1
            else:
                post_id = 1
            idx = idx + 1
            time = datetime.datetime.now()
            time_str = datetime.datetime.strftime(time, '%Y%m%d%H%M%S')
            path = imgs_root + 'imgs_' + str(author_id) + '_' + str(post_id) + '_' + str(idx) + \
                   '_' + time_str + '.jpg'
            imgs_path.append(path)
            file = open('app/' + path, 'wb')

            data = request.files[s].read()
            file.write(data)

            file.close()
    if 'video' in request.files:
        last = user.posts.order_by(Post.timestamp.desc()).first()
        if last is not None:
            post_id = last.id + 1
        else:
            post_id = 1
        time = datetime.datetime.now()
        time_str = datetime.datetime.strftime(time, '%Y%m%d%H%M%S')
        path = video_root + 'video_' + str(author_id) + '_' + str(post_id) + \
               '_' + time_str + '.mp4'
        video_path = path
        file = open('app/' + path, 'wb')
        input = request.files['video'].read()

        file.write(input)

        file.close()

    if len(imgs_path) > 0:
        post = Post(author_id = author_id, body = body, imgs_path = imgs_path)
    elif video_path is not None:
        post = Post(author_id = author_id, body = body, video_path = video_path)
    else:
        post = Post(author_id = author_id, body = body)
    db.session.add(post)
    db.session.commit()
    return jsonify({'posts': [post.to_json()],
                     'code': True,
                     'followers': [User.query.filter_by(
                         id=follow.follower_id).to_json()
                        for follow in user.followers.all()]})

# @api.route('/posts/', methods=['POST'])
# # @permission_required(Permission.WRITE_ARTICLES)
# def new_post():
#     body = request.json.get('body')
#     author_id = request.json.get('id')
#     user = User.query.filter_by(id=author_id).first()
#     if user is None and not user.can(Permission.WRITE_ARTICLES):
#         return jsonify({'code': False})
#     post = Post(author_id=author_id, body=body)
#     db.session.add(post)
#     db.session.commit()
#     return jsonify({'posts': [post.to_json()],
#                      'code': True})


# @api.route('/posts/<int:id>', methods=['PUT'])
# @permission_required(Permission.WRITE_ARTICLES)
# def edit_post(id):
#     post = Post.query.get_or_404(id)
#     if g.current_user != post.author and \
#             not g.current_user.can(Permission.ADMINISTER):
#         return forbidden('Insufficient permissions')
#     post.body = request.json.get('body', post.body)
#     db.session.add(post)
#     return jsonify(post.to_json())

@api.route('/posts/<int:id>', methods=['POST'])
def edit_post(id):
    post = Post.query.get_or_404(id)
    author_id = request.form['author_id']
    # author_id = request.json.get('author_id')
    user = User.query.filter_by(id=author_id).first()
    if user is None or not user.can(Permission.WRITE_ARTICLES) or author_id != post.author_id:
        return forbidden('Insufficient permissions')
    body = request.form.get('body')
    # body = request.json.get('body')
    post.body = body
    db.session.commit()
    return jsonify({'posts': [post.to_json()]})


@api.route('/users/<int:id>/timeline/')
def get_user_followed_posts(id):
    user = User.query.get_or_404(id)
    # page = request.args.get('page', 1, type=int)
    # pagination = user.followed_posts.order_by(Post.timestamp.desc()).paginate(
    #     page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
    #     error_out=False)
    # posts = pagination.items
    # prev = None
    # if pagination.has_prev:
    #     prev = url_for('api.get_user_followed_posts', page=page-1,
    #                    _external=True)
    # next = None
    # if pagination.has_next:
    #     next = url_for('api.get_user_followed_posts', page=page+1,
    #                    _external=True)
    posts = user.followed_posts.order_by(db.desc(Post.id)).all()
    return jsonify({
        'posts': [post.to_json() for post in posts],
        # 'prev': prev,
        # 'next': next,
        # 'count': pagination.total
    })

# @api.route('/posts/<int:post_id>/like/', method=['POST'])
# def like(post_id):




# @api.route("/posts/<int:id>/video", methods = ['POST', 'GET'])
# def get_video(id):
#     post = Post.query.filter_by(id=id).first()
#     root = 'static/'
#     file = open(root + str(post.author_id) + '_' + str(post.id), 'r')
#     data = file.read()

@api.route('/posts/<int:id>/isliked/', methods = ['GET'])
def is_liked(id):
    user_id = request.args.get('user_id')
    user = User.query.filter_by(id=user_id).first()
    post = Post.query.filter_by(id=id).first()
    isliked = post.is_liked_by(user)
    return jsonify({
        'liked': isliked,
        'code': True
    })

@api.route('/posts/<int:id>/like/', methods = ['POST'])
def like(id):
    user_id = request.form.get('user_id')
    user = User.query.filter_by(id=user_id).first()
    post = Post.query.filter_by(id=id).first()
    user.like(post)
    return jsonify({
        'liked': True,
        'code': True,
        'author': User.query.filter_by(id=post.author_id).first().to_json()
    })

@api.route('/posts/<int:id>/unlike/', methods = ['POST'])
def unlike(id):
    user_id = request.form.get('user_id')
    user = User.query.filter_by(id=user_id).first()
    post = Post.query.filter_by(id=id).first()
    user.unlike(post)
    return jsonify({
        'liked': False,
        'code': True
    })

@api.route('/posts/<int:id>/like_count/', methods = ['GET'])
def like_count(id):
    post = Post.query.filter_by(id = id).first()
    count = post.likers_sum
    return jsonify({
        'count': count,
        'code': True
    })


