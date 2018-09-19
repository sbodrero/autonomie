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
    Training model : represents trainings

    >>> from autonomie.models.customer import Customer
    >>> c = Customer()
    >>> c.lastname = u"Dupont"
    >>> c.firstname = u"Jean"
    >>> c.name = u"Compagnie Dupont avec un t"
    >>> c.code = u"DUPT"
    >>> DBSESSION.add(c)

"""
import datetime
import logging

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    ForeignKey,
    Date,
)
from sqlalchemy.orm import (
    deferred,
    relationship,
)
from sqlalchemy.event import listen
from autonomie_base.models.types import (
    PersistentACLMixin,
)
from autonomie_base.models.base import (
    DBBASE,
    default_table_args,
)
from autonomie.models.services.training import TrainingService

log = logging.getLogger(__name__)

TYPE_TRAINING_OPTIONS = (
    ('solo', u"Individuelle",),
    ('group', u"Groupe",),
    ('small_groupe', u"Petit groupe",),
    ('custom', u"Sur mesure groupe",),
    ('remote', u"À distance",),
)


class Training(DBBASE, PersistentACLMixin):
    """
        Training model
        Stores company trainings
        :param title: title of the training item
        :param goals: goals of title of the training item
        :param prerequisites: prerequisites to subscribe to the training session
        :param for_who: target of the training item
        :param duration: duration of the training item
        :param content: content of the training item
        :param teaching_method: teaching_method used in training session
        :param logistics_means: logistics_means implemented for the training session
        :param evaluation: evaluation criteria
        :param place: place if the training session
        :param modality: modality of the training session
        :param type: type of the training
        :param date: date og the training session
        :param price: price of the training session
        :param free_1: free input
        :param free_2: free input
        :param free_3: free input
    """
    __tablename__ = 'customer'
    __table_args__ = default_table_args
    id = Column(
        'id',
        Integer,
        primary_key=True,
        info={
            'colanderalchemy': {
                'exclude': True,
                'title': u"Identifiant Autonomie",
            }
        },
    )

    company_id = Column(
        "company_id",
        Integer,
        ForeignKey('company.id'),
        info={
            'export': {'exclude': True},
            'colanderalchemy': {'exclude': True},
        },
        nullable=False,
    )

    title = deferred(
        Column(
            'title',
            String(255),
            info={
                'colanderalchemy': {
                    'title': u"Intitulé",
                }
            },
            nullable=False,
            default=u''
        ),
        group='edit',
    )

    goals = deferred(
        Column(
            'goals',
            String(10),
            info={
                'colanderalchemy': {
                    'title': u"Objectifs à atteindre à l'issue de la formation",
                }
            },
            default=u'Les objectifs doivent être obligatoirement décrit avec des verbes d\'actions',
        ),
        group='edit',
    )

    prerequisites = deferred(
        Column(
            'prerequisites',
            String(255),
            info={
                'colanderalchemy': {
                    'title': u"Pré-requis obligatoire de la formation",
                }
            },
            default=u''
        ),
        group='edit',
    )

    for_who = deferred(
        Column(
            'for_who',
            String(255),
            info={
                'colanderalchemy': {
                    'title': u"Pour qui?",
                }
            },
            default=u'Public susceptible de participer à cette formation'
        ),
        group='edit',
    )

    duration = deferred(
        Column(
            'duration',
            String(255),
            info={
                'colanderalchemy': {
                    'title': u"Durée en heures et en jour(s) pour la formation",
                }
            },
            nullable=False,
            default=u'Public susceptible de participer à cette formation'
        ),
        group='edit',
    )

    content = deferred(
        Column(
            'duration',
            String(255),
            info={
                'colanderalchemy': {
                    'title': u"Contenu détaillé de la formation",
                }
            },
            default=u'trame par étapes'
        ),
        group='edit',
    )

    teaching_method = deferred(
        Column(
            'teaching_method',
            String(255),
            info={
                'colanderalchemy': {
                    'title': u"Les moyens pédagogiques utilisés",
                }
            },
            default=u''
        ),
        group='edit',
    )

    logistics_means = deferred(
        Column(
            'logistics_means',
            String(255),
            info={
                'colanderalchemy': {
                    'title': u"Moyens logistiques",
                }
            },
            default=u''
        ),
        group='edit',
    )

    evaluation = deferred(
        Column(
            'evaluation',
            String(255),
            info={
                'colanderalchemy': {
                    'title': u"Modalités d'évaluation de la formation",
                }
            },
            default=u'Par exemple : questionnaire d\'évaluation, exercices-tests, questionnaire de satisfaction, '
                    u'évaluation formative,... '
        ),
        group='edit',
    )

    place = deferred(
        Column(
            'place',
            String(255),
            info={
                'colanderalchemy': {
                    'title': u"Lieu de la formation",
                }
            },
            default=u'Villes, zones géographiques où la formation peut être mise en place'
        ),
        group='edit',
    )

    modality = deferred(
        Column(
            'modality',
            String(255),
            info={
                'colanderalchemy': {
                    'title': u"Modalité de formation",
                }
            },
            default=u''
        ),
        group='edit',
    )

    type = deferred(
        Column(
            'type',
            String(255),
            info={
                'colanderalchemy': {
                    'title': u"Modalité de formation",
                }
            },
            default=u''
        ),
        group='edit',
    )

    date = deferred(
        Column(
            'date',
            String(255),
            info={
                'colanderalchemy': {
                    'title': u"Dates de la formation",
                }
            },
            default=u''
        ),
        group='edit',
    )

    price = deferred(
        Column(
            'price',
            String(255),
            info={
                'colanderalchemy': {
                    'title': u"Tarif de la formation",
                }
            },
            default=u''
        ),
        group='edit',
    )

    free_1 = deferred(
        Column(
            'free_1',
            String(255),
            info={
                'colanderalchemy': {
                    'title': u"Champ libre 1",
                }
            },
            default=u''
        ),
        group='edit',
    )

    free_2 = deferred(
        Column(
            'free_2',
            String(255),
            info={
                'colanderalchemy': {
                    'title': u"Champ libre 2",
                }
            },
            default=u''
        ),
        group='edit',
    )

    free_3 = deferred(
        Column(
            'free_3',
            String(255),
            info={
                'colanderalchemy': {
                    'title': u"Champ libre 3",
                }
            },
            default=u''
        ),
        group='edit',
    )


TRAINING_FORM_GRID = (
    (
        ('title', 12),
    ),
    (
        ('goals', 12),
    ),
    (
        ('prerequisites', 12),
    ),
    (
        ('for_who', 12),
    ),
    (
        ('duration', 12),
    ),
    (
        ('content', 12),
    ),
    (
        ('teaching_method', 12),
    ),
    (
        ('logistics_means', 12),
    ),
    (
        ('evaluation', 12),
    ),
    (
        ('place', 12),
    ),
    (
        ('modality', 12),
    ),
    (
        ('date', 4),
        ('type', 4),
        ('price', 4),
    ),
    (
        ('free_1', 12),
    ),
    (
        ('free_2', 12),
    ),
    (
        ('free_3', 12),
    )
)
