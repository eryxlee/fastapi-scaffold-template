# -*- coding: utf-8 -*-

import json
import time
from datetime import datetime, timedelta
from typing import ClassVar

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.datastructures import MutableHeaders
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp, Message, Receive, Scope, Send


# https://github.com/tiangolo/fastapi/discussions/6223
class TimingMiddleware(BaseHTTPMiddleware):
    """API计时中间件."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:  # noqa: D102
        begin = time.time()
        response = await call_next(request)
        response_time = time.time() - begin
        response.headers["X-Response-Time"] = str(response_time)
        return response


# https://github.com/tiangolo/fastapi/issues/4766
class MetaDataAdderMiddleware:
    """将API输出结果进行统一格式化的中间件."""

    application_generic_urls: ClassVar[list[str]] = [
        "/openapi.json",
        "/docs",
        "/docs/oauth2-redirect",
        "/redoc",
        "/ws",
        "/static",
    ]

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:  # noqa: D102
        if scope["type"] == "http" and not any(
            scope["path"].startswith(endpoint)
            for endpoint in MetaDataAdderMiddleware.application_generic_urls
        ):
            responder = MetaDataAdderMiddlewareResponder(
                self.app,
            )  # , self.standard_meta_data, self.additional_custom_information)
            await responder(scope, receive, send)
            return
        await self.app(scope, receive, send)


class MetaDataAdderMiddlewareResponder:
    """将API输出结果进行统一格式化."""

    def __init__(
        self,
        app: ASGIApp,
    ) -> None:
        self.app = app
        self.initial_message: Message = {}

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:  # noqa: D102
        self.send = send
        await self.app(scope, receive, self.send_with_meta_response)

    async def send_with_meta_response(self, message: Message) -> None:
        """修改response信息."""
        message_type = message["type"]
        if message_type == "http.response.start":
            # Don't send the initial message until we've determined how to
            # modify the outgoing headers correctly.
            self.initial_message = message

        elif message_type == "http.response.body":
            if message.get("more_body"):
                response_body = json.loads(message["body"].decode())

                data = {}
                if not isinstance(response_body, dict) or response_body.get("status") is None:
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


# immediately after imports
# https://semaphoreci.com/blog/custom-middleware-fastapi
class RateLimitingMiddleware(BaseHTTPMiddleware):
    """限流中间件."""

    # Rate limiting configurations
    RATE_LIMIT_DURATION = timedelta(minutes=1)
    RATE_LIMIT_REQUESTS = 3

    def __init__(self, app) -> None:  # noqa: ANN001
        super().__init__(app)
        # Dictionary to store request counts for each IP
        self.request_counts = {}

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):  # noqa: D102, ANN201
        # Get the client's IP address
        client_ip = request.client.host

        # Check if IP is already present in request_counts
        request_count, last_request = self.request_counts.get(client_ip, (0, datetime.min))

        # Calculate the time elapsed since the last request
        elapsed_time = datetime.now() - last_request  # noqa: DTZ005

        if elapsed_time > self.RATE_LIMIT_DURATION:
            # If the elapsed time is greater than the rate limit duration, reset the count
            request_count = 1
        else:
            if request_count >= self.RATE_LIMIT_REQUESTS:
                # If the request count exceeds the rate limit, return a JSON response
                # with an error message
                return JSONResponse(
                    status_code=429,
                    content={"message": "Rate limit exceeded. Please try again later."},
                )
            request_count += 1

        # Update the request count and last request timestamp for the IP
        self.request_counts[client_ip] = (request_count, datetime.now())  # noqa: DTZ005

        # Proceed with the request
        return await call_next(request)
