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

from jx_base.expressions import DivOp as DivOp_
from jx_elasticsearch.es52.expressions.not_op import NotOp
from jx_elasticsearch.es52.expressions.utils import ES52


class DivOp(DivOp_):
    def to_es(self, schema):
        return NotOp(self.missing(ES52)).partial_eval(ES52).to_es(schema)
