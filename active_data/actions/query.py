# encoding: utf-8
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Contact: Kyle Lahnakoski (kyle@lahnakoski.com)
#
from __future__ import absolute_import, division, unicode_literals

import flask
from flask import Response

import mo_math
from active_data import record_request
from active_data.actions import QUERY_TOO_LARGE, find_container, save_query, send_error, test_mode_wait
from jx_base.container import Container
from jx_python import jx
from mo_files import File
from mo_future import binary_type
from mo_json import json2value, value2json
from mo_logs import Except, Log
from mo_threads.threads import register_thread, MAIN_THREAD
from mo_times.timer import Timer
from pyLibrary.env.flask_wrappers import cors_wrapper

DEBUG = False
BLANK = File("active_data/public/error.html").read().encode('utf8')
QUERY_SIZE_LIMIT = 10*1024*1024


@cors_wrapper
@register_thread
def jx_query(path):
    try:
        with Timer("total duration", verbose=DEBUG) as query_timer:
            preamble_timer = Timer("preamble", silent=True)
            with preamble_timer:
                if flask.request.headers.get("content-length", "") in ["", "0"]:
                    # ASSUME A BROWSER HIT THIS POINT, SEND text/html RESPONSE BACK
                    return Response(
                        BLANK,
                        status=400,
                        headers={
                            "Content-Type": "text/html"
                        }
                    )
                elif int(flask.request.headers["content-length"]) > QUERY_SIZE_LIMIT:
                    Log.error(QUERY_TOO_LARGE)

                request_body = flask.request.get_data().strip()
                text = request_body.decode('utf8')
                data = json2value(text)
                record_request(flask.request, data, None, None)
                if data.meta.testing:
                    test_mode_wait(data, MAIN_THREAD.please_stop)

            find_table_timer = Timer("find container", verbose=DEBUG)
            with find_table_timer:
                frum = find_container(data['from'], after=None)

            translate_timer = Timer("translate", verbose=DEBUG)
            with translate_timer:
                result = jx.run(data, container=frum)

                if isinstance(result, Container):  # TODO: REMOVE THIS CHECK, jx SHOULD ALWAYS RETURN Containers
                    result = result.format(data.format)

            save_timer = Timer("save", verbose=DEBUG)
            with save_timer:
                if data.meta.save:
                    try:
                        result.meta.saved_as = save_query.query_finder.save(data)
                    except Exception as e:
                        Log.warning("Unexpected save problem", cause=e)

            result.meta.timing.find_table = mo_math.round(find_table_timer.duration.seconds, digits=4)
            result.meta.timing.preamble = mo_math.round(preamble_timer.duration.seconds, digits=4)
            result.meta.timing.translate = mo_math.round(translate_timer.duration.seconds, digits=4)
            result.meta.timing.save = mo_math.round(save_timer.duration.seconds, digits=4)
            result.meta.timing.total = "{{TOTAL_TIME}}"  # TIMING PLACEHOLDER

            with Timer("jsonification", verbose=DEBUG) as json_timer:
                response_data = value2json(result).encode('utf8')

        with Timer("post timer", verbose=DEBUG):
            # IMPORTANT: WE WANT TO TIME OF THE JSON SERIALIZATION, AND HAVE IT IN THE JSON ITSELF.
            # WE CHEAT BY DOING A (HOPEFULLY FAST) STRING REPLACEMENT AT THE VERY END
            timing_replacement = (
                b'"total":' + binary_type(mo_math.round(query_timer.duration.seconds, digits=4)) +
                b', "jsonification":' + binary_type(mo_math.round(json_timer.duration.seconds, digits=4))
            )
            response_data = response_data.replace(b'"total":"{{TOTAL_TIME}}"', timing_replacement)
            Log.note("Response is {{num}} bytes in {{duration}}", num=len(response_data), duration=query_timer.duration)

            return Response(
                response_data,
                status=200,
                headers={
                    "Content-Type": result.meta.content_type
                }
            )
    except Exception as e:
        e = Except.wrap(e)
        return send_error(query_timer, request_body, e)


