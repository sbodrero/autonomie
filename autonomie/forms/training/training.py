# -*- coding: utf-8 -*-
# * Copyright (C) 2012-2013 Croissance Commune
# * Authors:
#       * Arezki Feth <f.a@majerti.fr>;
#       * Miotte Julien <j.m@majerti.fr>;
#       * Pettier Gabriel;
#       * TJEBBES Gaston <g.t@majerti.fr>
#       * BODRERO Sébastien <bodrero.sebastien@gmail.com>
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
Training handling forms schemas and related widgets
"""

import colander
import deform
from colanderalchemy import SQLAlchemySchemaNode

from autonomie.models.training.training import Training
from autonomie.compute.math_utils import convert_to_int
from autonomie import forms
from autonomie.forms.lists import BaseListsSchema

MODALITIES_OPTIONS = (
    ('', u'Non renseigné', ),
    ('intra', u'Intra-entreprise',),
    ('inter', u'Inter-entreprise',),
)

TYPE_TRAINING_OPTIONS =(
    ('', u'Non renseigné', ),
    ('solo', u'Individuelle',),
    ('group', u'Groupe',),
    ('small_group', u'Petit groupe (moins de 5 personnes) ',),
    ('custom', u'Sur mesure',),
    ('remote', u'À distance',),
)


def get_list_schema():
    """
    Return the schema for the training search list
    """
    schema = BaseListsSchema().clone()
    schema['search'].description = u"Nom de la formation"
    return schema


def _customize_schema(schema):
    """
    Add common widgets configuration for the training forms schema

    :param obj schema: The Training form schema
    """
    schema['goals'].widget = deform.widget.TextAreaWidget(
        cols=25,
        row=1,
    )
    schema['prerequisites'].widget = deform.widget.TextAreaWidget(
        cols=25,
        row=1,
    )
    schema['for_who'].widget = deform.widget.TextAreaWidget(
        cols=25,
        row=1,
    )
    schema['content'].widget = deform.widget.TextAreaWidget(
        cols=25,
        row=1,
    )
    schema['teaching_method'].widget = deform.widget.TextAreaWidget(
        cols=25,
        row=1,
    )
    schema['logistics_means'].widget = deform.widget.TextAreaWidget(
        cols=25,
        row=1,
    )
    schema['evaluation'].widget = deform.widget.TextAreaWidget(
        cols=25,
        row=1,
    )
    schema['place'].widget = deform.widget.TextAreaWidget(
        cols=25,
        row=1,
    )
    schema['modality'].widget = forms.get_deferred_model_select(
        MODALITIES_OPTIONS[1:],
        multi=True,
        mandatory=True,
    )
    schema['type'].widget = forms.get_deferred_model_select(
        TYPE_TRAINING_OPTIONS[1:],
        multi=True,
        mandatory=True,
    )
    schema['free_1'].widget = deform.widget.TextAreaWidget(
        cols=25,
        row=1,
    )
    schema['free_2'].widget = deform.widget.TextAreaWidget(
        cols=25,
        row=1,
    )
    schema['free_3'].widget = deform.widget.TextAreaWidget(
        cols=25,
        row=1,
    )
    return schema


def get_training_schema():
    """
    return the schema for user add/edit regarding the current user's role
    """
    schema = SQLAlchemySchemaNode(Training)
    schema = _customize_schema(schema)
    return schema


def get_add_edit_training_schema(excludes=None, includes=None):
    """
    Build a generic add edit training schema
    """
    if includes is not None:
        excludes = None
    elif excludes is None:
        excludes = ('company_id',)

    schema = SQLAlchemySchemaNode(
        Training,
        excludes=excludes,
        includes=includes
    )


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
        Filter the records by customer name or contact lastname
        """
        search = appstruct.get('search')
        if search:
            records = records.filter(Training.title.like("%" + search + "%"))
        return records
