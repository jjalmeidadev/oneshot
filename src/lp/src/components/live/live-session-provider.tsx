import type { ReactNode } from "react";
import { LiveSessionContext } from "@/lib/liveSessionContext";
import { useLiveSession } from "@/lib/useLiveSession";

/**
 * Entra na sala uma única vez e distribui o id para a página.
 *
 * Fica no topo da árvore justamente para que a entrada aconteça uma vez só,
 * independentemente de quantos componentes precisem do id.
 */
export default function LiveSessionProvider({ children }: { children: ReactNode }) {
    const { sessionId } = useLiveSession();

    return (
        <LiveSessionContext.Provider value={sessionId}>
            {children}
        </LiveSessionContext.Provider>
    );
}
