import { chromium } from '@playwright/test';

async function captureScreenshots(outputPath: string) {
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
      path: outputPath,
      fullPage: true
    });

    console.log(`Screenshot captured successfully at ${outputPath}`);
  } catch (error) {
    console.error('Error capturing screenshot:', error);
  } finally {
    // Clean up
    await browser.close();
  }
}

// Get filename from command line arguments
const outputPath = process.argv[2];

if (!outputPath) {
  console.error('Please provide an output filename as an argument');
  process.exit(1);
}

// Run the screenshot capture
captureScreenshots(outputPath).catch(console.error);