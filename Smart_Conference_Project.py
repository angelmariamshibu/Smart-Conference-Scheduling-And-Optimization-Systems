import pandas as pd
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt

# GLOBAL VARIABLES
df = pd.DataFrame()

# CONSTANTS
WORKING_START = 8
WORKING_END = 16
REQUIRED_COLUMNS = {'Meeting_ID', 'Meeting_Name', 'Start_Time', 'End_Time', 'Priority', 'Room', 'Participants'}

# Helper Functions 
def convert_time(t):
    return datetime.strptime(t, "%H:%M")

def priority_value(p):
    return {"High": 1, "Medium": 2, "Low": 3}.get(p, 3)

def participant_conflict(p1, p2):
    set1 = set(x.strip() for x in p1.split(","))
    set2 = set(x.strip() for x in p2.split(","))
    return len(set1 & set2) > 0

def calculate_duration(start, end):
    delta = end - start
    hours, remainder = divmod(delta.seconds, 3600)
    minutes = remainder // 60
    return f"{hours:02d}h {minutes:02d}m"

def find_next_available_slot(meeting, schedule, rooms):
    temp_start = meeting['Start']
    temp_end = meeting['End']
    working_end = temp_start.replace(hour=WORKING_END, minute=0)
    for hour_shift in range(0, 8):
        candidate_start = temp_start + timedelta(hours=hour_shift)
        candidate_end = temp_end + timedelta(hours=hour_shift)
        if candidate_end > working_end:
            break
        for room in rooms:
            conflict = False
            for m in schedule[room]:
                # Separate time overlap and participant conflict checks
                time_overlap = not (candidate_end <= m['Start'] or candidate_start >= m['End'])
                p_conflict = participant_conflict(meeting['Participants'], m['Participants'])
                if time_overlap or p_conflict:
                    conflict = True
                    break
            if not conflict:
                return candidate_start, candidate_end, room
    return None, None, None

# Scheduling Algorithm
def schedule_meetings(df):
    df = df.copy()
    df['Start'] = df['Start_Time'].apply(convert_time)
    df['End'] = df['End_Time'].apply(convert_time)
    df['Priority_Value'] = df['Priority'].apply(priority_value)
    df = df.sort_values(by=['Priority_Value', 'End'])

    rooms = df['Room'].unique()
    schedule = {room: [] for room in rooms}
    rejected = []
    rescheduled = []

    for _, row in df.iterrows():
        placed = False
        for room in rooms:
            conflict = False
            for meeting in schedule[room]:
                # Separate time overlap and participant conflict checks
                time_overlap = not (row['End'] <= meeting['Start'] or row['Start'] >= meeting['End'])
                p_conflict = participant_conflict(row['Participants'], meeting['Participants'])
                if time_overlap or p_conflict:
                    conflict = True
                    break
            if not conflict:
                row_copy = row.copy()
                row_copy['Room'] = room
                row_copy['Duration'] = calculate_duration(row_copy['Start'], row_copy['End'])
                row_copy['Status'] = "Scheduled"
                schedule[room].append(row_copy)
                placed = True
                break

        if not placed:
            next_start, next_end, next_room = find_next_available_slot(row, schedule, rooms)
            if next_start:
                row_copy = row.copy()
                row_copy['Start'] = next_start
                row_copy['End'] = next_end
                row_copy['Start_Time'] = next_start.strftime("%H:%M")
                row_copy['End_Time'] = next_end.strftime("%H:%M")
                row_copy['Duration'] = calculate_duration(next_start, next_end)
                row_copy['Room'] = next_room
                row_copy['Status'] = "Rescheduled"
                schedule[next_room].append(row_copy)
                rescheduled.append(row_copy)
                placed = True

        if not placed:
            row_copy = row.copy()
            row_copy['Duration'] = calculate_duration(row_copy['Start'], row_copy['End'])
            row_copy['Status'] = "Rejected"
            rejected.append(row_copy)

    return schedule, rejected, rescheduled

