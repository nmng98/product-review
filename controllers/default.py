# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------


def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    rows = db(db.product.starred == True).select()
    return dict(rows=rows)



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


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


def list():
    query = db.product
    links = []
    
    links.append(
        dict(header = "Star",
            body = lambda row : get_star(row)
        )
    )
    links.append(
        dict(header = " ",
            body = lambda row : get_incr(row)
        )
    )
    links.append(
        dict(header = " ",
            body = lambda row : get_decr(row)
        )
    )
    links.append(
        dict(header = " ",
            body = lambda row : get_edit(row)
        )
    )
    links.append(
        dict(header = " ",
            body = lambda row : get_delete(row)
        )
    )
    
    if len(request.args) > 0 and request.args[0] == 'new':
        db.product.seller.readable = False
        
        
    grid = SQLFORM.grid (
        query, 
        field_id = db.product.id,
        fields = [db.product.seller, db.product.name, db.product.stock, db.product.sold, 
        db.product.price, db.product.costs, db.product.profit, db.product.starred],
        links = links,
        details = False,
        create = True, editable = False, deletable = False,
        csv = False,
        searchable = False,
        user_signature = True,
    )
    return dict(grid=grid)

def get_edit(row): 
    product = db.product(row.id)   
    if 'user' in db.product.seller:
        if (auth.user and auth.user.email) == row.seller:
            return SPAN(A('',  
            _href=URL('default', 'edit', args=[row.id], user_signature=True),
            _class='fa fa-pencil-square-o'))

        else:
            return SPAN()
    else:
       return SPAN() 

@auth.requires_login()
def edit():

    product = db.product(request.args(0))
    
    db.product.profit.readable = False
    db.product.sold.readable = False
    
    if product is None:
        logging.info("Invalid edit call")
        redirect(URL('default', 'index'))

    if product.seller != auth.user.email:
        logging.info("Attempt to edit some one else's post by: %r" % auth.user.email)
        redirect(URL('default', 'index'))

    form = SQLFORM(db.product, record=product)
    if form.process(onvalidation=mychecks).accepted:
        redirect(URL('default', 'list'))
    
    return dict(form=form)

def mychecks(form):
    """Performs form validation.  
    See http://www.web2py.com/books/default/chapter/29/07/forms-and-validators#onvalidation 
    for details."""
    # form.vars contains what the user put in.
    if form.vars.stock < 0:
        form.errors.stock = "I am sorry but that's unacceptable to have %d" % form.vars.stock


def get_delete(row):
    product = db.product(row.id)   
    if 'user' in db.product.seller:
        if (auth.user and auth.user.email) == row.seller:
            return SPAN(A('',  
                _href=URL('default', 'delete', args =[row.id], user_signature=True),
                _class='fa fa-trash-o'),
                _class="haha")    
        else:
            return SPAN() 
    else:
            return SPAN() 

@auth.requires_signature()
@auth.requires_login()
def delete():
    product = db.product(request.args(0))
    
    if product is None:
        logging.info("Invalid edit call")
        redirect(URL('default', 'index'))
    
    if product.seller != auth.user.email:
        logging.info("Attempt to edit some one else's post by: %r" % auth.user.email)
        redirect(URL('default', 'index'))
    
    db(db.product.id == product.id).delete()
    redirect(URL('default', 'list'))

 
def get_incr(row):
    if auth.user is not None:
        return SPAN(A('', 
            _href=URL('default', 'increment',vars=dict(id=row.id), user_signature=True),
            _class='fa fa-plus-square-o'),
        _class="haha")
    
    else:
        return SPAN()
   
@auth.requires_signature()
def increment():
    product = db.product(request.vars.id)
    product.stock = 0 if product.stock is None else product.stock + 1
    product.update_record()
    redirect(URL('default', 'list'))
    return dict(form=form)

def get_decr(row):
    if auth.user is not None:
        if row.stock > 0:
            return SPAN(A('', 
                _href=URL('default', 'decrement',args=[row.id], user_signature=True),
                _class='fa fa-minus-square-o'))
        else:
            return SPAN(A('', 
                _href=URL(args=[row.id], user_signature=True),
                _class='fa fa-minus-square gray'))  # change style        
    else:
        return SPAN()

@auth.requires_signature()
def decrement():
    product = db.product(request.args(0))
    
    if product.stock == 0:
        redirect(URL('default', 'list'))
        product.update_record()
    else:
        product.stock = product.stock - 1
        product.update_record()
        product.sold = product.sold + 1
        product.update_record()
        product.profit = product.sold * (product.price - product.costs)
        product.update_record()
        redirect(URL('default', 'list'))


def get_star(row):      
    if auth.user is not None:
        if row.starred is False:
            return A(I(_class='fa fa-star-o'),
                _href=URL('default', 'toggle_star', args=[row.id], user_signature=True),
                )

        else:
            return A(I(_class='fa fa-star'),
                _href=URL('default', 'toggle_star', args=[row.id], user_signature=True),
            )
    else:
        if row.starred is False:
            return A(I(_class='fa fa-star-o'),
                _href=URL(args=[row.id], user_signature=True),
            )
        else:
            return A(I(_class='fa fa-star'),
                _href=URL(args=[row.id], user_signature=True),
            )

@auth.requires_signature()
def toggle_star():
    star_record = db((db.star.product_id == int(request.args[0])) &
        (db.star.user_id == auth.user_id)).select().first()
    
    product = db.product(request.args(0))
    if star_record is not None:
        # Removes star.
        db(db.star.id == star_record.id).delete()
        product.starred = False
        product.update_record()
    
    else:
        # Adds the star.
        db.star.insert(
            user_id = auth.user.id,
            product_id = int(request.args[0]))     
        product.starred = True
        product.update_record()
    
    product.update_record()
        
    redirect(URL('default', 'list'))

