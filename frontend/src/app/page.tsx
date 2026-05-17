import { redirect } from "next/navigation";

/**
 * National platform entry — routes operators to the regulator command overview.
 * Citizen access remains at /citizen; authentication is enforced on /regulator.
 */
export default function RootPage() {
  redirect("/regulator");
}
