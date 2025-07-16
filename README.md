.

🚀 PaleoApp Setup Guide (Linux)
Guide to installing and running the PaleoApp Django project on a Linux machine.

🔧 1. Install Python 3 and Virtual Environment Tools
Ensure Python 3 and related tools are installed:

bash

sudo apt update
sudo apt install python3 python3-venv python3-pip -y
Verify installation:

bash

python3 --version
pip3 --version


📥 2. Clone the Repository
Clone the project from GitHub:

bash

git clone https://github.com/nicahgaturi/PaleoApp.git
cd PaleoApp


🧱 3. Create and Activate a Virtual Environment

bash


python3 -m venv venv
source venv/bin/activate


📦 4. Install Required Python Packages
Install dependencies listed in requirements.txt:

bash


pip install -r requirements.txt
If no requirements.txt exists, install Django manually:

bash


pip install django



✅ 5. Apply Database Migrations
Set up the initial database schema:

bash


python manage.py migrate


🔐 6. Create an Admin (Superuser) Account
bash

python manage.py createsuperuser
Enter your desired username, email, and password when prompted.



🖥 7. Start the Development Server
bash

python manage.py runserver
Visit:

App: http://127.0.0.1:8000/

Admin Panel: http://127.0.0.1:8000/admin


🔚 9. Deactivate Virtual Environment (Optional)
When you're done working:

bash

deactivate
