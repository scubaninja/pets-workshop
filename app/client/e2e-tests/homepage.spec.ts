import { test, expect } from '@playwright/test';

test.describe('MatchMyMutt Homepage', () => {
  test('should load homepage and display title', async ({ page }) => {
    await page.goto('/');

    await expect(page).toHaveTitle(/MatchMyMutt - Find Your Forever Friend/);

    await expect(page.getByRole('heading', { name: 'Welcome to MatchMyMutt' })).toBeVisible();

    await expect(page.getByText('Find your perfect companion from our wonderful selection')).toBeVisible();
  });

  test('should display dog list', async ({ page }) => {
    await page.goto('/');

    await expect(page.getByRole('heading', { name: 'Available Dogs' })).toBeVisible();

    const dogList = page.getByTestId('dog-list');
    await expect(dogList).toBeVisible();

    // Should show up to 6 dogs per page
    const dogCards = page.getByTestId('dog-card');
    const count = await dogCards.count();
    expect(count).toBeGreaterThan(0);
    expect(count).toBeLessThanOrEqual(6);
  });

  test('should display dog cards with names and breeds', async ({ page }) => {
    await page.goto('/');

    // First dog card should have a name and breed
    const firstDogName = page.getByTestId('dog-name').first();
    const firstDogBreed = page.getByTestId('dog-breed').first();
    
    await expect(firstDogName).toBeVisible();
    await expect(firstDogBreed).toBeVisible();
    
    // Name should not be empty
    const nameText = await firstDogName.textContent();
    expect(nameText?.length).toBeGreaterThan(0);
  });

  test('should display pagination when multiple pages exist', async ({ page }) => {
    await page.goto('/');

    const pagination = page.getByTestId('pagination');
    // Pagination only shows if there are multiple pages
    const isVisible = await pagination.isVisible().catch(() => false);
    
    if (isVisible) {
      await expect(page.getByTestId('pagination-info')).toBeVisible();
    }
  });

  test('should navigate to dog detail page when clicking a card', async ({ page }) => {
    await page.goto('/');

    const firstDogCard = page.getByTestId('dog-card').first();
    await firstDogCard.click();

    // Should navigate to dog detail page
    await expect(page).toHaveURL(/\/dog\/\d+/);
    await expect(page.getByTestId('dog-details')).toBeVisible();
  });
});
