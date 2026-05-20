/**
 * Phase 24E — security hardening placeholders (native modules wired later).
 */

let screenshotProtectionEnabled = false;

export const MobileSecurity = {
  enableScreenshotProtection() {
    screenshotProtectionEnabled = true;
    // FLAG_SECURE on Android / UITextField secure — native bridge TBD
  },

  disableScreenshotProtection() {
    screenshotProtectionEnabled = false;
  },

  isScreenshotProtectionEnabled() {
    return screenshotProtectionEnabled;
  },

  /** Placeholder — integrate jail-monkey / SafetyNet attestation. */
  async detectCompromisedDevice(): Promise<{ rooted: boolean; jailbroken: boolean; note: string }> {
    return {
      rooted: false,
      jailbroken: false,
      note: "Root/jailbreak detection abstraction — not wired to native attestation",
    };
  },

  /** Mask sensitive UI regions during backgrounding (hook for regulators). */
  shouldMaskSensitiveScreen(routeName: string) {
    return /login|evidence|case|inspect/i.test(routeName);
  },
};
