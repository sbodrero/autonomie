# -*- coding: utf-8 -*-
# * Copyright (C) 2012-2013 Croissance Commune
# * Authors:
#       * Arezki Feth <f.a@majerti.fr>;
#       * Miotte Julien <j.m@majerti.fr>;
#       * Pettier Gabriel;
#       * TJEBBES Gaston <g.t@majerti.fr>
#
# This file is part of Autonomie : Progiciel de gestion de CAE.
#
#    Autonomie is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Autonomie is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Autonomie.  If not, see <http://www.gnu.org/licenses/>.
#

"""
    Customer views
"""
import logging

from sqlalchemy import (
    or_,
    not_,
)
from sqlalchemy.orm import undefer_group
from webhelpers.html.builder import HTML

from deform import Form

from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPFound
from pyramid.security import has_permission

from autonomie.models.customer import (
    Customer,
    COMPANY_FORM_GRID,
    INDIVIDUAL_FORM_GRID,
)
from autonomie.utils.widgets import (
    ViewLink,
    StaticWidget,
    ItemActionLink,
)
from autonomie.forms.customer import (
    get_list_schema,
    get_company_customer_schema,
    get_individual_customer_schema,
)
from deform_extensions import GridFormWidget
from autonomie.views import (
    BaseListView,
    BaseCsvView,
    BaseFormView,
    submit_btn,
)
from autonomie.views.csv_import import (
    CsvFileUploadView,
    ConfigFieldAssociationView,
)

logger = log = logging.getLogger(__name__)


def get_company_customer_form(request, counter=None):
    """
    Returns the customer add/edit form
    :param obj request: Pyramid's request object
    :param obj counter: An iterator for field number generation
    :returns: a deform.Form instance
    """
    schema = get_company_customer_schema(request)
    schema = schema.bind(request=request)
    form = Form(
        schema,
        buttons=(submit_btn,),
        counter=counter,
        formid='company',
    )
    form.widget = GridFormWidget(named_grid=COMPANY_FORM_GRID)
    return form


def get_individual_customer_form(request, counter=None):
    """
    Return a form for an individual customer
    :param obj request: Pyramid's request object
    :param obj counter: An iterator for field number generation
    :returns: a deform.Form instance
    """
    schema = get_individual_customer_schema(request)

    schema = schema.bind(request=request)
    form = Form(
        schema,
        buttons=(submit_btn,),
        counter=counter,
        formid='individual'
    )
    form.widget = GridFormWidget(named_grid=INDIVIDUAL_FORM_GRID)
    return form


class CustomersListTools(object):
    """
    Customer list tools
    """
    title = u"Liste des clients"
    schema = get_list_schema()
    sort_columns = {
        'name': Customer.name,
        "code": Customer.code,
        "lastname": Customer.lastname,
        "created_at": Customer.created_at,
    }
    default_sort = "created_at"
    default_direction = "desc"

    def query(self):
        company = self.request.context
        return Customer.query().filter_by(company_id=company.id)

    def filter_archived(self, query, appstruct):
        archived = appstruct.get('archived')
        if archived is False:
            query = query.filter_by(archived=False)
        return query

    def filter_type(self, query, appstruct):
        individual = appstruct.get('individual')
        company = appstruct.get('company')
        if not individual:
            query = query.filter(not_(Customer.type_ == 'individual'))
        if not company:
            query = query.filter(not_(Customer.type_ == 'company'))
        return query

    def filter_name_or_contact(self, records, appstruct):
        """
        Filter the records by customer name or contact lastname
        """
        search = appstruct.get('search')
        if search:
            records = records.filter(
                or_(Customer.name.like("%" + search + "%"),
                    Customer.lastname.like("%" + search + "%")))
        return records


