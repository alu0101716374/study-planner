import streamlit as st
from lib.auth import get_profile
from lib.state_manager import get_repository
from lib.ui import render_sidebar, handle_result, render_session
from services.schedule_service import get_daily_stats


def main():
    render_sidebar()
    profile = handle_result(get_profile())
    stats = get_daily_stats(get_repository())

    st.title("📚 Study Dashboard")
    st.caption("Focus on your goals without the burnout.")

    col1, col2, col3 = st.columns(3)
    print(stats)
    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="card-header">
                    <span>🔥 CURRENT STREAK</span>
                    <span class="badge-red">FIRE</span>
                </div>
                <h2>{profile['streak']} DAYS</h2>
                <p>Longest: {profile['longest_streak']} days</p>
            </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        percent = int(stats["progress_percentage"] * 100)
        st.markdown(
            f"""
            <div class="metric-card flex-row">
                <svg width="60" height="60" viewBox="0 0 36 36" class="circular-chart">
                    <path class="circle-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                    <path class="circle-progress" stroke-dasharray="{percent}, 100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                </svg>
                <div>
                    <span>DAILY PROGRESS</span>
                    <h2>{percent}%</h2>
                    <p>{stats['completed_sessions']}/{stats['total_sessions']} Sessions</p>
                </div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <span>SESSIONS LEFT</span>
                <h2 class="text-blue">{stats['remaining_sessions']} REMAINING</h2>
                <p>Total today: {stats['total_sessions']}</p>
            </div>
        """,
            unsafe_allow_html=True,
        )

    st.divider()
    st.subheader(f"Today's Logic-Based Schedule ({stats['date']})")

    todays_sessions = get_repository().get_todays_sessions_as_objects(profile["id"])
    if not todays_sessions:
        st.info("No study sessions planned for today. High-integrity resting!")
    else:
        for task in todays_sessions:
            render_session(task)


if __name__ == "__main__":
    main()
