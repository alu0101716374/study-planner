import streamlit as st
from lib.auth import get_user
from lib.ui import handle_result, render_sidebar

def main():
    render_sidebar()
    user = handle_result(get_user())
    if user:
        st.rerun()

    st.markdown('<div id="hero-container">', unsafe_allow_html=True)
    st.title("Smart Study Planner: Optimize your schedule")
    st.write("Stop Planning. Start Studying. Maximize efficiency, eliminate burnout.")

    if st.button("Log In / Sign Up", type="primary"):
        st.switch_page("pages/login.py")
    st.markdown('</div>', unsafe_allow_html=True)


    st.divider()

    # Core Features
    st.header("Core Features")
    st.write("An intelligent approach to academic management.")

    f_col1, f_col2, f_col3 = st.columns(3)

    with f_col1:
        st.markdown('''
            <div class="feature-card">
                <h3>Dynamic Task Management</h3>
                <p>Track complex projects with integrated deadline, subject, and difficulty weighting.</p>
            </div>
        ''', unsafe_allow_html=True)

    with f_col2:
        st.markdown('''
            <div class="feature-card">
                <h3>Smart Scheduling</h3>
                <p>AI-assisted optimization that mathematically balances urgency and remaining workload.</p>
            </div>
        ''', unsafe_allow_html=True)

    with f_col3:
        st.markdown('''
            <div class="feature-card">
                <h3>Availability Mapping</h3>
                <p>A flexible interface that adapts to your daily time constraints in real-time.</p>
            </div>
        ''', unsafe_allow_html=True)

    st.divider()

    # The Logic Section
    st.header("The Logic: Adaptive Optimization")

    l_col1, l_col2 = st.columns([3, 2])

    with l_col1:
        st.subheader("From To-Do Lists to Optimization Engines")
        st.write("""
        The Study Planner doesn't just list tasks—it solves a multi-variable optimization problem.
        """)
        st.markdown("""
        - **Adaptive Urgency:** Deadlines trigger automatic priority boosts.
        - **Cognitive Load Balancing:** Subject rotation to avoid plateaus.
        - **Dynamic Workload:** Automatic reallocation if you fall behind.
        """)

    with l_col2:
        st.info("**Algorithm Visualization:** The scheduler continuously reallocates study blocks based on your real-time progress.")

    st.divider()

    # Footer
    st.markdown('<div id="footer-container">', unsafe_allow_html=True)
    if st.button("Get Started for Free", key="footer_btn"):
        st.switch_page("pages/login.py")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        "<p style='text-align: center; margin-top: 1rem; color: #64748b;'>"
        "<a href='https://github.com/alu0101716374/study-planner/' target='_blank'>View Code on GitHub</a>"
        "</p>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()