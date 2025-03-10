#!/usr/bin/env node

/**
 * Script to diagnose common frontend test failures.
 * This script analyzes test failure outputs and provides diagnostic information.
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const glob = require('glob');

// Define common failure patterns and their likely causes
const FAILURE_PATTERNS = {
  'Cannot find module': {
    regex: /Cannot find module '([^']+)'/,
    diagnosis: 'Missing dependency: {0}',
    fix: 'Run: npm install {0}'
  },
  'Property does not exist': {
    regex: /Property '([^']+)' does not exist on type/,
    diagnosis: 'Missing property: {0}',
    fix: 'Check if the property {0} exists on the object'
  },
  'is not a function': {
    regex: /([^']+) is not a function/,
    diagnosis: 'Not a function: {0}',
    fix: 'Check if {0} is defined and is a function'
  },
  'Unexpected token': {
    regex: /Unexpected token '([^']+)'/,
    diagnosis: 'Syntax error: Unexpected token {0}',
    fix: 'Fix the syntax error in the file'
  },
  'Cannot read property': {
    regex: /Cannot read properties? of ([^ ]+) \(reading '([^']+)'\)/,
    diagnosis: 'Cannot read property {1} of {0}',
    fix: 'Check if the object is defined before accessing property {1}'
  },
  'Test timeout': {
    regex: /Timeout - Async callback was not invoked within the (\d+)ms/,
    diagnosis: 'Test timeout after {0}ms',
    fix: 'Increase the timeout or optimize the test'
  },
  'Failed to load module': {
    regex: /Failed to load module from ([^:]+)/,
    diagnosis: 'Failed to load module from {0}',
    fix: 'Check if the module exists at {0}'
  },
  'Invalid hook call': {
    regex: /Invalid hook call\. Hooks can only be called inside/,
    diagnosis: 'Invalid hook call',
    fix: 'Ensure hooks are only called inside functional components or custom hooks'
  },
  'Expected value to be': {
    regex: /Expected:[\s\n]+([^\n]+)[\s\n]+Received:[\s\n]+([^\n]+)/,
    diagnosis: 'Assertion failed: expected {0}, got {1}',
    fix: 'Check the expected and actual values in the test'
  }
};

/**
 * Find test output files in the current directory and subdirectories.
 * @returns {string[]} Array of file paths
 */
function findTestOutputFiles() {
  try {
    // Look for Jest output files or other test output files
    const patterns = [
      'frontend/junit.xml',
      'frontend/test-results/*.xml',
      'frontend/coverage/lcov.info',
      'frontend/test-output.log'
    ];
    
    let outputFiles = [];
    patterns.forEach(pattern => {
      try {
        const files = glob.sync(pattern);
        outputFiles = outputFiles.concat(files);
      } catch (error) {
        console.error(`Error searching for pattern ${pattern}:`, error);
      }
    });
    
    return outputFiles;
  } catch (error) {
    console.error('Error finding test output files:', error);
    return [];
  }
}

/**
 * Parse test output file and extract failure information.
 * @param {string} filePath - Path to the test output file
 * @returns {Object[]} Array of failure objects
 */
function parseTestOutput(filePath) {
  const failures = [];
  
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const fileExt = path.extname(filePath);
    
    if (fileExt === '.xml') {
      // Parse XML output (e.g., JUnit format)
      const parseXml = require('xml2js').parseString;
      parseXml(content, (err, result) => {
        if (err) {
          console.error(`Error parsing XML file ${filePath}:`, err);
          return;
        }
        
        try {
          // Extract failures from JUnit XML format
          const testsuites = result.testsuites || { testsuite: [result.testsuite] };
          const testsuiteArray = testsuites.testsuite || [];
          
          testsuiteArray.forEach(testsuite => {
            const testcases = testsuite.testcase || [];
            testcases.forEach(testcase => {
              if (testcase.failure) {
                failures.push({
                  testName: testcase.$.name,
                  testClass: testcase.$.classname,
                  message: testcase.failure[0].$.message,
                  details: testcase.failure[0]._
                });
              }
            });
          });
        } catch (parseError) {
          console.error(`Error extracting failures from XML:`, parseError);
        }
      });
    } else {
      // Parse text output
      // Look for test failure patterns in text output
      const lines = content.split('\n');
      let currentTest = null;
      let currentError = null;
      
      lines.forEach(line => {
        // Look for test name
        const testMatch = line.match(/FAIL\s+([^\s]+)/);
        if (testMatch) {
          currentTest = testMatch[1];
        }
        
        // Look for error message
        if (line.includes('Error:') || line.includes('AssertionError:')) {
          currentError = line;
          
          if (currentTest) {
            failures.push({
              testName: currentTest,
              testClass: currentTest.split(' ')[0],
              message: currentError,
              details: line
            });
            
            currentTest = null;
            currentError = null;
          }
        }
      });
    }
  } catch (error) {
    console.error(`Error parsing file ${filePath}:`, error);
  }
  
  return failures;
}

/**
 * Diagnose the cause of a test failure and suggest a fix.
 * @param {Object} failure - Failure object
 * @returns {Object} Diagnosis and fix
 */
