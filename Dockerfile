FROM python:3.9-alpine AS base

ARG ENVIRONMENT

ENV PYROOT /pyroot
ENV PYTHONUSERBASE ${PYROOT}
ENV PATH=${PATH}:${PYROOT}/bin

RUN PIP_USER=1 pip install pipenv
COPY Pipfile Pipfile.lock ./

RUN if [ "ENVIRONMENT" = "test" ]; then PIP_USER=1 pipenv install --system --deploy --ignore-pipfile --dev; \
    else PIP_USER=1 pipenv install --system --deploy --ignore-pipfile; fi


FROM python:3.9-alpine

ENV PYROOT /pyroot
ENV PYTHONUSERBASE ${PYROOT}
ENV PATH=${PATH}:${PYROOT}/bin

RUN addgroup -S myapp && adduser -S -G myapp -u 1234 user
COPY --chown=user:myapp --from=base ${PYROOT}/ ${PYROOT}/

RUN mkdir -p /usr/src/backend/backend
WORKDIR /usr/src/backend

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=user:myapp backend ./backend
COPY --chown=user:myapp run.py ./

USER user

CMD ["python", "run.py"]


