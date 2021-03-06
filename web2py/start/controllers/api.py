from __future__ import unicode_literals
import json
import os
from generator import sentGenerator
from image_generator import image_generator


def generate_text():
    """
    nlg text gen
    """
    file_path = os.path.join(request.folder, 'static', 'json', 'post_compilation.json')
    with open(file_path) as post_comp:
        ngrams = json.load(post_comp)
        gen = sentGenerator(ngrams)
        return gen().encode('utf-8')


def generate_image():
    """
    Generates original image
    """
    bkgd_path = os.path.join(request.folder, 'static', 'images', 'src', 'bkgd')
    back_overlay_path = os.path.join(request.folder, 'static', 'images', 'src', 'back overlays')
    overlay_path = os.path.join(request.folder, 'static', 'images', 'src')
    vector_path = os.path.join(request.folder, 'static', 'images', 'src', 'vectors')
    dest_path = os.path.join(request.folder, 'static', 'images', 'gen')
    gen = image_generator(bkgd_path, back_overlay_path, overlay_path, vector_path, dest_path)
    return gen()


def generate_post():
    p_id = db.shitpost.insert(
        text_post = generate_text(),
        image = generate_image()
    )
    p = db.shitpost(p_id)
    return response.json(dict(post=p))


# These are the controllers for your ajax api.
def get_posts():
    """This controller is used to get the posts.  Follow what we did in lecture 10, to ensure
    that the first time, we get 4 posts max, and each time the "load more" button is pressed,
    we load at most 4 more posts."""
    start_idx = int(request.vars.start_idx) if request.vars.start_idx is not None else 0
    end_idx = int(request.vars.end_idx) if request.vars.end_idx is not None else 0
    # We just generate a lot of of data.
    posts = []
    has_more = False
    rows = db().select(db.shitpost.ALL, orderby=~db.shitpost.created_on, limitby=(start_idx, end_idx + 1))
    for i, r in enumerate(rows):
        if i < end_idx - start_idx:
            sp = get_post_output(r)
            posts.append(sp)
            #comments = db(db.post_comment.shitpost==r.id).select(db.post_comment.ALL, orderby=~db.post_comment.created_on, limitby=(0,4))
        else:
            has_more = True
    logged_in = auth.user_id is not None
    return response.json(dict(
        posts=posts,
        logged_in=logged_in,
        has_more=has_more
    ))


def get_best_posts():
    start_idx = int(request.vars.start_idx) if request.vars.start_idx is not None else 0
    end_idx = 25
    # We just generate a lot of of data.
    posts = []
    has_more = False
    posts = []
    rows = db().select(db.shitpost.ALL, orderby=~db.shitpost.upvotes, limitby=(start_idx, end_idx))
    for i, r in enumerate(rows):
        if i < end_idx - start_idx:
            sp = get_post_output(r)
            posts.append(sp)
        else:
            has_more = True
    logged_in = auth.user_id is not None
    return response.json(dict(
        posts=posts,
        logged_in=logged_in,
        has_more=has_more
    ))


def view_post():
    post = db.shitpost[request.args(0)] or redirect(URL(r=request, f='index'))
    sp = get_post_output(post)
    list = db(db.post_comment.shitpost==post.id).select(db.post_comment.ALL)
    comments = []
    logged_in = auth.user_id is not None
    for comment in list:
        comments.append(get_comment_output(comment))
    return response.json(dict(
        post=sp,
        comments=comments,
        logged_in=logged_in
    ))


def get_post():
    post = db.shitpost[request.vars.post_id]
    sp = get_post_output(post)
    list = db(db.post_comment.shitpost == post.id).select(db.post_comment.ALL)
    comments = []
    logged_in = auth.user_id is not None
    for comment in list:
        comments.append(get_comment_output(comment))
    return response.json(dict(
        post=sp,
        comments=comments,
        logged_in=logged_in
    ))

def add_comment_lb():
    """Here you get a new post and add it.  Return what you want."""
    post = db.shitpost[request.vars.post_id]
    c_id =  db.post_comment.insert(
        shitpost=post.id,
        comment_content=request.vars.comment_content
    )
    c = get_comment_output(db.post_comment(c_id))
    return response.json(dict(comment=c))

