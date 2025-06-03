# TDS Course Q&A System

A semantic search-based Q&A system for the Tools in Data Science course.

## Live Demo

Visit the live demo at: https://akashvinoo.github.io/tds-project-1/

## Features

- Semantic search for course-related questions
- Real-time answers from course materials
- Source attribution for all answers
- Confidence scoring for answer relevance
- Modern, responsive UI

## Local Development

1. Clone the repository:
```bash
git clone https://github.com/AkashVinoo/tds-project-1.git
cd tds-project-1
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the API server:
```bash
python run_server.py
```

4. Open index.html in your browser to use the frontend.

## API Endpoints

- POST `/ask`: Submit a question
  ```json
  {
    "question": "What is the course about?"
  }
  ```

## Deployment

The frontend is automatically deployed to GitHub Pages when changes are pushed to the main branch.

The backend API needs to be deployed separately. You can deploy it to:
- Render
- Railway
- DigitalOcean
- Or any other Python hosting service

## License

MIT License - See LICENSE file for details. 