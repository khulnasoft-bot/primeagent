import { BASENAME } from "@/customization/config-constants";

const SETUP_GUIDES = new Map([
  [
    "google",
    "https://prime.khulnasoft.com/docs/connection-oauth#customer-owned-google-registration",
  ],
  ["microsoft", "https://prime.khulnasoft.com/docs/entra-app-registration"],
  [
    "slack",
    "https://prime.khulnasoft.com/docs/connection-oauth#customer-owned-slack-registration",
  ],
]);

export function connectionSetupGuide(provider: string, usesToken = false) {
  if (provider === "slack" && usesToken) {
    return "https://prime.khulnasoft.com/docs/bundles-slack#two-executing-identities";
  }
  return SETUP_GUIDES.get(provider);
}

export function suggestedCallbackUrl(provider: string, origin: string) {
  if (!SETUP_GUIDES.has(provider)) return undefined;
  try {
    const url = new URL(origin);
    const loopback = ["localhost", "127.0.0.1", "[::1]"].includes(url.hostname);
    // Match the broker's HTTPS / loopback HTTP rule. Desktop shells may have
    // a non-HTTP origin, which cannot be registered as an OAuth callback.
    if (url.protocol !== "https:" && !(url.protocol === "http:" && loopback)) {
      return undefined;
    }
    return `${url.origin}${BASENAME}/api/v1/connections/oauth/${provider}/callback`;
  } catch {
    return undefined;
  }
}
