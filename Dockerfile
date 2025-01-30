# Use the official Python 3.13 image
FROM python:3.13

# Set the working directory
WORKDIR /app


COPY . /app

# Install Poetry
RUN pip install poetry

# Install dependencies
RUN poetry install --no-root


EXPOSE 8002


CMD ["poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8002"]
