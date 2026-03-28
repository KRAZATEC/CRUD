import streamlit as st
import pandas as pd
from datetime import datetime
from task_manager import TaskManager, FileStorage, Task, TASKS_FILE

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Task Manager Pro",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- DARK MODE STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

    /* Global Font & App Dark Background */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif !important;
        color: #E0E0E0 !important;
    }
    
    .stApp {
        background: radial-gradient(circle at top right, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        color: #E0E0E0;
    }
    
    /* Header Gradient Text for Dark Theme */
    h1, h2, h3 {
        background: -webkit-linear-gradient(45deg, #00d2ff, #3a7bd5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0b0f19 0%, #1a1a2e 100%);
        border-right: 1px solid #1f2937;
    }
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] .st-emotion-cache-16idsys p {
        background: none;
        -webkit-text-fill-color: #E2E2E9;
        color: #E2E2E9;
    }

    /* Vibrant Metrics Cards in Sidebar */
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        padding: 15px 20px;
        border-radius: 12px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #E0E0E0;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.5);
    }
    div[data-testid="metric-container"] label {
        color: #00d2ff !important;
        font-weight: 800 !important;
        font-size: 1.1rem;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-weight: 800 !important;
    }

    /* Special alternating metric colors via nth-child logic */
    div.st-emotion-cache-1wmy9hl:nth-child(2) div[data-testid="metric-container"] {
        background: rgba(0, 210, 255, 0.05);
        border: 1px solid rgba(0, 210, 255, 0.2);
    }
    div.st-emotion-cache-1wmy9hl:nth-child(2) div[data-testid="metric-container"] label {
        color: #536DFE !important;
    }
    div.st-emotion-cache-1wmy9hl:nth-child(3) div[data-testid="metric-container"] {
        background: rgba(0, 255, 135, 0.05);
        border: 1px solid rgba(0, 255, 135, 0.2);
    }
    div.st-emotion-cache-1wmy9hl:nth-child(3) div[data-testid="metric-container"] label {
        color: #00FF87 !important;
    }

    /* Expander Container (Task Cards) */
    .streamlit-expanderHeader {
        background-color: rgba(30,30,45, 0.7);
        border-radius: 12px;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: #E0E0E0 !important;
        border: 1px solid #2b2b40;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        transition: 0.3s;
    }
    .streamlit-expanderHeader:hover {
        border: 1px solid #536DFE;
        background-color: #1e1e2d;
    }
    .streamlit-expanderContent {
        background-color: rgba(15, 15, 25, 0.6);
        backdrop-filter: blur(10px);
        border-bottom-left-radius: 12px;
        border-bottom-right-radius: 12px;
        border: 1px solid #2b2b40;
        border-top: none;
        padding: 1rem;
        color: #D1D5DB;
    }
    
    /* Input Fields for Dark Mode */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div, .stDateInput>div>div>input {
        border-radius: 10px;
        border: 1px solid #374151;
        background-color: #111827 !important;
        color: #F9FAFB !important;
    }
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #00d2ff;
        box-shadow: 0 0 0 2px rgba(0, 210, 255, 0.2);
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        background: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        border-radius: 12px 12px 0 0;
        background-color: rgba(255,255,255,0.05);
        border: 1px solid transparent;
        border-bottom: none;
        padding: 0 25px;
        font-weight: 600;
        letter-spacing: 0.5px;
        color: #9CA3AF;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(30, 30, 45, 0.8);
        color: #00d2ff !important;
        border: 1px solid #374151;
        border-bottom: 3px solid #00d2ff !important;
    }

    /* Badges Layout */
    .badge {
        padding: 6px 14px;
        border-radius: 20px;
        color: white;
        font-size: 0.85em;
        font-weight: 800;
        letter-spacing: 0.5px;
        display: inline-block;
        box-shadow: 0 2px 6px rgba(0,0,0,0.3);
    }
    /* Adjusted Badges for Dark Mode Contrast */
    .badge.critical { background: linear-gradient(45deg, #FF0055 0%, #FF5A5F 100%); }
    .badge.high { background: linear-gradient(45deg, #FF6B00 0%, #FFA500 100%); }
    .badge.medium { background: linear-gradient(45deg, #00C6FF 0%, #0072FF 100%); }
    .badge.low { background: linear-gradient(45deg, #00B4DB 0%, #0083B0 100%); }

    .badge.completed { background: linear-gradient(45deg, #11998E 0%, #38EF7D 100%); }
    .badge.inprogress { background: linear-gradient(45deg, #F2C94C 0%, #F2994A 100%); color: #111; }
    .badge.pending { background: linear-gradient(45deg, #8E2DE2 0%, #4A00E0 100%); }
    .badge.cancelled { background: linear-gradient(45deg, #CB2D3E 0%, #EF473A 100%); }
</style>
""", unsafe_allow_html=True)

# Toggle dark theme using Streamlit configuration
# Note: Streamlit handles system/light/dark via Settings properly, but our custom CSS forces the dark aesthetic!

# --- STATE MANAGEMENT ---
@st.cache_resource
def get_manager():
    """Load the task manager once and persist it across reruns."""
    storage = FileStorage(TASKS_FILE)
    return TaskManager(storage)

manager = get_manager()

def trigger_rerun():
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()

# --- HELPER FUNCS ---
def get_priority_badge(priority: str) -> str:
    p = priority.lower()
    return f'<span class="badge {p}">{priority}</span>'

def get_status_badge(status: str) -> str:
    s = status.replace(" ", "").lower()
    return f'<span class="badge {s}">{status}</span>'

# --- SIDEBAR: DASHBOARD & STATS ---
with st.sidebar:
    st.markdown("<h1>✦ Task Manager</h1>", unsafe_allow_html=True)
    st.markdown("<p style='margin-top:-15px; margin-bottom: 20px; opacity:0.6;'>Manage your flow in the dark.</p>", unsafe_allow_html=True)
    
    st.markdown("<h2>📊 Insights</h2>", unsafe_allow_html=True)
    stats = manager.stats()
    
    # Render Custom Metrics
    st.metric(label="🎯 Total Overview", value=f"{stats['total']} Tasks")
    
    st.markdown("<br><h3>🚦 By Status</h3>", unsafe_allow_html=True)
    for s, count in stats["by_status"].items():
        if count > 0:
            st.metric(label=s, value=count)
            
    st.markdown("<br><h3>🔥 By Priority</h3>", unsafe_allow_html=True)
    for p, count in stats["by_priority"].items():
        if count > 0:
            st.metric(label=p, value=count)

# --- MAIN CONTENT ---
st.markdown("<h1>🌌 Your Productivity Universe</h1>", unsafe_allow_html=True)
st.markdown("<p style='font-size: 1.2rem; color:#9CA3AF;'>Stay focused, stay productive, even in the dark.</p>", unsafe_allow_html=True)
st.markdown("---")

# Navigation Tabs
tab_view, tab_create, tab_manage = st.tabs([
    "📂 View & Search", 
    "🚀 Create New Task", 
    "⚙️ Manage & Edit"
])

# --- TAB 1: VIEW TASKS ---
with tab_view:
    st.markdown("<h2>Explore Tasks</h2>", unsafe_allow_html=True)
    
    # Filter Container
    with st.container():
        f_c1, f_c2, f_c3 = st.columns([1.5, 1.5, 2.5])
        with f_c1:
            f_status = st.selectbox("Status Filter", ["All"] + Task.STATUSES, key="f_status")
        with f_c2:
            f_priority = st.selectbox("Priority Filter", ["All"] + Task.PRIORITIES, key="f_priority")
        with f_c3:
            search_q = st.text_input("🔍 Quick Search", placeholder="Type title or decription...")

    # Fetch tasks
    if search_q.strip():
        tasks = manager.search(search_q.strip())
    else:
        status_filter = None if f_status == "All" else f_status
        priority_filter = None if f_priority == "All" else f_priority
        tasks = manager.read_all(filter_status=status_filter, filter_priority=priority_filter)
        
    if not tasks:
        st.warning("📭 No tasks found matching your criteria. Try creating one!")
    else:
        st.write("") # spacing
        for t in tasks:
            # Custom expander logic
            icon = "🔥" if t.priority == "Critical" else ("🚀" if t.status == "In Progress" else ("✅" if t.status == "Completed" else "📝"))
            
            with st.expander(f"{icon} {t.title}"):
                
                # Top Row: Badges
                st.markdown(f"**Priority:** {get_priority_badge(t.priority)} &nbsp;&nbsp; **Status:** {get_status_badge(t.status)}", unsafe_allow_html=True)
                st.markdown("<hr style='margin: 10px 0; border: none; border-top: 1px dashed #374151;'/>", unsafe_allow_html=True)
                
                # Desc + Date
                desc = t.description if t.description else "*No specific details added...*"
                st.markdown(f"<div style='font-size: 1.05rem; background:rgba(0,0,0,0.4); padding:10px; border-radius:8px; border: 1px solid #1f2937;'>{desc}</div>", unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                c_dt1, c_dt2 = st.columns(2)
                with c_dt1:
                    st.caption(f"🗓️ **Due Date:** {t.due_date if t.due_date else 'Not set'}")
                with c_dt2:
                    st.caption(f"🕒 **Created:** {t.created_at[:10]}")

# --- TAB 2: CREATE TASK ---
with tab_create:
    st.markdown("<h2>⚡ Bring a New Idea to Life</h2>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div style='background: rgba(15,20,35,0.7); padding: 25px; border-radius: 15px; border: 1px solid #2d3748; box-shadow: inset 0 2px 4px rgba(0,0,0,0.5);'>", unsafe_allow_html=True)
        with st.form("create_task_form", clear_on_submit=True):
            title = st.text_input("Task Title *", placeholder="What do you need to accomplish?")
            description = st.text_area("Task Description", placeholder="Add exciting details here...")
            
            cc1, cc2, cc3 = st.columns(3)
            with cc1:
                priority = st.selectbox("Priority Level", Task.PRIORITIES, index=1)
            with cc2:
                status = st.selectbox("Current Status", Task.STATUSES, index=0)
            with cc3:
                due_date = st.date_input("Target Due Date", value=None)
                
            submitted = st.form_submit_button("Launch Task 🚀")
            
            if submitted:
                if not title.strip():
                    st.error("Hold up! A title is absolutely necessary.")
                else:
                    d_str = due_date.strftime("%Y-%m-%d") if due_date else ""
                    manager.create_task(
                        title=title, 
                        description=description, 
                        priority=priority, 
                        status=status, 
                        due_date=d_str
                    )
                    st.balloons()
                    st.success(f"Amazing! '{title}' is now in the pipeline.")
                    
        st.markdown("</div>", unsafe_allow_html=True)

# --- TAB 3: MANAGE TASKS ---
with tab_manage:
    st.markdown("<h2>🛠️ Tweak Your Workflow</h2>", unsafe_allow_html=True)
    
    all_tasks = manager.read_all()
    if not all_tasks:
        st.info("Nothing to manage right now. Take a break! 🏖️")
    else:
        # Custom dict mapping UI string to task
        task_dict = {f"({t.status.upper()}) {t.title} [ID: {t.id}]": t for t in all_tasks}
        selected_key = st.selectbox("Select a task to fine-tune:", list(task_dict.keys()))
        selected_task = task_dict[selected_key]
        
        st.markdown(f"#### Modifying: <span style='color:#00d2ff;'>{selected_task.title}</span>", unsafe_allow_html=True)
        st.write("")
        
        edit_col, delete_col = st.columns([2.5, 1])
        
        with edit_col:
            st.markdown("<div style='background: #1e293b; padding: 20px; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.5); border: 1px solid #334155;'>", unsafe_allow_html=True)
            with st.form("edit_form"):
                u_title = st.text_input("Title", value=selected_task.title)
                u_desc = st.text_area("Description", value=selected_task.description)
                
                hc1, hc2, hc3 = st.columns(3)
                with hc1:
                    u_priority = st.selectbox("Priority", Task.PRIORITIES, index=Task.PRIORITIES.index(selected_task.priority))
                with hc2:
                    u_status = st.selectbox("Status", Task.STATUSES, index=Task.STATUSES.index(selected_task.status))
                with hc3:
                    try:
                        parsed_date = datetime.strptime(selected_task.due_date, "%Y-%m-%d").date() if selected_task.due_date else None
                    except:
                        parsed_date = None
                    u_due = st.date_input("Due Date", value=parsed_date)
                    
                if st.form_submit_button("Save Enhancements ✨"):
                    if not u_title.strip():
                        st.error("Title cannot be blank!")
                    else:
                        d_str = u_due.strftime("%Y-%m-%d") if u_due else ""
                        manager.update_task(
                            selected_task.id, 
                            title=u_title, 
                            description=u_desc, 
                            priority=u_priority, 
                            status=u_status, 
                            due_date=d_str
                        )
                        st.success(f"'{u_title}' was successfully updated!")
                        trigger_rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            
        with delete_col:
            st.markdown("<div style='background: #3f1515; padding: 20px; border-radius: 15px; border: 1px solid #7f1d1d;'>", unsafe_allow_html=True)
            st.markdown("<h4 style='color:#fca5a5; margin-top:0;'>⚠️ Danger Zone</h4>", unsafe_allow_html=True)
            st.caption("These actions are permanent.")
            
            if st.button("🗑️ Delete This Task", use_container_width=True):
                manager.delete_task(selected_task.id)
                st.toast(f"Poof! {selected_task.title} is gone forever.", icon="🌪️")
                trigger_rerun()
                
            st.markdown("<hr style='border-top:1px solid #7f1d1d;'/>", unsafe_allow_html=True)
            
            if st.button("🚨 Delete ALL Tasks", use_container_width=True):
                manager.delete_all()
                st.toast("Wiped everything clean!", icon="🧼")
                trigger_rerun()
            st.markdown("</div>", unsafe_allow_html=True)
