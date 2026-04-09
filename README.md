# Smart Conference Scheduling and Optimization System

## Overview
This project implements a Smart Conference Scheduling and Optimization System using a priority-based greedy algorithm. It automates meeting scheduling by efficiently allocating time slots and rooms while avoiding conflicts and maximizing resource utilization.

## Features
- Priority-based scheduling (High → Medium → Low)
- Conflict detection (time and participant conflicts)
- Automatic rescheduling of conflicting meetings
- Identification of rejected meetings
- Graphical User Interface (GUI) using Tkinter
- Gantt chart visualization using matplotlib
- Terminal-based tabular output
- CSV export for scheduled, rescheduled, and rejected meetings

## Tools Used
- Python
- Pandas
- Tkinter
- Matplotlib

## How It Works
1. Load meeting data from a CSV file  
2. Validate input data  
3. Sort meetings by priority and end time  
4. Schedule meetings without conflicts  
5. Reschedule conflicting meetings if possible  
6. Reject meetings if no slot is available  
7. Display results via GUI, terminal output, and Gantt chart  

## Output
- GUI Tables:
  - Scheduled Meetings
  - Rescheduled Meetings
  - Rejected Meetings  
- Terminal Output (formatted tables)  
- Gantt Chart Visualization  
- CSV Files:
  - optimized_schedule.csv  
  - rescheduled_meetings.csv  
  - rejected_meetings.csv  

## Project Structure

Smart-Conference-Scheduler/
- Smart_Conference_Project.py   # Main program file (GUI + scheduling logic)
- sample_meetings.csv           # Sample input dataset for testing
- optimized_schedule.csv        # Output: scheduled meetings
- rescheduled_meetings.csv      # Output: rescheduled meetings
- rejected_meetings.csv         # Output: rejected meetings
-  README.md                     # Project documentation

## Algorithm Used
The system uses a **Greedy Algorithm**:
- Meetings are sorted by priority and end time  
- Each meeting is scheduled in the first available room without conflicts  
- Conflicts are resolved through rescheduling  
- Meetings that cannot be scheduled are rejected  

## Complexity
- Time Complexity: O(n log n + n × m × p)  
- Space Complexity: O(n)  

Where:  
- n = number of meetings  
- m = number of rooms  
- p = number of participants  
