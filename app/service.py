import requests
import time
import logging
from app.otel import tracer
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator


def call_server_3(item_price: float):
    with tracer.start_as_current_span("server-2-call-server-3"):
        carrier = {}
        TraceContextTextMapPropagator().inject(carrier)
        header = {"traceparent": carrier["traceparent"]}
        response = requests.get(
            f"http://fastapi-server-3-svc.sangwoo-otel-poc.svc.cluster.local:8000/items-price-check?price={item_price}",
            headers=header)
        # Pretend it is taking time to process, sleep for 1 second.
        time.sleep(1)
        logging.warning(f"[SERVER-2] Received response from server 3: {response}")
        return response


def handle_request_from_server_1(item_name: str, item_price: float):
    with tracer.start_as_current_span("server-2-handle-request-from-server-1"):
        logging.info(f"[SERVER-2] Checking if item_name starts with uppercase letter.")
        if item_name[0].islower():
            logging.warning(f"[SERVER-2] Item name did not start with uppercase letter. (item_name: {item_name})")
            raise HTTPException(status_code=400, detail="Item name should start with uppercase letter.")

        else:
            logging.warning(f"[SERVER-2] Item name started with uppercase letter. Calling server 3. (item_name: {item_name})")
            result = call_server_3(item_price)
            if result.status_code != 200:
                logging.warning(f"[SERVER-2] Server 3 returned non-200 status code. (status_code: {result.status_code})")
                raise HTTPException(status_code=result.status_code, detail=result.json())
            return JSONResponse(content=jsonable_encoder(result.json()), status_code=200)
