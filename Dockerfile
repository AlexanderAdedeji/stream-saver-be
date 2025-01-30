# Use the official Python 3.13 image
FROM python:3.13

# Set the working directory
WORKDIR /app

# Install Poetry
RUN pip install poetry


RUN poetry config virtualenvs.create false


COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --no-root


COPY . .


EXPOSE 8002

# Command to run the FastAPI app
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
