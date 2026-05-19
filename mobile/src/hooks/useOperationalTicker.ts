import { useEffect, useState } from "react";

export type OperationalSnapshot = {
  verificationsToday: string;
  activeRecalls: string;
  counterfeitAlerts: string;
  enforcementReadiness: string;
};

export const SNAPSHOTS: OperationalSnapshot[] = [
  {
    verificationsToday: "128,442",
    activeRecalls: "17",
    counterfeitAlerts: "42",
    enforcementReadiness: "94%",
  },
  {
    verificationsToday: "128,891",
    activeRecalls: "17",
    counterfeitAlerts: "43",
    enforcementReadiness: "94%",
  },
  {
    verificationsToday: "129,204",
    activeRecalls: "18",
    counterfeitAlerts: "44",
    enforcementReadiness: "95%",
  },
  {
    verificationsToday: "129,558",
    activeRecalls: "18",
    counterfeitAlerts: "41",
    enforcementReadiness: "95%",
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
