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

from jx_base.expressions import BasicEqOp as BasicEqOp_, is_literal
from jx_elasticsearch.es52.painless._utils import Painless
from jx_elasticsearch.es52.painless.and_op import AndOp
from jx_elasticsearch.es52.painless.es_script import EsScript
from mo_json import BOOLEAN


class BasicEqOp(BasicEqOp_):
    def to_es_script(self, schema, not_null=False, boolean=False, many=True):
        simple_rhs = Painless[self.rhs].partial_eval()
        lhs = Painless[self.lhs].partial_eval().to_es_script(schema)
        rhs = simple_rhs.to_es_script(schema)

        if lhs.many:
            if rhs.many:
                return AndOp(
                    [
                        EsScript(
                            type=BOOLEAN,
                            expr="(" + lhs.expr + ").size()==(" + rhs.expr + ").size()",
                            frum=self,
                            schema=schema,
                        ),
                        EsScript(
                            type=BOOLEAN,
                            expr="(" + rhs.expr + ").containsAll(" + lhs.expr + ")",
                            frum=self,
                            schema=schema,
                        ),
                    ]
                ).to_es_script(schema)
            else:
                if lhs.type == BOOLEAN:
                    if is_literal(simple_rhs) and simple_rhs.value in ("F", False):
                        return EsScript(
                            type=BOOLEAN, expr="!" + lhs.expr, frum=self, schema=schema
                        )
                    elif is_literal(simple_rhs) and simple_rhs.value in ("T", True):
                        return EsScript(
                            type=BOOLEAN, expr=lhs.expr, frum=self, schema=schema
                        )
                    else:
                        return EsScript(
                            type=BOOLEAN,
                            expr="(" + lhs.expr + ")==(" + rhs.expr + ")",
                            frum=self,
                            schema=schema,
                        )
                else:
                    return EsScript(
                        type=BOOLEAN,
                        expr="(" + lhs.expr + ").contains(" + rhs.expr + ")",
                        frum=self,
                        schema=schema,
                    )
        elif rhs.many:
            return EsScript(
                type=BOOLEAN,
                expr="(" + rhs.expr + ").contains(" + lhs.expr + ")",
                frum=self,
                schema=schema,
            )
        else:
            if lhs.type == BOOLEAN:
                if is_literal(simple_rhs) and simple_rhs.value in ("F", False):
                    return EsScript(
                        type=BOOLEAN, expr="!" + lhs.expr, frum=self, schema=schema
                    )
                elif is_literal(simple_rhs) and simple_rhs.value in ("T", True):
                    return EsScript(
                        type=BOOLEAN, expr=lhs.expr, frum=self, schema=schema
                    )
                else:
                    return EsScript(
                        type=BOOLEAN,
                        expr="(" + lhs.expr + ")==(" + rhs.expr + ")",
                        frum=self,
                        schema=schema,
                    )
            else:
                return EsScript(
                    type=BOOLEAN,
                    expr="(" + lhs.expr + ")==(" + rhs.expr + ")",
                    frum=self,
                    schema=schema,
                )