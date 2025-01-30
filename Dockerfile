# Use the official Python 3.12 image (since your pyproject.toml specifies Python 3.12)
FROM python:3.12

# Set the working directory
WORKDIR /app

# Copy project files into the container
COPY . /app

# Install Poetry
RUN pip install poetry

# Configure poetry to not create a virtual environment inside the container
RUN poetry config virtualenvs.create false

# Install dependencies including the current project
RUN poetry install --no-interaction --no-ansi

# Expose the application port
EXPOSE 8002

# Command to run your FastAPI app
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]