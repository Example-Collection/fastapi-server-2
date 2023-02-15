from fastapi import FastAPI, Request
from app.service import handle_request_from_server_1
from app.otel import tracer
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
import logging

app = FastAPI()


def get_trace_parent_header(request: Request):
    return request.headers.get("traceparent")


@app.get("/items-name-check", status_code=200)
async def server_2_handler(name: str = "", price: float = 0.0, request: Request = None):
    traceparent = get_trace_parent_header(request)
    carrier = {"traceparent": traceparent}
    ctx = TraceContextTextMapPropagator().extract(carrier)
    with tracer.start_as_current_span("server-2-handler", context=ctx):
        logging.warning(f"[SERVER-2] Received item name: {name}, price: {price}")
        return handle_request_from_server_1(item_name=name, item_price=price)
