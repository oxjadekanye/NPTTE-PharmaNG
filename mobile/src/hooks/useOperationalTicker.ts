import { useEffect, useState } from "react";

export type OperationalSnapshot = {
  verificationsToday: string;
  activeRecalls: string;
  enforcementActions: string;
  systemUptime: string;
};

export const SNAPSHOTS: OperationalSnapshot[] = [
  {
    verificationsToday: "128,442",
    activeRecalls: "17",
    enforcementActions: "42",
    systemUptime: "99.94%",
  },
  {
    verificationsToday: "128,891",
    activeRecalls: "17",
    enforcementActions: "43",
    systemUptime: "99.95%",
  },
  {
    verificationsToday: "129,204",
    activeRecalls: "18",
    enforcementActions: "44",
    systemUptime: "99.96%",
  },
  {
    verificationsToday: "129,558",
    activeRecalls: "18",
    enforcementActions: "41",
    systemUptime: "99.97%",
  },
];

export function useOperationalTicker(intervalMs = 3500) {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const id = setInterval(() => {
      setIndex((i) => (i + 1) % SNAPSHOTS.length);
    }, intervalMs);
    return () => clearInterval(id);
  }, [intervalMs]);

  return SNAPSHOTS[index];
}
