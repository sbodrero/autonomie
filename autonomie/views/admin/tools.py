# -*- coding: utf-8 -*-
# * Copyright (C) 2012-2015 Croissance Commune
# * Authors:
#       * Arezki Feth <f.a@majerti.fr>;
#       * Miotte Julien <j.m@majerti.fr>;
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
import logging
import os

from pyramid.httpexceptions import HTTPFound
from sqlalchemy.orm.query import Query

from autonomie.models.config import Config
from autonomie.forms import flatten_appstruct
from autonomie.forms.admin import (
    get_sequence_model_admin,
    build_config_appstruct,
)
from autonomie_base.utils.ascii import (
    camel_case_to_name,
)
from autonomie.views import (
    BaseFormView,
    BaseView,
    BaseAddView,
    BaseEditView,
    DisableView,
    DeleteView,
    TreeMixinMetaClass,
)
logger = logging.getLogger(__name__)


class AdminTreeMixin:
    """
    Mixin adding tree structure to admin views


    class MyAdminView(BaseView, AdminTreeMixin):
        route_name = "/adminumyadminview"

    config.add_admin_view(MyAdminView, parent=ParentViewClass)

    route_name

        current route_name

    children

        class attribute in list format registering all view children

    parent

        weakref to the parent view
    """
    __metaclass__ = TreeMixinMetaClass
    route_name = None
    parent_view = None
    description = ""
    title = ""

    @classmethod
    def get_url(cls, request):
        if getattr(cls, 'url', None) is not None:
            return cls(request).url
        elif getattr(cls, 'route_name', None) is not None:
            if isinstance(cls.route_name, property):
                return cls(request).route_name
            else:
                return request.route_path(cls.route_name)
        else:
            return ""

    @classmethod
    def get_title(cls, request):
        if isinstance(cls.title, property):
            return cls(request).title
        else:
            return cls.title

    @classmethod
    def get_breadcrumb(cls, request, local=False):
        """
        Collect breadcrumb entries

        :param obj request: The Pyramid request
        :param bool local: Is the breadcrumb for local use
        :returns: A generator of 2-uples (title, url)
        """
        if cls.parent_view is not None:
            for title, url in cls.parent_view.get_breadcrumb(request):
                yield title, url

        if not local:
            yield cls.get_title(request), cls.get_url(request)
        else:
            yield cls.get_title(request), ""

    @classmethod
    def get_back_url(cls, request):
        logger.debug(u"Asking for the parent url : {0}".format(cls))
        if cls.parent_view is not None:
            return cls.parent_view.get_url(request)
        else:
            return None

    @classmethod
    def get_navigation(cls, request):
        result = []
        for child in cls.children:
            if getattr(child, 'route_name', None) is not None:
                result.append(
                    dict(
                        label=child.title,
                        route_name=child.route_name,
                        title=child.description,
                    )
                )
            else:
                url = child.get_url(request)
                if url:
                    result.append(
                        dict(
                            label=child.title,
                            title=child.description,
                            url=url,
                        )
                    )
        return result

    @property
    def navigation(self):
        return self.get_navigation(self.request)

    @property
    def breadcrumb(self):
        return self.get_breadcrumb(self.request, local=True)

    @property
    def back_link(self):
        return self.get_back_url(self.request)

    @classmethod
    def add_child(cls, view_class):
        cls.children.append(view_class)
        view_class.parent_view = cls


class BaseAdminFormView(BaseFormView, AdminTreeMixin):
    add_template_vars = ('message', 'breadcrumb', 'navigation', 'back_link')
    redirect_route_name = "admin_index"
    info_message = ""

    @property
    def message(self):
        return self.info_message


class BaseConfigView(BaseAdminFormView):
    """
    Base view for configuring elements in the config key-value table
    """
    keys = ()
    validation_msg = u""
    schema = None
    redirect_route_name = None

    def before(self, form):
        appstruct = build_config_appstruct(self.request, self.keys)
        form.set_appstruct(appstruct)

    def submit_success(self, appstruct):
        """
        Handle successfull configuration
        """
        appstruct = flatten_appstruct(appstruct)
        for key in self.keys:

            value = appstruct.pop(key, None)
            if value is None:
                continue

            cfg_obj = Config.get(key) or Config(name=key)
            cfg_obj.value = value

            self.dbsession.add(cfg_obj)

            logger.debug(u" # Setting configuration")
            logger.debug(u"{0} : {1}".format(key, value))

        self.request.session.flash(self.validation_msg)
        back_link = self.back_link
        if back_link is not None:
            result = HTTPFound(self.back_link)
        else:
            logger.error(u"This view %s is not able to provide a back_link "
                         u"after validation" % self)
            result = None
        return result


