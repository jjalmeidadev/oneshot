import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

/**
 * Corpo da resposta do agente.
 *
 * O backend devolve texto livre em `GeminiChatResponse.text`, e o prompt de
 * `build_rag_input` pede que as fontes sejam citadas como `[Fonte N]`. O
 * markdown e renderizado; as citacoes ficam a cargo de `source-citations.tsx`,
 * logo abaixo da mensagem.
 */
export function MarkdownMessage({ content }: { content: string }) {
  return (
    <div className="space-y-3 text-sm leading-6 text-fg">
      <Markdown
        remarkPlugins={[remarkGfm]}
        components={{
          p: ({ children }) => <p className="leading-6">{children}</p>,
          strong: ({ children }) => (
            <strong className="font-semibold text-fg">{children}</strong>
          ),
          em: ({ children }) => <em className="text-fg-muted">{children}</em>,
          ul: ({ children }) => (
            <ul className="list-disc space-y-1 pl-5 marker:text-fg-subtle">
              {children}
            </ul>
          ),
          ol: ({ children }) => (
            <ol className="list-decimal space-y-1 pl-5 marker:text-fg-subtle">
              {children}
            </ol>
          ),
          li: ({ children }) => <li className="leading-6">{children}</li>,
          a: ({ children, href }) => (
            <a
              href={href}
              target="_blank"
              rel="noreferrer"
              className="text-primary underline underline-offset-2 hover:text-primary-hover"
            >
              {children}
            </a>
          ),
          code: ({ children }) => (
            <code className="rounded bg-muted px-1 py-0.5 font-mono text-xs text-fg">
              {children}
            </code>
          ),
          pre: ({ children }) => (
            <pre className="overflow-x-auto rounded-lg border border-border bg-muted p-3 font-mono text-xs">
              {children}
            </pre>
          ),
          blockquote: ({ children }) => (
            <blockquote className="border-l-2 border-border-strong pl-3 text-fg-muted">
              {children}
            </blockquote>
          ),
          table: ({ children }) => (
            <div className="overflow-x-auto">
              <table className="w-full border-collapse text-xs">{children}</table>
            </div>
          ),
          th: ({ children }) => (
            <th className="border border-border bg-muted px-2 py-1 text-left font-semibold">
              {children}
            </th>
          ),
          td: ({ children }) => (
            <td className="border border-border px-2 py-1 align-top">{children}</td>
          ),
        }}
      >
        {content}
      </Markdown>
    </div>
  );
}
