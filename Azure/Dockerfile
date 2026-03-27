FROM python:3.11-slim

COPY app/wheels/ /tmp/wheels/
RUN pip install --no-cache-dir --no-index --find-links /tmp/wheels/ -r /tmp/wheels/requirements.txt \
    && pip install --no-cache-dir --no-index --find-links /tmp/wheels/ vmware-aria-operations-integration-sdk-lib \
    && rm -rf /tmp/wheels

COPY app/ /adapter
WORKDIR /adapter
