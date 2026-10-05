import { useId } from 'react';

/**
 * Campo do token de acesso da sessao. Fica dentro da engrenagem de ajustes
 * (S5-20): e um dado tecnico e nao precisa ocupar a barra lateral.
 * O valor vive apenas em memoria, informado pelo ambiente de execucao.
 */
export function UserCard({
  accessToken,
  onAccessTokenChange,
}: {
  accessToken: string;
  onAccessTokenChange: (token: string) => void;
}) {
  const id = useId();
  return (
    <div className="text-xs text-fg-muted">
      <label htmlFor={id} className="font-medium text-fg">
        Token de acesso da sessão
      </label>
      <input
        id={id}
        aria-describedby={`${id}-hint`}
        type="password"
        autoComplete="off"
        value={accessToken}
        onChange={(event) => onAccessTokenChange(event.target.value)}
        className="mt-1.5 h-8 w-full rounded-lg border border-border bg-surface px-2.5 text-fg outline-none focus:border-primary focus:ring-2 focus:ring-primary/15"
        placeholder="Token fornecido pelo ambiente"
      />
      <span id={`${id}-hint`} className="mt-1 block text-2xs text-fg-subtle">
        Válido apenas nesta sessão.
      </span>
    </div>
  );
}
