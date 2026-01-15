"""
Email sender module for Daily News Agent V5
Adds multi-recipient email support
"""

import os
import json
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import markdown2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class EmailSenderV5:
    def __init__(self, sender_email: str = None, sender_password: str = None):
        """
        Initialize email sender with Gmail credentials

        Args:
            sender_email: Gmail address to send from
            sender_password: Gmail app password (not regular password)
        """
        self.sender_email = sender_email or os.getenv('GMAIL_ADDRESS', 'jon.sims@gmail.com')
        self.sender_password = sender_password or os.getenv('GMAIL_APP_PASSWORD')

        # V5: Load multiple recipients from environment or JSON file
        self.recipients = self._load_recipients()

        if not self.sender_password:
            logger.warning("Gmail app password not configured. Email sending disabled.")
            self.enabled = False
        else:
            self.enabled = True
            logger.info(f"Email sender V5 initialized for {self.sender_email}")
            logger.info(f"Will send to {len(self.recipients)} recipient(s): {', '.join(self.recipients)}")

    def _load_recipients(self):
        """
        Load recipient email addresses from:
        1. GMAIL_ADDRESSES_V5 environment variable (priority)
        2. config/v5-recipients.json file (fallback)
        3. Sender email (final fallback)
        """
        # First, try environment variable
        recipients_env = os.getenv('GMAIL_ADDRESSES_V5', '')
        if recipients_env:
            recipients = [email.strip() for email in recipients_env.split(',') if email.strip()]
            logger.info(f"Loaded {len(recipients)} recipient(s) from environment variable")
            return recipients

        # Second, try JSON file
        try:
            script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            json_path = os.path.join(script_dir, "config", "v5-recipients.json")

            if os.path.exists(json_path):
                with open(json_path, 'r') as f:
                    data = json.load(f)
                    recipients = data.get('recipients', [])
                    if recipients:
                        logger.info(f"Loaded {len(recipients)} recipient(s) from config/v5-recipients.json")
                        return recipients
        except Exception as e:
            logger.warning(f"Could not load recipients from JSON file: {e}")

        # Final fallback: sender email
        logger.info("Using sender email as fallback recipient")
        return [self.sender_email]

    def send_daily_update(self,
                         markdown_content: str,
                         recipients: list = None,
                         subject: str = None,
                         source_label: str = None,
                         version: str = None,
                         test_mode: bool = False,
                         model_used: str = None) -> bool:
        """
        Send daily news update via email to multiple recipients

        Args:
            markdown_content: The markdown content to send
            recipients: List of email addresses (defaults to configured recipients)
            subject: Email subject (auto-generates if not provided)
            source_label: Label for update source (e.g., "Local" or "Web")
            version: Version identifier (e.g., "v5")
            test_mode: If True, only send to jon.sims@gmail.com
            model_used: AI model name to display in footer (e.g., "Claude Haiku 4.5")

        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.enabled:
            logger.info("Email sending disabled - no app password configured")
            return False

        try:
            # In test mode, only send to jon.sims@gmail.com
            if test_mode:
                recipients_list = ['jon.sims@gmail.com']
                logger.info("Test mode: Sending only to jon.sims@gmail.com")
            else:
                # Use provided recipients or default to configured list
                recipients_list = recipients or self.recipients

            # Generate subject with today's date
            if not subject:
                now = datetime.now()
                day_abbr = now.strftime('%a')  # Wed
                month_abbr = now.strftime('%b')  # Oct
                day_num = now.strftime('%-d')  # 16 (no leading zero)
                year_short = now.strftime('%y')  # 25

                # Format: "Update Agent Email v5 beta - Wed Oct 16"
                subject = f"Update Agent Email v5 beta - {day_abbr} {month_abbr} {day_num}"

            # Convert markdown to HTML for better email rendering
            html_content = self._markdown_to_html(markdown_content, model_used=model_used)

            # Save HTML copy to archive
            self._save_html_archive(html_content, version="v5", test_mode=test_mode)

            # Create plain text version
            plain_content = self._clean_markdown_for_plain(markdown_content)

            # Send to each recipient
            success_count = 0
            for recipient in recipients_list:
                try:
                    # Create message for this recipient
                    msg = MIMEMultipart('alternative')
                    msg['Subject'] = subject
                    msg['From'] = f"My Update V5 <{self.sender_email}>"
                    msg['To'] = recipient

                    # Attach both plain text and HTML versions
                    part1 = MIMEText(plain_content, 'plain')
                    part2 = MIMEText(html_content, 'html')

                    msg.attach(part1)
                    msg.attach(part2)

                    # Send email via Gmail SMTP
                    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                        server.login(self.sender_email, self.sender_password)
                        server.send_message(msg)

                    logger.info(f"✅ V5 update emailed to {recipient}")
                    success_count += 1

                except Exception as e:
                    logger.error(f"❌ Failed to send email to {recipient}: {str(e)}")

            # Return True if at least one email was sent successfully
            if success_count > 0:
                logger.info(f"✅ V5 update sent to {success_count}/{len(recipients_list)} recipients")
                return True
            else:
                logger.error("❌ Failed to send to any recipients")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to send email: {str(e)}")
            return False

    def _markdown_to_html(self, markdown_content: str, model_used: str = None) -> str:
        """
        Convert markdown to HTML with nice styling

        Args:
            markdown_content: Markdown content to convert
            model_used: AI model name to display in footer
        """
        # Convert markdown to HTML
        html_body = markdown2.markdown(
            markdown_content,
            extras=['fenced-code-blocks', 'tables', 'strike', 'target-blank-links', 'break-on-newline', 'html-classes']
        )

        # Wrap in HTML template with inline CSS for email clients
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                /* Reset and base styles */
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}

                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, 'Helvetica Neue', Arial, sans-serif;
                    font-size: 16px !important;
                    line-height: 1.6;
                    color: #2c3e50;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #ffffff;
                }}

                /* V5 Test Banner */
                .v5-banner {{
                    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
                    color: white;
                    padding: 16px;
                    text-align: center;
                    border-radius: 8px;
                    margin-bottom: 24px;
                    font-weight: 600;
                    font-size: 18px !important;
                    box-shadow: 0 4px 6px rgba(239, 68, 68, 0.3);
                }}

                /* Consistent heading hierarchy */
                h1 {{
                    font-size: 28px !important;
                    font-weight: 700;
                    color: #1a202c;
                    border-bottom: 3px solid #3182ce;
                    padding-bottom: 12px;
                    margin: 0 0 24px 0;
                    line-height: 1.2;
                    text-align: center;
                }}

                h2 {{
                    font-size: 24px !important;
                    font-weight: 600;
                    color: #2d3748;
                    margin: 32px 0 16px 0;
                    line-height: 1.3;
                }}

                h3 {{
                    font-size: 18px !important;
                    font-weight: 600;
                    color: #1e293b;
                    margin: 32px 0 16px 0;
                    line-height: 1.4;
                    background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
                    padding: 12px 16px;
                    border-radius: 6px;
                    border-left: 4px solid #3182ce;
                    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                }}

                /* Paragraph and text content */
                p {{
                    font-size: 14px !important;
                    line-height: 1.6;
                    margin: 0 0 16px 0;
                    color: #2d3748;
                }}

                /* Links */
                a {{
                    color: #3182ce;
                    text-decoration: none;
                    font-weight: 500;
                }}

                a:hover {{
                    text-decoration: underline;
                    color: #2c5aa0;
                }}

                /* Lists */
                ul, ol {{
                    margin: 0 0 16px 0;
                    padding-left: 24px;
                }}

                li {{
                    font-size: 14px !important;
                    line-height: 1.5 !important;
                    margin: 4px 0 !important;
                    color: #2d3748 !important;
                }}

                /* Footer styling */
                .footer {{
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 2px solid #e2e8f0;
                    text-align: center;
                    color: #718096;
                    font-size: 13px !important;
                }}
            </style>
        </head>
        <body>
            <div class="v5-banner">
                🧪 V5 TEST VERSION - Experimental Build
            </div>
            {html_body}
            <div class="footer">
                <p>This is a V5 TEST version of your daily update</p>
                <p>V5 features multi-recipient email support</p>
                <p>View in Obsidian for full functionality and cross-references</p>
                {f'<p style="font-size: 11px; color: #999; margin-top: 12px;">Generated using {model_used}</p>' if model_used else ''}
            </div>
        </body>
        </html>
        """

        return html_template

    def _clean_markdown_for_plain(self, markdown_content: str) -> str:
        """
        Clean up markdown for plain text email version
        """
        # Remove frontmatter
        if markdown_content.startswith('---'):
            parts = markdown_content.split('---', 2)
            if len(parts) > 2:
                markdown_content = parts[2]

        # Simple cleanup for plain text
        plain = markdown_content
        plain = plain.replace('###', '\n▸')
        plain = plain.replace('##', '\n▶')
        plain = plain.replace('#', '\n◆')
        plain = plain.replace('**', '')
        plain = plain.replace('*', '')
        plain = plain.replace('---', '\n' + '='*50 + '\n')

        return plain

    def _save_html_archive(self, html_content: str, version: str = None, test_mode: bool = False) -> str:
        """
        Save HTML email to archive folder for web viewing

        Args:
            html_content: The HTML email content
            version: Version identifier (e.g., "v5")
            test_mode: If True, adds "-test" to filename to avoid overwriting production

        Returns:
            str: Path to saved file
        """
        try:
            # Determine archive directory relative to project root
            script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            archive_dir = os.path.join(script_dir, "Published Updates", "email-html")

            # Create archive directory if it doesn't exist
            os.makedirs(archive_dir, exist_ok=True)

            # Generate filename with date, version, and test suffix
            today = datetime.now().strftime('%Y-%m-%d')
            version_suffix = f"-{version}" if version else ""
            test_suffix = "-test" if test_mode else ""
            filename = f"{today}{version_suffix}{test_suffix}-email.html"
            filepath = os.path.join(archive_dir, filename)

            # Save HTML content
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)

            logger.info(f"📁 V5 Email HTML archived to: {filepath}")
            return filepath

        except Exception as e:
            logger.warning(f"Failed to save HTML archive: {str(e)}")
            return None

def test_email_setup():
    """
    Test function to verify v5 email configuration
    """
    sender = EmailSenderV5()

    if not sender.enabled:
        print("❌ Email not configured. Please set GMAIL_APP_PASSWORD in .env file")
        return False

    # Send test email
    test_content = """
# Test V5 Daily News Update

## Multi-Recipient Email Test

Your V5 daily news agent email integration is working correctly!

**New V5 Features:**
- ✅ Multi-recipient email support
- ✅ Send to multiple addresses simultaneously
- ✅ V5 TEST labeling in email subject

**Recipients configured:** {}

---

*Sent from your Daily News Agent V5*
    """.format(', '.join(sender.recipients))

    success = sender.send_daily_update(
        test_content,
        subject="V5 TEST: Multi-Recipient Email Integration"
    )

    if success:
        print(f"✅ V5 test email sent to {len(sender.recipients)} recipient(s)")
        for recipient in sender.recipients:
            print(f"   - {recipient}")
    else:
        print("❌ Failed to send test email. Check logs for details.")

    return success

if __name__ == "__main__":
    # Run test when module is executed directly
    test_email_setup()
