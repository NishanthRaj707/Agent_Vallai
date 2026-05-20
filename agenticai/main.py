from google import genai
from google.genai import types
from agenticai.functions.get_files_info import schema_get_files_info
from agenticai.functions.get_file_content import schema_get_file_content
from agenticai.functions.run_program_file import schema_run_program_file
from agenticai.functions.writefile import schema_write_file
from agenticai.functions.call_function import call_function
from agenticai.functions.execute_network_commands import schema_execute_network_commands
import time

def main(user_input,working_dir,gemini_api_key,chat=None):
    api_key=gemini_api_key
    prompt=user_input
    system_prompt=open('agenticai/systemprompt.txt',encoding='utf-8').read()

    available_functions=types.Tool(
        function_declarations=[
            schema_get_files_info,
            schema_write_file,
            schema_get_file_content,
            schema_run_program_file,
            schema_execute_network_commands
        ]
    )
    messages=[types.Content(role="user",parts=[types.Part(text=prompt)])] if not chat else [i[-1] for i in chat]+[types.Content(role="user",parts=[types.Part(text=prompt)])]
    config=types.GenerateContentConfig(
        tools=[available_functions],
        system_instruction=system_prompt)

    client=genai.Client(api_key=api_key)
    for i in range(10):
        try:
            response=client.models.generate_content(
                model="gemini-2.5-flash",contents=messages,
                config=config
            )
            if response.candidates:
                for candidate in response.candidates:
                    if candidate is None or candidate.content is None:
                        continue
                    messages.append(candidate.content)

            if response.function_calls:
                for function in response.function_calls:
                    result=call_function(function_call_part=function,working_directory=working_dir)
                    messages.append(result)
            else:
                return response.text
            time.sleep(10)
        except Exception as e:
            print(e)
            print("Quota exceeded wait 30 seconds")
            time.sleep(30)
            continue
            
