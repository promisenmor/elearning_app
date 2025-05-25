# 📚 eLearning App

An interactive and user-friendly eLearning platform developed as a final year school project. This application aims to enhance online education by providing seamless learning experiences for both educators and students.

## 🚀 Features

- **User Management**: Secure registration and authentication for students and instructors.
- **Course Management**: Instructors can create, update, and manage courses with ease.
- **Content Delivery**: Support for various educational content types, including videos, documents, and quizzes.
- **Progress Tracking**: Students can monitor their learning progress and course completion status.
- **Interactive Learning**: Features like chat and discussion forums to facilitate communication between students and instructors.

## 🛠️ Technologies Used

- **Backend**: Django (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite
- **Others**: Django REST Framework, Bootstrap

## 📂 Project Structure

elearning_app/
├── accounts/
├── chat/ 
├── courses/ 
├── elearning_platform/ 
├── media/ 
├── static/ 
├── templates/ 
├── db.sqlite3 
├── manage.py
├── requirements.txt



## ⚙️ Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/promisenmor/elearning_app.git
   cd elearning_app

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install -r requirements.txt

python manage.py migrate

python manage.py runserver

Access the application:
Navigate to http://127.0.0.1:8000/ in your web browser.


## 📌 Future Enhancements
Implementing advanced analytics for student performance.

Integrating video conferencing tools for live classes.

Enhancing mobile responsiveness and accessibility.

Deploying the application to cloud platforms for wider accessibility.


## 🤝 Contributing
Contributions are welcome! Please fork the repository and submit a pull request for any enhancements or bug fixes.


## 👨‍💼 Author
Promise Nmor
Backend Developer | Django | Python
