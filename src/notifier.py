"""
Notifier Module
Sends automated reports via email and Slack.
"""

import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional


class Notifier:
    """
    Sends notifications about pipeline runs.
    Supports email (SMTP) and Slack (webhook).
    """

    def __init__(self):
        # Email settings (configure these for real use)
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = None  # Set to your email
        self.sender_password = None  # App password, not your real password

        # Slack webhook URL (get from Slack app settings)
        self.slack_webhook = None

    def configure_email(
        self, email: str, password: str, server: str = "smtp.gmail.com", port: int = 587
    ):
        """Set up email credentials."""
        self.sender_email = email
        self.sender_password = password
        self.smtp_server = server
        self.smtp_port = port

    def configure_slack(self, webhook_url: str):
        """Set up Slack webhook URL."""
        self.slack_webhook = webhook_url

    def send_email_report(
        self, recipient: str, subject: str, stats: dict, department_stats: list
    ) -> bool:
        """
        Send an HTML email report.

        Args:
            recipient: Who receives the email
            subject: Email subject line
            stats: Pipeline statistics dict
            department_stats: List of department summary dicts

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.sender_email:
            print("⚠️  Email not configured. Call configure_email() first.")
            return False

        # Build HTML email body
        html = self._build_html_report(stats, department_stats)

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.sender_email
        msg["To"] = recipient

        msg.attach(MIMEText(html, "html"))

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            print(f"✅ Email report sent to {recipient}")
            return True
        except Exception as e:
            print(f"❌ Email failed: {e}")
            return False

    def send_slack_message(self, message: str) -> bool:
        """
        Send a simple text message to Slack.

        Args:
            message: Text to send

        Returns:
            True if sent successfully
        """
        if not self.slack_webhook:
            print("⚠️  Slack not configured. Call configure_slack() first.")
            return False

        payload = {"text": message}

        try:
            response = requests.post(self.slack_webhook, json=payload)
            response.raise_for_status()
            print("✅ Slack message sent")
            return True
        except Exception as e:
            print(f"❌ Slack failed: {e}")
            return False

    def _build_html_report(self, stats: dict, dept_stats: list) -> str:
        """Build a professional HTML report."""

        rows = ""
        for d in dept_stats:
            rows += f"""
            <tr>
                <td>{d["department"]}</td>
                <td>{d["count"]}</td>
                <td>${d["avg_salary"]:,.2f}</td>
                <td>${d["total_salary"]:,.2f}</td>
            </tr>
            """

        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2>📊 Enterprise Data Pipeline Report</h2>
            <p><strong>Run Time:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            
            <h3>Pipeline Statistics</h3>
            <table border="1" cellpadding="8" style="border-collapse: collapse;">
                <tr style="background: #f0f0f0;">
                    <td><b>File Processed</b></td>
                    <td>{stats.get("file_processed", "N/A")}</td>
                </tr>
                <tr>
                    <td><b>Total Rows</b></td>
                    <td>{stats.get("total_rows", 0)}</td>
                </tr>
                <tr style="background: #e8f5e9;">
                    <td><b>✅ Valid Records</b></td>
                    <td>{stats.get("valid_rows", 0)}</td>
                </tr>
                <tr style="background: #ffebee;">
                    <td><b>❌ Invalid Records</b></td>
                    <td>{stats.get("invalid_rows", 0)}</td>
                </tr>
                <tr>
                    <td><b>💾 Stored in DB</b></td>
                    <td>{stats.get("stored_in_db", 0)}</td>
                </tr>
            </table>
            
            <h3>Department Breakdown</h3>
            <table border="1" cellpadding="8" style="border-collapse: collapse;">
                <tr style="background: #f0f0f0;">
                    <th>Department</th>
                    <th>Count</th>
                    <th>Avg Salary</th>
                    <th>Total Salary</th>
                </tr>
                {rows}
            </table>
            
            <p style="color: #666; margin-top: 20px;">
                <em>Generated by Enterprise Data Pipeline</em>
            </p>
        </body>
        </html>
        """
        return html

    def console_report(self, stats: dict, dept_stats: list):
        """
        Print a report to console (works without any configuration).
        """
        print("\n" + "=" * 60)
        print("📧 NOTIFICATION REPORT")
        print("=" * 60)
        print(f"File: {stats.get('file_processed', 'N/A')}")
        print(
            f"Valid: {stats.get('valid_rows', 0)} | Invalid: {stats.get('invalid_rows', 0)}"
        )
        print(f"Stored: {stats.get('stored_in_db', 0)}")
        print("\nDepartment Summary:")
        for d in dept_stats:
            print(
                f"  {d['department']}: {d['count']} employees, avg ${d['avg_salary']:,.0f}"
            )
        print("=" * 60)
