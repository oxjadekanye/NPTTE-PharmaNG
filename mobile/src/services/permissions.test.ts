import { describe, expect, it } from "vitest";
import { PERMISSION_COPY } from "@/services/permission-messages";

describe("PERMISSION_COPY", () => {
  it("includes rationale for camera and location", () => {
    expect(PERMISSION_COPY.camera.rationale).toContain("scan");
    expect(PERMISSION_COPY.location.denied).toContain("GPS");
  });
});
