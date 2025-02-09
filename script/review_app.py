from analyze_screenshot import analyze_screenshot

def generate_review_prompt(creative_vision: str, additional_instructions: str) -> str:
    """
    Generate a prompt for reviewing a screenshot based on user instructions.
    
    Args:
        creative_vision (str): The user's creative vision for the landing page
        additional_instructions (str): Additional instructions for the review
    Returns:
        str: A prompt for analyzing the screenshot
    """
    vision = creative_vision
    if additional_instructions and len(additional_instructions.strip()) > 0:
        vision = additional_instructions

    return f"Please review this screenshot of a website's landing page and provide feedback on what changes could be made to improve the implementation of the following creative vision:\n<creative_vision>\n{vision}\n</creative_vision>\n\n"

def review_landing_page(app_name: str, creative_vision: str, additional_instructions: str) -> str:
    """
    Review a landing page screenshot based on creative vision and additional instructions.
    
    Args:
        app_name (str): The name of the application to review
        creative_vision (str): The user's creative vision for the landing page
        additional_instructions (str): Additional instructions for the review
    Returns:
        str: Analysis results from the screenshot review
    """
    review_prompt = generate_review_prompt(creative_vision, additional_instructions)
    return analyze_screenshot(app_name, review_prompt)