function diagnoseFailure(failure) {
  const message = failure.message || '';
  const details = failure.details || '';
  const fullText = `${message} ${details}`;
  
  // Check for known failure patterns
  for (const [key, pattern] of Object.entries(FAILURE_PATTERNS)) {
    const match = fullText.match(pattern.regex);
    if (match) {
      const groups = match.slice(1);
      let diagnosis = pattern.diagnosis;
      let fix = pattern.fix;
      
      // Replace placeholders with matched groups
      groups.forEach((group, index) => {
        diagnosis = diagnosis.replace(`{${index}}`, group);
        fix = fix.replace(`{${index}}`, group);
      });
      
      return { diagnosis, fix };
    }
  }
  
  // If no known pattern is found
  return { diagnosis: 'Unknown failure cause', fix: null };
}

/**
 * Check for common issues in the codebase that might cause test failures.
 * @returns {Object[]} Array of issue objects
 */
function checkForCommonIssues() {
  const issues = [];
  
  // Check for missing dependencies in package.json
  try {
    const packageJsonPath = path.join(process.cwd(), 'frontend', 'package.json');
    if (fs.existsSync(packageJsonPath)) {
      const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
      
      // Check for common testing dependencies
      const requiredDevDependencies = [
        'jest',
        '@testing-library/react',
        '@testing-library/jest-dom'
      ];
      
      requiredDevDependencies.forEach(dep => {
        if (!packageJson.devDependencies || !packageJson.devDependencies[dep]) {
          issues.push({
            type: 'missing_dependency',
            location: 'package.json',
            description: `Missing dev dependency: ${dep}`,
            fix: `Run: npm install --save-dev ${dep}`
          });
        }
      });
      
      // Check for Jest configuration
      if (!packageJson.jest && !fs.existsSync(path.join(process.cwd(), 'frontend', 'jest.config.js'))) {
        issues.push({
          type: 'missing_config',
          location: 'package.json or jest.config.js',
          description: 'Missing Jest configuration',
          fix: 'Add Jest configuration to package.json or create jest.config.js'
        });
      }
    }
  } catch (error) {
    console.error('Error checking package.json:', error);
  }
  
  // Check for common configuration files
  const configFiles = [
    { path: 'frontend/tsconfig.json', description: 'TypeScript configuration' },
    { path: 'frontend/.babelrc', description: 'Babel configuration' }
  ];
  
  configFiles.forEach(file => {
    if (!fs.existsSync(path.join(process.cwd(), file.path))) {
      issues.push({
        type: 'missing_config',
        location: file.path,
        description: `Missing ${file.description}`,
        fix: `Create ${file.path} with appropriate configuration`
      });
    }
  });
  
  // Check for test setup file
  const setupFilePath = path.join(process.cwd(), 'frontend', 'jest.setup.js');
  if (!fs.existsSync(setupFilePath)) {
    issues.push({
      type: 'missing_setup',
      location: 'frontend/jest.setup.js',
      description: 'Missing Jest setup file',
      fix: 'Create jest.setup.js with appropriate test setup'
    });
  }
  
  return issues;
}

/**
 * Main function to diagnose test failures.
 */
function main() {
  console.log('Diagnosing frontend test failures...');
  
  // Find test output files
  const outputFiles = findTestOutputFiles();
  if (outputFiles.length === 0) {
    console.log('No test output files found.');
    
    // Check if we can run Jest to generate output
    try {
      execSync('cd frontend && npx jest --listTests', { stdio: 'pipe' });
      console.log('Jest is available. You can run tests to generate output files.');
    } catch (error) {
      console.log('Jest not found or error listing tests. Make sure it\'s installed.');
    }
    
    // Check for common issues anyway
    const issues = checkForCommonIssues();
    if (issues.length > 0) {
      console.log('\nFound potential issues:');
      issues.forEach(issue => {
        console.log(`- ${issue.description}`);
        console.log(`  Fix: ${issue.fix}`);
      });
    }
    
    return;
  }
  
  // Parse test output files and diagnose failures
  let allFailures = [];
  outputFiles.forEach(filePath => {
    console.log(`Analyzing ${filePath}...`);
    const failures = parseTestOutput(filePath);
    allFailures = allFailures.concat(failures);
  });
  
  if (allFailures.length === 0) {
    console.log('No test failures found in output files.');
    return;
  }
  
  // Diagnose each failure
  console.log(`\nFound ${allFailures.length} test failures:`);
  allFailures.forEach((failure, index) => {
    const testName = failure.testName || 'Unknown test';
    const testClass = failure.testClass || '';
    
    console.log(`\n${index + 1}. Test: ${testName} (${testClass})`);
    
    const { diagnosis, fix } = diagnoseFailure(failure);
    console.log(`   Diagnosis: ${diagnosis}`);
    
    if (fix) {
      console.log(`   Suggested fix: ${fix}`);
    } else {
      console.log('   No automatic fix available. Manual investigation required.');
    }
  });
  
  // Check for common issues
  const issues = checkForCommonIssues();
  if (issues.length > 0) {
    console.log('\nAdditional potential issues:');
    issues.forEach(issue => {
      console.log(`- ${issue.description}`);
      console.log(`  Fix: ${issue.fix}`);
    });
  }
  
  // Write diagnostic report to file
  const report = {
    failures: allFailures,
    diagnoses: allFailures.map(failure => {
      const { diagnosis, fix } = diagnoseFailure(failure);
      return {
        test: failure.testName,
        diagnosis,
        fix
      };
    }),
    issues
  };
  
  fs.writeFileSync('frontend_test_diagnosis_report.json', JSON.stringify(report, null, 2));
  console.log('\nDiagnostic report written to frontend_test_diagnosis_report.json');
}

// Run the main function
main(); 