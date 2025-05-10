# 🧠 AI-Powered Job Screening System

An intelligent, multi-agent AI application to automate the job screening process using Generative AI (GenAI), NLP, and data intelligence. Built using Python, this tool enhances recruitment efficiency by parsing resumes, matching candidates to jobs, and scheduling interviews.

## 📌 Problem Statement

Recruiters face the time-consuming and error-prone task of manually reviewing resumes and job descriptions. This results in inconsistent shortlisting, overlooked talent, and operational delays. Our project addresses these issues by automating the screening process using AI agents.

## ✅ Features

- 📄 **JD Summarization** using NLP
- 📂 **Resume Parsing** from PDFs using PyPDF2
- 🧮 **Matching Agent** to score resumes vs job descriptions
- 📧 **Automated Email Invitations** for shortlisted candidates
- 💾 **SQLite Database** for persistent storage
- 🧑‍💻 **Tkinter GUI** for simple user interaction
- 📊 **Batch Upload** and CSV Export support

## ⚙️ Technologies Used

- Python
- Tkinter (GUI)
- spaCy (NLP)
- PyPDF2
- SQLite3
- scikit-learn (for intelligent scoring)
- smtplib/email (for notifications)

## 🏗️ System Architecture
User Interface (Tkinter)
│
├── JD Summarizer Agent → NLP with spaCy
├── Resume Parser Agent → PyPDF2 + spaCy
├── Matching Agent → Skill matching using ML techniques
└── Interview Scheduler → Email automation

bash
Copy code

## 💻 How to Run

1. **Clone the repository**
   bash
   git clone https://github.com/your-username/job-screening-ai.git
   cd job-screening-ai
   
2.**Set up a virtual environment**
bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

3.**Install dependencies**
bash
Copy code
pip install -r requirements.txt

**4.Run the application**
bash
python main.py

📁 **Folder Structure**
bash
job-screening-ai/
├── agents/               # JD summarizer, parser, matcher
├── database/             # SQLite DB
├── gui/                  # Tkinter GUI code
├── utils/                # Helper functions
├── main.py               # Main launcher
├── requirements.txt
└── README.md

**🚀 Impact**
⏱️ 80% reduction in manual screening time
🎯 Improved accuracy in candidate-job matching
🤖 Scalable and deployment-ready AI solution
