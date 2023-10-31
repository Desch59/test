import tkinter as tk
from tkinter import filedialog
import os
from tkinter import Toplevel
import sqlparse


def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("Supported Files", "*.sql *.txt *.log")])
    if file_path:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, file_path)


def process_file():
    file_path = file_entry.get()

    if not file_path:
        result_label.config(text="Please select a file first.")
        return

    # Read the content of the selected file
    with open(file_path, 'r') as f:
        content = f.readlines()

    # Process the content: remove DEBUG lines, COMPONENT_TIME lines, and extract SELECT lines
    processed_content = []
    inside_select = False
    query_num = 1

    for line in content:
        if "DEBUG" not in line and "COMPONENT_TIME" not in line:
            if "SELECT" in line:
                inside_select = True
                select_text = line[line.index("SELECT"):].strip()
                if query_num == 1:
                    processed_content.append(f"\nQuery {query_num}: {select_text}\n")
                else:
                    processed_content.append(f"\n\nQuery {query_num}: {select_text}\n")
                    processed_content.append("\n")  # Add an extra line after each query
                query_num += 1  # Increment the query number for the next SELECT line
            elif inside_select:
                processed_content.append(line)
            else:
                processed_content.append(line)

    # Replace ? with values from [] in each line
    final_content = []
    for line in processed_content:
        line = line.strip()  # Remove leading/trailing whitespace
        start = line.find("[")
        end = line.find("]")
        if start != -1 and end != -1:
            values = line[start + 1: end].split(",")
            line = line.replace("?", f"'{values.pop(0).strip()}'", 1)
            for val in values:
                line = line.replace("?", f"'{val.strip()}'", 1)
            final_content.append(line)
        else:
            final_content.append(line)

    # Save the processed content to a new file
    output_file_path = os.path.splitext(file_path)[0] + "_processed.sql"
    with open(output_file_path, 'w') as f:
        for line in final_content:
            formatted_sql = sqlparse.format(line, reindent=True, keyword_case='upper')
            f.write(formatted_sql + "\n")

    # Show a message box with processing information
    result_message = f"Processing completed.\nNumber of SELECT lines processed: {query_num - 1}\nOutput file: {output_file_path}"

    result_window = Toplevel(root)
    result_window.title("Processing Result")
    result_window.configure(bg='#0046FE')

    result_label = tk.Label(result_window, text=result_message, font=("Helvetica", 12), bg='#0046FE', fg='white')
    result_label.pack(padx=20, pady=10)

    ok_button = tk.Button(result_window, text="OK", command=result_window.destroy, fg='black', bg='orange')
    ok_button.pack(pady=10)


# Create the main window
root = tk.Tk()
root.title("DebugURFileProcessor")
root.configure(bg='#0046FE')  # Set background color to blue

# Create a label with a bold font
header_label = tk.Label(root, text="DebugURFileProcessor", font=("Helvetica", 16, "bold"), bg='#0046FE', fg='white')
header_label.pack(pady=20)

# Create a frame for the file selection
file_frame = tk.Frame(root, bg='#0046FE')
file_frame.pack()

select_button = tk.Button(file_frame, text="Select File", command=select_file, fg='black', bg='orange')
select_button.pack(side=tk.LEFT, padx=10)

file_entry = tk.Entry(file_frame, width=50)
file_entry.pack(side=tk.LEFT, padx=10)

# Create a button to process the file
process_button = tk.Button(root, text="Process File", command=process_file, fg='black', bg='orange')
process_button.pack(pady=10)

# Create a label to display the result
result_label = tk.Label(root, text="", font=("Helvetica", 12), bg='#0046FE', fg='white')
result_label.pack()

# Add the "Copyright" and "Coded With ChatGPT" labels
author_label = tk.Label(root, text="© DDESCHAMPS 2023", font=("Helvetica", 10), bg='#0046FE', fg='black')
author_label.pack(side=tk.BOTTOM)

coded_label = tk.Label(root, text="Coded With ChatGPT", font=("Helvetica", 10), bg='#0046FE', fg='black')
coded_label.pack(side=tk.BOTTOM)  # Display below the "© DDESCHAMPS 2023" label

root.mainloop()
