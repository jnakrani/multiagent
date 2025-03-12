from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
# from agent_duckduckgo import CourseGenerationGraph
import os
from dotenv import load_dotenv
from agent_serp_search import CourseGenerationGraph

load_dotenv()

app = FastAPI()
course_generator = CourseGenerationGraph(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    serpapi_key=os.getenv("SERP_API_KEY")
)

class CourseRequest(BaseModel):
    brief: str
    target_audience: str
    course_duration: str

@app.get("/")
async def normal_message():
    return {"message": "Welcome to the Course Generation API!"}

@app.post("/generate-course")
async def generate_course(course_input: CourseRequest):
    try:
        result = await course_generator.generate_course(
            course_brief=course_input.brief,
            target_audience=course_input.target_audience
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))