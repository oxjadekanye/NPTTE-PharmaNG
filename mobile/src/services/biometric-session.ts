/** Session-scoped biometric gate — avoid re-blocking every nested route change. */
let sessionGatePassed = false;

export function isBiometricSessionGatePassed() {
  return sessionGatePassed;
}

export function markBiometricSessionGatePassed() {
  sessionGatePassed = true;
}

export function resetBiometricSessionGate() {
  sessionGatePassed = false;
}
