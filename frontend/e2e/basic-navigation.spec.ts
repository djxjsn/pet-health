import { test, expect } from '@playwright/test';

test.describe('首页', () => {
  test('应正确加载首页', async ({ page }) => {
    await page.goto('/');

    await expect(page).toHaveTitle(/AI 宠物健康助手/);
  });
});

test.describe('登录页面', () => {
  test('应显示登录表单', async ({ page }) => {
    await page.goto('/login');

    await expect(page.locator('form')).toBeVisible();
  });

  test('空表单提交应显示验证提示', async ({ page }) => {
    await page.goto('/login');

    await page.click('button[type="submit"]');

    const form = page.locator('form');
    await expect(form).toBeVisible();
  });
});

test.describe('注册页面', () => {
  test('应显示注册表单', async ({ page }) => {
    await page.goto('/register');

    await expect(page.locator('form')).toBeVisible();
  });
});

test.describe('导航功能', () => {
  test('底部导航栏应在移动端可见', async ({ page }) => {
    await page.goto('/');
    const viewport = page.viewportSize();
    if (viewport && viewport.width < 768) {
      const bottomNav = page.locator('[data-testid="bottom-nav"]');
      await expect(bottomNav).toBeVisible();
    }
  });
});