# Terminal Output
def print_terminal_output(schedule, rejected, rescheduled):
    W_ID       = 6
    W_NAME     = 20   
    W_START    = 6
    W_END      = 6
    W_DUR      = 9
    W_ROOM     = 20   
    W_PRIORITY = 8
    W_PARTS    = 22   

    SEP  = "=" * 115
    SEP2 = "-" * 115

    total_scheduled = sum(1 for room in schedule for m in schedule[room] if m.get('Status') == 'Scheduled')

    print("\n" + SEP)
    print("              SMART CONFERENCE SCHEDULING AND OPTIMIZATION SYSTEM — RESULTS")
    print(SEP)
    print(f"  Total Scheduled  : {total_scheduled}")
    print(f"  Total Rescheduled: {len(rescheduled)}")
    print(f"  Total Rejected   : {len(rejected)}")
    print(SEP)

    header = (f"{'ID':<{W_ID}} {'Meeting Name':<{W_NAME}} {'Start':<{W_START}} {'End':<{W_END}} "
              f"{'Duration':<{W_DUR}} {'Room':<{W_ROOM}} {'Priority':<{W_PRIORITY}} "
              f"{'Participants':<{W_PARTS}} {'Status'}")

    def sched_row(m):
        return (f"{str(m['Meeting_ID']):<{W_ID}} {str(m['Meeting_Name']):<{W_NAME}} "
                f"{str(m['Start_Time']):<{W_START}} {str(m['End_Time']):<{W_END}} "
                f"{str(m.get('Duration','')):<{W_DUR}} {str(m['Room']):<{W_ROOM}} "
                f"{str(m['Priority']):<{W_PRIORITY}} {str(m['Participants']):<{W_PARTS}} "
                f"{str(m.get('Status',''))}")

    def rej_row(m):
        return (f"{str(m['Meeting_ID']):<{W_ID}} {str(m['Meeting_Name']):<{W_NAME}} "
                f"{str(m['Start_Time']):<{W_START}} {str(m['End_Time']):<{W_END}} "
                f"{str(m.get('Duration','')):<{W_DUR}} {str(m['Priority']):<{W_PRIORITY}} "
                f"{str(m['Participants']):<{W_PARTS}} {str(m.get('Status',''))}")

    rej_header = (f"{'ID':<{W_ID}} {'Meeting Name':<{W_NAME}} {'Start':<{W_START}} {'End':<{W_END}} "
                  f"{'Dur':<{W_DUR}} {'Priority':<{W_PRIORITY}} "
                  f"{'Participants':<{W_PARTS}} {'Status'}")

    # Optimized Meetings 
    print("\n  OPTIMIZED MEETINGS")
    print(SEP2)
    print(header)
    print(SEP2)
    for room in schedule:
        for m in schedule[room]:
            if m.get('Status') == 'Scheduled':
                print(sched_row(m))
    print(SEP2)

    # Rescheduled Meetings
    print("\n  RESCHEDULED MEETINGS")
    print(SEP2)
    if rescheduled:
        print(header)
        print(SEP2)
        for m in rescheduled:
            print(sched_row(m))
    else:
        print("  No meetings were rescheduled.")
    print(SEP2)

    # Rejected Meetings
    print("\n  REJECTED MEETINGS")
    print(SEP2)
    if rejected:
        print(rej_header)
        print(SEP2)
        for m in rejected:
            print(rej_row(m))
    else:
        print("  No meetings were rejected.")
    print(SEP2)
    print("\n" + SEP)
    print("  Schedule generation complete.")
    print(SEP + "\n")

