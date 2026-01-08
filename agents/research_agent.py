from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from observability.langfuse_setup import ObservabilityManager
import datetime
import json

class ResearchAgent:
    def __init__(self):
        self.observability = ObservabilityManager()
        self.llm = ChatOpenAI(
            model="gpt-4-turbo",
            temperature=0.1,
            callbacks=[self.observability.get_callback_handler()]
        )
        
        self.tools = [
            Tool(
                name="web_search",
                func=self.search_web,
                description="Search the web for current information"
            ),
            Tool(
                name="summarize",
                func=self.summarize_content,
                description="Summarize long documents"
            )
        ]
        
        self.agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.get_prompt()
        )
        
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            callbacks=[self.observability.get_callback_handler()]
        )
    
    def search_web(self, query):
        """Mock web search function"""
        # In production, connect to actual search API
        trace = self.observability.trace_agent_execution(
            "web_search",
            {"query": query}
        )
        
        try:
            # Simulate search results
            results = f"Search results for: {query}"
            
            # Log successful search
            self.observability.log_structured_event(
                "search_executed",
                {
                    "query": query,
                    "result_count": 1,
                    "agent": "research_agent",
                    "latency": 0.5  # simulated
                }
            )
            
            return results
        except Exception as e:
            # Log error
            self.observability.log_structured_event(
                "search_error",
                {
                    "query": query,
                    "error": str(e),
                    "timestamp": datetime.datetime.now().isoformat()
                }
            )
            raise
    
    def run(self, research_topic):
        """Execute research agent with observability"""
        trace = self.observability.trace_agent_execution(
            "research_agent",
            {"topic": research_topic}
        )
        
        start_time = datetime.datetime.now()
        
        try:
            result = self.agent_executor.invoke(
                {"input": f"Research this topic: {research_topic}"}
            )
            
            # Calculate metrics
            end_time = datetime.datetime.now()
            latency = (end_time - start_time).total_seconds()
            
            # Log success metrics
            self.observability.log_agent_metric(
                trace.id,
                "execution_latency",
                latency,
                {"agent": "research_agent", "topic": research_topic}
            )
            
            self.observability.log_agent_metric(
                trace.id,
                "token_usage",
                result.get("usage", {}).get("total_tokens", 0),
                {"agent": "research_agent"}
            )
            
            return result
            
        except Exception as e:
            # Log error
            self.observability.log_structured_event(
                "agent_error",
                {
                    "agent": "research_agent",
                    "error": str(e),
                    "input": research_topic,
                    "timestamp": datetime.datetime.now().isoformat()
                }
            )
            raise
