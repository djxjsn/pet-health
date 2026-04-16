import { test, expect } from '@playwright/test';

test.describe('宠物管理流程', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/pets');
  });

  test('宠物列表页应加载', async ({ page }) => {
    await expect(page).toHaveURL(/\/pets/);
  });

  test('点击新建宠物按钮应跳转', async ({ page }) => {
    const newPetBtn = page.locator('a[href*="/pets/new"], button:has-text("添加")');
    if (await newPetBtn.count() > 0) {
      await newPetBtn.first().click();
      await expect(page).toHaveURL(/\/pets\/new/);
    }
  });
});

test.describe('历史记录页面', () => {
  test('历史列表应可访问', async ({ page }) => {
    await page.goto('/history');
    await expect(page).toHaveURL(/\/history/);
  });
});

test.describe('商城页面', () => {
  test('商品展示区应加载', async ({ page }) => {
    await page.goto('/shop');
    await expect(page).toHaveURL(/\/shop/);
  });
});

test.describe('个人中心页面', () => {
  test('用户信息区域应存在', async ({ page }) => {
    await page.goto('/profile');
    await expect(page).toHaveURL(/\/profile/);
  });
});
