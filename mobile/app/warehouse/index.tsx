import { MenuButton } from "@/components/MenuButton";
import { ScreenShell } from "@/components/ScreenShell";

export default function WarehouseHome() {
  return (
    <ScreenShell title="Warehouse" subtitle="Receiving, transfers, cold chain">
      <MenuButton href="/warehouse/receive" label="Receive batch" />
      <MenuButton href="/warehouse/transfer" label="Transfer stock" />
      <MenuButton href="/warehouse/cold-chain" label="Cold-chain breach alert" />
      <MenuButton href="/warehouse/timeline" label="Custody timeline" />
      <MenuButton href="/offline-queue" label="Offline queue" />
      <MenuButton href="/sync-health" label="Sync health" />
      <MenuButton href="/settings" label="Settings" />
    </ScreenShell>
  );
}
