import streamlit as st
import openai
from typing import Dict
import time


class OpenAIChallengeGenerator:
    def __init__(self, api_key: str):
        openai.api_key = api_key

    def generate_challenge(self, difficulty: str = "medium") -> Dict:
        prompt = f"""Generate a {difficulty} Python coding challenge. 
        Include:
        1. A problem description
        2. Function signature (name and parameters)
        3. 3 test cases with inputs and expected outputs
        Format the response as a Python dictionary."""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a Python expert creating coding challenges."},
                {"role": "user", "content": prompt}
            ]
        )

        # Parse the response and structure it as needed
        challenge_dict = eval(response.choices[0].message.content)
        return challenge_dict

    def evaluate_solution(self, challenge: Dict, user_code: str) -> Dict:
        prompt = f"""Evaluate this Python code for the following challenge:
        Challenge: {challenge['description']}
        User's code:
        {user_code}

        Test cases: {challenge['test_cases']}

        Provide the evaluation results as a Python dictionary with keys:
        'passed_tests' (list of test case indices that passed),
        'failed_tests' (list of test case indices that failed),
        'feedback' (string with overall feedback and suggestions for improvement)."""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a Python expert evaluating code submissions."},
                {"role": "user", "content": prompt}
            ]
        )

        # Parse the response and structure it as needed
        evaluation_results = eval(response.choices[0].message.content)
        return evaluation_results


# Custom CSS to enhance the design
def local_css(file_name):
    with open(file_name, "r") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def main():
    st.set_page_config(page_title="PythonDuel: AI vs Human", layout="wide")
    local_css("style.css")  # Make sure to create this CSS file

    st.title("🐍 PythonDuel: Challenge the AI")
    st.markdown("### Test your Python skills against our AI opponent!")

    # Initialize session state
    if 'challenge' not in st.session_state:
        st.session_state.challenge = None
    if 'evaluation' not in st.session_state:
        st.session_state.evaluation = None

    # Sidebar for API key and difficulty selection
    with st.sidebar:
        st.header("Settings")
        api_key = st.text_input("Enter your OpenAI API Key", type="password")
        difficulty = st.select_slider("Select Difficulty", options=["easy", "medium", "hard"])

        if st.button("Generate New Challenge"):
            with st.spinner("Generating challenge..."):
                generator = OpenAIChallengeGenerator(api_key)
                st.session_state.challenge = generator.generate_challenge(difficulty)
                st.session_state.evaluation = None  # Reset evaluation

    # Main content area
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
                        generator = OpenAIChallengeGenerator(api_key)
                        st.session_state.evaluation = generator.evaluate_solution(st.session_state.challenge, user_code)
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

    # Footer
    st.markdown("---")
    st.markdown(
        "Created with ❤️ by Your Team | [GitHub](https://github.com/your-repo) | [About Us](https://your-website.com)")


if __name__ == "__main__":
    main()