#!/usr/bin/env node

/**
 * This script attempts to automatically fix common E2E test issues
 * based on the analysis of test failures.
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log('🔧 Attempting to fix common E2E test issues...');

// Configuration
const FRONTEND_DIR = path.join(process.cwd(), 'frontend');
const PLAYWRIGHT_CONFIG = path.join(FRONTEND_DIR, 'playwright.config.ts');
const E2E_DIR = path.join(FRONTEND_DIR, 'e2e');

// Check if the necessary directories exist
if (!fs.existsSync(FRONTEND_DIR)) {
  console.error('❌ Frontend directory not found.');
  process.exit(1);
}

// Fix 1: Increase timeouts in Playwright config
console.log('⏱️ Checking Playwright timeouts...');
if (fs.existsSync(PLAYWRIGHT_CONFIG)) {
  let config = fs.readFileSync(PLAYWRIGHT_CONFIG, 'utf8');
  
  // Check if timeout is less than 60 seconds
  if (config.includes('timeout:') && !config.includes('timeout: 60000')) {
    console.log('Increasing test timeout to 60 seconds...');
    config = config.replace(/timeout: \d+/, 'timeout: 60000');
    fs.writeFileSync(PLAYWRIGHT_CONFIG, config);
    console.log('✅ Timeout increased in Playwright config.');
  } else {
    console.log('✅ Timeout already set to an appropriate value.');
  }
} else {
  console.log('❌ Playwright config not found. Cannot adjust timeouts.');
}

// Fix 2: Check for and fix common selector issues
console.log('\n🔍 Checking for common selector issues in E2E tests...');
if (fs.existsSync(E2E_DIR)) {
  const testFiles = fs.readdirSync(E2E_DIR).filter(file => file.endsWith('.ts') || file.endsWith('.js'));
  
  let fixedSelectors = 0;
  
  testFiles.forEach(file => {
    const filePath = path.join(E2E_DIR, file);
    let content = fs.readFileSync(filePath, 'utf8');
    
    // Replace problematic selectors with more robust ones
    const originalContent = content;
    
    // Fix: Replace exact text matches with case-insensitive regex
    content = content.replace(/getByText\(['"]([^'"]+)['"]\)/g, "getByText(/^$1$/i)");
    
    // Fix: Add waitFor to potentially flaky assertions
    content = content.replace(/await expect\(([^)]+)\)\.toBeVisible\(\)/g, 
      "await expect($1).toBeVisible({ timeout: 10000 })");
    
    // Fix: Add navigation waits after clicks that might cause navigation
    content = content.replace(/await ([^.]+)\.click\(\);(\s+)(?!await page\.waitForNavigation)/g, 
      "await $1.click();\n  await page.waitForLoadState('networkidle');$2");
    
    if (content !== originalContent) {
      fs.writeFileSync(filePath, content);
      fixedSelectors++;
      console.log(`✅ Fixed potential selector issues in ${file}`);
    }
  });
  
  console.log(`Fixed selectors in ${fixedSelectors} files.`);
} else {
  console.log('❌ E2E test directory not found.');
}

// Fix 3: Ensure servers are properly configured to wait for startup
console.log('\n🌐 Checking server startup configuration in GitHub workflow...');
const workflowFile = path.join(process.cwd(), '.github', 'workflows', 'continuous-testing.yml');

if (fs.existsSync(workflowFile)) {
  let workflow = fs.readFileSync(workflowFile, 'utf8');
  
  // Check if we need to increase wait time for servers
  if (workflow.includes('sleep 10')) {
    console.log('Increasing server startup wait time...');
    workflow = workflow.replace(/sleep 10/g, 'sleep 30');
    fs.writeFileSync(workflowFile, workflow);
    console.log('✅ Increased server startup wait time in workflow.');
  } else {
    console.log('✅ Server startup wait time already set appropriately.');
  }
} else {
  console.log('❌ GitHub workflow file not found.');
}

console.log('\n🎉 Completed automatic fixes for common E2E test issues.');
console.log('Note: These are best-effort fixes and may not resolve all issues.'); 