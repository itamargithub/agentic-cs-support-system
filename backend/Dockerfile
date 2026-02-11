FROM python:3.11-slim
WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY backend /app/backend
COPY README.md /app/README.md

# Ensure Python can import the local "backend" package during image build
ENV PYTHONPATH=/app
RUN python -m backend.scripts.build_index

EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
