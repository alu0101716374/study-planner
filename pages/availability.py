import streamlit as st
from lib.auth import get_user
from lib.ui import handle_result

AVAILABILITY_PREF_OPTIONS = ["No Preference", "Morning", "Afternoon", "Evening"]


def render_availability_ui():
    """
    Renders number inputs and radios for preference, filling them with the current users availability settings. Userscan change these settings, click save, and it updates the database
    """
    st.subheader("Set Your Weekly Availability")
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

    repository = st.session_state.repository
    user = handle_result(get_user())

    if "current_availability" not in st.session_state or st.session_state.reload_availability:
        st.session_state.current_availability = repository.get_user_availability(user_id=user.id)
        st.session_state.reload_availability = False

    loaded_availability = st.session_state.current_availability

    weekly_data = {}
    for day in days:
        default_hours = loaded_availability.get(day, {}).get("hours")
        # Ensure default preference string is normalized for comparison
        default_pref_str = loaded_availability.get(day, {}).get(
            "preference", AVAILABILITY_PREF_OPTIONS[0]
        )

        default_pref_idx = (
            AVAILABILITY_PREF_OPTIONS.index(default_pref_str)
            if default_pref_str in AVAILABILITY_PREF_OPTIONS
            else 0
        )

        col1, col2 = st.columns(2)
        with col1:

            h = st.number_input(
                f"Hours: {day}", 0.0, 24.0, value=default_hours, step=0.5, key=f"h_{day}"
            )
        with col2:
            p = st.selectbox(
                f"Pref: {day}", AVAILABILITY_PREF_OPTIONS, index=default_pref_idx, key=f"p_{day}"
            )

        weekly_data[day] = {
            "hours": h,
            "preference": None if p == AVAILABILITY_PREF_OPTIONS[0] else p.lower(),
        }

    if st.button("Save Changes"):
        repository.update_user_availability(user_id=user.id, availability_data=weekly_data)
        st.success("Availability updated successfully!")
        st.session_state.reload_availability = True
        st.rerun()

    st.divider()

    st.subheader("Fill: Set Whole Week")
    b_col1, b_col2 = st.columns(2)
    with b_col1:
        blanket_hours = st.number_input(
            "Hours for ALL days", 0.0, 24.0, step=0.5, key="blanket_hours"
        )
    with b_col2:
        blanket_pref = st.selectbox(
            "Preference for ALL days", AVAILABILITY_PREF_OPTIONS, key="blanket_pref"
        )

    if st.button("Apply to All Days & Save"):
        final_pref = None if blanket_pref == AVAILABILITY_PREF_OPTIONS[0] else blanket_pref.lower()

        updated_weekly_data_for_blanket = {}
        for day in days:
            updated_weekly_data_for_blanket[day] = {
                "hours": blanket_hours,
                "preference": final_pref,
            }

        repository.update_user_availability(
            user_id=user.id, availability_data=updated_weekly_data_for_blanket
        )
        st.success("Blanket availability updated successfully!")
        st.session_state.reload_availability = True
        st.rerun()


def main():
    st.title("Your Weekly Availability")
    if "reload_availability" not in st.session_state:
        st.session_state.reload_availability = True
    render_availability_ui()


if __name__ == "__main__":
    main()