class AdminOption(BaseAdminFormView):
    """
    Main view for option configuration
    It allows to configure a sequence of models

        factory

            The model we are manipulating.

        disable

            True : If the model has an "active" column, it can be used to
            enable/disable elements  (default)
            False : Elements are deleted

        validation_msg

            The message shown to the end user on successfull validation

        redirect_route_name

            The route we're redirecting to after successfull validation

        js_resources

            specific fanstatic javascript resources we want to add to the page

        widget_options

            Options passed to the sequence widget used here

        customize_schema

            Method taking schema as parameter that allows to customize the given
            schema by, for example, adding a global validator
    """
    title = u""
    validation_msg = u""
    factory = None
    disable = True
    js_resources = []
    widget_options = {}

    def __init__(self, *args, **kwargs):
        BaseAdminFormView.__init__(self, *args, **kwargs)
        self._schema = None

    def customize_schema(self, schema):
        return schema

    @property
    def schema(self):
        if self._schema is None:
            self._schema = get_sequence_model_admin(
                self.factory,
                "",
                widget_options=self.widget_options,
            )
            self._schema.title = self.title
            self.customize_schema(self._schema)
        return self._schema

    @schema.setter
    def schema(self, value):
        self._schema = value

    @property
    def message(self):
        """
        Return an optionnal message to help to configure datas
        """
        help_msg = getattr(self, 'help_msg', None)
        if help_msg is None:
            calchemy_dict = getattr(
                self.factory, '__colanderalchemy_config__', {}
            )
            help_msg = calchemy_dict.get('help_msg', '')
        return help_msg

    def before(self, form):
        """
        Populate the form with existing elements
        """
        if not hasattr(self.js_resources, '__iter__'):
            self.js_resources = (self.js_resources,)

        for js_resource in self.js_resources:
            js_resource.need()

        form.set_appstruct(self.get_appstruct())

    def query_items(self):
        """
        the query used to retrieve items in the database
        :results: a list of element we want to display as default in the form
        :rtype: list
        """
        return self.factory.query().all()

    def get_appstruct(self):
        """
        Return the appstruct used to generate default form entries
        :results: A data structure (list or dict) representing the existing
        datas
        :rtype: dict or list
        """
        return self.schema.dictify(self.query_items())

    def _get_edited_elements(self, appstruct):
        """
        Return the elements that are edited (already have an id)
        """
        return dict(
            (data['id'], data)
            for data in appstruct.get('datas', {})
            if 'id' in data
        )

    def _disable_or_remove_elements(self, appstruct):
        """
        Disable or delete existing elements that are no more in the results

        :param appstruct: The validated form datas
        """
        edited = self._get_edited_elements(appstruct)

        for element in self.query_items():
            if element.id not in edited.keys():
                if self.disable:
                    element.active = False
                    self.dbsession.merge(element)
                else:
                    self.dbsession.delete(element)

    def _add_or_edit(self, index, datas):
        """
        Add or edit an element of the given factory
        """
        node_schema = self.schema.children[0].children[0]
        element = node_schema.objectify(datas)
        element.order = index
        if element.id is not None:
            element = self.dbsession.merge(element)
        else:
            self.dbsession.add(element)
        return element

    def submit_success(self, appstruct):
        """
        Handle successfull submission
        """
        self._disable_or_remove_elements(appstruct)

        for index, datas in enumerate(appstruct.get('datas', [])):
            self._add_or_edit(index, datas)

        self.request.session.flash(self.validation_msg)
        return HTTPFound(self.request.route_path(self.redirect_route_name))


def get_model_admin_view(model, js_requirements=[], r_path="admin_userdatas"):
    """
    Return a view object and a route_name for administrating a sequence of
    models instances (like options)
    """
    infos = model.__colanderalchemy_config__
    view_title = infos.get('title', u'Titre inconnu')

    subroute_name = camel_case_to_name(model.__name__)
    view_route_name = os.path.join(r_path, subroute_name)

    class MyView(AdminOption):
        title = view_title
        description = infos.get('description', u'')
        route_name = view_route_name

        validation_msg = infos.get('validation_msg', u'')
        factory = model
        redirect_route_name = r_path
        js_resources = js_requirements

    return MyView


