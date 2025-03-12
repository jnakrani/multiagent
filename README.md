# AI Course Generator

An AI-powered course generation system that creates detailed course outlines using search results and AI processing. The system uses FastAPI for the backend, LangChain for AI operations, and Google Serper API for web research.

## Features

- Automated course research using Google Serper API
- AI-powered course outline generation
- Structured JSON output with course modules and lessons
- RESTful API interface
- Asynchronous processing

## Prerequisites

- Python 3.8+
- OpenAI API key
- Google Serper API key

## Installation

1. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with your API keys:
```env
OPENAI_API_KEY=your_openai_api_key
SERP_API_KEY=your_serper_api_key
```

## Usage

1. Start the FastAPI server:
```bash
uvicorn main:app --reload
```

2. The API will be available at `http://localhost:8000`

3. Generate a course by sending a POST request to `/generate-course`:
```bash
curl -X POST "http://localhost:8000/generate-course" \
     -H "Content-Type: application/json" \
     -d '{
           "brief": "Introduction to Python Programming",
           "target_audience": "Beginners",
           "course_duration": "6 weeks"
         }'
```

## API Endpoints

### POST /generate-course

Generates a course outline based on the provided brief and target audience.

**Request Body:**
```json
{
    "brief": "string",
    "target_audience": "string",
    "course_duration": "string"
}
```

**Response:**
```json
{
    "course_title": "string",
    "description": "string",
    "modules": [
        {
            "title": "string",
            "duration": "string",
            "objectives": ["string"],
            "lessons": [
                {
                    "title": "string",
                    "content": "string",
                    "resources": ["string"]
                }
            ]
        }
    ]
}
```