# -*- coding: utf-8 -*-
# * Authors:
#       * TJEBBES Gaston <g.t@majerti.fr>
#       * Arezki Feth <f.a@majerti.fr>;
#       * Miotte Julien <j.m@majerti.fr>;
"""
Status change related views

Common to :
    Estimation
    Invoice
    CancelInvoice
    ExpenseSheet
"""
import logging
import colander

from pyramid.httpexceptions import (
    HTTPNotFound,
)
from autonomie.events.status_changed import StatusChanged

from autonomie.exception import (
    Forbidden,
    BadRequest,
)
from autonomie.utils.rest import RestError
from autonomie.views import BaseView

logger = logging.getLogger(__name__)


class StatusView(BaseView):
    """
    View for status handling

    See the call method for the workflow and the params
    passed to the methods
    """
    valid_msg = u"Le statut a bien été modifié"

    def redirect(self):
        """
        Redirect function to be used after status processing
        """
        return HTTPNotFound()

    def _get_status(self, params):
        """
        Get the status that has been asked for
        """
        return params['submit']

    def check_allowed(self, status, params):
        """
        Check that the status change is allowed

        :param str status: The new status that should be affected
        :param dict params: Params currently passed
        :rtype: bool
        :raises: Forbidden exception if the action isn't allowed
        """
        return True

    def pre_status_process(self, status, params):
        """
        Launch pre process functions
        """
        self.check_allowed(status, params)

        if hasattr(self, "pre_%s_process" % status):
            func = getattr(self, "pre_%s_process" % status)
            return func(status, params)
        return params

    def status_process(self, status, params):
        """
        Definitively Set the status of the element

        :param str status: The new status that should be affected
        :param dict params: The params that were transmitted by the pre_process
        function
        """
        return self.context.set_status(
            status,
            self.request,
            **params
        )

    def post_status_process(self, status, params):
        """
        Launch post status process functions

        :param str status: The new status that should be affected
        :param dict params: The params that were transmitted by the associated
        State's callback
        """
        if hasattr(self, "post_%s_process" % status):
            func = getattr(self, "post_%s_process" % status)
            func(status, params)

    def set_status(self, status, params):
        """
        Set the new status to the given item
        handle pre_status and post_status processing

        :param str status: The new status that should be affected
        :param str params: The params retrieved from the request
        """
        pre_params = params
        params = self.pre_status_process(status, pre_params)
        post_params = self.status_process(status, params)
        self.post_status_process(status, post_params)
        return True

    def notify(self, status):
        """
        Notify the change to the registry

        :param str status: The new status that was affected
        """
        self.request.registry.notify(
            StatusChanged(
                self.request,
                self.context,
                status,
            )
        )

    def __call__(self):
        """
            Main entry for this view object
        """
        logger.debug("# Entering the status view")
        if self.request.is_xhr:
            params = self.request.json_body
        else:
            params = self.request.POST

        if "submit" in params:
            try:
                status = self._get_status(params)
                logger.debug(u"New status : %s " % status)
                self.set_status(status, params)
                self.context = self.request.dbsession.merge(self.context)
                self.notify(status)
                if not self.request.is_xhr:
                    self.session.flash(self.valid_msg)

                logger.debug(u" + The status has been set to {0}".format(
                    status))

            except Forbidden, e:
                logger.exception(u" !! Unauthorized action by : {0}".format(
                    self.request.user.login
                ))
                if self.request.is_xhr:
                    raise RestError(e.message, code=403)
                else:
                    self.session.pop_flash("")
                    self.session.flash(e.message, queue='error')

            except (colander.Invalid, BadRequest), e:
                logger.exception("Invalid datas")
                if self.request.is_xhr:
                    raise RestError(e.asdict(translate=colander._))
                else:
                    for message in e.messages():
                        self.session.flash(message, 'error')

            return self.redirect()

        if self.request.is_xhr:
            raise RestError(
                [
                    u'Il manque des arguments pour changer le statut '
                    u'du document'
                ])
        else:
            self.session.flash(
                u"Il manque des arguments pour changer le statut du document",
                "error"
            )
            return self.redirect()