# Note that we need the URL to be signed, as this changes the db.
# @auth.requires_signature()
def add_comment():
    """Here you get a new post and add it.  Return what you want."""
    post = db.shitpost[request.args(0)] or redirect(URL(r=request, f='index'))
    c_id =  db.post_comment.insert(
        shitpost=post.id,
        comment_content=request.vars.comment_content
    )
    c = get_comment_output(db.post_comment(c_id))
    return response.json(dict(comment=c))


@auth.requires_signature()
def del_comment():
    """Used to delete a comment."""
    comment = db.post_comment[request.vars.comment_id]
    if not auth.user or comment.user_email != auth.user.email:
        return "no"
    db( db.post_comment.id == request.vars.comment_id).delete()
    return "ok"


@auth.requires_signature()
def edit_comment():
    """Used to edit a comment."""
    comment = db.post_comment[request.vars.comment_id]
    if not auth.user or comment.user_email != auth.user.email:
        return "no"
    db( db.post_comment.id == request.vars.comment_id).update(comment_content = request.vars.comment_content)
    return "{0}{1}".format("Edited On ", comment.updated_on)


@auth.requires_signature()
def vote():
    """Used to vote on a post."""
    if not auth.user:
        return response.json(dict(
            success="no"
        ))
    post = db.shitpost[request.vars.post_id]
    list = db(db.votelog.shitpost == post.id).select(db.votelog.ALL)
    my_vote = None
    for vote in list:
        if vote.user_email == auth.user.email:
            my_vote = vote
            break

    success = False
    new_value = post.upvotes
    vote_value = int(request.vars.vote_value)
    succ = ""
    # Vote
    if my_vote is None:
        v_id = db.votelog.insert(
            shitpost = post,
            is_upvote = True if vote_value == 1 else False
        )
        new_value = post.upvotes + vote_value
        db(db.shitpost.id == post.id).update(upvotes = new_value)
        v = db.votelog(v_id)
        success = True
        succ = "vote"
    else:
        # Delete vote
        if (my_vote.is_upvote and vote_value == 1) or \
           (not my_vote.is_upvote and vote_value == -1):
            db(db.votelog.id == my_vote.id).delete()
            new_value = post.upvotes - vote_value
            db(db.shitpost.id == post.id).update(upvotes=new_value)
            success = True
            succ = "del"
        else:
            db(db.votelog.id == my_vote.id).update(is_upvote = not my_vote.is_upvote)
            new_value = post.upvotes + vote_value * 2
            db(db.shitpost.id == post.id).update(upvotes=new_value)

            success = True
            succ = "vote"

    if success:
        return response.json(dict(
            success=succ,
            count = new_value
        ))
    return response.json(dict(
        success="no"
    ))


# Utility functions
def get_user_name_from_email(email):
    """Returns a string corresponding to the user first and last names,
    given the user email."""
    u = db(db.auth_user.email == email).select().first()
    if u is None:
        return 'None'
    else:
        return ' '.join([u.first_name, u.last_name])


def get_comment_output(comment):
    id = comment.id
    shitpost_id = comment.shitpost
    user_email = comment.user_email
    comment_content = comment.comment_content
    user_name = (comment.username if comment.username is not None \
                 else get_user_name_from_email(user_email))
    created_on = comment.created_on
    updated = comment.created_on != comment.updated_on
    updated_on = "" if not updated else "{0}{1}".format("Edited On ", comment.updated_on)
    is_mine = auth.user and user_email == auth.user.email
    return dict(
                id=id,
                shitpost=shitpost_id,
                user_email=user_email,
                comment_content=comment_content,
                user_name=user_name,
                created_on=created_on,
                updated=updated,
                updated_on=updated_on,
                is_mine=is_mine
            )

def get_post_output(post):
    id = post.id
    text_post = post.text_post
    image = post.image
    upvotes = post.upvotes
    created_on = post.created_on
    my_vote = 0
    if auth.user:
        list = db(db.votelog.shitpost == post.id).select(db.votelog.ALL)
        my_vote = None
        for vote in list:
            if vote.user_email == auth.user.email:
                my_vote = vote
                break
        if my_vote is not None:
            my_vote = 1 if my_vote.is_upvote else -1
        else:
            my_vote = 0
    return dict(
        id=id,
        my_vote=my_vote,
        text_post=text_post,
        image=image,
        upvotes=upvotes,
        created_on=created_on,
    )