# Gantt Chart
def generate_gantt_chart(schedule, rescheduled):
    colors = {'High': 'red', 'Medium': 'yellow', 'Low': 'lightgreen'}
    rooms = list(schedule.keys())

    # Determine dynamic x-axis range
    all_starts = []
    all_ends = []
    for room in schedule:
        for m in schedule[room]:
            all_starts.append(m['Start'].hour + m['Start'].minute / 60)
            all_ends.append(m['End'].hour + m['End'].minute / 60)
    x_min = int(min(all_starts)) if all_starts else WORKING_START
    x_max = int(max(all_ends)) + 1 if all_ends else WORKING_END

    fig, ax = plt.subplots(figsize=(12, 6))

    for i, room in enumerate(rooms):
        for m in schedule[room]:
            # Skip rescheduled in main loop — drawn separately in orange
            if m.get('Status') == 'Rescheduled':
                continue
            ax.barh(y=i, width=(m['End'] - m['Start']).seconds / 3600,
                    left=m['Start'].hour + m['Start'].minute / 60,
                    height=0.4, color=colors.get(m['Priority'], 'gray'),
                    edgecolor='black')
            ax.text(x=m['Start'].hour + m['Start'].minute / 60 + 0.05, y=i,
                    s=m['Meeting_Name'], va='center', ha='left', fontsize=8)

    # Draw rescheduled meetings in orange
    for m in rescheduled:
        room_idx = rooms.index(m['Room'])
        ax.barh(y=room_idx, width=(m['End'] - m['Start']).seconds / 3600,
                left=m['Start'].hour + m['Start'].minute / 60,
                height=0.4, color='orange', edgecolor='black', alpha=0.6)
        ax.text(x=m['Start'].hour + m['Start'].minute / 60 + 0.05, y=room_idx,
                s=m['Meeting_Name'], va='center', ha='left', fontsize=8)

    ax.set_yticks(range(len(rooms)))
    ax.set_yticklabels(rooms)
    # FIX: Dynamic x-axis range
    ax.set_xticks(range(x_min, x_max + 1))
    ax.set_xlabel('Time (Hours)')
    ax.set_title('Conference Schedule Gantt Chart')
    plt.grid(True, axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

# GUI Functions
def load_csv():
    global df
    path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if not path:
        return
    try:
        loaded = pd.read_csv(path)
        # Validate required columns before accepting the file
        missing = REQUIRED_COLUMNS - set(loaded.columns)
        if missing:
            messagebox.showerror("Missing Columns", f"CSV is missing required columns:\n{', '.join(missing)}")
            return
        df = loaded
        status_label.config(text=f"✔ CSV Loaded: {len(df)} meetings", fg="green")
        btn_generate.config(state="normal")
    except Exception as e:
        messagebox.showerror("Error", f"Could not read file:\n{e}")

def generate_schedule():
    if df.empty:
        messagebox.showwarning("No Data", "Load a CSV first")
        return

    frame.pack(fill="both", expand=True, padx=20, pady=10)
    schedule, rejected, rescheduled = schedule_meetings(df)

    # Print results to terminal
    print_terminal_output(schedule, rejected, rescheduled)

    # Clear previous rows
    for tree in [tree_sched, tree_resched, tree_rej]:
        for row in tree.get_children():
            tree.delete(row)

    # Optimized Schedule Table
    all_scheduled_output = []
    for room in schedule:
        for m in schedule[room]:
            priority_tag = m['Priority']
            tree_sched.insert("", "end", values=(
                m['Meeting_ID'], m['Meeting_Name'], m['Start_Time'], m['End_Time'],
                m.get('Duration', ''), m['Room'], m['Priority'], m['Participants'], m.get('Status', 'Scheduled')
            ), tags=(priority_tag,))
            all_scheduled_output.append([
                m['Meeting_ID'], m['Meeting_Name'], m['Start_Time'], m['End_Time'],
                m.get('Duration', ''), m['Room'], m['Priority'], m['Participants'], m.get('Status', 'Scheduled')
            ])

    # Rescheduled Table
    for m in rescheduled:
        tree_resched.insert("", "end", values=(
            m['Meeting_ID'], m['Meeting_Name'], m['Start_Time'], m['End_Time'],
            m.get('Duration', ''), m['Room'], m['Priority'], m['Participants'], m.get('Status', 'Rescheduled')
        ), tags=("Rescheduled",))

    # Rejected Table
    for m in rejected:
        tree_rej.insert("", "end", values=(
            m['Meeting_ID'], m['Meeting_Name'], m['Start_Time'], m['End_Time'],
            m.get('Duration', ''), m['Priority'], m['Participants'], m.get('Status', 'Rejected')
        ), tags=("Rejected",))

    # Correct summary count — rescheduled are inside schedule too, so subtract them
    total_scheduled = sum(
        1 for room in schedule for m in schedule[room] if m.get('Status') == 'Scheduled'
    )
    summary_label.config(
        text=f"Scheduled: {total_scheduled} | Rescheduled: {len(rescheduled)} | Rejected: {len(rejected)}"
    )

    # Save CSVs
    folder_path = filedialog.askdirectory(title="Select Folder to Save CSVs")
    if folder_path:
        pd.DataFrame(all_scheduled_output, columns=[
            "Meeting_ID", "Meeting_Name", "Start_Time", "End_Time", "Duration", "Room", "Priority", "Participants", "Status"
        ]).to_csv(f"{folder_path}/optimized_schedule.csv", index=False)

        # Safe export even if rescheduled/rejected lists are empty
        if rescheduled:
            pd.DataFrame([[m['Meeting_ID'], m['Meeting_Name'], m['Start_Time'], m['End_Time'], m.get('Duration', ''),
                           m['Room'], m['Priority'], m['Participants'], m.get('Status', 'Rescheduled')] for m in rescheduled],
                         columns=["Meeting_ID", "Meeting_Name", "Start_Time", "End_Time", "Duration", "Room", "Priority", "Participants", "Status"]
                         ).to_csv(f"{folder_path}/rescheduled_meetings.csv", index=False)
        else:
            pd.DataFrame(columns=["Meeting_ID", "Meeting_Name", "Start_Time", "End_Time", "Duration", "Room", "Priority", "Participants", "Status"]
                         ).to_csv(f"{folder_path}/rescheduled_meetings.csv", index=False)

        if rejected:
            pd.DataFrame([[m['Meeting_ID'], m['Meeting_Name'], m['Start_Time'], m['End_Time'], m.get('Duration', ''),
                           m['Priority'], m['Participants'], m.get('Status', 'Rejected')] for m in rejected],
                         columns=["Meeting_ID", "Meeting_Name", "Start_Time", "End_Time", "Duration", "Priority", "Participants", "Status"]
                         ).to_csv(f"{folder_path}/rejected_meetings.csv", index=False)
        else:
            pd.DataFrame(columns=["Meeting_ID", "Meeting_Name", "Start_Time", "End_Time", "Duration", "Priority", "Participants", "Status"]
                         ).to_csv(f"{folder_path}/rejected_meetings.csv", index=False)

    messagebox.showinfo("Success",
                        f"Scheduled: {total_scheduled} | Rescheduled: {len(rescheduled)} | Rejected: {len(rejected)}")

    generate_gantt_chart(schedule, rescheduled)

def reset_all():
    global df
    frame.pack_forget()
    for tree in [tree_sched, tree_resched, tree_rej]:
        for row in tree.get_children():
            tree.delete(row)
    # FIX: Also reset the dataframe on reset
    df = pd.DataFrame()
    status_label.config(text="")
    summary_label.config(text="")
    btn_generate.config(state="disabled")

# GUI Setup 
# Guard for direct execution
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Smart Conference Scheduler")
    root.geometry("1300x800")
    root.configure(bg="lightcyan")

    tk.Label(root, text="Smart Conference Scheduling and Optimization System",
             font=("Arial", 20, "bold"), bg="lightcyan", fg="darkblue").pack(pady=10)
    tk.Label(root, text="Efficient Meeting Planning & Optimization",
             font=("Arial", 11), bg="lightcyan").pack()

    btn_frame = tk.Frame(root, bg="lightcyan")
    btn_frame.pack(pady=10)

    btn_load = tk.Button(btn_frame, text="Load CSV", font=("Arial", 12, "bold"),
                         bg="green", fg="white", padx=10, command=load_csv)
    btn_load.pack(side="left", padx=10)

    btn_generate = tk.Button(btn_frame, text="Generate Schedule", font=("Arial", 12, "bold"),
                             bg="navy", fg="white", padx=10, state="disabled", command=generate_schedule)
    btn_generate.pack(side="left", padx=10)

    tk.Button(btn_frame, text="Reset", font=("Arial", 12, "bold"),
              bg="red", fg="white", padx=10, command=reset_all).pack(side="left", padx=10)

    status_label = tk.Label(root, text="", bg="lightcyan", fg="green")
    status_label.pack()

    summary_label = tk.Label(root, text="", font=("Arial", 12, "bold"), bg="lightcyan", fg="blue")
    summary_label.pack(pady=5)

    frame = tk.Frame(root, bg="white")

    def create_table(frame, title, columns):
        tk.Label(frame, text=title, font=("Arial", 13, "bold"), bg="white").pack()
        table_frame = tk.Frame(frame)
        table_frame.pack(padx=10, pady=10, fill="x", expand=True)
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=6)
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscroll=vsb.set, xscroll=hsb.set)
        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=130, anchor="center")
        return tree

    # Create Tables
    tree_sched = create_table(frame, "Optimized Schedule",
                              ("Meeting_ID", "Meeting_Name", "Start_Time", "End_Time", "Duration", "Room", "Priority", "Participants", "Status"))
    tree_resched = create_table(frame, "Rescheduled Meetings",
                                ("Meeting_ID", "Meeting_Name", "Start_Time", "End_Time", "Duration", "Room", "Priority", "Participants", "Status"))
    tree_rej = create_table(frame, "Rejected Meetings",
                            ("Meeting_ID", "Meeting_Name", "Start_Time", "End_Time", "Duration", "Priority", "Participants", "Status"))

    # Tag Colors
    tree_sched.tag_configure("High", background="red")
    tree_sched.tag_configure("Medium", background="yellow")
    tree_sched.tag_configure("Low", background="lightgreen")
    tree_resched.tag_configure("Rescheduled", background="orange")
    tree_rej.tag_configure("Rejected", background="red")

    root.mainloop()
