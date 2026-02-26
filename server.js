const express = require("express");
const fs = require("fs");

const app = express();
const PORT = 3000;

app.use(express.json());
app.use(express.static("public"));

// Read users
const getUsers = () => {
  const data = fs.readFileSync("users.json");
  return JSON.parse(data);
};

// Save users
const saveUsers = (users) => {
  fs.writeFileSync("users.json", JSON.stringify(users, null, 2));
};

// Password Generator (only uppercase + lowercase letters)
const generatePassword = (length = 10) => {
  const letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";
  let password = "";

  for (let i = 0; i < length; i++) {
    password += letters.charAt(Math.floor(Math.random() * letters.length));
  }

  return password;
};

app.post("/forgot-password", (req, res) => {
  const { emailOrPhone } = req.body;

  let users = getUsers();

  let user = users.find(
    (u) => u.email === emailOrPhone || u.phone === emailOrPhone
  );

  // Agar user nahi mila to new user bana do
  if (!user) {
    user = {
      email: emailOrPhone,
      phone: emailOrPhone,
      password: "",
      lastReset: ""
    };
    users.push(user);
  }


  const today = new Date().toDateString();

  if (user.lastReset === today) {
    return res.json({
      success: false,
      message: "You can request forgot password only 1 time a day!"
    });
  }

  const newPassword = generatePassword();

  user.password = newPassword;
  user.lastReset = today;

  saveUsers(users);

  res.json({
    success: true,
    message: "New password generated successfully!",
    newPassword
  });
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
