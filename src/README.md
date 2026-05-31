# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Sign up for activities
- Teacher login for management actions
- Dynamic announcements with scheduling and expiration

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Run the application:

   ```
   python app.py
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up for an activity                                             |
| POST   | `/activities/{activity_name}/unregister?email=student@mergington.edu&teacher_username=...` | Remove a student from an activity (teacher required)               |
| POST   | `/auth/login?username=...&password=...`                          | Authenticate a teacher                                               |
| GET    | `/auth/check-session?username=...`                               | Validate a teacher username session                                  |
| GET    | `/announcements`                                                  | Get currently active announcements for public display               |
| GET    | `/announcements/all?teacher_username=...`                        | Get all announcements for management (teacher required)             |
| POST   | `/announcements?teacher_username=...`                            | Create an announcement (teacher required)                           |
| PUT    | `/announcements/{announcement_id}?teacher_username=...`          | Update an announcement (teacher required)                           |
| DELETE | `/announcements/{announcement_id}?teacher_username=...`          | Delete an announcement (teacher required)                           |

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

Data is stored in MongoDB.
