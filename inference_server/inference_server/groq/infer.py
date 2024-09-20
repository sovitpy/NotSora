import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import json
import logging

load_dotenv()
key = os.environ["GROQ_API_KEY"]

codegen_system_prompt = """You are a Manim expert tasked with generating Manim code from user prompts. Follow the following steps to create the code. Write down the thought process before writing the code and place the though process between <Thinking> and </Thinking> tags.
1. Analyze the user's prompt:
   - Identify the key elements or concepts they want to visualize
   - Consider how these elements could be represented in an animated video
   - Think about the logical sequence of animations that would best convey the idea
2. Plan the animation structure:
   - Determine the main objects or shapes needed
   - Outline the sequence of animations and transformations
   - Consider any text or labels that should be included
3. Develop the code structure:
   - Start with importing necessary Manim modules
   - Create a class named GenerateVideo that inherits from Scene
   - Within the construct method, plan out your animation sequence
4. Write the Manim code:
   - Implement the planned animations step by step
   - Use appropriate Manim classes and methods for each element
   - Ensure smooth transitions between different parts of the animation
5. Review and refine:
   - Check that all elements from the user's prompt are included
   - Ensure the code follows Manim best practices
   - Make any final adjustments for clarity, efficiency, and ease of rendering
6. Present the code:
   - Place the complete Manim code within a fenced code block
   - Ensure the class name is GenerateVideo as specified
Remember: Always generate code for an animated video and name the class GenerateVideo, regardless of the complexity of the user's prompt. Your goal is to create a visual representation that brings their idea to life through animation, while ensuring the code can be easily rendered by users with standard Manim setups."""

# codegen_system_prompt = "You are a Manim expert that can generate Manim code from user prompts. You should always generate code for an animated video. You will return code in a fenced code block. The class name for scene should always be GenerateVideo."
log_analyzer_system_prompt = """You are a Manim error analysis system designed to process error logs and provide structured analysis for another LLM. Your output should be concise, precise, and easily parseable. When presented with a Manim error log, generate a response in the following format:
   - Error Type: [Specific error type, e.g., SyntaxError, AttributeError]
   - Error Location: [File name and line number]
   - Error Message: [Exact error message including any relevant details and context]
Ensure all information is factual, based on the provided error log and known Manim behaviors. Avoid speculative statements. If certain information cannot be determined from the error log, explicitly state "Insufficient information" for that section."""

groq = ChatGroq(
    model="llama3-70b-8192",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

logging.basicConfig(
    level=logging.INFO,  # Set the logging level
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Log format
)

logger = logging.getLogger(__name__)


# Generates Manim code and returns a fenced code block.
def generate_manim_code(query):
    messages = [
        ("system", codegen_system_prompt),
        ("human", query),
    ]
    groq_response = groq.invoke(messages)
    logger.info(f"Groq response: {groq_response.content}")
    fenced_code_block = groq_response.content.split("```")[1]
    return fenced_code_block


def analyze_error_log(error_log):
    messages = [
        ("system", log_analyzer_system_prompt),
        ("human", error_log),
    ]
    groq_response = groq.invoke(messages)
    logger.info(f"Groq response: {groq_response}")
    return groq_response.content


def format_manim_code(fenced_code_block):
    code_lines = fenced_code_block.split("\n")
    formatted_code = code_lines[1:-1]
    return formatted_code


if __name__ == "__main__":
    pass
