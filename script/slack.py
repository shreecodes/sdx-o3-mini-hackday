import os
import requests

SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL')
if not SLACK_WEBHOOK_URL:
    raise ValueError("SLACK_WEBHOOK_URL environment variable is not set")

def send_slack_message(message: str) -> bool:
    """
    Send a message to Slack using the webhook URL.
    
    Args:
        message (str): The message to send to Slack
        
    Returns:
        bool: True if message was sent successfully, False otherwise
    """
    try:
        payload = {"text": message}
        response = requests.post(SLACK_WEBHOOK_URL, json=payload)
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending Slack message: {e}")
        return False

# Example usage:
if __name__ == "__main__":
    success = send_slack_message("Hello from Python!")
    print("Message sent successfully" if success else "Failed to send message")