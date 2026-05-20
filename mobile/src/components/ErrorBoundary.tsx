import React, { Component, type ReactNode } from "react";
import { ScreenErrorFallback } from "@/components/ScreenErrorFallback";
import { CrashReporting } from "@/services/crash-reporting";

type Props = { children: ReactNode; screenLabel?: string };
type State = { error: Error | null };

export class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error) {
    return { error };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    CrashReporting.captureException(error, {
      componentStack: info.componentStack,
      screen: this.props.screenLabel,
    });
  }

  reset = () => this.setState({ error: null });

  render() {
    if (this.state.error) {
      return (
        <ScreenErrorFallback
          message={this.state.error.message}
          onRetry={this.reset}
        />
      );
    }
    return this.props.children;
  }
}
