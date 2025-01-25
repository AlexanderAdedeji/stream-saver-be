# StreamSaver Backend API

## Overview

This document provides comprehensive information for developers working with the StreamSaver backend API.  This API allows for metadata retrieval and download functionality for Instagram and YouTube content.  It is built using FastAPI, SQLAlchemy, and MongoDB, providing a robust and scalable solution.

<br>

## Table of Contents

* [Project Title](#project-title)
* [Overview](#overview)
* [Installation Instructions](#installation-instructions)
* [Usage Guide](#usage-guide)
*   [Instagram API Usage](#instagram-api-usage)
*   [YouTube API Usage](#youtube-api-usage)
* [Configuration](#configuration)
* [Technical Details](#technical-details)
* [Contribution Guidelines](#contribution-guidelines)
* [License](#license)
* [FAQs](#faqs)
* [Support](#support)


<br>

## Installation Instructions

**Prerequisites:**

* Python 3.7 or higher
* PostgreSQL
* MongoDB
* Node.js (for frontend, if applicable)

**Steps:**

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd streamSaver/backend
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Create a `.env` file based on the `.env.example` file, populating it with your database credentials, secret keys, and other necessary configurations.  Ensure that the environment variables defined in `.env.example` are correctly set in your environment.

5. **Database setup:**
   * **PostgreSQL:** Ensure your PostgreSQL database is running and accessible.  The connection string should be correctly set in your `.env` file.
   * **MongoDB:** Ensure your MongoDB database is running and accessible.  The connection string and database name should be correctly set in your `.env` file.


<br>

## Usage Guide


The API is structured around several routes for managing and accessing Instagram and YouTube content.

### Instagram API Usage

* **`/auth/login`**:  Handles user login.  (Further details needed)
* **`/instagram/metadata/{url}`**: Retrieves metadata for an Instagram post.
  ```bash
  curl -X GET "http://localhost:8000/<API_URL_PREFIX>/instagram/metadata?url=<instagram_post_url>"
  ```
* **`/instagram/download/{url}`**:  Downloads media from an Instagram post.
  ```bash
  curl -X GET "http://localhost:8000/<API_URL_PREFIX>/instagram/download?url=<instagram_post_url>&media_index=0"
  ```

### YouTube API Usage

* **`/video/metadata/{url}`**: Retrieves metadata for a YouTube video.
  ```bash
  curl -X GET "http://localhost:8000/<API_URL_PREFIX>/video/metadata?url=<youtube_video_url>"
  ```
* **`/youtube/download/{url}`**: Downloads a YouTube video.
    ```bash
    curl -X POST "http://localhost:8000/<API_URL_PREFIX>/youtube/download?url=<youtube_video_url>"
    ```


<br>

## Configuration

The API's behavior is controlled by environment variables defined in the `.env` file.  Key configuration parameters include:

* `POSTGRES_DB_URL`: PostgreSQL database connection string.
* `MONGO_DB_URL`: MongoDB connection string.
* `MONGO_DB_NAME`: MongoDB database name.
* `SECRET_KEY`:  Secret key for JWT authentication.
* `ALLOWED_HOSTS`, `ALLOWED_ORIGINS`, `ALLOWED_METHODS`: CORS settings.


<br>

## Technical Details

* **Programming Language:** Python
* **Framework:** FastAPI
* **Database:** PostgreSQL (SQLAlchemy), MongoDB (Motor)
* **Authentication:** JWT
* **Libraries:** `yt-dlp`, `instaloader`, `SQLAlchemy`, `Pydantic`, `Loguru`


The application uses a layered architecture, separating concerns into models, repositories, services, and API routes.  The database interaction is handled by SQLAlchemy for PostgreSQL and Motor for MongoDB.  The API is built using FastAPI, utilizing Pydantic for data validation and serialization.


<br>

## Contribution Guidelines

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and ensure they are well-documented and adhere to the coding standards.
4. Run the tests using `<COMMAND>`.
5. Submit a pull request with a clear description of your changes.


<br>

## License

This project is licensed under the <LICENSE_NAME> License - see the [LICENSE](LICENSE) file for details.


<br>

## FAQs

* **Q: How do I handle errors?**
   A: The API returns standard HTTP status codes and JSON responses indicating success or failure.  Error messages provide details about the issue.

* **Q: What authentication is used?**
   A: JWT (JSON Web Tokens) is used for authentication.

* **Q: How do I troubleshoot connection issues?**
    A: Verify your `.env` file contains correct database credentials and that the databases are running and accessible. Check the logs for any connection errors.


<br>

## Support

For support or to report issues, please open a new issue on the GitHub repository.  You can also contact us at <EMAIL_ADDRESS_OR_LINK>.
