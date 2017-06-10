from flask import jsonify, request, g, url_for, current_app
from .. import db
from ..models import Post, Permission, Comment, User
from . import api
from .decorators import permission_required


@api.route('/comments/')
def get_comments():
    # page = request.args.get('page', 1, type=int)
    # pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
    #     page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
    #     error_out=False)
    # comments = pagination.items
    # prev = None
    # if pagination.has_prev:
    #     prev = url_for('api.get_comments', page=page-1, _external=True)
    # next = None
    # if pagination.has_next:
    #     next = url_for('api.get_comments', page=page+1, _external=True)
    comments = Comment.query.order_by(db.desc(Post.id)).all()
    return jsonify({
        'comments': [comment.to_json() for comment in comments],
        # 'prev': prev,
        # 'next': next,
        # 'count': pagination.total
    })


@api.route('/comments/<int:id>')
def get_comment(id):
    comment = Comment.query.get_or_404(id)
    return jsonify(comment.to_json())


@api.route('/posts/<int:id>/comments/')
def get_post_comments(id):
    post = Post.query.get_or_404(id)
    # page = request.args.get('page', 1, type=int)
    # pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
    #     page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
    #     error_out=False)
    # comments = pagination.items
    # prev = None
    # if pagination.has_prev:
    #     prev = url_for('api.get_post_comments', page=page-1, _external=True)
    # next = None
    # if pagination.has_next:
    #     next = url_for('api.get_post_comments', page=page+1, _external=True)
    comments = Comment.query.filter_by(post_id = post.id).order_by(db.desc(Post.id)).all()
    return jsonify({
        'comments': [comment.to_json() for comment in comments],
        # 'prev': prev,
        # 'next': next,
        # 'count': pagination.total
    })


# @api.route('/posts/<int:id>/comments/', methods=['POST'])
# @permission_required(Permission.COMMENT)
# def new_post_comment(id):
#     post = Post.query.get_or_404(id)
#     comment = Comment.from_json(request.json)
#     comment.author = g.current_user
#     comment.post = post
#     db.session.add(comment)
#     db.session.commit()
#     return jsonify(comment.to_json()), 201, \
#         {'Location': url_for('api.get_comment', id=comment.id,
#                              _external=True)}

@api.route('/posts/<int:id>/comments/', methods = ['POST'])
def new_post_comment(id):
    body = request.form['body']
    author_id = request.form['author_id']
    # body = request.json.get('body')
    # author_id = request.json.get('author_id')
    user = User.query.filter_by(id=author_id).first()
    post = Post.query.filter_by(id=id).first()
    post_author = User.query.filter_by(id=post.author_id).first()
    if author_id is None and not user.can(Permission.COMMENT):
        return jsonify({'code': False})
    comment = Comment(body=body, post_id=id, author_id=author_id)
    db.session.add(comment)
    db.session.commit()
    return jsonify({'code': True,
                     'comments': [comment.to_json()],
                     'post_author': post_author.to_json()})


