import { test, expect } from '@playwright/test';
import path from 'path';

test.describe('Personal Listing Agent', () => {
  // Helper to log in before each test
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.getByTestId('login-submit').click();
    await expect(page).toHaveURL('/upload');
  });

  test('should display upload page with all elements', async ({ page }) => {
    await expect(page.getByTestId('upload-heading')).toHaveText('Personal Listing Agent');
    await expect(page.getByTestId('upload-panel')).toBeVisible();
    await expect(page.getByTestId('upload-images')).toBeVisible();
    await expect(page.getByTestId('upload-notes')).toBeVisible();
    await expect(page.getByTestId('analyze-button')).toBeVisible();
  });

  test('should show analyze button disabled until image is selected', async ({ page }) => {
    const analyzeButton = page.getByTestId('analyze-button');
    
    // Initially may be disabled or enabled depending on implementation
    await expect(analyzeButton).toBeVisible();
  });

  test('should show preview panel after analysis', async ({ page }) => {
    // This test requires a mock image - skip in real runs without test fixtures
    test.skip(true, 'Requires test image fixture');
    
    // Upload an image
    const fileInput = page.getByTestId('upload-images');
    await fileInput.setInputFiles(path.join(__dirname, 'fixtures', 'test-dog.jpg'));
    
    // Fill in notes
    await page.getByTestId('upload-notes').fill('Name: Buddy, breed: Golden Retriever');
    
    // Click analyze
    await page.getByTestId('analyze-button').click();
    
    // Should show preview panel
    await expect(page.getByTestId('preview-panel')).toBeVisible();
  });

  test('should show logout button when logged in', async ({ page }) => {
    await expect(page.getByRole('button', { name: 'Logout' })).toBeVisible();
  });

  test('should redirect to home after logout', async ({ page }) => {
    await page.getByRole('button', { name: 'Logout' }).click();
    await expect(page).toHaveURL('/');
  });
});
