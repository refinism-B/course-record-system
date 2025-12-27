# Course Record System (課程記錄系統)

A streamlined, web-based application designed to manage and track student attendance and course records. Built with **Python** and **Streamlit**, this system leverages **Google Sheets** as a cloud-based database to ensure real-time data accessibility and ease of management.

## 📖 Overview

The Course Record System is tailored for course managers to efficiently record and monitor student learning progress. It replaces traditional manual tracking with a digital interface that offers:
- **Centralized Data Management**: All student records are stored securely in Google Sheets.
- **Role-Based Access**: Managers can view specific courses and groups assigned to them.
- **Intuitive Interface**: User-friendly dashboard for viewing student lists and logging attendance.

## ✨ Key Features

- **Dashboard & Announcements**: A centralized homepage displaying the latest course announcements and system usage instructions.
- **Student Overview**:
  - Filter students by **Manager** (Course) and **Group**.
  - Tab-based navigation for different groups (e.g., 社青小組, 善牧小組).
  - Real-time display of student details including birthday and monthly attendance records.
- **Attendance Input**:
  - Dedicated interface for logging attendance status.
  - Support for batch selection (single student per entry) and monthly logging (Jan-Apr).
  - **Data Safety**: Confirmation dialogs prevent accidental submissions.
- **Manual Data Synchronization**: Functionality to force a refresh of local data from the Google Sheets database to ensure consistency.

## 🛠️ Technology Stack

- **Frontend/Backend**: [Streamlit](https://streamlit.io/)
- **Data Manipulation**: [Pandas](https://pandas.pydata.org/)
- **Database Connection**: [st-gsheets-connection](https://github.com/streamlit/gsheets-connection)
- **Database**: Google Sheets

## 📂 Project Structure

```text
course-record-system/
├── code/
│   ├── mod/
│   │   ├── O_config.py       # Configuration constants (Managers, Groups, etc.)
│   │   └── O_general.py      # Core functions for DB connection and data processing
│   └── streamlit_app.py      # Main Streamlit application entry point
├── doc/
│   ├── overview.md           # Project documentation
│   └── announcement.md       # Announcement content file
├── key/                      # Credentials directory (Git-ignored)
├── .gitignore
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- A Google Cloud Service Account with access to the target Google Sheet.

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/course-record-system.git
   cd course-record-system
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Secrets**
   Set up your Google Sheets credentials. Streamlit looks for secrets in `.streamlit/secrets.toml`.
   
   Example `.streamlit/secrets.toml`:
   ```toml
   [connections.gsheets]
   spreadsheet = "YOUR_SPREADSHEET_URL_OR_NAME"
   type = "service_account"
   project_id = "..."
   private_key_id = "..."
   private_key = "..."
   client_email = "..."
   client_id = "..."
   auth_uri = "https://accounts.google.com/o/oauth2/auth"
   token_uri = "https://oauth2.googleapis.com/token"
   auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
   client_x509_cert_url = "..."
   ```

### Usage

Run the Streamlit application:

```bash
streamlit run code/streamlit_app.py
```

Open your browser and navigate to the local URL provided (usually `http://localhost:8501`).

## 📝 License

This project is intended for internal use.

---
*Built with ❤️ using Streamlit*