def make_enter_point_view(parent_route, views_to_link_to, title=u""):
    """
    Builds a view with links to the views passed as argument

        views_to_link_to

            list of 2-uples (view_obj, route_name) we'd like to link to

        parent_route

            route of the parent page
    """
    def myview(request):
        """
        The dinamycally built view
        """
        menus = []
        menus.append(dict(label=u"Retour", route_name=parent_route,
                          icon="fa fa-step-backward"))
        for view, route_name, tmpl in views_to_link_to:
            menus.append(dict(label=view.title, route_name=route_name,))
        return dict(title=title, menus=menus)
    return myview


class AdminCrudListView(BaseView, AdminTreeMixin):
    title = "Missing title"
    columns = []

    def _get_item_url(self, item, action=None):
        """
        Build an url to an item's action

        Usefull from inside the stream_actions method

        :param obj item: An instance with an id
        :param str action: The name of the action
        (duplicate/disable/edit...)

        :returns: An url
        :rtype: str
        """
        if not hasattr(self, 'item_route_name'):
            raise Exception(u"Un attribut item_route_name doit être défini")

        query = dict(self.request.GET)
        if action is not None:
            query['action'] = action

        return self.request.route_path(
            self.item_route_name,
            id=item.id,
            _query=query,
            **self.request.matchdict
        )

    def get_actions(self, items):
        """
        Return additionnal list related actions (other than add)

        :returns: An iterator providing autonomie.utils.widgets.Link instances

        :rtype: iterator
        """
        return []

    def get_addurl(self):
        """
        Build the url to the add form

        :returns: An url string
        :rtype: str
        """
        return self.request.route_path(
            self.route_name, _query={'action': 'add'}
        )

    def stream_columns(self, item):
        """
        Each item is a row in a table, here we stream the different columns for
        the given row except the actions column

        :param obj item: A SQLAlchemy model instance
        :returns: an iterator (can be used in a for loop) of column contents
        :rtype: iterator
        """
        raise NotImplemented()

    def load_items(self):
        """
        Perform the listing query and return the result

        :returns: List of SQLAlchemy object to present in the UI
        :rtype: obj
        """
        raise NotImplemented()

    def more_template_vars(self, result):
        """
        Add template vars to the result

        :param dict result: The currently built dict that will be returned as
        templating context
        :returns: The templating context for the given view
        :rtype: dict
        """
        return result

    def __call__(self):
        items = self.load_items()
        # We ensure we return a list
        if isinstance(items, Query):
            items = items.all()

        result = dict(
            breadcrumb=self.breadcrumb,
            back_link=self.back_link,
            title=self.title,
            addurl=self.get_addurl(),
            columns=self.columns,
            items=items,
            stream_columns=self.stream_columns,
            stream_actions=self.stream_actions,
        )
        result['actions'] = self.get_actions(items)

        if hasattr(self, "more_template_vars"):
            self.more_template_vars(result)

        return result


class BaseAdminIndexView(BaseView, AdminTreeMixin):
    """
    Base admin view

    Used to manage Admin view hierachies


    add_template_vars

        property or attribute names to add to the templating context dict

    """
    add_template_vars = ()

    def more_template_vars(self, result):
        for propname in self.add_template_vars:
            result.update(getattr(self, propname))
        return result

    def __call__(self):
        result = dict(
            title=self.title,
            navigation=self.navigation,
            breadcrumb=self.breadcrumb,
            back_link=self.back_link,
        )
        result = self.more_template_vars(result)
        return result


class BaseAdminAddView(BaseAddView, AdminTreeMixin):
    add_template_vars = ('help_msg', 'breadcrumb', 'back_link')

    def redirect(self, model=None):
        back_link = self.back_link
        if back_link is not None:
            result = HTTPFound(self.back_link)
        else:
            logger.error(u"This view %s is not able to provide a back_link "
                         u"after validation" % self)
            result = None
        return result


class BaseAdminEditView(BaseEditView, AdminTreeMixin):
    add_template_vars = ('help_msg', 'breadcrumb', 'back_link')

    def redirect(self):
        back_link = self.back_link
        if back_link is not None:
            result = HTTPFound(self.back_link)
        else:
            logger.error(u"This view %s is not able to provide a back_link "
                         u"after validation" % self)
            result = None
        return result


class BaseAdminDisableView(DisableView, AdminTreeMixin):
    def redirect(self):
        back_link = self.back_link
        if back_link is not None:
            result = HTTPFound(self.back_link)
        else:
            logger.error(u"This view %s is not able to provide a back_link "
                         u"after validation" % self)
            result = None
        return result


class BaseAdminDeleteView(DeleteView, AdminTreeMixin):
    def redirect(self):
        back_link = self.back_link
        if back_link is not None:
            result = HTTPFound(self.back_link)
        else:
            logger.error(u"This view %s is not able to provide a back_link "
                         u"after validation" % self)
            result = None
        return result
