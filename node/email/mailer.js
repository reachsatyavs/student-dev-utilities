// mailer.js
// Reusable email-sending module built on Nodemailer + a Gmail account.
// Copy this single file into any Node.js project to send email.

require("dotenv").config();
const nodemailer = require("nodemailer");

const transporter = nodemailer.createTransport({
  service: "gmail",
  auth: {
    user: process.env.GMAIL_USER,
    pass: process.env.GMAIL_APP_PASSWORD, // Google App Password, not your normal password
  },
});

/**
 * Send an email using the configured Gmail account.
 * @param {{ to: string, subject: string, text?: string, html?: string }} options
 */
async function sendEmail({ to, subject, text, html }) {
  if (!to || !subject) {
    throw new Error("`to` and `subject` are required");
  }

  const info = await transporter.sendMail({
    from: process.env.GMAIL_USER,
    to,
    subject,
    text,
    html,
  });

  return info;
}

module.exports = { sendEmail };
