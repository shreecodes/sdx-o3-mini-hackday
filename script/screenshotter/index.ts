import { chromium } from '@playwright/test';
import * as fs from 'fs';

// outputPath will be: filename_<timestamp>.png
async function captureScreenshots(outputPath: string) {
  
  // Launch browser
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  // Array to store console errors
  const consoleErrors: string[] = [];

  // Listen for console errors
  page.on('console', msg => {
    if (msg.type() === 'error') {
      consoleErrors.push(`Console Error: ${msg.text()}`);
    }
  });

  // Also listen for page errors
  page.on('pageerror', exception => {
    consoleErrors.push(`Page Error: ${exception.message}`);
  });

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

    // Report any errors that were captured
    if (consoleErrors.length > 0) {
      console.error('screenshotter: Errors found during page load.');

      // Create corresponding log path by replacing .png with .log
      const logPath = outputPath.replace(/\.png$/, '.log');

      // Write errors to log file
      fs.writeFileSync(
        logPath,
        consoleErrors.join('\n'),
        'utf-8'
      );
      console.log(`Console errors saved to ${logPath}`);
    }

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