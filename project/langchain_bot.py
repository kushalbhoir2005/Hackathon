import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser


api_key = "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"

from langchain_openai import ChatOpenAI

def generate_langchain_insights(dashboard_data):
    """Uses LangChain to orchestrate the AI analysis."""
    print(" Running LangChain pipeline via NVIDIA Cloud...")

    llm = ChatOpenAI(
        model="meta/llama-3.1-8b-instruct",
        openai_api_key=api_key,   # ✅ FIXED
        openai_api_base="https://integrate.api.nvidia.com/v1",
        temperature=0.2,
        max_tokens=500
    )
    

 
    parser = JsonOutputParser()

    
    prompt = PromptTemplate(
        template="""You are an expert retail data analyst. Review this store data:
        
        {data}
        
        Write exactly 3 short, highly actionable business recommendations based on these numbers.
        
        {format_instructions}
        
        Ensure the output is a list of objects containing 'type' (success, warning, danger, info), 'title', and 'body'.""",
        input_variables=["data"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    
    chain = prompt | llm | parser

    
    try:
        
        result = chain.invoke({"data": json.dumps(dashboard_data)})
        return result
    except Exception as e:
        print(f"\n LangChain execution failed: {e}")
        return []
    
    
# Add this below your existing generate_langchain_insights function
from langchain_core.output_parsers import StrOutputParser

def chat_with_data(user_query, data_context):
    """Takes a user's question and answers it based on the current data."""
    print(f"💬 User asked: {user_query}")
    
    # 1. Setup the LLM (Same as your other function)
    llm = ChatOpenAI(
        model="meta/llama-3.1-8b-instruct",
        openai_api_key=api_key,   # ✅ FIXED # Assumes you set this up at the top of the file
        openai_api_base="https://integrate.api.nvidia.com/v1",
        temperature=0.2,
        max_tokens=500
    )

    # 2. Setup a standard String parser (we just want normal text back, not JSON)
    parser = StrOutputParser()

    # 3. Create a dynamic prompt
    prompt = PromptTemplate(
        template="""You are an expert AI data analyst. You are chatting with a user about their business data.
        
        Here is the current data context from their uploaded file or dashboard:
        {data}
        
        The user asks: "{query}"
        
        Answer the user's question clearly, concisely, and professionally using ONLY the data provided above. 
        If the answer is not in the data, politely say that you don't have enough information to answer that.
        """,
        input_variables=["data", "query"],
    )

    # 4. Build and execute the chain
    chain = prompt | llm | parser

    try:
        # Pass both the data and the user's specific question
        result = chain.invoke({
            "data": json.dumps(data_context), 
            "query": user_query
        })
        return result
    except Exception as e:
        print(f"\n❌ Chat execution failed: {e}")
        return "I'm sorry, my connection to the server was interrupted. Please try asking again."


if __name__ == "__main__":
    
    try:
        with open("dashboard_output.json", 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        print(" Error: Could not find 'dashboard_output.json'.")
        exit()
        
    
    insights = generate_langchain_insights(data)
    
    
    print("\n" + "="*60)
    print(" LANGCHAIN AI INSIGHTS".center(60))
    print("="*60)
    
    for i, insight in enumerate(insights, 1):
        alert_type = insight.get("type", "info")
        icon = {"success": "✅", "warning": "⚠️", "danger": "🚨"}.get(alert_type, "💡")
        print(f"\n{i}. {icon} {insight.get('title', 'Insight').upper()}")
        print(f"   {insight.get('body', 'No details provided.')}")
        
    print("\n" + "="*60 + "\n")