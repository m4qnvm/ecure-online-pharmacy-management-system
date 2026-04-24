# Ecure Pharmacy - E-Pharmacy Management System

Ecure Pharmacy is a comprehensive full-stack web application designed to streamline the process of browsing, searching, and purchasing pharmaceutical products online. Modeled after modern e-commerce platforms, it provides a seamless experience for users to manage their healthcare needs.

## 🚀 Features
* **User Authentication:** Secure sign-up and login functionality.
* **Product Catalog:** Organized categories for medicines and healthcare products.
* **Search Functionality:** Quickly find specific medications or brands.
* **Shopping Cart:** Add, remove, and update product quantities before checkout.
* **Responsive Design:** Optimized for both desktop and mobile viewing.
* **Admin Dashboard:** Backend management for inventory and user orders via Django Admin.

## 🛠️ Tech Stack
* **Backend:** Python, Django Framework
* **Frontend:** HTML5, CSS3, JavaScript (Bootstrap)
* **Database:** MySQL
* **Version Control:** Git & GitHub

## 📦 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git)
   cd YOUR_REPO_NAME
2. Create a virtual environment:
   python -m venv env
   source env/bin/activate  # On Windows use: env\Scripts\activate
3. Install dependencies:
   pip install -r requirements.txt
4. Database configuration:
   Create a MySQL database named ecure_db.
   Update the DATABASES setting in settings.py with your MySQL credentials.
5. Run Migrations:
   python manage.py makemigrations
   python manage.py migrate
6. Start the server:
   python manage.py runserver

Developed as a final year project to demonstrate full-stack development capabilities.
