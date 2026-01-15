"""
Email sender module for Daily News Agent
Sends daily updates via Gmail SMTP
"""

import os
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

class EmailSender:
    def __init__(self, sender_email: str = None, sender_password: str = None):
        """
        Initialize email sender with Gmail credentials
        
        Args:
            sender_email: Gmail address to send from
            sender_password: Gmail app password (not regular password)
        """
        self.sender_email = sender_email or os.getenv('GMAIL_ADDRESS', 'jon.sims@gmail.com')
        self.sender_password = sender_password or os.getenv('GMAIL_APP_PASSWORD')
        
        if not self.sender_password:
            logger.warning("Gmail app password not configured. Email sending disabled.")
            self.enabled = False
        else:
            self.enabled = True
            logger.info(f"Email sender initialized for {self.sender_email}")
    
    def send_daily_update(self,
                         markdown_content: str,
                         recipient: str = None,
                         subject: str = None,
                         source_label: str = None,
                         version: str = None) -> bool:
        """
        Send daily news update via email

        Args:
            markdown_content: The markdown content to send
            recipient: Email address to send to (defaults to sender)
            subject: Email subject (auto-generates if not provided)
            source_label: Label for update source (e.g., "Local" or "Web")
            version: Version identifier (e.g., "v2" or "v4")

        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.enabled:
            logger.info("Email sending disabled - no app password configured")
            return False

        try:
            # Default recipient is sender (sending to yourself)
            recipient = recipient or self.sender_email

            # Generate subject with today's date
            if not subject:
                now = datetime.now()
                day_abbr = now.strftime('%a')  # Sat
                date_str = now.strftime('%-m-%-d-%y')  # 9-27-25 (no leading zeros)
                time_str = now.strftime('%-I:%M%p').lower()  # 4:15pm

                # Build subject parts
                prefix = "Update"

                # Add version if provided (e.g., "Update v4")
                if version:
                    prefix = f"Update {version}"

                # Add source label if provided (e.g., "Update v4 (Web)")
                label = f" ({source_label})" if source_label else ""

                subject = f"{prefix}{label}: {day_abbr} {date_str} at {time_str}"
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"My Update <{self.sender_email}>"
            msg['To'] = recipient
            
            # Convert markdown to HTML for better email rendering
            html_content = self._markdown_to_html(markdown_content)

            # Save HTML copy to archive
            self._save_html_archive(html_content, version=version)

            # Create plain text version (strip some markdown for readability)
            plain_content = self._clean_markdown_for_plain(markdown_content)
            
            # Attach both plain text and HTML versions
            part1 = MIMEText(plain_content, 'plain')
            part2 = MIMEText(html_content, 'html')
            
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email via Gmail SMTP
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            logger.info(f"✅ Daily update emailed to {recipient}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send email: {str(e)}")
            return False
    
    def _markdown_to_html(self, markdown_content: str) -> str:
        """
        Convert markdown to HTML with nice styling
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
                
                h4, h5, h6 {{
                    font-size: 16px !important;
                    font-weight: 600;
                    color: #4a5568;
                    margin: 16px 0 8px 0;
                    line-height: 1.4;
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
                
                /* Strong/Bold text */
                strong, b {{
                    font-weight: 600;
                    color: #1a202c;
                    font-size: inherit !important;
                }}
                
                /* Emphasis/Italic text */
                em, i {{
                    font-style: italic;
                    color: #4a5568;
                    font-size: inherit !important;
                }}
                
                /* Lists - CRITICAL: Consistent sizing for all list items */
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
                
                /* Ensure all text inside list items maintains size */
                li * {{
                    font-size: 14px !important;
                }}
                
                li a {{
                    font-size: 14px !important;
                    font-weight: 500;
                }}
                
                li strong, li b {{
                    font-size: 14px !important;
                    font-weight: 600;
                }}
                
                li em, li i {{
                    font-size: 14px !important;
                }}
                
                /* Blockquotes (for Stoic quotes only) */
                blockquote {{
                    border-left: 4px solid #3182ce;
                    padding: 20px 24px;
                    margin: 24px 0;
                    background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
                    color: #4a5568;
                    font-style: italic;
                    font-size: 16px !important;
                    line-height: 1.6 !important;
                    border-radius: 6px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                }}
                
                blockquote p {{
                    margin: 8px 0;
                    font-size: 16px !important;
                    line-height: 1.6 !important;
                }}
                
                blockquote * {{
                    font-size: 16px !important;
                    line-height: 1.6 !important;
                }}
                
                /* Enhanced horizontal rules for section transitions */
                hr {{
                    border: none;
                    height: 3px;
                    background: linear-gradient(90deg, #3182ce, #60a5fa, #3182ce);
                    margin: 32px auto;
                    width: 80%;
                    border-radius: 2px;
                    opacity: 0.7;
                }}
                
                /* Alternative section divider styling */
                .section-divider {{
                    text-align: center;
                    margin: 40px 0;
                    position: relative;
                }}
                
                .section-divider::before {{
                    content: "◆ ◆ ◆";
                    color: #3182ce;
                    font-size: 14px;
                    letter-spacing: 8px;
                    opacity: 0.6;
                }}
                
                /* Special sections */
                .weather-section {{
                    background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                }}
                
                /* Beautiful article containers */
                .articles-container {{
                    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
                    border: 1px solid #cbd5e1;
                    border-radius: 8px;
                    padding: 16px 20px;
                    margin: 16px 0 24px 0;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                }}
                
                /* Articles header styling */
                .articles-header {{
                    font-size: 15px !important;
                    font-weight: 600;
                    color: #1e293b;
                    margin: 0 0 12px 0 !important;
                    border-bottom: 2px solid #e2e8f0;
                    padding-bottom: 6px;
                }}
                
                .articles-header strong {{
                    font-size: 15px !important;
                    font-weight: 600;
                    color: #1e293b;
                }}
                
                /* Individual article link styling */
                .article-link {{
                    font-size: 14px !important;
                    line-height: 1.6 !important;
                    margin: 6px 0 !important;
                    color: #334155 !important;
                    font-style: normal !important;
                    padding-left: 0 !important;
                }}
                
                /* Links within article containers */
                .articles-container a {{
                    font-size: 14px !important;
                    font-weight: 500;
                    color: #1e40af !important;
                    text-decoration: none !important;
                }}
                
                .articles-container a:hover {{
                    color: #1d4ed8 !important;
                    text-decoration: underline !important;
                }}
                
                /* Source attribution styling */
                .article-link {{
                    position: relative;
                }}
                
                .article-link::before {{
                    content: "📎";
                    margin-right: 6px;
                    font-size: 14px;
                    opacity: 0.6;
                }}
                
                /* General article container paragraph styling */
                .articles-container p {{
                    font-size: 14px !important;
                    line-height: 1.6 !important;
                    margin: 6px 0 !important;
                    color: #334155 !important;
                    font-style: normal !important;
                }}
                
                /* Force all text in article containers to be consistent */
                .articles-container * {{
                    font-size: 14px !important;
                    font-style: normal !important;
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
                
                /* Nuclear option: Force ALL elements to respect sizing */
                span, div, a, strong, b, em, i {{
                    font-size: inherit !important;
                }}
                
                /* Force specific elements that commonly cause issues */
                [style*="font-size"] {{
                    font-size: 14px !important;
                }}
                
                /* Override any inline styles that might be causing issues */
                * [style] {{
                    font-size: inherit !important;
                }}
                
                /* Article Links section - small font */
                .article-links-section {{
                    font-size: 11px !important;
                    line-height: 1.4 !important;
                    color: #64748b !important;
                }}
                
                .article-links-section * {{
                    font-size: 11px !important;
                    line-height: 1.4 !important;
                }}
                
                .article-links-section p {{
                    font-size: 11px !important;
                    margin: 4px 0 !important;
                }}
                
                .article-links-section a {{
                    font-size: 11px !important;
                    color: #3182ce !important;
                }}
                
                .article-links-section strong {{
                    font-size: 11px !important;
                    color: #475569 !important;
                }}
                
                /* Comprehensive mobile responsive design */
                @media only screen and (max-width: 600px) {{
                    body {{
                        padding: 12px !important;
                        font-size: 15px !important;
                        line-height: 1.5 !important;
                    }}
                    
                    h1 {{
                        font-size: 22px !important;
                        text-align: left !important;
                        padding-bottom: 8px !important;
                        margin-bottom: 16px !important;
                    }}
                    
                    h2 {{
                        font-size: 18px !important;
                        margin: 24px 0 12px 0 !important;
                    }}
                    
                    h3 {{
                        font-size: 16px !important;
                        padding: 8px 12px !important;
                        margin: 20px 0 12px 0 !important;
                    }}
                    
                    /* Mobile article containers */
                    .articles-container {{
                        padding: 12px 16px !important;
                        margin: 12px 0 16px 0 !important;
                        border-radius: 6px !important;
                        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
                    }}
                    
                    .article-link {{
                        font-size: 13px !important;
                        line-height: 1.5 !important;
                        margin: 4px 0 !important;
                    }}
                    
                    .articles-header {{
                        font-size: 14px !important;
                        margin-bottom: 8px !important;
                        padding-bottom: 4px !important;
                    }}
                    
                    /* Mobile blockquotes */
                    blockquote {{
                        padding: 12px 16px !important;
                        margin: 16px 0 !important;
                        font-size: 14px !important;
                    }}
                    
                    blockquote * {{
                        font-size: 14px !important;
                    }}
                    
                    /* Mobile links - larger touch targets */
                    a {{
                        font-size: 13px !important;
                        padding: 2px 0 !important;
                        display: inline-block !important;
                        min-height: 20px !important;
                    }}
                    
                    .articles-container a {{
                        font-size: 13px !important;
                        line-height: 1.4 !important;
                    }}
                    
                    /* Mobile horizontal rules */
                    hr {{
                        width: 90% !important;
                        margin: 20px auto !important;
                        height: 2px !important;
                    }}
                    
                    /* Mobile paragraph spacing */
                    p {{
                        font-size: 15px !important;
                        margin: 8px 0 !important;
                    }}
                    
                    /* Mobile footer */
                    .footer {{
                        margin-top: 30px !important;
                        padding-top: 15px !important;
                        font-size: 14px !important;
                    }}
                }}
                
                /* Extra small screens */
                @media only screen and (max-width: 400px) {{
                    body {{
                        padding: 8px !important;
                    }}
                    
                    h1 {{
                        font-size: 20px !important;
                    }}
                    
                    .articles-container {{
                        padding: 8px 12px !important;
                    }}
                    
                    .article-link {{
                        font-size: 14px !important;
                    }}
                }}
            </style>
        </head>
        <body>
            {html_body}
            <div class="footer">
                <p>This daily update was automatically generated and sent at 5:00 AM EST</p>
                <p>View in Obsidian for full functionality and cross-references</p>
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

    def _save_html_archive(self, html_content: str, version: str = None) -> str:
        """
        Save HTML email to archive folder for web viewing

        Args:
            html_content: The HTML email content
            version: Version identifier (e.g., "v2" or "v4")

        Returns:
            str: Path to saved file
        """
        try:
            # Determine archive directory relative to project root
            script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            archive_dir = os.path.join(script_dir, "Published Updates", "email-html")

            # Create archive directory if it doesn't exist
            os.makedirs(archive_dir, exist_ok=True)

            # Generate filename with date and version
            today = datetime.now().strftime('%Y-%m-%d')
            version_suffix = f"-{version}" if version else ""
            filename = f"{today}{version_suffix}-email.html"
            filepath = os.path.join(archive_dir, filename)

            # Save HTML content
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)

            logger.info(f"📁 Email HTML archived to: {filepath}")
            return filepath

        except Exception as e:
            logger.warning(f"Failed to save HTML archive: {str(e)}")
            return None

def test_email_setup():
    """
    Test function to verify email configuration
    """
    sender = EmailSender()
    
    if not sender.enabled:
        print("❌ Email not configured. Please set GMAIL_APP_PASSWORD in .env file")
        print("\nTo set up Gmail App Password:")
        print("1. Go to https://myaccount.google.com/security")
        print("2. Enable 2-factor authentication if not already enabled")
        print("3. Search for 'App passwords'")
        print("4. Generate a new app password for 'Mail'")
        print("5. Add to .env file: GMAIL_APP_PASSWORD='your-16-char-password'")
        return False
    
    # Send test email
    test_content = """
# Test Daily News Update

## This is a test email

Your daily news agent email integration is working correctly!

**Articles:**
- [Test Article 1](https://example.com) - *Test Source*
- [Test Article 2](https://example.com) - *Test Source*

---

*Sent from your Daily News Agent*
    """
    
    success = sender.send_daily_update(
        test_content,
        subject="TEST: Daily News Email Integration"
    )
    
    if success:
        print(f"✅ Test email sent successfully to {sender.sender_email}")
    else:
        print("❌ Failed to send test email. Check logs for details.")
    
    return success

if __name__ == "__main__":
    # Run test when module is executed directly
    test_email_setup()