#Welcome to the Kahua Project Management Integration system.
//Kahua PMIS 

A Django-based web application for managing projects, tasks, and users. This system allows project teams to organize, monitor, and track various project details efficiently.

📑 Table of Contents
Features
Technologies Used
Setup and Installation
Usage
Contributing
License
🌟 Features
Project Management: Create, update, and delete projects, with details such as description, start date, and end date.
Task Management: Add, update, delete, and view tasks associated with each project. Tasks include properties like start date, end date, assigned user, and status.
User Management: Manage user roles and assign users to specific tasks and projects.
CSV Import: Upload tasks in bulk through CSV files for streamlined data entry.
Real-Time Updates: Frontend updates via JavaScript for seamless data input and feedback.
Notifications: Success/error messages displayed for real-time feedback on actions.

🛠️ Technologies Used
Backend: Django, Django REST Framework
Frontend: HTML, CSS, JavaScript
Database: SQLite (development), PostgreSQL (recommended for production)
Additional Libraries: Django import-export, Chart.js for data visualization

⚙️ Setup and Installation
Prerequisites
Ensure you have the following installed:

Python 3.8+
Django 3.2+
pip for managing Python packages
Installation Steps
Clone the repository:

git clone https://github.com/your-username/pmis.git
cd pmis
Create and activate a virtual environment:


python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
Install required packages:

pip install -r requirements.txt
Database setup: Configure the database in settings.py (default is SQLite). For production, use PostgreSQL and set up the appropriate environment variables.
Run migrations:


python manage.py migrate
Create a superuser:


python manage.py createsuperuser
Run the server:

python manage.py runserver


🚀 Usage
1. Access the Admin Panel
Go to admin panel and log in with your superuser credentials.
Manage users, projects, and tasks from the admin interface.

2. Project and Task Management
Go to the Project list to add or update projects.
Use the "ADD TASK" button in each project to add tasks, either individually or through CSV import.

3. CSV Import (Client-Side)
Upload task data from the client side by selecting the "Upload CSV" option.
Ensure the CSV file adheres to the required format.
CSV Import Format:

id, project_id, name, date_created, task_start_date, task_end_date, status, assigned_to_id