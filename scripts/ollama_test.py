
import ollama

response = ollama.chat(
    model='gemma:2b',
    messages=[
        {
            'role': 'user',
            'content': 'Generate a professional MRI stroke report.'
        }
    ]
)

print(response['message']['content'])