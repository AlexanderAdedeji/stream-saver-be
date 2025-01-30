# Use the official Python 3.13 image
FROM python:3.13

# Set the working directory
WORKDIR /app

# Copy project files into the container
COPY . /app

# Install Poetry
RUN pip install poetry

# Install dependencies
RUN poetry install --no-root

# Expose the application port (adjust as needed)
EXPOSE 8002

# Command to run your FastAPI app (adjust as needed)
CMD ["poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
