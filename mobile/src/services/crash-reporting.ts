/**
 * Phase 24 — crash reporting abstraction (Sentry-ready, not wired externally).
 */
export type CrashLevel = "info" | "warning" | "error" | "fatal";

export type CrashReport = {
  level: CrashLevel;
  message: string;
  stack?: string;
  context?: Record<string, unknown>;
  at: string;
};

const buffer: CrashReport[] = [];
let sentryEnabled = false;

export const CrashReporting = {
  /** Placeholder — enable when SENTRY_DSN configured in EAS secrets. */
  configureSentry(_dsn: string | null) {
    sentryEnabled = Boolean(_dsn);
  },

  capture(level: CrashLevel, message: string, context?: Record<string, unknown>) {
    const entry: CrashReport = {
      level,
      message,
      context,
      at: new Date().toISOString(),
    };
    buffer.unshift(entry);
    if (buffer.length > 50) buffer.pop();
    if (__DEV__) {
      // eslint-disable-next-line no-console
      console[level === "fatal" || level === "error" ? "error" : "warn"](
        `[nptte-crash] ${message}`,
        context ?? ""
      );
    }
    if (sentryEnabled) {
      // Sentry.captureException / captureMessage — wire when DSN available
    }
  },

  captureException(error: unknown, context?: Record<string, unknown>) {
    const err = error instanceof Error ? error : new Error(String(error));
    this.capture("error", err.message, {
      ...context,
      stack: err.stack,
    });
  },

  getRecent(limit = 20) {
    return buffer.slice(0, limit);
  },

  isSentryReady() {
    return sentryEnabled;
  },
};
