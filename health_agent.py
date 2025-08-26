import os
import streamlit as st
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.google import Gemini

# Load the Gemini API key from .env file
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

st.set_page_config(
    page_title="AI Health & Fitness Planner",
    page_icon="🏋️‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main { padding: 2rem; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; }
    .success-box { padding: 1rem; border-radius: 0.5rem; background-color: #f0fff4; border: 1px solid #9ae6b4; }
    .warning-box { padding: 1rem; border-radius: 0.5rem; background-color: #fffaf0; border: 1px solid #fbd38d; }
    div[data-testid="stExpander"] div[role="button"] p { font-size: 1.1rem; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

def display_dietary_plan(plan_content):
    with st.expander("📋 Your Personalized Dietary Plan", expanded=True):
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("### 🎯 Why this plan works")
            st.info(plan_content.get("why_this_plan_works", "Information not available"))
            st.markdown("### 🍽️ Meal Plan")
            st.write(plan_content.get("meal_plan", "Plan not available"))
        with col2:
            st.markdown("### ⚠️ Important Considerations")
            for item in plan_content.get("important_considerations", "").split("\n"):
                if item.strip():
                    st.warning(item)

def display_fitness_plan(plan_content):
    with st.expander("💪 Your Personalized Fitness Plan", expanded=True):
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("### 🎯 Goals")
            st.success(plan_content.get("goals", "Goals not specified"))
            st.markdown("### 🏋️‍♂️ Exercise Routine")
            st.write(plan_content.get("routine", "Routine not available"))
        with col2:
            st.markdown("### 💡 Pro Tips")
            for tip in plan_content.get("tips", "").split("\n"):
                if tip.strip():
                    st.info(tip)

def main():
    if not GEMINI_API_KEY:
        st.error("🔐 Gemini API Key not found. Please check your .env file.")
        return

    try:
        gemini_model = Gemini(id="gemini-2.5-flash-preview-05-20", api_key=GEMINI_API_KEY)
    except Exception as e:
        st.error(f"❌ Failed to initialize Gemini model: {e}")
        return

    if 'dietary_plan' not in st.session_state:
        st.session_state.dietary_plan = {}
        st.session_state.fitness_plan = {}
        st.session_state.qa_pairs = []
        st.session_state.plans_generated = False

    st.title("🏋️‍♂️ AI Health & Fitness Planner")
    st.markdown("""
        <div style='background-color: #00008B; padding: 1rem; border-radius: 0.5rem; margin-bottom: 2rem; color: white;'>
        Get personalized dietary and fitness plans tailored to your goals and preferences.
        Our AI-powered system considers your unique profile to create the perfect plan for you.
        </div>
    """, unsafe_allow_html=True)

    st.header("👤 Your Profile")
    col1, col2 = st.columns(2)

    with col1:
        age = st.number_input("Age", min_value=10, max_value=100, step=1)
        height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, step=0.1)
        activity_level = st.selectbox("Activity Level", ["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Extremely Active"])
        dietary_preferences = st.selectbox("Dietary Preferences", ["Vegetarian", "Keto", "Gluten Free", "Low Carb", "Dairy Free"])

    with col2:
        weight = st.number_input("Weight (kg)", min_value=20.0, max_value=300.0, step=0.1)
        sex = st.selectbox("Sex", ["Male", "Female", "Other"])
        fitness_goals = st.selectbox("Fitness Goals", ["Lose Weight", "Gain Muscle", "Endurance", "Stay Fit", "Strength Training"])

    if st.button("🎯 Generate My Personalized Plan", use_container_width=True):
        with st.spinner("Creating your perfect health and fitness routine..."):
            try:
                user_profile = f"""
                Age: {age}
                Weight: {weight}kg
                Height: {height}cm
                Sex: {sex}
                Activity Level: {activity_level}
                Dietary Preferences: {dietary_preferences}
                Fitness Goals: {fitness_goals}
                """

                dietary_agent = Agent(
                    name="Dietary Expert",
                    role="Provides personalized dietary recommendations",
                    model=gemini_model,
                    instructions=[
                        "Consider the user's input, including dietary restrictions and preferences.",
                        "Suggest a detailed meal plan for the day, including breakfast, lunch, dinner, and snacks.",
                        "Provide a brief explanation of why the plan is suited to the user's goals.",
                        "Focus on clarity, coherence, and quality of the recommendations."
                    ]
                )

                fitness_agent = Agent(
                    name="Fitness Expert",
                    role="Provides personalized fitness recommendations",
                    model=gemini_model,
                    instructions=[
                        "Provide exercises tailored to the user's goals.",
                        "Include warm-up, main workout, and cool-down exercises.",
                        "Explain the benefits of each recommended exercise.",
                        "Ensure the plan is actionable and detailed."
                    ]
                )

                dietary_plan = {
                    "why_this_plan_works": "High Protein, Healthy Fats, Moderate Carbohydrates, and Caloric Balance",
                    "meal_plan": dietary_agent.run(user_profile).content,
                    "important_considerations": """
                    - Hydration: Drink plenty of water throughout the day
                    - Electrolytes: Monitor sodium, potassium, and magnesium levels
                    - Fiber: Ensure adequate intake through vegetables and fruits
                    - Listen to your body: Adjust portion sizes as needed
                    """
                }

                fitness_plan = {
                    "goals": "Build strength, improve endurance, and maintain overall fitness",
                    "routine": fitness_agent.run(user_profile).content,
                    "tips": """
                    - Track your progress regularly
                    - Allow proper rest between workouts
                    - Focus on proper form
                    - Stay consistent with your routine
                    """
                }

                st.session_state.dietary_plan = dietary_plan
                st.session_state.fitness_plan = fitness_plan
                st.session_state.plans_generated = True
                st.session_state.qa_pairs = []

                display_dietary_plan(dietary_plan)
                display_fitness_plan(fitness_plan)

            except Exception as e:
                st.error(f"❌ An error occurred while generating plans: {e}")

    if st.session_state.plans_generated:
        st.header("❓ Questions about your plan?")
        question = st.text_input("Ask your question below:")

        if st.button("Get Answer"):
            if question:
                with st.spinner("Finding the best answer..."):
                    try:
                        context = f"""
                        Dietary Plan: {st.session_state.dietary_plan.get('meal_plan')}
                        Fitness Plan: {st.session_state.fitness_plan.get('routine')}
                        User Question: {question}
                        """
                        agent = Agent(model=gemini_model, show_tool_calls=True, markdown=True)
                        answer = agent.run(context).content
                        st.session_state.qa_pairs.append((question, answer))
                    except Exception as e:
                        st.error(f"❌ Failed to get answer: {e}")

        if st.session_state.qa_pairs:
            st.header("💬 Q&A History")
            for q, a in st.session_state.qa_pairs:
                st.markdown(f"**Q:** {q}")
                st.markdown(f"**A:** {a}")

if __name__ == "__main__":
    main()
