import streamlit as st
import requests

# FastAPI endpoints
user_info_url = "http://localhost:8000/collect_user_info"
query_url = "http://localhost:8000/query"

# Language support setup
languages = {
    "English": {
        "title": "Airbnb Property Search System",
        "title_user": "User Information",
        "name": "Name",
        "max_price": "Max Price per Night",
        "num_guests": "Number of Guests",
        "ask_question": "Enter your question about Airbnb listings",
        "submit_info": "Submit Information",
        "submit_query": "Search Listings",
        "hello": "Hello",
        "please_fill": "Please fill out all required fields and select at least one accessibility amenity.",
        "info_submitted": "User information submitted successfully!"
    },
    "עברית": {
        "title": "מערכת חיפוש נכסים",
        "title_user": "מידע אישי",
        "name": "שם",
        "max_price": "מחיר מקסימלי ללילה",
        "num_guests": "מספר אורחים",
        "ask_question": "שאל את שאלתך על הנכסים",
        "submit_info": "שלח מידע",
        "submit_query": "חפש נכסים",
        "hello": "שלום",
        "please_fill": "אנא מלא את כל השדות הנדרשים",
        "info_submitted": "המידע נשלח בהצלחה!"
    }
}

# Accessibility amenities
accessibility_amenities = [
    "Elevator", "Wheelchair accessible", "Step-free access", "Flat path to front door",
    "Wide doorway", "Accessible-height bed", "Wide clearance to shower",
    "Wide entryway", "Wide hallway clearance", "Wide clearance to bed"
]

# translations
def t(key):
    return languages[st.session_state["language"]][key]

# Set default language and session states
if "language" not in st.session_state:
    st.session_state["language"] = "English"
if "page" not in st.session_state:
    st.session_state["page"] = "user_info"

# Sidebar language selector
st.sidebar.selectbox("Choose Language / בחר שפה", ["English", "עברית"], key="language")

# Collect user information and send it to the FastAPI backend
def user_info_page():
    st.title(t("title_user"))
    name = st.text_input(t("name"))
    max_price = st.number_input(t("max_price"), min_value=0.0, step=1.0)
    num_guests = st.number_input(t("num_guests"), min_value=1, step=1)

    # Accessibility amenities checklist
    selected_amenities = st.multiselect(
        "Select accessibility amenities (must select at least one):",
        accessibility_amenities
    )

    if st.button(t("submit_info")):
        if not name or not selected_amenities:
            st.error(t("please_fill"))
        else:
            user_info = {
                "first_name": name.split()[0],
                "last_name": name.split()[-1] if len(name.split()) > 1 else "",
                "max_price": max_price,
                "num_guests": num_guests,
                "accessibility_amenities": selected_amenities
            }
            response = requests.post(user_info_url, json=user_info)
            if response.ok:
                st.session_state["user_info"] = user_info
                st.session_state["page"] = "search"
                st.success(t("info_submitted"))
                st.rerun()
            else:
                st.error("Failed to submit user information.")

# Search for properties and display the top results
def search_page():
    st.title(t("title"))

    st.sidebar.markdown(
        f"<div class='sidebar-title'>{t('hello')}, {st.session_state['user_info']['first_name']}!</div>",
        unsafe_allow_html=True
    )
    st.sidebar.write(f"Max Price per Night: {st.session_state['user_info']['max_price']}")
    st.sidebar.write(f"Number of Guests: {st.session_state['user_info']['num_guests']}")
    st.sidebar.write(f"Accessibility Amenities: {', '.join(st.session_state['user_info']['accessibility_amenities'])}")

    # User input for the property search query
    user_query = st.text_input(t("ask_question"))

    if st.button(t("submit_query")):
        if user_query:
            query_payload = {
                "query": user_query,
                "user_info": st.session_state["user_info"],
                "conversation_history": []
            }
            response = requests.post(query_url, json=query_payload)

            if response.ok:
                results = response.json().get("response", [])

                if isinstance(results, list) and results:
                    st.write("### Top Recommended Listings")
                    for property_info in results:
                        st.write("#### Listing:", property_info.get("name", "No Name"))
                        st.write(f"**ID**: {property_info.get('_id', 'N/A')}")
                        st.write(f"**URL**: [View Listing]({property_info.get('listing_url', '#')})")
                        st.write(f"**Description**: {property_info.get('description', 'No Description')}")
                        st.write("---")
                else:
                    st.write("No matching listings found.")
            else:
                st.error("Failed to retrieve property listings. Please ensure the server is running and accessible.")

# Route to the appropriate page
if st.session_state["page"] == "user_info":
    user_info_page()
else:
    search_page()
