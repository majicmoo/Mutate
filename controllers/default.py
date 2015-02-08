import applications.Mutate.models.testinggithubapi.authenticate as authenticate
import os

CLONED_REPOS_PATH = "applications/Mutate/models/testinggithubapi/clonedrepos"


def index():

    return dict(dict=dict)

def mutateprojects():

    # Subject Selection
    form=FORM(DIV(FIELDSET(
    LEGEND('Search For Repositories'),
    # Keyword
      DIV(LABEL('Keyword', _for='keyword', _class='control-label'),
      DIV(INPUT(_name='keyword'), _class='controls'),  _class='control-group'),
    #Repo Size
      DIV(LABEL('Repository Size', _for='repo_size', _class='control-label'),
      DIV(INPUT(_name='min_repo_size', requires=[IS_NOT_EMPTY(), IS_INT_IN_RANGE(0,1000000)], _class='span2', _placeholder='min'),
      INPUT(_name='max_repo_size', requires=[IS_NOT_EMPTY(), IS_INT_IN_RANGE(0,1000000)], _class='span2', _placeholder='max'),
      _class='controls controls-row'), _class='control-group'),

    # Language
      DIV(LABEL('Language', _for='language', _class='control-label'),
      DIV(SELECT(OPTION("Java"), _name='language'), _class='controls'),
      _class='control-group'),
    # Order By
      DIV(LABEL('Order Results by', _for='order_by', _class='control-label'),
      DIV(SELECT(OPTION("Forks"),OPTION("Stars"), _name='order_by'), _class='controls'),
      _class='control-group'),
    # Asc/Desc
      DIV(LABEL('Ascending/Descending', _for='asc_desc', _class='control-label'),
      DIV(SELECT(OPTION("Descending"),OPTION("Ascending"), _name='asc_desc'), _class='controls'),
      _class='control-group'),
    # Number of results
      DIV(LABEL('Number of Results', _for='no_results', _class='control-label'),
      DIV(INPUT(_name='no_results', requires=[IS_NOT_EMPTY(), IS_INT_IN_RANGE(0,1000000)]), _class='controls'),
      _class='control-group'),
    # submit
      DIV(DIV(DIV(BUTTON('Submit',_type='submit', _class="btn btn-large btn-primary")),_class="row"),
          _class="offset3 span3"))), _class = 'form-horizontal')

    if form.accepts(request, session):
        # User has made search, submit task
        if request.vars.min_value > request.vars.max_value:
            session.flash = "Min should be lower than Max"
            redirect(location=URL('default','mutateprojects.html'))
        # Check if keyword is none
        if request.vars.keyword is None:
            keyword = ""
        else:
            keyword = request.vars.keyword
        # Check Ascending v descending
        if request.vars.asc_desc == "Ascending":
            asc_desc = "asc"
        else:
            asc_desc = "desc"
        #Check Order by
        if request.vars.order_by == "Stars":
            order_by = "stars"
        else:
            order_by = "forks"

        username = db.auth_user[auth._get_user_id()].username
        print request.vars.max_repo_size, request.vars.min_repo_size, request.vars.language, order_by, asc_desc,\
            request.vars.no_results,username, session.token
        task = scheduler.queue_task('findProjects', pvars=dict(keyword=keyword, maxsize=int(request.vars.max_repo_size),
                                                        minsize=int(request.vars.min_repo_size),
                                                        language=request.vars.language.lower(), sortby=order_by,
                                                        orderby=asc_desc, number_of_projects=int(request.vars.no_results),
                                                        username=username, token=session.token) ,timeout=9999)
        print 'task', task.id, 'started'



        session.search.append(task)
        redirect(URL('projectmutation','results',args=[str(task.id)]))

    return dict(form=form)

def register():
     form=FORM(DIV(FIELDSET(
         LEGEND('Register'),
         #username
         DIV( LABEL('Github Username', _for='username', _class='control-label'),
              DIV(INPUT(_name='username', requires=[IS_NOT_EMPTY(),
                                                    IS_NOT_IN_DB(db, db.auth_user.username,
                                                                 error_message="Username already taken")])
                  , _class='controls'),  _class='control-group'),

         #submit
         DIV(DIV(DIV(BUTTON('Submit',_type='submit', _class="btn btn-large btn-primary")),_class="row"),
             _class="offset3 span3"))), _class = 'form-horizontal')

     if form.accepts(request, session):
         db.auth_user.insert(username=request.vars.username)
         redirect(URL('default','login.html'))

     return dict(form=form)

def login():
    # Github Auth
    form=FORM(DIV(FIELDSET(
        LEGEND('User Details'),
        # username
          DIV( LABEL('Username', _for='username', _class='control-label'),
          DIV(INPUT(_name='username', requires=IS_NOT_EMPTY()), _class='controls'),  _class='control-group'),
        # token
          DIV(LABEL('Token', _for='token', _class='control-label'),
          DIV(INPUT(_name='token', requires=IS_NOT_EMPTY()), _class='controls'),
          _class='control-group'),
        # submit
          DIV(DIV(DIV(BUTTON('Submit',_type='submit', _class="btn btn-large btn-primary")),_class="row"),
              _class="offset3 span3"))), _class = 'form-horizontal')

    if form.accepts(request, session):
        session.token = request.vars.token
        session.search=[]
        user=db(db.auth_user.username==request.vars.username).select().first()
        if user is None:
            session.flash = H1('Please Register')
            redirect(location=URL('default','register.html'))
        else:
            auth.login_user(user=user)
            redirect(location=URL('default','index.html'))

        # test = authenticate.Authenticate()
        # token = test.check_authentication(request.vars.username, request.vars.password, None)
        # if token is False:
        #     #Bad Credentials
        #     session.flash=DIV(H4('Credentials Denied'), _class="alert alert-danger")
        #     redirect(location=URL('default','index.html'))
        #
        # else:
        #     # Inform user logged in
        #     session.flash=DIV(H4('Credentials Accepeted', token), _class="alert alert-success")
        #     redirect(location=URL('default','index.html'))
        #
        #
        # #pass


    return dict(form=form)



def about():

    return dict(dict=dict)
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
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


@auth.requires_login() 
def api():
    """
    this is example of API with access control
    WEB2PY provides Hypermedia API (Collection+JSON) Experimental
    """
    from gluon.contrib.hypermedia import Collection
    rules = {
        '<tablename>': {'GET':{},'POST':{},'PUT':{},'DELETE':{}},
        }
    return Collection(db).process(request,response,rules)
