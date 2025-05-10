import sqlite3
import os


def init_db():
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    conn = sqlite3.connect(os.path.join(data_dir, 'jobs.db'))
    cursor = conn.cursor()

    # Create Jobs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Jobs (
            JobID INTEGER PRIMARY KEY,
            Title TEXT,
            Skills TEXT,
            MatchScore REAL
            
        )
    ''')

    # Create Candidates table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Candidates (
            CandidateID INTEGER PRIMARY KEY,
            Name TEXT,
            Email TEXT,
            Phone TEXT,
            Education TEXT,
            WorkExperience TEXT,
            Skills TEXT,
            Certifications TEXT,
            Achievements TEXT,
            TechStack TEXT
        )
    ''')

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()