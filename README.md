# StreamSaver Backend

## Overview

This document provides a comprehensive guide for developers working with the StreamSaver backend application.  StreamSaver is a RESTful API built with FastAPI, providing endpoints for downloading and metadata retrieval of videos and images from various social media platforms, including Instagram and YouTube.  The backend uses PostgreSQL for relational data and MongoDB for NoSQL needs.


[//]: # (This is a comment, not part of the generated README)


## Table of Contents

* [Installation Instructions](#installation-instructions)
* [Usage Guide](#usage-guide)
    * [Instagram Endpoints](#instagram-endpoints)
    * [YouTube Endpoints](#youtube-endpoints)
* [Configuration](#configuration)
* [Technical Details](#technical-details)
* [Contribution Guidelines](#contribution-guidelines)
* [License](#license)
* [FAQs](#faqs)
* [Support](#support)


[//]: # (This is a comment, not part of the generated README)


## Installation Instructions

**Prerequisites:**

* Python 3.8 or higher
* PostgreSQL
* MongoDB
* `pip` (Python package installer)
* `virtualenv` (Recommended for isolated environments)

**Steps:**

1. **Clone the repository:**
   ```bash
   git clone <REPOSITORY_URL>
   cd StreamSaver/backend
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:** Create a `.env` file based on the `.env.example` file, populating it with your database credentials and other necessary settings.

5. **Database Setup:** Ensure your PostgreSQL and MongoDB instances are running and accessible.  The database schema will be automatically created upon application startup.

6. **Run the application:**
   ```bash
   uvicorn src.main:app --reload
   ```

[//]: # (This is a comment, not part of the generated README)


## Usage Guide

The StreamSaver API uses standard RESTful principles.  All endpoints are prefixed with `/api/v1`.  Authentication mechanisms are not fully detailed here, and placeholders will be used. Replace these placeholders with your actual authentication logic.

### Instagram Endpoints

* **/api/v1/instagram/metadata**:  GET request to retrieve metadata for an Instagram post.
    * **Request:**  `GET /api/v1/instagram/metadata?url=<INSTAGRAM_POST_URL>`
    * **Response:**  JSON containing metadata (shortcode, caption, media URLs, etc.).  See `src/schemas/stream_saver_schema.py` for the detailed response schema.
* **/api/v1/instagram/download**: GET request to download Instagram media.
    * **Request:** `GET /api/v1/instagram/download?url=<INSTAGRAM_POST_URL>&media_index=<MEDIA_INDEX>`
    * **Response:** A stream of the media file.


### YouTube Endpoints

* **/api/v1/youtube/video/metadata**: GET request to fetch YouTube video metadata.
    * **Request:** `GET /api/v1/youtube/video/metadata?url=<YOUTUBE_VIDEO_URL>`
    * **Response:** JSON containing video metadata (title, thumbnail, duration, etc.). See `src/schemas/stream_saver_schema.py`.
* **/api/v1/youtube/video/download**: POST request to download a YouTube video.
    * **Request:** `POST /api/v1/youtube/video/download` with JSON body `{"url": "<YOUTUBE_VIDEO_URL>", "quality": "720p"}` (or other quality).
    * **Response:** A stream of the downloaded video file.


[//]: # (This is a comment, not part of the generated README)


## Configuration

The application's behavior is configurable through environment variables defined in the `.env` file.  Key settings include:

* `DATABASE_URL`: PostgreSQL connection string.
* `MONGO_DB_URL`: MongoDB connection string.
* `SECRET_KEY`:  Secret key for JWT.  **Do not commit this to version control.**
* `ALLOWED_HOSTS`, `ALLOWED_ORIGINS`, `ALLOWED_METHODS`: CORS settings.  Adjust according to your deployment.
* `JWT_EXPIRE_MINUTES`: JWT token expiration time (in minutes).


Refer to `src/core/settings/configurations/config.py` for a complete list of configurable settings.

[//]: # (This is a comment, not part of the generated README)


## Technical Details

**Tech Stack:**

* **Backend Framework:** FastAPI
* **Database:** PostgreSQL (Relational), MongoDB (NoSQL)
* **ORM:** SQLAlchemy (PostgreSQL), Pydantic (Data Validation)
* **Asynchronous Programming:** `async` and `await`
* **Authentication:** JWT (JSON Web Tokens)  (Implementation details are not included in this sample.)
* **External Libraries:** `yt_dlp`, `instaloader`, `loguru`

**Architecture:**

The application follows a layered architecture, separating concerns into distinct modules for API endpoints, database interactions, business logic, and error handling.

**Main Components:**

* **API Routers:** Define API endpoints for interacting with the application.
* **Services:** Handle business logic and interactions with external resources.
* **Repositories:** Abstract database interactions, providing consistent interfaces for both relational and NoSQL databases.
* **Models:** Define data structures for both the database and API responses.
* **Error Handling:** Comprehensive error handling and logging.


[//]: # (This is a comment, not part of the generated README)


## Contribution Guidelines

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and ensure they are well-documented. Follow the existing coding style.
4. Run the tests to confirm everything is working as expected.
5. Submit a pull request with a clear description of your changes.

**Coding Standards:**

* Use PEP 8 style guide.
* Write comprehensive docstrings for functions and classes.
* Keep functions concise and focused.
* Use type hints consistently.


[//]: # (This is a comment, not part of the generated README)


## License

This project is licensed under the <LICENSE_NAME> License - see the [LICENSE](LICENSE) file for details.

[//]: # (This is a comment, not part of the generated README)


## FAQs

* **Q: How do I troubleshoot connection errors?**  A:  Check your `.env` file for correct database credentials and network connectivity. Examine the application logs for more specific error messages.

* **Q: What are the supported video qualities for YouTube downloads?** A: The available qualities depend on the uploaded video. The API will return a list of available qualities, but you can specify a quality in your download request.


[//]: # (This is a comment, not part of the generated README)


## Support

For support or to report issues, please open a new issue on the GitHub repository.
