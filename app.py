from dotenv import load_dotenv
import streamlit as st
import os
import google.generativeai as genai
from PIL import Image

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")

# ------------------------------
# Helper functions
# ------------------------------

def get_gemini_response(prompt, image_data=None):

    content = [prompt]

    if image_data:
        content.extend(image_data)

    response = model.generate_content(content)

    return response.text


def input_image_setup(uploaded_file):

    if uploaded_file is not None:

        bytes_data = uploaded_file.getvalue()

        image_parts = [{
            "mime_type": uploaded_file.type,
            "data": bytes_data
        }]

        return image_parts

    return None


# ------------------------------
# Streamlit UI
# ------------------------------

st.set_page_config(page_title="AI Health Companion", layout="wide")

st.header("🤖 AI Health Companion")

# ------------------------------
# SIDEBAR PROFILE
# ------------------------------

with st.sidebar:

    st.subheader("Your Health Profile")

    health_goals = st.text_area(
        "Health Goals",
        value="Lose 5kg in 2 months\nImprove stamina"
    )

    medical_conditions = st.text_area(
        "Medical Conditions",
        value="None"
    )

    fitness_routines = st.text_area(
        "Fitness Routines",
        value="30-minute walk 3x/week"
    )

    food_preferences = st.text_area(
        "Food Preferences",
        value="Vegetarian"
    )

    restrictions = st.text_area(
        "Dietary Restrictions",
        value="No dairy"
    )

    if st.button("Update Profile"):

        st.session_state.health_profile = {
            "goals": health_goals,
            "conditions": medical_conditions,
            "routines": fitness_routines,
            "preferences": food_preferences,
            "restrictions": restrictions
        }

        st.success("Profile updated!")


if "health_profile" not in st.session_state:

    st.session_state.health_profile = {
        "goals": health_goals,
        "conditions": medical_conditions,
        "routines": fitness_routines,
        "preferences": food_preferences,
        "restrictions": restrictions
    }

# ------------------------------
# TABS
# ------------------------------

tab1, tab2, tab3 = st.tabs([
    "Meal Planning",
    "Food Analysis",
    "Health Insights"
])

# =================================================
# TAB 1 : MEAL PLAN
# =================================================

with tab1:

    st.subheader("Personalized Meal Planning")

    col1, col2 = st.columns(2)

    with col1:

        user_input = st.text_area(
            "Describe any additional requirements",
            placeholder="e.g., quick meals for busy days"
        )

    with col2:

        st.write("### Your Health Profile")
        st.json(st.session_state.health_profile)

    if st.button("Generate Personalized Meal Plan"):

        with st.spinner("Generating your meal plan..."):

            prompt = f"""
Create a personalized meal plan based on the following health profile.

Health Goals:
{st.session_state.health_profile['goals']}

Medical Conditions:
{st.session_state.health_profile['conditions']}

Fitness Routine:
{st.session_state.health_profile['routines']}

Food Preferences:
{st.session_state.health_profile['preferences']}

Dietary Restrictions:
{st.session_state.health_profile['restrictions']}

Additional Requirements:
{user_input}

Provide:

1. 7-day meal plan (breakfast, lunch, dinner, snacks)
2. Daily nutritional breakdown (calories, protein, carbs, fat)
3. Explanation for food choices
4. Grocery shopping list
5. Preparation tips
"""

            response = get_gemini_response(prompt)

            st.subheader("Your Personalized Meal Plan")

            st.markdown(response)

            st.download_button(
                label="Download Meal Plan",
                data=response,
                file_name="meal_plan.txt",
                mime="text/plain"
            )

# =================================================
# TAB 2 : FOOD IMAGE ANALYSIS
# =================================================

with tab2:

    st.subheader("Food Analysis")

    uploaded_file = st.file_uploader(
        "Upload an image of your food",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_file is not None:

        image = Image.open(uploaded_file)

        st.image(image, caption="Uploaded Food Image")

    if st.button("Analyze Food"):

        if uploaded_file is None:

            st.warning("Please upload an image")

        else:

            with st.spinner("Analyzing food..."):

                image_data = input_image_setup(uploaded_file)

                prompt = """
You are a nutrition expert.

Analyze the uploaded food image and provide:

1. Estimated calories
2. Macronutrient breakdown
3. Health benefits
4. Possible concerns
5. Portion recommendations
"""

                response = get_gemini_response(prompt, image_data)

                st.subheader("Food Analysis Results")

                st.markdown(response)

# =================================================
# TAB 3 : HEALTH INSIGHTS
# =================================================

with tab3:

    st.subheader("Health Insights")

    health_query = st.text_input(
        "Ask any health or nutrition question",
        placeholder="e.g., How can I improve low blood pressure?"
    )

    if st.button("Get Expert Insights"):

        if not health_query:

            st.warning("Please enter a question")

        else:

            with st.spinner("Analyzing your question..."):

                prompt = f"""
You are a certified nutritionist and health expert.

Answer the following question:

{health_query}

Consider the user's health profile:

{st.session_state.health_profile}

Provide:

1. Scientific explanation
2. Practical advice
3. Precautions
4. Food recommendations
"""

                response = get_gemini_response(prompt)

                st.subheader("Expert Health Insights")

                st.markdown(response)