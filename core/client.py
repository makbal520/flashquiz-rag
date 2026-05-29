from openai import OpenAI
import os

def get_client() -> OpenAI:
    return OpenAI(
        api_key="sk-zw2iqM_gBO6gjwKqbuXy1g",  
        base_url="http://10.162.13.14:4000"  
    )