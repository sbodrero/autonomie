# -*- coding: utf-8 -*-
# * Copyright (C) 2012-2015 Croissance Commune
# * Authors:
#       * Arezki Feth <f.a@majerti.fr>;
#       * Miotte Julien <j.m@majerti.fr>;
#       * TJEBBES Gaston <g.t@majerti.fr>;
#       * BODRERO Sébastien <bodrero.sebastien@gmail.com>;
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
"""
    Training catalog views
"""
import logging
import colander

from sqlalchemy import (
    or_,
    not_,
)
from sqlalchemy.orm import undefer_group

from deform import Form

from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPFound

from autonomie.models.training.training import (
    Training,
    TRAINING_FORM_GRID,
)
from autonomie.utils.widgets import (
    ViewLink,
)
from autonomie.utils.rest import add_rest_views
from autonomie.forms.training.training import (
    get_list_schema,
    get_training_schema,
    get_add_edit_training_schema,
)
from deform_extensions import GridFormWidget
from autonomie.views import (
    BaseListView,
    BaseCsvView,
    BaseFormView,
    submit_btn,
    cancel_btn,
    BaseRestView,
)

logger = log = logging.getLogger(__name__)

#def get_company_customer_form(request, counter=None): NOT IMLEMENTED YET
#def get_individual_customer_form(request, counter=None): NOT IMLEMENTED YET


class CustomersListTools(object):
    """
    Customer list tools
    """
    title = u"Liste des clients"
    schema = get_list_schema()
    sort_columns = {
        'Titre': Training.titre,
        "Type": Training.type,
    }
    default_sort = "Titre"
    default_direction = "desc"

    def query(self):
        company = self.request.context
        return Training.query().filter_by(company_id=company.id)

    def filter_on_title(self, records, appstruct):
        """
        Filter the records by training title
        """
        search = appstruct.get('search')
        if search:
            records = records.filter(Training.title.like("%" + search + "%"))
        return records


class CustomersListView(CustomersListTools, BaseListView):
    """
    Customer listing view
    """
    add_template_vars = (
        'stream_actions',
        'title',
        'forms',
    )
    grid = (
        (
            ('search', 3),
        ),
        (
            ('items_per_page', 2),
        ),
    )

    @property
    def forms(self):
        res = []
        form_title = u"Fiche formation"
        form = get_training_schema(self.request)
        res.append((form_title, form))
        return res

    def stream_actions(self, customer):
        """
            Return action buttons with permission handling
        """
        yield (
            self.request.route_path("customer", id=customer.id),
            u"Voir",
            u"Voir/Modifier la fiche formation",
            u"pencil",
            {}
        )

        if self.request.has_permission('delete_customer', customer):
            yield (
                self.request.route_path(
                    "customer",
                    id=customer.id,
                    _query=dict(action="archive"),
                ),
                u"Supprimer",
                u"Supprimer définitivement ce client",
                "trash",
                {
                    "onclick": (
                        u"return confirm('Êtes-vous sûr de "
                        "vouloir supprimer ce client ?')"
                    )
                }

            )