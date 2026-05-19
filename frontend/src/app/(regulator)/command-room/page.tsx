"use client";

import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { CommandRoomWallboard } from "@/components/command-room/CommandRoomWallboard";

export default function CommandRoomPage() {
  return (
    <RegulatorGuard>
      <CommandRoomWallboard />
    </RegulatorGuard>
  );
}
