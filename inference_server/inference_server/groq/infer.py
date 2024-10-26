import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import json
import logging
from inference_server.groq.rag import get_relevant_snippets

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
# codegen_system_prompt = """You are a highly skilled Manim expert tasked with generating animated Manim scenes from user prompts. Think step by step, considering which Manim objects to use, how to animate them, and how they interact with each other. Clearly explain your choices before providing the final code. Return the code inside a fenced code block, ensuring the scene class is named GenerateVideo."""
                            
log_analyzer_system_prompt = """You are a Manim error analysis system designed to process error logs and provide structured analysis for another LLM. Your output should be concise, precise, and easily parseable. When presented with a Manim error log, generate a response in the following format:
   - Error Type: [Specific error type, e.g., SyntaxError, AttributeError]
   - Error Message: [Exact error message including with detailed context]
Ensure all information is factual, based on the provided error log and known Manim behaviors. Avoid speculative statements. If certain information cannot be determined from the error log, explicitly state "Insufficient information" for that section."""

code_generator = ChatGroq(
    model="llama-3.1-70b-versatile",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

error_analyzer = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.4,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

logging.basicConfig(
    level=logging.INFO,  # Set the logging level
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Log format
)

logger = logging.getLogger(__name__)

class CodeGenerator:
    def __init__(self, query, enable_rag=False):
        self.query = query
        self.enable_rag = enable_rag
        self.similar_snippets_to_query = None
        self.errors = []  # List to track (code_tried, error_received) tuples

        # If RAG is enabled, retrieve relevant code snippets
        if self.enable_rag:
            self.similar_snippets_to_query = self.get_relevant_snippets()

    # Fetch relevant snippets when RAG is enabled
    def get_relevant_snippets(self):
        relevant_snippets = get_relevant_snippets(self.query)
        logger.info(f"Relevant snippets retrieved: {relevant_snippets}")
        return relevant_snippets

    # Method to generate Manim code
    def generate_manim_code(self):
        # Create a message chain inside the method
        messages = [("system", codegen_system_prompt), ("human", self.query)]
        latest_error = self.get_latest_error()

        # Add RAG message if applicable
        if self.enable_rag and not latest_error:
            rag_message = (
                "\nBelow are relevant Manim code snippets. "
                "You can use these snippets as inspiration or guidance when generating the Manim code. "
                "If they are relevant, you can adapt, combine, or modify these examples as needed to best address the user's query. "
                "Remember to maintain the GenerateVideo class name for the scene."
            )
            rag_message += self.similar_snippets_to_query
            messages.append(("human", rag_message))  # Append RAG message as another human prompt
        if latest_error:
            code_tried, error_analysis = latest_error
            error_query = f"I tried this:\n{code_tried} and I received an error. Here is the error analysis: {error_analysis}."
            messages.append(("human", error_query))
        logger.info(f"Query chain: {messages}")
        groq_response = code_generator.invoke(messages)
        logger.info(f"Groq response: {groq_response.content}")
        
        fenced_code_block = groq_response.content.split("```")[1]  # Extract code block
        return fenced_code_block

    # Method to analyze errors and append as a new message in the chat
    def analyze_error_and_update_messages(self, error_log, code_tried):
        messages = [("system", log_analyzer_system_prompt), ("human", error_log)]
        groq_response = error_analyzer.invoke(messages)
        logger.info(f"Groq response: {groq_response}")
        
        # Track the code tried and the error received
        self.errors.append((code_tried, groq_response.content))

        # Return the latest error for appending to query chain in generate function
        latest_error = self.get_latest_error()
        if latest_error:
            return latest_error[1]
        logger.info(f"No errors to update.")
        return None

    # Get the latest error received (most recent entry)
    def get_latest_error(self):
        if self.errors:
            return self.errors[-1]  # Return the most recent (code_tried, error_received) tuple
        else:
            return None

    # Format the Manim code
    @staticmethod
    def format_manim_code(fenced_code_block):
        code_lines = fenced_code_block.split("\n")
        formatted_code = code_lines[1:-1]
        return formatted_code



if __name__ == "__main__":
    pass
