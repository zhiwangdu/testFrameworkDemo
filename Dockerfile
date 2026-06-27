FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /opt/test-framework-demo

COPY requirements.txt /opt/test-framework-demo/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY selftest_framework /opt/test-framework-demo/selftest_framework

CMD ["python", "-m", "selftest_framework.runner"]
