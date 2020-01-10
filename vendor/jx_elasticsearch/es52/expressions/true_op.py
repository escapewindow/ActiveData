# encoding: utf-8
#
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http:# mozilla.org/MPL/2.0/.
#
# Contact: Kyle Lahnakoski (kyle@lahnakoski.com)
#

from __future__ import absolute_import, division, unicode_literals

from jx_base.expressions import TrueOp as TrueOp_
from mo_dots import wrap


class TrueOp(TrueOp_):

    def to_esfilter(self, schema):
        return MATCH_ALL


MATCH_ALL = wrap({"match_all": {}})
