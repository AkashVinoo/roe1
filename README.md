# TDS Course Q&A API

An intelligent Q&A system for the Tools in Data Science (TDS) course that uses semantic search and natural language processing to answer student questions.

## Features

- Semantic search using sentence transformers
- Support for both text questions and image attachments
- RESTful API with FastAPI
- Automated content crawling from course website and forum
- Production-ready server setup

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/tds-qa-api.git
cd tds-qa-api
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. First, crawl the course content:
```bash
python forum_spider.py
```

2. Start the API server:
```bash
python run_server.py
```

The server will start on `http://localhost:8000`.

## API Endpoints

### POST /api/
Ask a question about the TDS course.

Request format:
```json
{
    "question": "Your question here",
    "image": "Optional base64 encoded image"
}
```

Example:
```bash
curl "http://localhost:8000/api/" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Should I use gpt-4o-mini which AI proxy supports, or gpt3.5 turbo?",
    "image": "'$(base64 -w0 screenshot.png)'"
  }'
```

Response format:
```json
{
    "answer": "The answer text...",
    "links": [
        {
            "url": "Source URL",
            "text": "Context from the source"
        }
    ]
}
```

### GET /api/health
Check API health status.

## Project Structure

```
.
├── api.py              # FastAPI application
├── project1.py         # QA system core
├── forum_spider.py     # Content crawler
├── run_server.py       # Production server
├── requirements.txt    # Dependencies
├── uploads/           # Uploaded images
└── logs/             # Server logs
```

## Configuration

The system uses the following configuration files:

- `auth_config.json`: Authentication credentials (optional)
- `server.log`: Server logs
- `tds_content.jsonl`: Crawled course content

## Development

1. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Run tests:
```bash
pytest test_api.py
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 