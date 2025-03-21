from typing import Dict, List, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import Graph, StateGraph
from langchain.utilities import GoogleSerperAPIWrapper
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain.tools import Tool

class AgentState(TypedDict):
    messages: List[BaseMessage]
    research_results: Dict
    course_outline: Dict
    current_step: str

def create_research_agent(openai_api_key: str, serpapi_key: str):
    search = GoogleSerperAPIWrapper(serper_api_key=serpapi_key)
    
    # Create a simple function that returns the search results
    def research_topic(query: str) -> Dict:
        search_results = search.run(query)
        return {
            "search_results": search_results,
            "main_topics": [],  # You might want to process search results to extract these
            "references": []    # And these
        }
    
    return research_topic

def create_outline_agent(openai_api_key: str):
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        openai_api_key=openai_api_key
    )
    
    outline_tool = Tool(
        name="create_course_outline",
        func=lambda x: x,
        description="Create a structured course outline with modules and lessons",
        return_direct=True
    )
    
    tools = [outline_tool]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a course outline expert. Based on the research results, create:
        - A structured course outline with 5-6 modules
        - Learning objectives for each module
        - Estimated duration for each module
        
        Format your response as a JSON with this exact structure:
        {{
            "course_title": "string",
            "description": "string",
            "modules": [
                {{
                    "title": "string",
                    "duration": "string",
                    "objectives": ["string"],
                    "lessons": [
                        {{
                            "title": "string",
                            "content": "string",
                            "resources": ["string"]
                        }}
                    ]
                }}
            ]
        }}"""),
        ("user", "{input}"),
        ("assistant", "{agent_scratchpad}")
    ])
    
    agent = create_openai_functions_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )
    
    return AgentExecutor(agent=agent, tools=tools, verbose=True)

class CourseGenerationGraph:
    def __init__(self, openai_api_key: str, serpapi_key: str):
        self.research_agent = create_research_agent(openai_api_key, serpapi_key)
        self.outline_agent = create_outline_agent(openai_api_key)
        self.workflow = self.create_workflow()

    def research_step(self, state: AgentState) -> AgentState:
        """Research phase of course generation"""
        messages = state["messages"]
        last_message = messages[-1].content
        
        research_results = self.research_agent(f"Research this course topic: {last_message}")
        
        state["research_results"] = research_results
        state["current_step"] = "outline"
        return state
    
    def create_outline_step(self, state: AgentState) -> AgentState:
        """Course outline creation phase"""
        research_results = state["research_results"]
        last_message = state["messages"][-1].content
        print(f"Last message: {last_message}")
        outline = self.outline_agent.invoke({
            "input": f"Here is the research results: {research_results}, Based on the following research results, create a detailed course outline: {last_message}",
            "agent_scratchpad": ""
        })
        
        state["course_outline"] = outline
        state["current_step"] = "complete"
        return state
    
    def create_workflow(self) -> Graph:
        workflow = StateGraph(AgentState)
        
        workflow.add_node("research", self.research_step)
        workflow.add_node("create_outline", self.create_outline_step)
        
        workflow.add_edge("research", "create_outline")
        workflow.set_entry_point("research")
        
        workflow.set_finish_point("create_outline")
        
        return workflow.compile()

    async def generate_course(self, course_brief: str, target_audience: str) -> Dict:
        """Generate a complete course structure"""
        initial_state = AgentState(
            messages=[
                HumanMessage(content=f"""
                Course Brief: {course_brief}
                Target Audience: {target_audience}
                """)
            ],
            research_results={},
            course_outline={},
            current_step="research",
        )
        
        final_state = await self.workflow.ainvoke(initial_state)
        
        try:
            if "course_outline" in final_state:
                outline_str = final_state["course_outline"].get("output", "{}")
                
                import json
                outline = json.loads(outline_str)
                
                return {
                    "course_title": outline.get("course_title", "Course Title"),
                    "description": outline.get("description", f"A comprehensive course designed for {target_audience}"),
                    "modules": outline.get("modules", [])
                    }
                
        except Exception as e:
            print(f"Error processing course outline: {e}")
            
        return {
            "course_title": "Course Title",
            "description": f"A comprehensive course designed for {target_audience}",
            "modules": []
        }