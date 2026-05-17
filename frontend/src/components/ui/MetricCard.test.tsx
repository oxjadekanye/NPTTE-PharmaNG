import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { MetricCard } from "./MetricCard";

describe("MetricCard", () => {
  it("renders label and value", () => {
    render(<MetricCard label="Open alerts" value={42} />);
    expect(screen.getByText("Open alerts")).toBeInTheDocument();
    expect(screen.getByText("42")).toBeInTheDocument();
  });
});
