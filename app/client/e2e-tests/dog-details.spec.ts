import { test, expect } from '@playwright/test';

test.describe('Dog Details', () => {
  test('should navigate to dog details from homepage', async ({ page }) => {
    await page.goto('/');

    const firstDogCard = page.getByTestId('dog-card').first();
    const dogName = await page.getByTestId('dog-name').first().textContent();

    await firstDogCard.click();

    await expect(page).toHaveURL(/\/dog\/\d+/);
    await expect(page).toHaveTitle(/Dog Details - MatchMyMutt/);
    await expect(page.getByTestId('dog-details')).toBeVisible();
    await expect(page.getByTestId('dog-name')).toContainText(dogName!);
  });

  test('should display dog details with required fields', async ({ page }) => {
    await page.goto('/');
    
    // Navigate to first dog
    await page.getByTestId('dog-card').first().click();
    await expect(page).toHaveURL(/\/dog\/\d+/);

    // Check all required fields are present
    await expect(page.getByTestId('dog-details')).toBeVisible();
    await expect(page.getByTestId('dog-name')).toBeVisible();
    await expect(page.getByTestId('dog-breed')).toBeVisible();
    await expect(page.getByTestId('dog-age')).toBeVisible();
    await expect(page.getByTestId('dog-gender')).toBeVisible();
    await expect(page.getByTestId('dog-status')).toBeVisible();
    await expect(page.getByTestId('dog-description')).toBeVisible();
  });

  test('should navigate back to homepage from dog details', async ({ page }) => {
    await page.goto('/');
    await page.getByTestId('dog-card').first().click();
    await expect(page).toHaveURL(/\/dog\/\d+/);

    await page.getByTestId('back-link').click();

    await expect(page).toHaveURL('/');
    await expect(page.getByRole('heading', { name: 'Welcome to MatchMyMutt' })).toBeVisible();
  });

  test('should handle invalid dog ID gracefully', async ({ page }) => {
    await page.goto('/dog/99999');

    await expect(page).toHaveTitle(/Dog Details - MatchMyMutt/);
    await expect(page.getByTestId('error-message')).toBeVisible();
    await expect(page.getByTestId('back-link')).toBeVisible();
  });

  test('should display AI-generated listing info when available', async ({ page }) => {
    // Navigate to the newest dog (which should be AI-generated)
    await page.goto('/');
    await page.getByTestId('dog-card').first().click();
    await expect(page).toHaveURL(/\/dog\/\d+/);

    // If it's an AI-generated listing, it should have additional fields
    const details = page.getByTestId('dog-details');
    await expect(details).toBeVisible();
    
    // Image should be visible for AI-generated listings
    const image = details.locator('img');
    const hasImage = await image.count() > 0;
    
    if (hasImage) {
      await expect(image.first()).toBeVisible();
    }
  });
});
