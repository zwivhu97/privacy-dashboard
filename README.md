# Privacy Dashboard

#### Video Demo: https://youtu.be/VVTYq3NKRtk

#### Description:
Privacy Dashboard is a web application designed to help users monitor and protect their online security by checking email breaches and password strength. Inspired by the growing concern over data privacy, this project leverages the Have I Been Pwned (HIBP) API to scan for compromised accounts and the Pwned Passwords API to assess password safety. The app calculates a privacy health score based on breach counts and offers personalized tips to enhance security. Built as part of the CS50x course, it reflects my journey in learning Flask, database management, and API integration.

**Features**:
- User registration and login with secure password hashing using Werkzeug.
- Email breach scanning with a dynamic score (100 minus 10 per breach).
- Password strength check against a global database of breached passwords.
- Personalized dashboard displaying score, breach count, and privacy tips.
- Basic backup functionality for local database records.

**Files**:
- `app.py`: The Flask backend handling all routes—login, registration, dashboard, password checks, and backups. It uses cs50.SQL for SQLite database interactions and includes error handling for API limits.
- `templates/login.html`: Contains the login form with a "Register" link, styled with Bootstrap.
- `templates/register.html`: Registration form for new users, ensuring unique emails and secure passwords.
- `templates/dashboard.html`: The main interface showing user score, forms for scans, and dynamic content with Jinja2 templates.
- `templates/layout.html`: Base template with Bootstrap CSS for consistent styling across pages.
- `static/style.css`: Custom CSS for layout enhancements, including colors and spacing.
- `requirements.txt`: Lists dependencies (Flask, cs50, requests, werkzeug) for easy setup.

**Design Choices**:
- Opted for Flask due to its lightweight nature and familiarity from prior CS50 projects. SQLite was chosen for local development simplicity, though a cloud migration is planned.
- Integrated HIBP APIs for real-time data, handling free-tier limits with fallbacks to maintain usability.
- Implemented session-based authentication with a configurable `SECRET_KEY` for security, initially using a fallback due to deployment constraints.
- Challenges included API 401 errors—resolved with error messages and default scores—and ensuring template consistency across routes.

**How to Run**:
1. Clone the repository: `git clone https://github.com/zwivhu97/privacy-dashboard.git`.
2. Install dependencies: `pip install -r requirements.txt`.
3. Run the app: `python app.py`.
4. Access at `http://127.0.0.1:5000`.

**Challenges and Lessons**:
- Debugging database initialization errors taught me the importance of robust file handling in Python.
- Managing API rate limits highlighted the need for graceful degradation in web apps.
- Writing this README helped refine my documentation skills, a key takeaway for future projects.

**Future Work**:
- Integrate a real AI API (e.g., Grok) for advanced privacy tips.
- Migrate to a cloud database like Render Postgres for scalability.
- Add a favicon and improve UI with JavaScript validation.
