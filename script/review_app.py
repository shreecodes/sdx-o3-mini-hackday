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
    base_prompt = (
        "Please review this screenshot of the landing page and evaluate what changes need to be made in order to implement the following creative vision:\n"
        "<creative_vision>\n{creative_vision}\n</creative_vision>\n\n"
        "Focus on the following aspects:\n"
        "1. Visual consistency and alignment:\n"
        "   - Are elements properly aligned and spaced?\n"
        "   - Is the visual hierarchy clear and logical?\n"
        "   - Are fonts and colors consistent?\n\n"
        "2. Responsiveness and layout:\n"
        "   - Do all elements fit properly within their containers?\n"
        "   - Is there any overflow or cutoff content?\n\n"
        "3. Overall assessment:\n"
        "   - What works well?\n"
        "   - What specific improvements are needed?\n"
        "   - Are there any bugs or issues to address?"
    )

    if additional_instructions and len(additional_instructions.strip()) > 0:
        base_prompt += f"\n\nAlso heed these additional instructions:\n<additional_instructions>\n{additional_instructions}\n</additional_instructions>\n\n"
    
    return base_prompt.format(creative_vision=creative_vision, additional_instructions=additional_instructions)

def review_landing_page(app_name: str, creative_vision: str, additional_instructions: str) -> str:
    """
    Review a landing page screenshot based on user instructions.
    
    Args:
        user_instructions (str): The user's instructions for modifying the landing page
    """
    review_prompt = generate_review_prompt(creative_vision, additional_instructions)
    return analyze_screenshot(app_name, review_prompt)
