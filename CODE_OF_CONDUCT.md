Here is a step-by-step guide to setting up and running your **Medical Store Management System** on your Windows machine:

### 1. Open your Terminal
Open **Command Prompt** or **PowerShell** on your computer.

### 2. Navigate to the Project Directory
Change your active directory to where the project is located:
```powershell
cd C:\Users\Piyu\Downloads\Medical-Store-Management-System
```

### 3. Create a Virtual Environment
It is best practice to run Python projects inside an isolated virtual environment. Create one by running:
```powershell
python -m venv venv
```

### 4. Activate the Virtual Environment
Activate the environment so that any packages you install are contained within it:
```powershell
.\venv\Scripts\activate
```
*(You should see `(venv)` appear at the beginning of your terminal prompt line indicating it's active).*

### 5. Install Required Dependencies
Install all the necessary Python packages (like Flask, SQLAlchemy, etc.) from the `requirements.txt` file:
```powershell
pip install -r requirements.txt
```

### 6. Initialize the Database
Before running the application for the first time, you need to create the database structure and set up the default users. Run the included initialization script:
```powershell
python init_db.py
```
> [!NOTE]
> Based on your `init_db.py` script, this will create a default administrator account for you to log in with:
> **Username**: `Piyu`
> **Password**: `Piyu24`

### 7. Run the Application
Start the Flask development server:
```powershell
python app.py
```

### 8. Access the App
Open your web browser (Chrome, Edge, etc.) and navigate to the address shown in your terminal, which is usually:
👉 **[http://127.0.0.1:5000/](http://127.0.0.1:5000/)**

Log in using the admin credentials provided in step 6. The app will continue running in your terminal—to stop the server anytime, just go back to the terminal and press `Ctrl+C`.