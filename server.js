const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");
require("dotenv").config();

const app = express();
app.use(cors());
app.use(express.json());

// MongoDB Connection
mongoose
  .connect(process.env.MONGO_URL, { useNewUrlParser: true, useUnifiedTopology: true })
  .then(() => console.log("MongoDB Connected"))
  .catch((err) => console.error("MongoDB Error:", err));

// Model
const Item = require("./models/itemModel");

// Add Item
app.post("/api/items", async (req, res) => {
    try {
        const item = new Item(req.body);
        await item.save();
        res.json({ message: "Item added successfully", item });
    } catch (err) {
        res.status(500).json({ error: "Failed to add item" });
    }
});

// Get All Items
app.get("/api/items", async (req, res) => {
    try {
        const items = await Item.find().sort({ expiry_date: 1 });
        res.json(items);
    } catch (err) {
        res.status(500).json({ error: "Cannot fetch items" });
    }
});

// Get Expiring Items
app.get("/api/items/expiring", async (req, res) => {
    try {
        const days = parseInt(req.query.days) || 2;
        const today = new Date();
        const limitDate = new Date();
        limitDate.setDate(today.getDate() + days);

        const items = await Item.find({
            expiry_date: { $gte: today, $lte: limitDate }
        }).sort({ expiry_date: 1 });

        res.json(items);
    } catch (err) {
        res.status(500).json({ error: "Failed to fetch expiring items" });
    }
});

// Delete Item
app.delete("/api/items/:id", async (req, res) => {
    try {
        await Item.findByIdAndDelete(req.params.id);
        res.json({ message: "Item deleted" });
    } catch (err) {
        res.status(500).json({ error: "Cannot delete item" });
    }
});

// Update Item
app.put("/api/items/:id", async (req, res) => {
    try {
        const updated = await Item.findByIdAndUpdate(req.params.id, req.body, { new: true });
        res.json({ message: "Item updated", updated });
    } catch (err) {
        res.status(500).json({ error: "Cannot update item" });
    }
});

// Server Start
const PORT = 5000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
