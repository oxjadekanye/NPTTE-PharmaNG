import { MenuButton } from "@/components/MenuButton";
import { ScreenShell } from "@/components/ScreenShell";

export default function CustomsHome() {
  return (
    <ScreenShell title="Customs" subtitle="Import verification and holds">
      <MenuButton href="/customs/verify" label="Verify shipment scan" />
      <MenuButton href="/customs/batch" label="Scan import batch" />
      <MenuButton href="/customs/hold" label="Hold suspicious consignment" />
      <MenuButton href="/customs/escalate" label="Escalate to regulator" />
      <MenuButton href="/offline-queue" label="Offline queue" />
      <MenuButton href="/sync-health" label="Sync health" />
      <MenuButton href="/field-activity" label="Field activity" />
      <MenuButton href="/settings" label="Settings" />
    </ScreenShell>
  );
}
