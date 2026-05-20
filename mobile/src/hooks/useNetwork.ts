import NetInfo from "@react-native-community/netinfo";
import { useEffect, useState } from "react";
import { setApiNetworkOnline } from "@/services/api-client";

export function useNetwork() {
  const [online, setOnline] = useState(true);

  useEffect(() => {
    const unsub = NetInfo.addEventListener((state) => {
      const next = Boolean(state.isConnected && state.isInternetReachable !== false);
      setOnline(next);
      setApiNetworkOnline(next);
    });
    return () => unsub();
  }, []);

  return { online };
}
