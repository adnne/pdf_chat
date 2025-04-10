# PDF Chat Frontend

This is the Vue.js frontend for the PDF Chat application. It provides a user interface for chatting with PDF documents, featuring a split-screen layout with a PDF viewer on one side and a chat interface on the other.

## Features

- Split-screen layout with PDF viewer and chat interface
- Document navigation tabs to switch between different PDFs
- Real-time chat with AI about the document content
- Responsive design for various screen sizes
- Integration with Django backend API

## Tech Stack

- Vue.js 3 with Composition API
- PrimeVue for UI components
- PDF.js for PDF rendering
- Axios for API communication
- Docker for containerization

## Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

## Production Build

```bash
# Build for production
npm run build
```

## Docker

The frontend is containerized using Docker and can be run alongside the backend using docker-compose.

```bash
# Build and run with docker-compose
docker-compose up --build
```
