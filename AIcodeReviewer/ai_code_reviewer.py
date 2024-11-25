import streamlit as st
import google.generativeai as genai
import re
from typing import Dict, Tuple

# Set your Gemini API key directly
GEMINI_API_KEY = ""  #add your API key

class CodeReviewer:
    def __init__(self):
        """Initialize the CodeReviewer with Gemini AI."""
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
        
    def review_code(self, code: str) -> Tuple[Dict, str]:
        """
        Review the provided code using Gemini AI.
        Returns a tuple of (issues_dict, fixed_code).
        """
        try:
            # Prompt engineering for better code review results
            prompt = f"""
            Please review the following Python code and provide:
            1. A list of potential bugs and issues
            2. Code quality improvements
            3. A corrected version of the code
            
            Here's the code to review:
            ```python
            {code}
            ```
            
            Please format your response exactly as shown below:
            ISSUES:
            - [issue description]
            
            IMPROVEMENTS:
            - [improvement suggestion]
            
            FIXED_CODE:
            ```python
            [corrected code]
            ```
            
            Please ensure to maintain this exact format in your response.
            """
            
            # Get response from Gemini
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            # Initialize dictionary to store issues
            issues = {'bugs': [], 'improvements': []}
            
            # Extract issues
            issues_match = re.findall(r'ISSUES:\n(.*?)(?=IMPROVEMENTS:|FIXED_CODE:|$)', response_text, re.DOTALL)
            if issues_match:
                issues['bugs'] = [bug.strip() for bug in issues_match[0].split('\n') if bug.strip()]

            # Extract improvements
            improvements_match = re.findall(r'IMPROVEMENTS:\n(.*?)(?=FIXED_CODE:|$)', response_text, re.DOTALL)
            if improvements_match:
                issues['improvements'] = [imp.strip() for imp in improvements_match[0].split('\n') if imp.strip()]
            
            # Extract fixed code
            fixed_code_match = re.findall(r'```python\n(.*?)```', response_text, re.DOTALL)
            fixed_code = fixed_code_match[-1].strip() if fixed_code_match else ""
            
            return issues, fixed_code
        
        except Exception as e:
            st.error(f"Error during code review: {str(e)}")
            return {"bugs": [], "improvements": []}, ""


def main():
    st.set_page_config(
        page_title="AI Code Reviewer",
        page_icon="🔍",
        layout="wide"
    )
    
    st.title("🔍 AI Code Reviewer")
    st.markdown("""
    Submit your Python code for an AI-powered review using Google's Gemini AI.
    Get feedback on potential bugs, improvements, and see suggested fixes.
    """)
    
    # Main content area
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("📝 Enter Your Code")
        user_code = st.text_area(
            "Paste your Python code here",
            height=200,
            placeholder="# Paste your Python code here..."
        )
        
        if st.button("Review Code", type="primary"):
            if not user_code.strip():
                st.warning("Please enter some code to review.")
                return
                
            with st.spinner("Reviewing your code..."):
                reviewer = CodeReviewer()
                issues, fixed_code = reviewer.review_code(user_code)
                
                # Store results in session state for display
                if issues:  # Make sure issues is not None
                    st.session_state.issues = issues
                if fixed_code:
                    st.session_state.fixed_code = fixed_code
                
    with col2:
        st.header("📊 Review Results")
        
        # Check if 'issues' and 'fixed_code' are in session_state and not None
        if st.session_state.get('issues'):
            # Display issues and improvements
            st.subheader("🐛 Potential Bugs")
            for bug in st.session_state.issues['bugs']:
                if bug.strip():  # Skip empty lines
                    st.markdown(f"- {bug.strip('- ')}")
                    
            st.subheader("💡 Suggested Improvements")
            for improvement in st.session_state.issues['improvements']:
                if improvement.strip():  # Skip empty lines
                    st.markdown(f"- {improvement.strip('- ')}")
            
            # Display fixed code
            st.subheader("✨ Improved Code")
            if st.session_state.get('fixed_code'):
                st.code(st.session_state.fixed_code, language="python")

def initialize_session_state():
    """Initialize session state variables."""
    if 'issues' not in st.session_state or st.session_state.issues is None:
        st.session_state.issues = {'bugs': [], 'improvements': []}
    if 'fixed_code' not in st.session_state or st.session_state.fixed_code is None:
        st.session_state.fixed_code = ""
            
if __name__ == "__main__":
    initialize_session_state()
    main()
