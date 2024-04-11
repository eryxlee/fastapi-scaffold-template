# -*- coding: utf-8 -*-

import json
import time

from fastapi import Request, Response

from starlette.types import ASGIApp, Receive, Scope, Send, Message
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.datastructures import MutableHeaders


# https://github.com/tiangolo/fastapi/discussions/6223
class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        begin = time.time()
        response = await call_next(request)
        response_time = time.time() - begin
        response.headers["X-Response-Time"] = str(response_time)
        return response


# https://github.com/tiangolo/fastapi/issues/4766
class MetaDataAdderMiddleware:
    application_generic_urls = ['/openapi.json', '/docs', '/docs/oauth2-redirect', '/redoc']

    def __init__(
            self,
            app: ASGIApp
    ) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http" and not any([scope["path"].startswith(endpoint) for endpoint in MetaDataAdderMiddleware.application_generic_urls]):
            responder = MetaDataAdderMiddlewareResponder(self.app) #, self.standard_meta_data, self.additional_custom_information)
            await responder(scope, receive, send)
            return
        await self.app(scope, receive, send)


class MetaDataAdderMiddlewareResponder:

    def __init__(
            self,
            app: ASGIApp,
    ) -> None:
        """
        """
        self.app = app
        self.initial_message: Message = {}

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        self.send = send
        await self.app(scope, receive, self.send_with_meta_response)

    async def send_with_meta_response(self, message: Message):

        message_type = message["type"]
        if message_type == "http.response.start":
            # Don't send the initial message until we've determined how to
            # modify the outgoing headers correctly.
            self.initial_message = message

        elif message_type == "http.response.body":
            if message.get("more_body"):
                response_body = json.loads(message["body"].decode())

                data = {}
                if not isinstance(response_body, dict) or response_body.get("status") == None:
                    data["status"] = True
                    data["code"] = 0
                    data["message"] = "成功"
                    data["data"] = response_body
                else:
                    data = response_body

                data_to_be_sent_to_user = json.dumps(data, default=str).encode("utf-8")

                headers = MutableHeaders(raw=self.initial_message["headers"])
                headers["Content-Length"] = str(len(data_to_be_sent_to_user))
                message["body"] = data_to_be_sent_to_user

                await self.send(self.initial_message)
            await self.send(message)
