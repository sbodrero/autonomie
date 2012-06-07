# -*- coding: utf-8 -*-
# * File Name : auth.py
#
# * Copyright (C) 2012 Majerti <tech@majerti.fr>
#   This software is distributed under GPLV3
#   License: http://www.gnu.org/licenses/gpl-3.0.txt
#
# * Creation Date : 07-02-2012
# * Last Modified : jeu. 07 juin 2012 18:18:08 CEST
#
# * Project :
#
"""
    All Authentication views
"""
import logging

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPForbidden

from pyramid.security import authenticated_userid
from pyramid.security import forget
from pyramid.security import remember
from pyramid.security import NO_PERMISSION_REQUIRED

from deform import Form
from deform import Button
from deform import ValidationFailure

from autonomie.views.forms import authSchema
from autonomie.views.forms import pwdSchema

log = logging.getLogger(__name__)

@view_config(context=HTTPForbidden, permission=NO_PERMISSION_REQUIRED)
def forbidden_view(request):
    """
        The forbidden view (handles the redirection to login form)
    """
    log.warn("# An access has been forbidden #")
    if authenticated_userid(request):
        log.warn(" + An authenticated user tried to connect")
        return HTTPForbidden()
    log.debug(" + Not authenticated : try again")
    #redirecting to the login page with the current path as param
    loc = request.route_url('login', _query=(('nextpage', request.path),))
    return HTTPFound(location=loc)

@view_config(route_name='login', permission=NO_PERMISSION_REQUIRED,
                                                        renderer='login.mako')
def login_view(request):
    """
        The login view
    """
    form = Form(authSchema,
                buttons=(Button(name="submit",
                                title="Connexion",
                                type='submit'),))
    nextpage = request.params.get('nextpage') or request.route_url('index')
    # avoid looping
    if nextpage == request.route_url('login'):
        nextpage = request.route_url('index')
    app_struct = {'nextpage':nextpage}
    myform = form.render(app_struct)
    fail_message = None
    if 'submit' in request.params:
        log.debug("# Authentication process #")
        controls = request.params.items()
        try:
            datas = form.validate(controls)
        except ValidationFailure, e:
            log.exception(" - Authentication error")
            myform = e.render()
            fail_message = u"Erreur d'authentification"
            return {'title':"Authentification",
                    'html_form':myform,
                    'message':fail_message
                    }
        else:
            login = datas['login']
            log.info("User '{0}' has been authenticated".format(login))
            log.debug("  + Redirecting to {0}".format(nextpage))
            # Storing the datas in the request object
            remember(request, login)
            return HTTPFound(location=nextpage)
    return {
            'title':"Bienvenue dans Autonomie",
            'html_form':myform,
            'message':fail_message
            }

@view_config(route_name='logout', permission=NO_PERMISSION_REQUIRED)
def logout_view(request):
    """
        The logout view
    """
    headers = forget(request)
    loc = request.route_url('index')
    return HTTPFound(location=loc, headers=headers)

@view_config(route_name='account', renderer='account.mako')
def account(request):
    """
        Account handling page
    """
    avatar = request.user
    pwdformschema = pwdSchema.bind(check=True)
    pwdform = Form(pwdformschema, buttons=("submit",))
    html_form = pwdform.render({'login':avatar.login})
    if "submit" in request.params:
        controls = request.params.items()
        try:
            datas = pwdform.validate(controls)
        except ValidationFailure, e:
            html_form = e.render()
        else:
            log.debug("# User {0} has changed his password #")
            dbsession = request.dbsession()
            new_pass = datas['pwd']
            avatar.set_password(new_pass)
            dbsession.merge(avatar)
            dbsession.flush()
            request.session.flash(u"Votre mot de passe a bien été modifié",
                                                                    'main')

    return dict(title="Mon compte",
                html_form=html_form,
                account=avatar
                )
