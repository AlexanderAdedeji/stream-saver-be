# StreamSaver Backend

## Overview

This document provides a comprehensive guide to the StreamSaver backend application.  This backend API provides functionalities for retrieving metadata and downloading media from various social media platforms, including YouTube, Instagram, and Facebook.

[//]: # (This is a comment, it won't be rendered in the README)

[TOC]

## Table of Contents

* [Project Title](#project-title)
* [Overview](#overview)
* [Installation Instructions](#installation-instructions)
* [Usage Guide](#usage-guide)
    * [YouTube API Usage](#youtube-api-usage)
    * [Instagram API Usage](#instagram-api-usage)
    * [Facebook API Usage](#facebook-api-usage)
* [Configuration](#configuration)
* [Technical Details](#technical-details)
* [Contribution Guidelines](#contribution-guidelines)
* [License](#license)
* [FAQs](#faqs)
* [Support](#support)


## Project Title

StreamSaver Backend


## Installation Instructions

**Prerequisites:**

* Python 3.7 or higher
* PostgreSQL
* MongoDB
* Node.js (for frontend, if applicable)


**Setup:**

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd streamSaver/backend
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**  Copy the `.env.example` file to `.env` and populate it with your database credentials, API keys, and other necessary configurations.

5. **Database Setup:**
   * **PostgreSQL:** Ensure PostgreSQL is running and the database specified in your `.env` file exists.  You might need to create the database manually.
   * **MongoDB:** Ensure MongoDB is running and the database specified in your `.env` file exists.


6. **Run migrations (if applicable):**  If your project uses a database migration system (e.g., Alembic), run the necessary commands to apply migrations.  Example:
   ```bash
   alembic upgrade head
   ```


## Usage Guide


The StreamSaver backend exposes several APIs for accessing different social media platforms.  Below are examples demonstrating their usage.

### YouTube API Usage

**Retrieve Metadata:**

```bash
curl -X GET "http://localhost:8000/api/v1/youtube/video/metadata?url=<youtube_video_url>"
```

**Download Video:**

```bash
curl -X POST "http://localhost:8000/api/v1/youtube/video/download" -H "Content-Type: application/json" -d '{"url": "<youtube_video_url>", "quality": "720"}'
```


### Instagram API Usage

**Retrieve Metadata:**

```bash
curl -X GET "http://localhost:8000/api/v1/instagram/metadata?url=<instagram_post_url>"
```

**Download Media:**

```bash
curl -X GET "http://localhost:8000/api/v1/instagram/download?url=<instagram_post_url>&media_index=0"
```


### Facebook API Usage

**Retrieve Metadata:**

```bash
curl -X POST "http://localhost:8000/api/v1/facebook/metadata" -H "Content-Type: application/json" -d '{ "url": "<facebook_post_url>", "access_token": "<your_facebook_access_token>" }'
```


## Configuration

The application's behavior can be customized through environment variables defined in the `.env` file.  Key configuration parameters include:

* Database connection strings (PostgreSQL and MongoDB)
* API keys for Facebook, Instagram (if applicable)
* Server settings (port, allowed origins, etc.)
* JWT settings (secret key, algorithm, expiration time)


## Technical Details

**Tech Stack:**

* **Backend:** FastAPI (Python), SQLAlchemy (ORM),  yt-dlp, instaloader, requests
* **Database:** PostgreSQL, MongoDB
* **Authentication:** JWT (JSON Web Tokens)


**Architecture:**

The application follows a RESTful API architecture.  It uses FastAPI for routing and handling requests, SQLAlchemy for database interaction (PostgreSQL), and interacts with social media APIs via external libraries.  MongoDB is used for any non-relational data storage needs.


**Components:**

* API Routers (for YouTube, Instagram, Facebook, and Authentication)
* Database interaction layer (SQLAlchemy and MongoDB driver)
* Authentication and Authorization (JWT)
* Service layer for business logic
* Repository layer for data access


## Contribution Guidelines

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them with clear and concise messages.
4. Ensure your code adheres to the project's coding style (check for existing code style guidelines).
5. Write comprehensive unit tests for your code.
6. Submit a pull request with a detailed description of your changes.


## License

This project is licensed under the <insert license name here> license.  See the LICENSE file for details.


## FAQs

* **Q: What are the required permissions for Facebook API access?**

   **A:**  For public Page posts: `pages_manage_posts`. For user posts: `user_posts`.  Make sure to adjust accordingly in the FacebookPostRequest model.

* **Q: How do I handle rate limits?**

   **A:**  The code includes rate-limiting middleware for specific routes (currently commented out).  Uncomment and configure it as needed, and consider implementing exponential backoff for retry logic.

* **Q: How to debug the application?**

  **A:** Use a debugger such as pdb (python debugger) or add print statements/logging messages to the code.  Make sure to set the logging level appropriately in your `.env` file.


## Support

For support or to report issues, please open an issue on the GitHub repository.  You can also contact the developers at `<contact_email>`.



## Generated using Autodocify https://pypi.org/project/autodocify-cli/
