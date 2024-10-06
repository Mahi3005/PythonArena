import streamlit as st
from transformers import pipeline  # Import pipeline from transformers
import os
import json
from typing import Dict


class HuggingFaceChallengeGenerator:
    def __init__(self):
        # Create a pipeline for text generation using a pre-trained language model from Hugging Face
        self.generator = pipeline("text-generation", model="distilgpt2")  # or "EleutherAI/gpt-neo-2.7B"


    def generate_challenge(self, difficulty: str = "medium") -> Dict:
        prompt = f"""Generate a {difficulty} Python coding challenge in JSON format. 
        The JSON object should contain the following keys:
        - 'description': A string describing the challenge
        - 'function_signature': The function name and parameters
        - 'test_cases': A list of dictionaries, each containing:
          - 'inputs': The inputs for the test case
          - 'expected_output': The expected output for the test case

        Format your response as a JSON object, without additional text."""

        # Generate the challenge using the Hugging Face model
        try:
            result = self.generator(prompt, max_length=300, num_return_sequences=1)
            raw_text = result[0]['generated_text']
            st.write("Generated Text:", raw_text)  # Display the generated text on Streamlit for debugging

            # Validate if the generated text starts and ends with curly braces (indicating a JSON object)
            if not (raw_text.startswith("{") and raw_text.endswith("}")):
                st.error("Generated text is not a valid JSON object. Please check the model's output.")
                return None

            # Try to parse the generated text as JSON
            challenge_dict = json.loads(raw_text)
            return challenge_dict

        except json.JSONDecodeError as json_err:
            st.error(f"JSON parsing error: {str(json_err)}. The generated text might not be in the correct format.")
        except Exception as e:
            st.error(f"Error generating challenge: {str(e)}")

        return None

    def evaluate_solution(self, challenge: Dict, user_code: str) -> Dict:
        # Since Hugging Face models can't evaluate code directly, let's create a prompt for it
        prompt = f"""Evaluate this Python code for the following challenge:
        Challenge: {challenge['description']}
        User's code:
        {user_code}

        Test cases: {challenge['test_cases']}

        Provide the evaluation results as a Python dictionary with keys:
        'passed_tests' (list of test case indices that passed),
        'failed_tests' (list of test case indices that failed),
        'feedback' (string with overall feedback and suggestions for improvement)."""

        # Generate feedback using the Hugging Face model
        try:
            result = self.generator(prompt, max_length=300, num_return_sequences=1)
            evaluation_results = json.loads(result[0]['generated_text'])
            return evaluation_results
        except Exception as e:
            st.error(f"Error evaluating solution: {str(e)}")
            return None


def local_css(file_name):
    with open(file_name, "r") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def display_leaderboard():
    st.subheader("Leaderboard")
    if 'leaderboard' not in st.session_state:
        st.session_state.leaderboard = []

    for i, entry in enumerate(st.session_state.leaderboard):
        st.write(f"{i + 1}. {entry['name']} - {entry['score']} points")


def update_leaderboard(name, score):
    if 'leaderboard' not in st.session_state:
        st.session_state.leaderboard = []

    st.session_state.leaderboard.append({'name': name, 'score': score})
    st.session_state.leaderboard.sort(key=lambda x: x['score'], reverse=True)
    st.session_state.leaderboard = st.session_state.leaderboard[:10]  # Keep top 10


def main():
    st.set_page_config(page_title="PythonDuel: AI vs Human", layout="wide")
    local_css("style.css")

    st.title("🐍 PythonDuel: Challenge the AI")
    st.markdown("### Test your Python skills against our AI opponent!")

    if 'challenge' not in st.session_state:
        st.session_state.challenge = None
    if 'evaluation' not in st.session_state:
        st.session_state.evaluation = None

    with st.sidebar:
        st.header("Settings")
        difficulty = st.select_slider("Select Difficulty", options=["easy", "medium", "hard"])
        user_name = st.text_input("Your Name", value="Anonymous")

        if st.button("Generate New Challenge"):
            with st.spinner("Generating challenge..."):
                generator = HuggingFaceChallengeGenerator()
                st.session_state.challenge = generator.generate_challenge(difficulty)
                st.session_state.evaluation = None

    col1, col2 = st.columns([3, 2])

    with col1:
        st.header("Challenge")
        if st.session_state.challenge:
            st.markdown(f"**Description:** {st.session_state.challenge['description']}")
            st.markdown(f"**Function Signature:** `{st.session_state.challenge['function_signature']}`")

            st.subheader("Your Code")
            user_code = st.text_area("Write your Python code here:", height=300)

            if st.button("Submit Solution"):
                if not user_code.strip():
                    st.error("Please enter your code before submitting.")
                else:
                    with st.spinner("Evaluating your solution..."):
                        generator = HuggingFaceChallengeGenerator()
                        st.session_state.evaluation = generator.evaluate_solution(st.session_state.challenge, user_code)
                        if st.session_state.evaluation:
                            score = len(st.session_state.evaluation['passed_tests']) * 10
                            update_leaderboard(user_name, score)
        else:
            st.info("Generate a new challenge to start coding!")

    with col2:
        st.header("Test Cases & Results")
        if st.session_state.challenge:
            for i, test_case in enumerate(st.session_state.challenge['test_cases']):
                with st.expander(f"Test Case {i + 1}"):
                    st.write(f"Input: {test_case['inputs']}")
                    st.write(f"Expected Output: {test_case['expected_output']}")

        if st.session_state.evaluation:
            st.subheader("Evaluation Results")
            st.markdown(f"**Passed Tests:** {', '.join(map(str, st.session_state.evaluation['passed_tests']))}")
            st.markdown(f"**Failed Tests:** {', '.join(map(str, st.session_state.evaluation['failed_tests']))}")
            st.markdown("**Feedback:**")
            st.write(st.session_state.evaluation['feedback'])

        display_leaderboard()

    st.markdown("---")
    st.markdown(
        "Created with ❤️ by Your Team | [GitHub](https://github.com/your-repo) | [About Us](https://your-website.com)")


if __name__ == "__main__":
    main()
