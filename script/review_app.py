from analyze_screenshot import analyze_screenshot

def generate_review_prompt(user_instructions: str) -> str:
    """
    Generate a prompt for reviewing a screenshot based on user instructions.
    
    Args:
        user_instructions (str): The user's instructions for modifying the landing page
        
    Returns:
        str: A prompt for analyzing the screenshot
    """
    base_prompt = (
        "Please review this screenshot of the landing page and evaluate the following aspects:\n\n"
        "1. Does the page accurately implement these requested changes:\n{instructions}\n\n"
        "2. Visual consistency and alignment:\n"
        "   - Are elements properly aligned and spaced?\n"
        "   - Is the visual hierarchy clear and logical?\n"
        "   - Are fonts and colors consistent?\n\n"
        "3. Responsiveness and layout:\n"
        "   - Do all elements fit properly within their containers?\n"
        "   - Is there any overflow or cutoff content?\n\n"
        "4. Overall assessment:\n"
        "   - What works well?\n"
        "   - What specific improvements are needed?\n"
        "   - Are there any bugs or issues to address?"
    )
    
    return base_prompt.format(instructions=user_instructions)

def review_landing_page(user_instructions: str):
    """
    Review a landing page screenshot based on user instructions.
    
    Args:
        user_instructions (str): The user's instructions for modifying the landing page
    """
    review_prompt = generate_review_prompt(user_instructions)
    analyze_screenshot(review_prompt)
