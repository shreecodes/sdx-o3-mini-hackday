import { chromium } from '@playwright/test';

async function captureScreenshots() {
  // Launch browser
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    // Navigate to localhost:3000
    await page.goto('http://localhost:3000');
    
    // Wait for the page to be fully loaded
    await page.waitForLoadState('networkidle');

    // Take a screenshot
    await page.screenshot({
      path: 'screenshot.png',
      fullPage: true
    });

    console.log('Screenshot captured successfully at screenshot.png');
  } catch (error) {
    console.error('Error capturing screenshot:', error);
  } finally {
    // Clean up
    await browser.close();
  }
}

// Run the screenshot capture
captureScreenshots().catch(console.error);