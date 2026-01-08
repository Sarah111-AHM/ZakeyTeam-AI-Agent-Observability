import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import json

def create_monitoring_dashboard():
    st.set_page_config(page_title="AI Agents Dashboard", layout="wide")
    
    st.title("🤖 AI Agents Observability Dashboard")
    
    # Load logs
    try:
        with open('agent_logs.json', 'r') as f:
            logs = [json.loads(line) for line in f]
    except:
        logs = []
    
    # Metrics columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_executions = len([l for l in logs if l.get('event_type') == 'search_executed'])
        st.metric("Total Executions", total_executions)
    
    with col2:
        error_rate = len([l for l in logs if 'error' in l.get('event_type', '')]) / max(len(logs), 1)
        st.metric("Error Rate", f"{error_rate:.2%}")
    
    with col3:
        avg_latency = 0.5  # Would calculate from actual data
        st.metric("Avg Latency", f"{avg_latency:.2f}s")
    
    with col4:
        st.metric("Active Agents", "2")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        if logs:
            df = pd.DataFrame(logs)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            hourly_counts = df.resample('H', on='timestamp').size()
            st.subheader("Requests per Hour")
            st.line_chart(hourly_counts)
    
    with col2:
        st.subheader("Agent Distribution")
        agent_counts = {'Research Agent': 65, 'Coding Agent': 35}
        fig = px.pie(values=list(agent_counts.values()), 
                    names=list(agent_counts.keys()))
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent logs
    st.subheader("Recent Activity")
    if logs:
        recent_logs = logs[-10:]
        for log in recent_logs:
            with st.expander(f"{log['timestamp']} - {log['event_type']}"):
                st.json(log)
    else:
        st.info("No logs available yet")

if __name__ == "__main__":
    create_monitoring_dashboard()
