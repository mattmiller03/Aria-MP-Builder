FROM base-adapter:python-1.2.0

USER root
COPY app/wheels/ /tmp/wheels/
RUN pip install --no-cache-dir --no-index --find-links /tmp/wheels/ requests vmware-aria-operations-integration-sdk-lib && rm -rf /tmp/wheels

USER aria-ops-adapter-user
COPY app/ /home/aria-ops-adapter-user/src/app/
WORKDIR /home/aria-ops-adapter-user/src/app
