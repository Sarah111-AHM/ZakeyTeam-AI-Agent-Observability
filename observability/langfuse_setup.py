from langfuse import Langfuse
from langfuse.callback import CallbackHandler
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

class ObservabilityManager:
    def __init__(self):
        self.langfuse = Langfuse(
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
        )
        self.handler = CallbackHandler()
        self.setup_logging()
    
    def setup_logging(self):
        """Configure structured logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('agent_logs.json'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def trace_agent_execution(self, agent_name, input_data):
        """Create trace for agent execution"""
        trace = self.langfuse.trace(
            name=f"{agent_name}_execution",
            input=input_data,
            metadata={
                "agent_type": agent_name,
                "timestamp": datetime.now().isoformat(),
                "environment": os.getenv("ENVIRONMENT", "development")
            }
        )
        return trace
    
    def log_agent_metric(self, trace_id, metric_name, value, metadata=None):
        """Log custom metrics"""
        self.langfuse.score(
            trace_id=trace_id,
            name=metric_name,
            value=value,
            comment=metadata or {}
        )
    
    def get_callback_handler(self):
        """Get Langfuse callback handler for LangChain/LlamaIndex"""
        return self.handler
    
    def log_structured_event(self, event_type, data):
        """Log structured events to file and Langfuse"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "data": data
        }
        
        # Log to file
        self.logger.info(json.dumps(log_entry))
        
        # Send to Langfuse
        self.langfuse.trace(
            name=event_type,
            input=data.get("input", ""),
            output=data.get("output", ""),
            metadata=data
        )
