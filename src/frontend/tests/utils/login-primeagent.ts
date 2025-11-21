import type { Page } from "playwright/test";

export const loginPrimeagent = async (page: Page) => {
  await page.goto("/");
  await page.getByPlaceholder("Username").fill("primeagent");
  await page.getByPlaceholder("Password").fill("primeagent");
  await page.getByRole("button", { name: "Sign In" }).click();
};
