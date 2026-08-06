// server.js
// Minimal Express server that serves a form and sends an email on submit.

const path = require("path");
const express = require("express");
const { sendEmail } = require("./mailer");

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, "public")));

app.post("/send-email", async (req, res) => {
  const { to, subject, message } = req.body;

  try {
    await sendEmail({ to, subject, text: message });
    res.json({ success: true, message: "Email sent!" });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: "Failed to send email" });
  }
});

app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});
