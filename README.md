# DataLogger_Graphtec_GL840_Evaluation

This script processes CSV files straight out of the **Graphtec GL840 DataLogger**. No prior editing or formatting of the CSV file is required!

### 🚀 Quick Start Guide

1. **File Placement:** Copy the script into the same folder as the CSV file you want to evaluate.
2. **Set File Name:** Open the code (e.g., in VS Code) and replace `"name.csv"` in **line 9** with your actual CSV file name.
3. **Set Date & Start Time:** In **line 95**, update the date and start time for the diagram.
   * Format: `'YYYY-MM-DD HH:MM:SS'` (e.g., `'2026-06-19 14:30:00'`)
4. **Adjust Time Window (Optional):** In **line 111**, you can change the duration of the diagram (in hours):
   * The **left value** determines how many hours *before* the start time the diagram begins.
   * The **right value** determines how many hours *after* the start time the diagram ends.
   * *Example:* `(left=0, right=1.5)` -> The diagram starts exactly at your start time and covers the next 1.5 hours.
