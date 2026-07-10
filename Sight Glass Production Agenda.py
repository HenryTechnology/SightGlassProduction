import streamlit as st #import the streamlit library
import pandas as pd #Panda is used to create manage table similar to excel
from datetime import datetime, date, timedelta #Display correct date and time tools
import holidays
import calendar


#Configure the webpage,
st.set_page_config(page_title="Sight Glass Furnace Agenda", # Text on browser tab
                   layout="wide") #"Wide" makes the page use the full browser width

st.title( "Sight Glass Furnace Agenda") # Large heading at the top of the page.

st.caption(
    f"Last Updated: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}"
) #Get current date and time # strftime() changes it into a readable format.

today = date.today() #Get today's date
selected_year = st.selectbox( ## Let user choose year
    "Year",
    [today.year, today.year +1]
)

selected_month = st.selectbox( # Let user choose month
    "Month",
    list(range(1, 13)),
    index=today.month - 1
)



us_holidays = holidays.US(years=[selected_year]) # Automatically load U.S. holidays for selected year

company_close_days = {date(2026,11,27): "Day after Thanksgiving",
                      date(2026, 12,24): "Christmas Eve"} #Not Federal holidays still company close days


# You only enter dates that actually have tasks.
# You do NOT enter every calendar date.

tasks = [
    ["2026-07-09", "6:00 AM", "9:00 AM", "First Run", "T1001", "S-8523B", 30, "Planned", "Normal priority"],
    ["2026-07-09", "9:00 AM", "11:00 AM", "Troubleshooting", "T1002", "S-8590G", 12, "Running", "Check furnace atmosphere"],
    ["2026-07-09", "11:00 AM", "2:00 PM", "Second Run", "T1003", "S-7741HE", 45, "Planned", "After adjustment"],
]

df_tasks = pd.DataFrame(
    tasks,
    columns=[
        "Planned Date",
        "Start Time",
        "End Time",
        "Activity",
        "Task ID",
        "Part #",
        "Qty",
        "Status",
        "Notes"
    ]
)

df_tasks["Planned Date"] = pd.to_datetime(df_tasks["Planned Date"]).dt.date #Convert Planned table into real date format


# Build calendar automatically
cal = calendar.Calendar(firstweekday=0)  # Create calendar object # 0 means Monday starts the week
month_weeks = cal.monthdatescalendar(selected_year, selected_month) # Get all weeks for selected month
weekday_cols = st.columns(7) # Display weekday header
weekday_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"] # Weekday names
for col, day_name in zip(weekday_cols, weekday_names):
    col.markdown(f"### {day_name}") # Show weekday names

# Loop through each week
for week in month_weeks:
    cols = st.columns(7) #Create 7 columns for one week
    for col, current_day in zip(cols,week): #Loop through each day in this week
        is_current_month = current_day.month == selected_month  # Check whether this day belongs to selected month
        is_past = current_day < today
        is_today = current_day == today # Check whether this day is today
        is_weekend = current_day.weekday() >= 5  # Check weekend
        is_holiday = current_day in us_holidays # Check U.S. holiday
        is_company_closed = current_day in company_close_days  # Check company closed day
        tasks_for_day = df_tasks[df_tasks["Planned Date"] == current_day] # Find tasks for this day
        block_text = f"<b>{current_day.day}</b>"  # Start calendar block text

        if not is_current_month:
            block_text += "\nOther Month"
            # Add weekend label
        elif is_weekend:
            block_text += "\nWeekend"

        # Add holiday label
        elif is_holiday:
            block_text += f"\nHoliday: {us_holidays[current_day]}"

        # Add company closed label
        elif is_company_closed:
            block_text += f"\nClosed: {company_close_days[current_day]}"

        # Add working day label
        else:
            block_text += "\nWorking Day"



        # Create empty HTML for task cards
        task_cards_html = ""

        # Add tasks into this date block
        for _, task in tasks_for_day.iterrows():
            # Choose status color
            if task["Status"] == "Planned":
                status_color = "#1E88E5"  # Blue

            elif task["Status"] == "Running":
                status_color = "#2E7D32"  # Green

            elif task["Status"] == "Delayed":
                status_color = "#D32F2F"  # Red

            else:
                status_color = "#000000"  # Black


            task_cards_html += f"""
               <div style="
                   border:1px solid #BFBFBF;
                   border-radius:6px;
                   padding:4px;
                   margin-top:4px;
                   margin-bottom:4px;
                   background-color:#FFFFFF;
                   font-size:12px;
                   line-height:1.2;
               ">
               <b>{task['Start Time']} - {task['End Time']}</b><br>
               Task ID: {task['Task ID']}<br>
               {task['Part #']} | Qty {task['Qty']}<br>
               <span style="color:{status_color};">
                {task['Status']}
                </span>
               </div>
                """
        if is_past: # Choose background color
            background_color = "#D9D9D9"
        else:
            background_color = "#FFFFFF"
        if is_today:# Decide border color for TODAY
            border_color = "#0078D4"  # Blue
            border_width = "3px"
        else:
            border_color = "#CCCCCC"
            border_width = "1px"

        # Display one calendar day block
        col.markdown(
            f"""
            <div style="
                border:{border_width} solid {border_color};
                border-radius:8px;
                padding:10px;
                min-height:180px;
                background-color:{background_color};
                margin-bottom:10px;
            ">
            {block_text.replace(chr(10), "<br>")}
{task_cards_html}
            </div>
            """,
            unsafe_allow_html=True
        )