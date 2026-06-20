const mongoose = require("mongoose");

mongoose.connect("mongodb://127.0.0.1:27017/groceryDB");

const Item = mongoose.model("Item", new mongoose.Schema({
  item_name: String,
  quantity: Number,
  category: String,
  expiry_date: Date
}));

Item.find().then(items => {
  console.log(items);
  process.exit();
});