class CustomersListView(CustomersListTools, BaseListView):
    """
    Customer listing view
    """
    add_template_vars = (
        'item_actions',
        'title',
        'forms',
    )
    grid = (
        (
            ('search', 3),
        ),
        (
            ('archived', 3), ('individual', 2), ('company', 2),
        ),
        (
            ('items_per_page', 2),
        ),
    )

    @property
    def forms(self):
        res = []
        form_title = u"Personne morale \
<small>(entreprise, administration, association ...)</small>"
        form = get_company_customer_form(self.request)
        res.append((form_title, form))
        field_counter = form.counter
        form_title = u"Personne physique <small>(particulier)</small>"
        form = get_individual_customer_form(self.request, field_counter)
        res.append((form_title, form))
        return res

    def _get_archived_btn(self, appstruct):
        """
            return the show archived button
        """
        archived = appstruct['archived']
        args = self.request.GET.copy()

        args.pop('archived', None)

        if not archived:
            msg = u"Afficher les clients archivés"
            args['archived'] = 'true'
        else:
            msg = u"Afficher les clients actifs"

        url = self.request.current_route_path(_query=args)
        link = HTML.a(msg, href=url)

        return StaticWidget(link)

    @property
    def item_actions(self):
        """
            return action buttons builder
        """
        return self._get_actions()

    def _get_actions(self):
        """
            Return action buttons with permission handling
        """
        btns = []
        btns.append(
            ItemActionLink(
                u"Voir",
                "view_customer",
                css='btn btn-default btn-sm',
                path="customer",
                icon="search"
            )
        )
        if self.request.params.get('archived', '0') in ('0', 'false'):
            btns.append(
                ItemActionLink(
                    u"Archiver",
                    "edit_customer",
                    css="btn btn-default btn-sm",
                    confirm=u'Êtes-vous sûr de vouloir archiver ce client ?',
                    path="customer",
                    title=u"Archiver le projet",
                    _query=dict(action="archive"),
                    icon="book",
                )
            )
        else:
            btns.append(
                ItemActionLink(
                    u"Désarchiver",
                    "edit_customer",
                    css="btn btn-default btn-sm",
                    path="customer",
                    title=u"Désarchiver le client",
                    _query=dict(action="archive"),
                    icon="book",
                )
            )
            del_link = ItemActionLink(
                u"Supprimer",
                "edit_customer",
                css="btn btn-danger",
                confirm=u'Êtes-vous sûr de vouloir supprimer ce client ?',
                path="customer",
                title=u"Supprimer le client",
                _query=dict(action="delete"),
                icon="trash"
            )

            def is_deletable_perm(context, req):
                """
                    Return True if the current item (context) is deletable
                """
                return context.is_deletable()
            del_link.set_special_perm_func(is_deletable_perm)
            btns.append(del_link)
        return btns


class CustomersCsv(CustomersListTools, BaseCsvView):
    """
        Customer csv view
    """
    model = Customer

    @property
    def filename(self):
        return "clients.csv"

    def query(self):
        company = self.request.context
        query = Customer.query().options(undefer_group('edit'))
        return query.filter(Customer.company_id == company.id)


def customer_archive(request):
    """
    Archive the current customer
    """
    customer = request.context
    if not customer.archived:
        customer.archived = True
    else:
        customer.archived = False
        request.session.flash(
            u"Le client '{0}' a été désarchivé".format(customer.name)
        )
    request.dbsession.merge(customer)
    return HTTPFound(request.referer)


def customer_delete(request):
    """
        Delete the current customer
    """
    customer = request.context
    request.dbsession.delete(customer)
    request.session.flash(
        u"Le client '{0}' a bien été supprimé".format(customer.name)
    )
    return HTTPFound(request.referer)


def customer_view(request):
    """
        Return the view of a customer
    """
    populate_actionmenu(request, request.context)
    return dict(
        title=u"Client : {0} {1}".format(
            request.context.get_label(),
            request.context.code
        ),
        customer=request.context
    )


class CustomerAdd(BaseFormView):
    """
    Customer add form
    """
    add_template_vars = ('title', 'customers', )
    title = u"Ajouter un client"
    _schema = None
    buttons = (submit_btn,)
    validation_msg = u"Le client a bien été ajouté"

    @property
    def form_options(self):
        if self.is_company_form():
            formid = 'company'
        else:
            formid = 'individual'

        return (('formid', formid),)

    @property
    def customers(self):
        codes = self.context.get_customer_codes_and_names()
        return codes

    def is_company_form(self):
        """
        :returns: True if it's a company customer add
        :rtype: bool
        """
        return self.request.POST.get('__formid__') == 'company'

    # Schema is here a property since we need to build it dynamically regarding
    # the current request (the same should have been built using the after_bind
    # method ?)
    @property
    def schema(self):
        """
        The getter for our schema property
        """
        if self._schema is None:
            if self.is_company_form():
                self._schema = get_company_customer_schema(self.request)
            else:
                self._schema = get_individual_customer_schema(self.request)
        return self._schema

    @schema.setter
    def schema(self, value):
        """
        A setter for the schema property
        The BaseClass in pyramid_deform gets and sets the schema attribute that
        is here transformed as a property
        """
        self._schema = value

    def before(self, form):
        populate_actionmenu(self.request, self.context)

        if self.is_company_form():
            grid = COMPANY_FORM_GRID
        else:
            grid = INDIVIDUAL_FORM_GRID
        form.widget = GridFormWidget(named_grid=grid)

    def submit_success(self, appstruct):
        if self.context.__name__ == 'company':
            # It's an add form
            model = self.schema.objectify(appstruct)
            model.company = self.context
            if self.is_company_form():
                model.type_ = "company"
            else:
                model.type_ = "individual"
            self.dbsession.add(model)
        else:
            # It's an edition one
            model = self.schema.objectify(appstruct, self.context)
            model = self.dbsession.merge(model)

        self.dbsession.flush()

        self.session.flash(self.validation_msg)
        return HTTPFound(
            self.request.route_path(
                'customer',
                id=model.id
            )
        )


