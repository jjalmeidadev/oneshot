import { useChatStore } from '@/state/chat-store';
import { useId } from 'react';

/** Token mantido apenas em memória, informado pelo ambiente de execução. */
export function UserCard() {
  const { accessToken, setAccessToken } = useChatStore();
  const id = useId();
  return (
    <div className="block p-2 text-xs text-fg-muted">
      <label htmlFor={id}>Token de acesso da sessão</label>
      <input
        id={id}
        aria-describedby={`${id}-hint`}
        type="password"
        autoComplete="off"
        value={accessToken}
        onChange={(event) => setAccessToken(event.target.value)}
        className="mt-1 w-full rounded border border-border bg-surface p-2"
        placeholder="Token fornecido pelo ambiente"
      />
      <span id={`${id}-hint`} className="mt-1 block text-2xs">
        Válido apenas nesta sessão.
      </span>
    </div>
  );
}
