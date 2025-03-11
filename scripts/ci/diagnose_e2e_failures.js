#!/usr/bin/env node

/**
 * This script analyzes E2E test failures and provides diagnostic information
 * to help identify common issues.
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Configuration
const PLAYWRIGHT_REPORT_DIR = path.join(process.cwd(), 'frontend', 'playwright-report');
const RESULTS_JSON = path.join(PLAYWRIGHT_REPORT_DIR, 'results.json');

console.log('🔍 Diagnosing E2E test failures...');

// Check if the report directory exists
if (!fs.existsSync(PLAYWRIGHT_REPORT_DIR)) {
  console.error('❌ Playwright report directory not found. No test results to analyze.');
  process.exit(1);
}

// Check if results.json exists
if (!fs.existsSync(RESULTS_JSON)) {
  console.error('❌ Playwright results.json not found. Cannot analyze test results.');
  process.exit(1);
}

try {
  // Read and parse the results
  const results = JSON.parse(fs.readFileSync(RESULTS_JSON, 'utf8'));
  
  // Count failures
  const failedTests = results.suites
    .flatMap(suite => suite.specs)
    .flatMap(spec => spec.tests)
    .filter(test => test.status === 'failed');
  
  console.log(`Found ${failedTests.length} failed tests.`);
  
  if (failedTests.length === 0) {
    console.log('✅ No failed tests found in the report.');
    process.exit(0);
  }
  
  // Analyze each failure
  failedTests.forEach((test, index) => {
    console.log(`\n🔍 Analyzing failure #${index + 1}: ${test.title}`);
    
    // Extract error message
    const error = test.errors[0]?.message || 'No error message available';
    console.log(`Error: ${error}`);
    
    // Common failure patterns and diagnostics
    if (error.includes('timeout')) {
      console.log('⏱️ This appears to be a timeout issue. Possible causes:');
      console.log('  - Network latency or slow server response');
      console.log('  - Element not appearing within expected timeframe');
      console.log('  - Incorrect selector causing wait to time out');
    } else if (error.includes('selector') || error.includes('locator')) {
      console.log('🔍 This appears to be a selector issue. Possible causes:');
      console.log('  - Element structure changed in the application');
      console.log('  - Element is in a different state than expected');
      console.log('  - Element is inside an iframe or shadow DOM');
    } else if (error.includes('navigation')) {
      console.log('🧭 This appears to be a navigation issue. Possible causes:');
      console.log('  - Page redirect not completing');
      console.log('  - URL structure changed');
      console.log('  - Navigation blocked by the application');
    } else if (error.includes('expect')) {
      console.log('✓ This appears to be an assertion failure. Possible causes:');
      console.log('  - Expected state does not match actual application state');
      console.log('  - Race condition where assertion runs before state updates');
      console.log('  - Application logic changed affecting expected outcomes');
    }
  });
  
  // Check for environment issues
  console.log('\n🌐 Checking for environment issues...');
  
  // Check if frontend server was running
  try {
    execSync('curl -s http://localhost:3000 > /dev/null');
    console.log('✅ Frontend server appears to be running.');
  } catch (e) {
    console.log('❌ Frontend server may not be running correctly.');
  }
  
  // Check if backend server was running
  try {
    execSync('curl -s http://localhost:8000 > /dev/null');
    console.log('✅ Backend server appears to be running.');
  } catch (e) {
    console.log('❌ Backend server may not be running correctly.');
  }
  
  console.log('\n📋 Recommendations:');
  console.log('1. Review screenshots and videos in the playwright-report directory');
  console.log('2. Try running tests with increased timeouts');
  console.log('3. Verify that selectors match the current application structure');
  console.log('4. Ensure both frontend and backend servers are running correctly');
  
} catch (error) {
  console.error('❌ Error analyzing test results:', error);
  process.exit(1);
} 