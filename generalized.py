import openai
from Tools.search import SerpAPIWrapper
from Tools.math import PythonREPL
import json

MESSAGES = [{"role":"system", "content":"You are a skillful assistant, use the given tools wisely to give efficient answer."}]

SERPAPI_API_KEY = 'be69ffa2d70955e35706cccd284de3207e1e79807ef47b73b5a3ec54dc4b9a34'

def search_google(query):
    #Uses the Serpapi api 
    search = SerpAPIWrapper(search_engine="google",serpapi_api_key=SERPAPI_API_KEY)
    result = search.run(query)
    search_info = {
        "query": query,
        "message" : result
    }
    return json.dumps(search_info)

def math(query):
    solve  = PythonREPL()
    query = f"print({query})"
    try:
        result = solve.run(query)
    except:
        result = "Unable to find the answer. Provide a valid answer yourself"
    math_info = {
        "query" : query,
        "message" : result
    }
    return json.dumps(math_info)

def search_llm(query,function_name,function_response,question):
    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo-0613",
        messages = [
            {"role":"user", "content":question},
            query,
            {
                "role": "function",
                "name" : function_name,
                "content" : function_response
            },
            {"role":"user", "content":"Frame the answer in good words in passive tense."}
        ]
    )
    return response

def math_llm(query,function_name,function_response,question):
    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo-0613",
        messages = [
            {"role":"user", "content":question},
            query,
            {
                "role": "function",
                "name" : function_name,
                "content" : function_response
            },
            {"role":"user", "content":"Frame the answer in logical sentence integrating with orignal question"}
        ]
    )
    return response

def ask(question):
    #print(f"******{question}********")
    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo-0613",
        messages = MESSAGES,
        functions = [
            {
                "name":"search_google",
                "description":"Gets the latest factual information from the internet",
                "parameters":
                {
                    "type": "object",
                    "properties": {
                        "query":{
                            "type" : "string",
                            "description" : "Small query who answer should be factual and latest"
                        }
                    },
                    "required" : ["query"]
                },
            },
            {
                "name" : "math_tool",
                "description" : "Use this tool only for mathematical calculations",
                "parameters":{
                    "type":"object",
                    "properties": {
                        "query":{
                            "type": "string",
                            "description" : """A properly constructed math problem.Remove all the currency constraints and strictly contain only digits.
                            No alphabets and digit. 
                            Always follow this format for generating query for this function as it is.Here is the expression format
                            print("<The actual mathematical expression>")
                            """
                        }
                    },
                    "required" : ["query"]
                },
            }
        ],
        function_call = "auto"
    )

    #print(response)
    msg = response["choices"][0]["message"] # type: ignore

    if msg.get("function_call"):
        #print("Function call made by model")
        name = msg["function_call"]["name"]
        args = json.loads(msg["function_call"]["arguments"])

        if name == "search_google":
            response = search_google(args.get("query"))
            result = search_llm(msg,function_name=name,function_response=response,question=question)
            print(result["choices"][0]["message"]) # type: ignore
            MESSAGES.append(result["choices"][0]["message"])
    
        if name == "math_tool":
            response = math(args.get("query"))
            result = math_llm(msg,function_name=name,function_response=response,question=question)
            print(result["choices"][0]["message"])
            MESSAGES.append(result["choices"][0]["message"])

    else:
        print(msg)
        MESSAGES.append(msg)
            
while True:
    query = input("Enter your query >>")
    if query == "END":
        break
    MESSAGES.append({"role":"user","content":query})
    #print(MESSAGES)
    ask(question=query)