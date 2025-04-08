# PDF Chat Application

A Django-based application that enables intelligent conversations with PDF documents using advanced text processing and vector similarity search. The application processes PDF documents, splits them into meaningful chunks, generates embeddings using NVIDIA's AI endpoints, and stores them for efficient similarity search using Qdrant vector database.

## Features

- PDF document processing and text extraction
- Intelligent text chunking for better context preservation
- Vector embeddings generation using NVIDIA's AI endpoints
- Efficient similarity search using Qdrant vector database
- Asynchronous document processing with Celery
- RESTful API endpoints for document management

## Tech Stack

- **Backend Framework**: Django
- **Task Queue**: Celery
- **Vector Database**: Qdrant
- **Embeddings**: NVIDIA AI Endpoints
- **PDF Processing**: LangChain's PyPDFLoader
- **Text Processing**: LangChain's RecursiveCharacterTextSplitter

## Prerequisites

- Python 3.8+
- Docker and Docker Compose
- NVIDIA API Key for embeddings generation

## Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd pdf_chat
   ```

2. Create a `.env` file in the project root with the following variables:

   ```env
   # Django settings
   DEBUG=1
   SECRET_KEY=your-secret-key-here
   DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]

   # Database settings
   POSTGRES_DB=pdf_chat
   POSTGRES_USER=pdf_chat_user
   POSTGRES_PASSWORD=pdf_chat_password
   POSTGRES_HOST=db

   # Redis settings
   REDIS_URL=redis://redis:6379/0

   # NVIDIA settings
   NVIDIA_API_KEY=your-nvidia-api-key
   QDRANT_HOST=http://qdrant:6333

   # Celery settings
   CELERY_BROKER_URL=redis://redis:6379/0
   CELERY_RESULT_BACKEND=redis://redis:6379/0

   # CORS settings
   CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

   # File upload settings
   MAX_UPLOAD_SIZE=10485760  # 10MB in bytes
   ```

3. Build and start the containers:
   ```bash
   docker-compose up --build
   ```

## Usage

1. Access the application at `http://localhost:8000`

2. Upload a PDF document through the API:

   ```bash
   curl -X POST -F "file=@your_document.pdf" http://localhost:8000/api/documents/
   ```

3. The document will be automatically processed:

   - Text extraction from PDF
   - Splitting into meaningful chunks
   - Generating embeddings
   - Storing in Qdrant for similarity search

4. Query the document using the search endpoint:
   ```bash
   curl -X POST -H "Content-Type: application/json" \
   -d '{"query": "your question here", "document_id": 1}' \
   http://localhost:8000/api/documents/1/search/
   ```

## Project Structure

- `core/`: Django project settings and configuration
- `documents/`: Main application module
  - `models.py`: Database models for documents and chunks
  - `tasks.py`: Celery tasks for document processing
  - `utils.py`: Utility functions for text processing and embeddings
  - `views.py`: API endpoints
  - `qdrant_client.py`: Qdrant vector database client

## Development

1. Install development dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Run migrations:

   ```bash
   python manage.py migrate
   ```

3. Start the development server:

   ```bash
   python manage.py runserver
   ```

4. Start Celery worker:
   ```bash
   celery -A core worker -l info
   ```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
