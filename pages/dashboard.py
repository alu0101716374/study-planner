import streamlit as st
from lib.auth import get_profile
from lib.state_manager import get_repository, reset_profile_cache
from lib.ui import render_sidebar, handle_result
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
        st.markdown(f"""
            <div class="metric-card">
                <div class="card-header">
                    <span>🔥 CURRENT STREAK</span>
                    <span class="badge-red">FIRE</span>
                </div>
                <h2>{profile['streak']} DAYS</h2>
                <p>Longest: {profile['longest_streak']} days</p>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        percent = int(stats['progress_percentage'] * 100)
        st.markdown(f"""
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
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <span>SESSIONS LEFT</span>
                <h2 class="text-blue">{stats['remaining_sessions']} REMAINING</h2>
                <p>Total today: {stats['total_sessions']}</p>
            </div>
        """, unsafe_allow_html=True)

    st.divider()
    st.subheader(f"Today's Logic-Based Schedule ({stats['date']})")
    
    todays_tasks = get_repository().get_todays_sessions(profile['id'])
    
    if not todays_tasks:
        st.info("No study sessions planned for today. High-integrity resting!")
    else:
        for item in todays_tasks:
            task_info = item['tasks']
            is_done = item['is_completed']
            diff_val = task_info['difficulty']
            load_label = ["Very Low", "Low", "Medium", "High", "Critical"][diff_val-1]
            
            with st.container():
                c1, c2, c3, c4 = st.columns([1, 3, 2, 1])
                
                with c1:
                    st.write(f"**{item['hours_allocated']}h**")
                
                with c2:
                    st.write(f"**{task_info['task']}**")
                    st.caption(f"{task_info['subject']}")
                
                with c3:
                    st.markdown(f'<span class="load-badge diff-{diff_val}">LOAD: {load_label}</span>', unsafe_allow_html=True)
                
                with c4:
                    if is_done:
                        st.write("✅")
                    else:
                        if st.button("DONE", key=f"check_{item['id']}"):
                            get_repository().complete_session(item['id'], item['task_id'], item['hours_allocated'], on_success=reset_profile_cache())
                            st.rerun()
                st.markdown("---")

if __name__ == "__main__":
    main()
