# Define your tables below (or better in another model file) for example
#
# >>> db.define_table('mytable', Field('myfield', 'string'))
#
# Fields can be 'string','text','password','integer','double','boolean'
#       'date','time','datetime','blob','upload', 'reference TABLENAME'
# There is an implicit 'id integer autoincrement' field
# Consult manual for more options, validators, etc.



# after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)

def get_user_email():
    return None if auth.user is None else auth.user.email

db.define_table('product',
        Field('seller', default=get_user_email()),
        Field('name', 'string'),
        Field('description', 'text'),
        Field('stock','integer', default=0),
        Field('sold', 'integer', default = 0),
        Field('price', 'double', default = 0),
        Field('costs', 'double', default = 0),
        Field('profit', 'integer', default = 0),
        Field('starred', 'boolean', default=False)
        )


db.product.seller.writable = False
db.product.seller.readable = False

db.product.sold.writable = False

db.product.sold.requires = IS_INT_IN_RANGE(0,1000)
db.product.sold.readable = True



db.product.profit.writable = False

db.product.id.readable = False

db.product.price.requires =  IS_FLOAT_IN_RANGE(0,1000)
db.product.price.writable = True

db.product.costs.represent = lambda v, r: v if v is not None else 0
db.product.costs.writable = True
db.product.costs.writable = True
db.product.costs.requires = IS_FLOAT_IN_RANGE(0,1000)

db.product.stock.writable = True
db.product.stock.represent = lambda v, r: v if v is not None else 0
db.product.stock.requires = IS_INT_IN_RANGE(0,1000)

db.product.profit.represent = lambda v, r: v if v is not None else 0
db.product.profit.requires = IS_INT_IN_RANGE(0,1000)

db.product.starred.writable = False
db.product.starred.readable = False


db.define_table('star',
    Field('user_id', 'reference auth_user'), 
    Field('product_id', 'reference product'), 
)



