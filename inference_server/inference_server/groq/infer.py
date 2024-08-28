import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import json

load_dotenv()
key = os.environ["GROQ_API_KEY"]

groq = ChatGroq(
    model="llama-3.1-70b-versatile",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)


# Generates Manim code and returns a fenced code block.
def generate_manim_code(query):
    messages = [
        (
            "system",
            "You are a Manim expert that can generate Manim code from user prompts. You should always generate code for an animated video. You will only return code and no explanation whatsover. The class name for scene should always be GenerateVideo.",
        ),
        ("human", query),
    ]
    groq_response = groq.invoke(messages)
    return groq_response.content


def format_manim_code(fenced_code_block):
    code_lines = fenced_code_block.split("\n")
    formatted_code = code_lines[1:-1]
    return formatted_code


if __name__ == "__main__":
    pass
