# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# This is a sample controller
# this file is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

# ---- example index page ----

POSTS_PER_PAGE = 10

def get_category():
    category_name = request.args(0)
    category = db.category(name = category_name)
    if not category:
        session.flash = 'page not found'
        redirect (URL('index'))
    return category

def index():
    row = db(db.category).select()
    return locals()

@auth.requires_login()
def create_post():
    category = get_category()
    db.post.category.default = category.id
    form = SQLFORM(db.post).process(next='view_post/[id]')
    return locals()

@auth.requires_login()
def edit_post():
    id = request.args(0,cast=int,)
    form = SQLFORM(db.post, id,showid=False).process(next='view_post/[id]')
    return locals()

def list_post_by_datetime():
    response.view = 'default/list_post_by_votes.html'
    category = get_category()
    page = request.args(1,cast=int,default=0)
    start = page*POSTS_PER_PAGE
    stop = start+POSTS_PER_PAGE
    rows = db(db.post.category==category.id).select(orderby=~db.post.created_on,limitby =(start,stop))
    return locals()

def list_post_by_votes():
    category = get_category()
    page = request.args(1,cast=int,default=0)
    start = page*POSTS_PER_PAGE
    stop = start+POSTS_PER_PAGE
    rows = db(db.post.category==category.id).select(orderby=~db.post.votes,limitby =(start,stop))
    return locals()

def list_post_by_author():
    response.view = 'default/list_post_by_votes.html'
    user_id = request.args(0,cast=int)
    page = request.args(1,cast=int,default=0)
    start = page*POSTS_PER_PAGE
    stop = start+POSTS_PER_PAGE
    rows = db(db.post.created_by==user_id).select(orderby=~db.post.created_on,limitby =(start,stop))
    return locals()

def view_post():
    id = request.args(0,cast=int,)
    post = db.post(id) or redirect(URL('index'))
    comment = db(db.comm.post==post.id).select(orderby=~db.comm.created_on,limitby=(0,1)).first()
    if auth.user:
        db.comm.post.default = id
        db.comm.parent_comm.default = comment
        form = SQLFORM(db.comm).process()
    else:
        form = A('login to comment',_href=URL('user/login',vars=dict(_next=URL(args=request.args))))
    comments = db(db.comm.post==post.id).select(orderby=db.comm.created_on)
    return locals()
 

def vote_callback():
    vars = request.get.vars
    if vars:
        id = vars.id
        direction = +1 if vars.direction == 'up' else -1
        post = db.post(id)
        if post:
            post.update_record(votes=post.votes+direction)
    return str(post.votes)

def comm_vote_callback():
    id = request.args(0,cast=int,)
    direction = request.args(1)
    #TO_DO
    return locals()


# ---- API (example) -----
@auth.requires_login()
def api_get_user_email():
    if not request.env.request_method == 'GET': raise HTTP(403)
    return response.json({'status':'success', 'email':auth.user.email})

# ---- Smart Grid (example) -----
@auth.requires_membership('admin') # can only be accessed by members of admin groupd
def grid():
    response.view = 'generic.html' # use a generic view
    tablename = request.args(0)
    if not tablename in db.tables: raise HTTP(403)
    grid = SQLFORM.smartgrid(db[tablename], args=[tablename], deletable=False, editable=False)
    return dict(grid=grid)

# ---- Embedded wiki (example) ----
def wiki():
    auth.wikimenu() # add the wiki to the menu
    return auth.wiki() 

# ---- Action for login/register/etc (required for auth) -----
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())

# ---- action to server uploaded static content (required) ---
@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)