class CustomerEdit(CustomerAdd):
    """
    Customer edition form
    """
    add_template_vars = ('title', 'customers',)
    validation_msg = u"Le client a été modifié avec succès"

    def is_company_form(self):
        """
        :returns: True if it's a company customer add
        :rtype: bool
        """
        return self.context.is_company()

    def appstruct(self):
        """
        Populate the form with the current edited context (customer)
        """
        return self.schema.dictify(self.request.context)

    @reify
    def title(self):
        return u"Modifier le client '{0}'".format(
            self.request.context.name
        )

    @property
    def customers(self):
        company = self.context.company
        codes = company.get_customer_codes_and_names()
        codes.filter(Customer.id != self.context.id)
        logger.debug(codes.all())
        return codes


def populate_actionmenu(request, context):
    """
        populate the actionmenu for the different views (list/add/edit ...)
    """
    company_id = request.context.get_company_id()
    request.actionmenu.add(get_list_view_btn(company_id))
    if context.__name__ == 'customer':
        request.actionmenu.add(get_view_btn(context.id))
        if has_permission('edit_customer', request.context, request):
            request.actionmenu.add(get_edit_btn(context.id))


def get_list_view_btn(id_):
    return ViewLink(
        u"Liste des clients",
        "list_customers",
        path="company_customers",
        id=id_)


def get_view_btn(customer_id):
    return ViewLink(u"Voir", "view_customer", path="customer", id=customer_id)


def get_edit_btn(customer_id):
    return ViewLink(
        u"Modifier",
        "edit_customer",
        path="customer",
        id=customer_id,
        _query=dict(action="edit")
    )


class CustomerImportStep1(CsvFileUploadView):
    title = u"Import des clients, étape 1 : chargement d'un fichier au \
format csv"
    model_types = ("customers",)
    default_model_type = 'customers'

    def get_next_step_route(self, args):
        return self.request.route_path(
            "company_customers_import_step2",
            id=self.context.id,
            _query=args
        )


class CustomerImportStep2(ConfigFieldAssociationView):

    title = u"Import de clients, étape 2 : associer les champs"
    model_types = CustomerImportStep1.model_types

    def get_previous_step_route(self):
        return self.request.route_path(
            "company_customers_import_step1",
            id=self.context.id,
        )

    def get_default_values(self):
        log.info("Asking for default values : %s" % self.context.id)
        return dict(company_id=self.context.id)


def add_routes(config):
    config.add_route(
        'customer',
        '/customers/{id}',
        traverse='/customers/{id}',
    )

    config.add_route(
        'company_customers',
        '/company/{id:\d+}/customers',
        traverse='/companies/{id}',
    )

    config.add_route(
        'customers.csv',
        '/company/{id:\d+}/customers.csv',
        traverse='/companies/{id}'
    )


def includeme(config):
    """
        Add module's views
    """
    add_routes(config)

    for i in range(2):
        index = i + 1
        route_name = 'company_customers_import_step%d' % index
        path = '/company/{id:\d+}/customers/import/%d' % index
        config.add_route(route_name, path, traverse='/companies/{id}')

    config.add_view(
        CustomerAdd,
        route_name='company_customers',
        renderer='customer_edit.mako',
        request_method='POST',
        permission='add_customer',
    )

    config.add_view(
        CustomerAdd,
        route_name='company_customers',
        renderer='customer_edit.mako',
        request_param='action=add',
        permission='add_customer',
    )

    config.add_view(
        CustomersListView,
        route_name='company_customers',
        renderer='customers.mako',
        request_method='GET',
        permission='list_customers',
    )

    config.add_view(
        CustomersCsv,
        route_name='customers.csv',
        request_method='GET',
        permission='list_customers',
    )

    config.add_view(
        CustomerEdit,
        route_name='customer',
        renderer='customer_edit.mako',
        request_param='action=edit',
        permission='edit_customer',
    )

    config.add_view(
        customer_view,
        route_name='customer',
        renderer='customer.mako',
        request_method='GET',
        permission='view_customer',
    )
    config.add_view(
        customer_delete,
        route_name="customer",
        request_param="action=delete",
        permission='edit_customer',
    )
    config.add_view(
        customer_archive,
        route_name="customer",
        request_param="action=archive",
        permission='edit_customer',
    )

    config.add_view(
        CustomerImportStep1,
        route_name="company_customers_import_step1",
        permission="add_customer",
        renderer="base/formpage.mako",
    )

    config.add_view(
        CustomerImportStep2,
        route_name="company_customers_import_step2",
        permission="add_customer",
        renderer="base/formpage.mako",
    )
