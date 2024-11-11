import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import llamadecision


class CSVUploaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Uploader")
        self.root.geometry("600x400")

        # Initialize variables
        self.uploaded_df = None
        self.file_path_to_save = None

        # Add GUI elements
        self.create_widgets()

    def create_widgets(self):
        # Upload CSV button
        self.upload_button = tk.Button(self.root, text="Upload CSV File", command=self.upload_file)
        self.upload_button.grid(row=0, column=0, columnspan=2, pady=20, sticky="ew")

        # Label for instructions
        self.instruction_label = tk.Label(self.root, text="Upload CSV and Save File Location:")
        self.instruction_label.grid(row=1, column=0, columnspan=2, pady=10, sticky="ew")

        # Button for selecting save file location
        self.resultfile = tk.Button(self.root, text="Place Categorized CSV File At", command=self.save_location)
        self.resultfile.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")

        # Button to run the program
        self.run_program_button = tk.Button(self.root, text="RUN PROGRAM", command=self.run_program)
        self.run_program_button.grid(row=3, column=0, columnspan=2, pady=20, sticky="ew")

    def upload_file(self):
        file_path = filedialog.askopenfilename(title="Select a CSV file", filetypes=[("CSV Files", "*.csv")])
        if file_path:
            try:
                # Store the file path of the uploaded CSV
                self.uploaded_file_path = file_path

                # Read the CSV file to check if it contains the necessary columns
                self.uploaded_df = pd.read_csv(file_path, nrows=0)  # Read only the header (first row)

                # Check if the required columns are present in the CSV file
                required_columns = ['QUALIFIER_TXT', 'PNT_ATRISKNOTES_TX']
                missing_columns = [col for col in required_columns if col not in self.uploaded_df.columns]

                if missing_columns:
                    raise ValueError(f"Missing columns in the uploaded CSV file: {', '.join(missing_columns)}")

                # If columns are found, show success
                messagebox.showinfo("Success", f"File uploaded successfully! Required columns found.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read the file: {e}")

    def save_location(self):
        """ Ask the user for the location to save the output file. """
        self.file_path_to_save = filedialog.asksaveasfilename(defaultextension=".csv",
                                                              filetypes=[("CSV Files", "*.csv")],
                                                              title="Save Your File")
        if self.file_path_to_save:
            messagebox.showinfo("Success", f"File will be saved at: {self.file_path_to_save}")
        else:
            messagebox.showerror("Error", "Failed to select file save location.")

    def run_program(self):
        """ Run the classification program with the predefined columns. """
        if self.uploaded_df is not None and self.file_path_to_save:
            try:
                # Extract the necessary columns directly (assuming they exist)
                required_columns = ['QUALIFIER_TXT', 'PNT_ATRISKNOTES_TX']

                # Filter the DataFrame by the required columns
                df_selected_columns = self.uploaded_df[required_columns]

                # Call the classification function (make sure it's adapted to handle this)
                llamadecision.LLMclassification(self.uploaded_file_path, required_columns, self.file_path_to_save)

                messagebox.showinfo("Success", "Program ran successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to run the program: {e}")
        else:
            messagebox.showerror("Error", "Please upload a file and specify a save location first.")


if __name__ == "__main__":
    root = tk.Tk()
    app = CSVUploaderApp(root)
    root.mainloop()
