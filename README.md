Smart Grocery Reminder System - Backend
Run:
1. Install dependencies: npm install
2. Start MongoDB (e.g., mongod)
3. Start server: npm start
Environment:
- MONGO_URL (optional) e.g. mongodb://127.0.0.1:27017/groceryDB
API:
- POST /api/items    { item_name, quantity, expiry_date }
- GET  /api/items
- GET  /api/items/expiring?days=2
- PUT  /api/items/:id
- DELETE /api/items/:id
