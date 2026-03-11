1️⃣ Create and activate virtual environment
python -m venv venv
# Linux / Mac
source venv/bin/activate
# Windows
venv\Scripts\activate

2️⃣ Install dependencies
cd project
pip install -r requirements.txt

3️⃣ Setup environment
cp .env.example .env
# Edit .env with your values

4️⃣ Run the application
uvicorn app:app --reload --port 8000

5️⃣ Access API docs

Swagger UI: http://127.0.0.1:8000/docs

Redoc: http://127.0.0.1:8000/redoc

Admin Routes

Admin-only routes protected with role-based dependency

Manage users, roles, products, and orders

Example usage:

GET /admin-only
Authorization: Bearer <admin-access-token>

Product Routes (CRUD)

Create, update, delete, and list products

Example usage:

POST /products
Authorization: Bearer <access-token>
Body: { "name": "Product A", "price": 25.99, "stock": 10 }

Cart Routes (CRUD)

Add/remove/update items in cart

View user cart

Example usage:

POST /cart/add
Authorization: Bearer <access-token>
Body: { "product_id": 1, "quantity": 2 }

Data Files

1️⃣ 1.png

Description: example dataset for products or users

2️⃣ 2.png

Description: example dataset for initial cart or orders

Notes

Google OAuth2 requires GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, and GOOGLE_REDIRECT_URI.

Refresh tokens are stored in DB and support revocation.

Roles system allows creating and assigning roles to users; use require_role() dependency for endpoint protection.