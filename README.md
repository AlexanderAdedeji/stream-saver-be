# StreamSaver Backend API

## Overview

This document provides comprehensive information for developers interacting with the StreamSaver backend API.  This API allows for metadata retrieval and download functionality for YouTube, Instagram, and Facebook posts.  It leverages FastAPI, SQLAlchemy, and MongoDB for a robust and efficient architecture.

## Table of Contents

* [Project Title](#project-title)
* [Overview](#overview)
* [Installation Instructions](#installation-instructions)
* [Usage Guide](#usage-guide)
    * [YouTube Integration](#youtube-integration)
    * [Instagram Integration](#instagram-integration)
    * [Facebook Integration](#facebook-integration)
* [Configuration](#configuration)
* [Technical Details](#technical-details)
* [Contribution Guidelines](#contribution-guidelines)
* [License](#license)
* [FAQs](#faqs)
* [Support](#support)


## Installation Instructions

**Prerequisites:**

* Python 3.9 or higher
* `pip` (Python package installer)
* PostgreSQL (database)
* MongoDB (database)

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

4. **Configure environment variables:**  Create a `.env` file based on `.env.example` and populate it with your database credentials, API keys, and other necessary settings.

5. **Run database migrations (if applicable):**  The project might include database migration scripts (e.g., Alembic).  Execute these scripts to set up the database schema.


## Usage Guide

The API is structured with separate endpoints for YouTube, Instagram, and Facebook integrations. Each section details usage examples.  Remember to replace placeholders like `<YOUR_API_KEY>` with your actual values.


### YouTube Integration

**Metadata Retrieval:**

```bash
curl -X GET "http://localhost:8000/api/v1/youtube/video/metadata?url=<YOUTUBE_VIDEO_URL>"
```

**Download:**

```bash
curl -X POST "http://localhost:8000/api/v1/youtube/video/download" -H "Content-Type: application/json" -d '{"url": "<YOUTUBE_VIDEO_URL>", "quality": "720"}'
```

### Instagram Integration

**Metadata Retrieval:**

```bash
curl -X GET "http://localhost:8000/api/v1/instagram/metadata?url=<INSTAGRAM_POST_URL>"
```

**Download:**

```bash
curl -X GET "http://localhost:8000/api/v1/instagram/download?url=<INSTAGRAM_POST_URL>&media_index=0"
```

### Facebook Integration

**Metadata Retrieval:**

```bash
curl -X POST "http://localhost:8000/api/v1/facebook/metadata" -H "Content-Type: application/json" -d '{
  "url": "<FACEBOOK_POST_URL>",
  "access_token": "<YOUR_FACEBOOK_ACCESS_TOKEN>"
}'
```


## Configuration

The API's behavior can be customized through environment variables defined in the `.env` file. Key settings include:

* **Database connections:**  PostgreSQL and MongoDB connection strings.
* **API keys:**  For accessing third-party APIs (Facebook, etc.).
* **Logging levels:**  Control the verbosity of logging output.


## Technical Details

**Technology Stack:**

* **Backend:** FastAPI (Python)
* **Database:** PostgreSQL (Relational), MongoDB (NoSQL)
* **ORM:** SQLAlchemy (PostgreSQL), Pydantic (Data validation)
* **Authentication:** JWT (JSON Web Tokens)
* **Other Libraries:**  yt-dlp, instaloader, requests, loguru

**Architecture:**

The API is designed as a microservice, with clear separation of concerns into routers, services, and repositories.  Data access is handled efficiently using appropriate ORMs for relational and NoSQL databases.


## Contribution Guidelines

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and ensure they pass all tests.
4. Submit a pull request with a clear description of your changes.


## License

This project is licensed under the <license_name> license.  See the [LICENSE](LICENSE) file for details.


## FAQs

* **Q: What error codes are used?**  A: Standard HTTP status codes are used (e.g., 200 OK, 404 Not Found, 500 Internal Server Error).  More specific error messages are included in the response body.

* **Q: How do I handle authentication?** A: JWT authentication is used.  You'll need to obtain a token through the `/auth/login` endpoint and include it in the `Authorization` header of subsequent requests.


## Support

For support or to report issues, please create a new issue on the [GitHub repository](<repository_url>).
