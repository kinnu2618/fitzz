import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import time

# Set page configuration
st.set_page_config(
    page_title="Fitness Progress Tracker",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #2ecc71;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .progress-bar {
        height: 20px;
        background-color: #e9ecef;
        border-radius: 10px;
        margin-bottom: 1rem;
        overflow: hidden;
    }
    .progress-fill {
        height: 100%;
        background: linear-gradient(to right, #3498db, #2ecc71);
        border-radius: 10px;
        transition: width 0.5s ease;
    }
    .completed-exercise {
        color: #2ecc71;
        text-decoration: line-through;
    }
    .section-header {
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
        color: #2c3e50;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for data storage
if 'workout_data' not in st.session_state:
    st.session_state.workout_data = {}
if 'weight_data' not in st.session_state:
    st.session_state.weight_data = {}

# Define workout routines
workout_routines = {
    "LEGS": [
        {"name": "Lying Leg Curls", "sets": 3, "reps": 10},
        {"name": "Squats", "sets": 3, "reps": 10},
        {"name": "Romanian Deadlift", "sets": 3, "reps": 10},
        {"name": "Leg Extension", "sets": 3, "reps": 10},
        {"name": "Standing Calf Raises", "sets": 3, "reps": 10}
    ],
    "ARMS": [
        {"name": "Unilateral Cross-Body Tricep Extension", "sets": 3, "reps": 10},
        {"name": "Unilateral Preacher Curls", "sets": 3, "reps": 10},
        {"name": "Unilateral Overhead Tricep Extension", "sets": 3, "reps": 10},
        {"name": "Incline Dumbbell Curls", "sets": 3, "reps": 10},
        {"name": "Cross Body Hammer Curls", "sets": 3, "reps": 10}
    ],
    "CHEST_SHOULDERS": [
        {"name": "Incline Barbell Press", "sets": 3, "reps": "8,10,15"},
        {"name": "Shoulder Press", "sets": 3, "reps": 12},
        {"name": "Chest Fly", "sets": 3, "reps": 12},
        {"name": "Lateral Raises", "sets": 3, "reps": 20},
        {"name": "Front Raises", "sets": 3, "reps": 20}
    ],
    "BACK": [
        {"name": "Dead Lift", "sets": 3, "reps": 10},
        {"name": "Lat Pulldown", "sets": 4, "reps": 10},
        {"name": "Omni-Grip Chest Supported Row", "sets": 3, "reps": 12},
        {"name": "Dumbbell Pullover", "sets": 3, "reps": 10},
        {"name": "Omni-Direction Face Pull", "sets": 3, "reps": 15}
    ]
}

# Helper functions
def get_date_key(date=None):
    if date is None:
        date = st.session_state.selected_date
    return date.strftime("%Y-%m-%d")

def load_date_data(date):
    date_key = get_date_key(date)
    if date_key not in st.session_state.workout_data:
        st.session_state.workout_data[date_key] = {}
    if date_key not in st.session_state.weight_data:
        st.session_state.weight_data[date_key] = None

def save_workout_data():
    # This would typically save to a file or database
    # For this demo, we're just using session state
    pass

def save_weight_data(weight):
    date_key = get_date_key()
    st.session_state.weight_data[date_key] = weight

def get_completion_percentage(workout_type):
    date_key = get_date_key()
    if date_key not in st.session_state.workout_data:
        return 0
    
    completed = 0
    total = len(workout_routines[workout_type])
    
    for exercise in workout_routines[workout_type]:
        ex_key = f"{workout_type}_{exercise['name']}"
        if ex_key in st.session_state.workout_data[date_key] and st.session_state.workout_data[date_key][ex_key]:
            completed += 1
    
    return (completed / total) * 100 if total > 0 else 0

def get_all_completion_data():
    dates = sorted(st.session_state.workout_data.keys())
    completion_data = {}
    
    for date in dates:
        completion_data[date] = {}
        for workout_type in workout_routines.keys():
            completed = 0
            total = len(workout_routines[workout_type])
            
            for exercise in workout_routines[workout_type]:
                ex_key = f"{workout_type}_{exercise['name']}"
                if ex_key in st.session_state.workout_data.get(date, {}) and st.session_state.workout_data[date][ex_key]:
                    completed += 1
            
            completion_data[date][workout_type] = (completed / total) * 100 if total > 0 else 0
    
    return completion_data

def export_data():
    data = {
        "workout_data": st.session_state.workout_data,
        "weight_data": st.session_state.weight_data
    }
    return json.dumps(data, indent=2)

def import_data(uploaded_file):
    try:
        data = json.load(uploaded_file)
        st.session_state.workout_data = data.get("workout_data", {})
        st.session_state.weight_data = data.get("weight_data", {})
        st.success("Data imported successfully!")
        time.sleep(1)
        st.rerun()
    except Exception as e:
        st.error(f"Error importing data: {str(e)}")

def render_progress_bar(percentage, height=20):
    return f"""
    <div class="progress-bar">
        <div class="progress-fill" style="width: {percentage}%;"></div>
    </div>
    <div style="text-align: center; font-weight: bold;">{percentage:.1f}%</div>
    """

# UI Layout
st.markdown('<h1 class="main-header">💪 Fitness Progress Tracker</h1>', unsafe_allow_html=True)
st.markdown("Track your daily workouts and monitor your progress over time")

# Sidebar for date selection and data management
with st.sidebar:
    st.markdown('<div class="section-header">Settings</div>', unsafe_allow_html=True)
    
    # Date selection
    selected_date = st.date_input("Select Date", datetime.now())
    st.session_state.selected_date = selected_date
    load_date_data(selected_date)
    
    # Data management
    st.markdown('<div class="section-header">Data Management</div>', unsafe_allow_html=True)
    
    # Export data
    data_str = export_data()
    st.download_button(
        label="📥 Download Data",
        data=data_str,
        file_name=f"fitness_data_{selected_date.strftime('%Y%m%d')}.json",
        mime="application/json",
        use_container_width=True
    )
    
    # Import data
    uploaded_file = st.file_uploader("📤 Import Data", type="json")
    if uploaded_file is not None:
        import_data(uploaded_file)
    
    # Progress summary
    st.markdown('<div class="section-header">Today\'s Progress</div>', unsafe_allow_html=True)
    for workout_type in workout_routines.keys():
        progress = get_completion_percentage(workout_type)
        display_name = workout_type.replace("_", " ").title()
        
        st.markdown(f'<div class="metric-card">{display_name}', unsafe_allow_html=True)
        st.markdown(render_progress_bar(progress), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Main content area
tab1, tab2, tab3, tab4 = st.tabs(["🏋️ Workout", "⚖️ Weight Tracking", "📊 Progress Charts", "📅 History"])

with tab1:
    st.markdown('<div class="section-header">Workout Tracking</div>', unsafe_allow_html=True)
    
    for workout_type, exercises in workout_routines.items():
        with st.expander(workout_type.replace("_", " ").title(), expanded=True):
            date_key = get_date_key()
            
            # Complete all button
            if st.button(f"✅ Complete All {workout_type.replace('_', ' ').title()}", key=f"complete_all_{workout_type}", use_container_width=True):
                for exercise in exercises:
                    ex_key = f"{workout_type}_{exercise['name']}"
                    st.session_state.workout_data[date_key][ex_key] = True
                st.rerun()
            
            # Exercise checkboxes
            for exercise in exercises:
                ex_key = f"{workout_type}_{exercise['name']}"
                reps_display = exercise['reps'] if isinstance(exercise['reps'], int) else f"{exercise['reps']} (pyramid)"
                
                completed = st.checkbox(
                    f"{exercise['name']} - {exercise['sets']} sets × {reps_display} reps",
                    value=st.session_state.workout_data[date_key].get(ex_key, False),
                    key=ex_key
                )
                st.session_state.workout_data[date_key][ex_key] = completed

with tab2:
    st.markdown('<div class="section-header">Weight Tracking</div>', unsafe_allow_html=True)
    
    date_key = get_date_key()
    current_weight = st.session_state.weight_data.get(date_key, None)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        weight = st.number_input(
            "Enter your weight (kg)",
            min_value=30.0,
            max_value=200.0,
            value=current_weight if current_weight else 70.0,
            step=0.1,
            key="weight_input"
        )
        
        if st.button("💾 Save Weight", use_container_width=True):
            save_weight_data(weight)
            st.success("Weight saved successfully!")
            time.sleep(1)
            st.rerun()
    
    with col2:
        if current_weight:
            st.markdown(f'<div class="metric-card">Current Weight<br><span style="font-size: 2rem;">{current_weight} kg</span></div>', unsafe_allow_html=True)
        else:
            st.info("No weight recorded for today")
    
    # Weight history chart
    st.markdown('<div class="section-header">Weight Progress</div>', unsafe_allow_html=True)
    
    # Filter out None values and sort by date
    weight_history = {k: v for k, v in st.session_state.weight_data.items() if v is not None}
    if weight_history:
        dates = sorted(weight_history.keys())
        weights = [weight_history[date] for date in dates]
        
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(dates, weights, marker='o', linestyle='-', color='steelblue', linewidth=2, markersize=6)
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Weight (kg)', fontsize=12)
        ax.set_title('Weight Progress Over Time', fontsize=14, fontweight='bold')
        ax.grid(True, linestyle='--', alpha=0.7)
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
        
        # Calculate statistics
        if len(weights) > 1:
            weight_change = weights[-1] - weights[0]
            avg_weight = sum(weights) / len(weights)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Average Weight", f"{avg_weight:.1f} kg")
            with col2:
                st.metric("Overall Change", f"{weight_change:+.1f} kg", 
                         delta=f"{weight_change:+.1f} kg" if weight_change != 0 else "0.0 kg")
    else:
        st.info("No weight data available yet.")

with tab3:
    st.markdown('<div class="section-header">Progress Charts</div>', unsafe_allow_html=True)
    
    completion_data = get_all_completion_data()
    
    if completion_data:
        dates = sorted(completion_data.keys())
        
        # Create a DataFrame for easier plotting
        chart_data = {}
        for workout_type in workout_routines.keys():
            display_name = workout_type.replace("_", " ").title()
            chart_data[display_name] = [completion_data[date].get(workout_type, 0) for date in dates]
        
        df = pd.DataFrame(chart_data, index=dates)
        
        # Plot progress
        fig, ax = plt.subplots(figsize=(12, 6))
        colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12']
        for i, (workout_type, color) in enumerate(zip(df.columns, colors)):
            ax.plot(df.index, df[workout_type], marker='o', linestyle='-', linewidth=2, 
                   label=workout_type, color=color, markersize=6)
        
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Completion (%)', fontsize=12)
        ax.set_title('Workout Completion Progress', fontsize=14, fontweight='bold')
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
        
        # Show progress table
        st.markdown('<div class="section-header">Completion Details</div>', unsafe_allow_html=True)
        display_df = df.copy()
        display_df = display_df.style.format("{:.1f}%").highlight_max(axis=0, color='#90EE90').highlight_min(axis=0, color='#FFCCCB')
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("No workout data available yet.")

with tab4:
    st.markdown('<div class="section-header">Workout History</div>', unsafe_allow_html=True)
    
    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
    with col2:
        end_date = st.date_input("End Date", datetime.now())
    
    # Filter data by date range
    filtered_dates = []
    for date_str in st.session_state.workout_data.keys():
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        if start_date <= date_obj <= end_date:
            filtered_dates.append(date_str)
    
    filtered_dates.sort()
    
    if filtered_dates:
        # Create history table
        history_data = []
        for date_str in filtered_dates:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            row = {"Date": date_obj}
            
            for workout_type in workout_routines.keys():
                completed = 0
                total = len(workout_routines[workout_type])
                
                for exercise in workout_routines[workout_type]:
                    ex_key = f"{workout_type}_{exercise['name']}"
                    if ex_key in st.session_state.workout_data[date_str] and st.session_state.workout_data[date_str][ex_key]:
                        completed += 1
                
                display_name = workout_type.replace("_", " ").title()
                row[display_name] = f"{completed}/{total}"
            
            # Add weight if available
            weight = st.session_state.weight_data.get(date_str, "N/A")
            row["Weight (kg)"] = weight if weight is not None else "N/A"
            
            history_data.append(row)
        
        df_history = pd.DataFrame(history_data)
        st.dataframe(df_history, use_container_width=True)
        
        # Download history as CSV
        csv = df_history.to_csv(index=False)
        st.download_button(
            label="📥 Download History as CSV",
            data=csv,
            file_name=f"workout_history_{start_date}_{end_date}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("No workout data available for the selected date range.")

# Footer
st.markdown("---")
st.markdown("### 💡 Tips for Success")
col1, col2, col3 = st.columns(3)
with col1:
    st.info("**Consistency is key** - Try to workout regularly")
with col2:
    st.info("**Track progress** - Monitor your improvements over time")
with col3:
    st.info("**Stay hydrated** - Drink plenty of water during workouts")

# Add some space at the bottom
st.markdown("<br><br>", unsafe_allow_html=True)