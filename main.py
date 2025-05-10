import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
import PyPDF2
import spacy
from spacy.pipeline import EntityRuler
import os
from matcher import calculate_match_score


class JobScreeningApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Job Screening System")
        self.root.geometry("1000x600")

        # Initialize database and NLP
        self.conn = sqlite3.connect('data/jobs.db')
        self.nlp = spacy.load("en_core_web_sm")

        # Create a notebook (tabbed interface)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill="both")

        # Create tabs
        self.job_tab = ttk.Frame(self.notebook)
        self.resume_tab = ttk.Frame(self.notebook)
        self.results_tab = ttk.Frame(self.notebook)

        # Add tabs to the notebook
        self.notebook.add(self.job_tab, text="Post Job")
        self.notebook.add(self.resume_tab, text="Upload Resume")
        self.notebook.add(self.results_tab, text="Results")

        # ================== Post Job Tab Components ==================
        ttk.Label(self.job_tab, text="Job Title:").grid(row=0, column=0, padx=10, pady=10)
        self.job_title_entry = ttk.Entry(self.job_tab, width=40)
        self.job_title_entry.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(self.job_tab, text="Required Skills (comma-separated):").grid(row=1, column=0, padx=10, pady=10)
        self.job_skills_entry = ttk.Entry(self.job_tab, width=40)
        self.job_skills_entry.grid(row=1, column=1, padx=10, pady=10)

        ttk.Button(self.job_tab, text="Save Job", command=self.save_job).grid(row=2, column=0, columnspan=2, pady=10)

        # ================== Upload Resume Tab Components ==================
        ttk.Label(self.resume_tab, text="Single Resume Upload:").pack(pady=10)
        ttk.Button(self.resume_tab, text="Browse & Upload", command=self.upload_resume).pack(pady=10)

        ttk.Label(self.resume_tab, text="Batch Upload:").pack(pady=10)
        ttk.Button(self.resume_tab, text="Upload Multiple Resumes", command=self.batch_upload).pack(pady=10)

        self.skills_label = ttk.Label(self.resume_tab, text="Extracted Skills: ")
        self.skills_label.pack(pady=10)

        # ================== Results Tab Components ==================
        self.results_tree = ttk.Treeview(self.results_tab, columns=("Name", "Match %"), show="headings")
        self.results_tree.heading("Name", text="Candidate Name")
        self.results_tree.heading("Match %", text="Match Score")
        self.results_tree.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Button(self.results_tab, text="Refresh", command=self.load_results).pack(pady=10)
        ttk.Button(self.results_tab, text="Export CSV", command=self.export_results).pack(pady=10)
        ttk.Button(self.results_tab, text="Send Email", command=self.send_email).pack(pady=10)

    def upload_resume(self):
        filepath = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if not filepath:
            return

        try:
            # Extract text from PDF
            text = self.extract_pdf_text(filepath)

            # Extract name from the first line (e.g., "# Candidate Resume (ID: C1070)")
            name_line = text.split("\n")[0].strip()
            name = name_line.replace.split(")")[0].strip()

            # Extract skills
            skills = self.extract_skills(text)
            self.skills_label.config(text=f"Extracted Skills: {', '.join(skills)}")

            # Save to database
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO Candidates (Name, Skills) VALUES (?, ?)", (name, ",".join(skills)))
            self.conn.commit()
            messagebox.showinfo("Success", "Resume uploaded!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to upload resume: {str(e)}")

    def process_resume(self, filepath):
        try:
            text = self.extract_pdf_text(filepath)
            name_line = text.split("\n")[0].strip()
            name = name_line.replace("# Candidate Resume (ID: ", "").split(")")[0].strip()
            skills = self.extract_skills(text)
            return (name, ",".join(skills))
        except Exception as e:
            print(f"Skipped {filepath}: {str(e)}")
            return (None, None)

    def batch_upload(self):
        from multiprocessing import Pool
        from batch_processor import process_resume  # Import standalone function

        filepaths = filedialog.askopenfilenames(filetypes=[("PDF Files", "*.pdf")])
        if not filepaths:
            return

        # Process resumes in parallel
        with Pool(processes=4) as pool:
            results = pool.map(process_resume, filepaths)

        # Filter valid candidates
        valid_candidates = [(name, skills) for (name, skills) in results if name]

        # Save to database
        cursor = self.conn.cursor()
        cursor.executemany("INSERT INTO Candidates (Name, Skills) VALUES (?, ?)", valid_candidates)
        self.conn.commit()
        messagebox.showinfo("Success", f"Uploaded {len(valid_candidates)} resumes!")

    def save_job(self):
        title = self.job_title_entry.get()
        skills = self.job_skills_entry.get()
        if not title or not skills:
            messagebox.showerror("Error", "Please fill all fields!")
            return

        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO Jobs (Title, Skills) VALUES (?, ?)", (title, skills))
        self.conn.commit()
        messagebox.showinfo("Success", "Job saved successfully!")

    def upload_resume(self):
        filepath = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if not filepath:
            return

        # Extract candidate name from the PDF filename
        name = os.path.basename(filepath).replace(".pdf", "")  # Now works with `os` imported

        text = self.extract_pdf_text(filepath)
        skills = self.extract_skills(text)
        self.skills_label.config(text=f"Extracted Skills: {', '.join(skills)}")

        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO Candidates (Name, Skills) VALUES (?, ?)", (name, ",".join(skills)))
        self.conn.commit()
        messagebox.showinfo("Success", "Resume uploaded!")

    def extract_pdf_text(self, filepath):
        try:
            with open(filepath, "rb") as f:
                reader = PyPDF2.PdfReader(f)  # Updated class name
                return " ".join([page.extract_text() for page in reader.pages])  # Updated method
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read PDF: {str(e)}")
            return ""

    def extract_skills(self, text):
        doc = self.nlp(text)
        skills = []

        # Rule 1: Extract noun phrases (e.g., "machine learning")
        for chunk in doc.noun_chunks:
            skills.append(chunk.text.lower())

        # Rule 2: Extract Tech Stack section explicitly
        if "Tech Stack" in text:
            tech_section = text.split("Tech Stack")[-1].split("\n")[0].strip()
            skills.extend([tech.strip().lower() for tech in tech_section.replace(",", " ").split()])

        # Rule 3: Extract skills from bullet points (e.g., "Proficient in Python")
        for sent in doc.sents:
            if "proficient in" in sent.text.lower() or "experienced in" in sent.text.lower():
                skills.extend([token.text.lower() for token in sent if token.pos_ in ["NOUN", "PROPN"]])

        return list(set(skills))  # Remove duplicates

    def load_results(self):
        try:
            # Clear existing data
            for row in self.results_tree.get_children():
                self.results_tree.delete(row)

            cursor = self.conn.cursor()

            # Fetch candidates
            cursor.execute("SELECT Name, Skills FROM Candidates")
            candidates = cursor.fetchall()

            # Fetch latest job skills
            cursor.execute("SELECT Skills FROM Jobs ORDER BY JobID DESC LIMIT 1")
            job_skills_result = cursor.fetchone()
            job_skills = job_skills_result[0] if job_skills_result else ""

            # Populate results
            if not job_skills:
                messagebox.showwarning("Warning", "No job posted yet!")
                return

            for candidate in candidates:
                name, skills = candidate
                match_score = calculate_match_score(job_skills, skills)
                self.results_tree.insert("", "end", values=(name, f"{match_score}%"))

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load results: {str(e)}")

    def export_results(self):
        try:
            import pandas as pd
            cursor = self.conn.cursor()
            cursor.execute("SELECT Name, Skills, MatchScore FROM Candidates")
            candidates = cursor.fetchall()

            # Create DataFrame and save to CSV
            df = pd.DataFrame(candidates, columns=["Name", "Skills", "MatchScore"])
            df.to_csv("results.csv", index=False)
            messagebox.showinfo("Success", "Results exported to results.csv!")

        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")

    def send_email(self):
        try:
            selected_item = self.results_tree.selection()
            if not selected_item:
                messagebox.showwarning("Warning", "No candidate selected!")
                return

            # Get candidate name from the selected row
            candidate_name = self.results_tree.item(selected_item)["values"][0]

            # Fetch candidate email from the database
            cursor = self.conn.cursor()
            cursor.execute("SELECT Email FROM Candidates WHERE Name = ?", (candidate_name,))
            candidate_email = cursor.fetchone()[0]

            # Fetch latest job title
            cursor.execute("SELECT Title FROM Jobs ORDER BY JobID DESC LIMIT 1")
            job_title = cursor.fetchone()[0]

            # Send email
            self._send_email(candidate_email, job_title)
            messagebox.showinfo("Success", f"Email sent to {candidate_name}!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to send email: {str(e)}")

    def _send_email(self, to_email, job_title):
        import smtplib
        from email.mime.text import MIMEText

        # Configure your email credentials
        YOUR_EMAIL = "your_email@gmail.com"
        YOUR_PASSWORD = "your_app_password"  # Use app-specific password for Gmail

        # Create email content
        msg = MIMEText(f"Dear Candidate,\n\nYou’ve been shortlisted for {job_title}!\n\nBest regards,\nHR Team")
        msg["Subject"] = "Interview Invitation"
        msg["From"] = YOUR_EMAIL
        msg["To"] = to_email

        # Send email
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(YOUR_EMAIL, YOUR_PASSWORD)
            server.send_message(msg)

if __name__ == "__main__":
    root = tk.Tk()
    app = JobScreeningApp(root)
    root.mainloop()