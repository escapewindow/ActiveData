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

from jx_elasticsearch.es52.expressions._utils import ES52

from jx_base.expressions import NestedOp as _NestedOp
from mo_future.exports import export


class NestedOp(_NestedOp):
    def to_es(self, schema):
        if self.path.var == ".":
            return ES52[self.select].to_es() | {"query": self.where.to_es(schema), "from": 0}
        else:
            return {
                "nested": {
                    "path": self.path.var,
                    "query": self.where.to_es(schema),
                    "inner_hits": (self.select.to_es() | {"size": 100000})
                    if self.select
                    else None,
                }
            }


export("jx_elasticsearch.es52.expressions._utils", NestedOp)
export("jx_elasticsearch.es52.expressions.eq_op", NestedOp)
