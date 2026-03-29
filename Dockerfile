FROM python:3.11-slim
WORKDIR /app
RUN pip install paramiko prometheus-client
COPY sonic_temp_exporter.py .
EXPOSE 9805
ENV PYTHONUNBUFFERED=1
CMD ["python3", "-u", "sonic_temp_exporter.py"]