import { test, expect } from '@playwright/test';

test.describe('Home Page', () => {
  test('should load the home page', async ({ page }) => {
    await page.goto('/');
    
    // Check if the page title is correct
    await expect(page).toHaveTitle(/AI Compliance Checker/);
    
    // Check if the main heading is visible
    const heading = page.getByRole('heading', { name: /AI Compliance Checker/i });
    await expect(heading).toBeVisible();
  });

  test('should have upload functionality', async ({ page }) => {
    await page.goto('/');
    
    // Check if the upload form is present
    const uploadForm = page.getByTestId('upload-form');
    await expect(uploadForm).toBeVisible();
  });
}); 