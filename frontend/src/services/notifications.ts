import { apiRequest } from "./api-client";

export async function fetchNotificationCenter() {
  return apiRequest<{ notifications: unknown[]; unread: number }>("/notifications/center/");
}

export async function markNotificationRead(id: string) {
  return apiRequest("/notifications/center/", {
    method: "POST",
    body: JSON.stringify({ id }),
  });
}

export async function fetchNotificationUnread() {
  return apiRequest<{ unread: number }>("/notifications/unread/");
}
