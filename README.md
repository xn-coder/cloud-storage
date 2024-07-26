# Cloud Storage

Welcome to the Cloud Storage project! This repository contains the code for a cloud storage service built using FastAPI and Telethon.

## Features

- **User Authentication**: Secure login and logout functionality.
- **File Upload**: Upload images and videos.
- **Media Gallery**: Display uploaded media in a gallery format.
- **Progress Tracking**: Real-time upload progress tracking.
- **Media Actions**: Download and remove media files.
- **Responsive Design**: Mobile-friendly navigation and layout.

## Getting Started

## Technologies Used

### Frontend

- **HTML**
- **CSS**
- **JavaScript**
- **FontAwesome**: For icons

### Backend

- **FastAPI**: A modern, fast (high-performance), web framework for building APIs with Python 3.6+.
- **Telethon**: A Python library to interact with Telegram's API.

### Prerequisites

- Python 3.7+
- Telegram API credentials (API ID and API Hash)

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/xn-coder/cloud-storage.git
    cd cloud-storage
    ```

2. Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Configuration

1. Set your Telegram API credentials in `api/main.py`:
    ```python
    api_id = YOUR_API_ID
    api_hash = "YOUR_API_HASH"
    ```

### Running the Application

1. Start the FastAPI server:
    ```bash
    uvicorn api.main:app --host 0.0.0.0 --port 8000
    ```

2. The API will be available at `http://localhost:8000`.

### API Endpoints

- **GET /**: Welcome message
- **POST /sign-in/**: Sign in with a phone number
- **POST /verify-code/**: Verify the code sent to the phone number
- **POST /logout/**: Log out from the session
- **POST /upload/**: Upload a file
- **GET /download/{id}**: Download a file by ID
- **GET /remove/**: Remove a file by ID
- **GET /media/**: Get media details by ID
- **GET /stream/{id}**: Stream a video by ID
- **GET /list-files/**: List uploaded files

### Contributing

Contributions are welcome! Please open an issue or submit a pull request for any changes.

### Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/)
- [Telethon](https://github.com/LonamiWebs/Telethon)

For more details, visit the [repository](https://github.com/xn-coder/cloud-storage).
