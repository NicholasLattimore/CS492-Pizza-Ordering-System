# CS492-Pizza-Ordering-System

CS492 Capstone - Pizza Restaurant Online Ordering System

## Pizza Restaurant Online Ordering System
**Course:** CS492 Computer Science Capstone  
**Instructor:** Prof. Fadi Almasri  

---

## Project Overview
A responsive web application designed for a local pizzeria, supporting customer menu browsing, order customization, automated bill calculation, customer order placement, and store manager/staff live order updates.

---

## Active Team Members
- **Michael Fabacher** - Product Owner
- **Kellen Jones** - Scrum Master
- **Ayden Lotter** - Development Team
- **Nicholas Lattimore** - Development Team

---

## Tech Stack & Tools
- **Language:** Python 3.x
- **Framework:** Flask (with Flask-SQLAlchemy)
- **Database:** SQLite3
- **Hosting:** Render.com
- **Version Control:** Git & GitHub
- **Frontend:** HTML5, CSS3, Bootstrap 5.3, Bootstrap Icons, Vanilla JS

---

## Sprint 1 Deliverables (Completed)

| Story ID | Title | Description | Status |
| :--- | :--- | :--- | :--- |
| **PB-01** | Restaurant Information and Home Page | Restaurant description, food photos, operating hours, campus location map, and contact info with responsive design. | ✅ Done |
| **PB-02** | Menu Browsing and Item Details | Grouped by category (Specialty Pizzas, Build Your Own, Appetizers, Beverages, Desserts). Shows descriptions, prices, size/crust options, and marked unavailable items. No login required. | ✅ Done |
| **PB-03** | Order Builder and Shopping Cart | Add items with customized size/crust/notes to cart, modify quantities (`+`/`-`), remove items, live cart summary, and clean empty-cart guidance. | ✅ Done |
| **PB-04** | Final Bill Calculation and Order Review | Itemized review displaying line totals, subtotal, sales tax (8.25%), fulfillment option (Pickup vs $4.99 Delivery), and final total. Disallows submitting empty carts. | ✅ Done |
| **PB-05** | Customer Order Submission and Confirmation | Input validation, unique order number generation (`#ORD-...`), database order record creation, customer receipt screen, and restaurant staff order dashboard (`/staff/orders`). | ✅ Done |

---

## Local Development Setup

### 1. Clone the repository
```bash
git clone https://github.com/kjones0587/CS492-Pizza-Ordering-System.git
cd CS492-Pizza-Ordering-System
```

### 2. Create and activate virtual environment
```bash
# Windows:
py -m venv .venv
.\.venv\Scripts\activate

# macOS / Linux:
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the application
```bash
python run.py
```
Open your browser and navigate to `http://localhost:5000`. The database automatically initializes and seeds default menu categories and items on first run.

### 5. Run the Automated Tests
```bash
pytest
```

---

## Deployment to Render.com

This repository contains everything required for zero-configuration 1-click deployment on Render:

1. Push this repository to GitHub:
   ```bash
   git add .
   git commit -m "Sprint 1 delivery: PB-01 through PB-05"
   git push origin main
   ```
2. Log into [Render.com](https://render.com) and click **New +** -> **Web Service**.
3. Select your GitHub repository `kjones0587/CS492-Pizza-Ordering-System`.
4. Configure the service:
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn run:app`
5. Click **Deploy Web Service**. Render will automatically build the service, initialize the SQLite database, and launch your live public URL!
