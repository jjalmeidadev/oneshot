/** Formatadores compartilhados pela interface. */

const DATE_TIME = new Intl.DateTimeFormat('pt-BR', {
  day: '2-digit',
  month: '2-digit',
  year: 'numeric',
  hour: '2-digit',
  minute: '2-digit',
});

const DATE_ONLY = new Intl.DateTimeFormat('pt-BR', {
  day: '2-digit',
  month: 'short',
  year: 'numeric',
});

const TIME_ONLY = new Intl.DateTimeFormat('pt-BR', {
  hour: '2-digit',
  minute: '2-digit',
});

const NUMBER = new Intl.NumberFormat('pt-BR');

/** Aceita ISO 8601 (formato de `lastModifiedDateTime` das listas do SharePoint). */
export function formatDateTime(value: string | Date | null | undefined): string {
  const date = toDate(value);
  return date ? DATE_TIME.format(date) : '—';
}

export function formatDate(value: string | Date | null | undefined): string {
  const date = toDate(value);
  return date ? DATE_ONLY.format(date) : '—';
}

export function formatTime(value: string | Date | null | undefined): string {
  const date = toDate(value);
  return date ? TIME_ONLY.format(date) : '—';
}

/** Rotulo relativo usado nos grupos da barra lateral. */
export function relativeDayLabel(value: string | Date): string {
  const date = toDate(value);
  if (!date) {
    return 'Sem data';
  }

  // A comparacao e entre inicios de dia: usar o horario cru colocaria uma
  // conversa das 18h de ontem em "Hoje" sempre que agora fosse antes das 18h.
  const startOfToday = new Date();
  startOfToday.setHours(0, 0, 0, 0);
  const startOfDate = new Date(date);
  startOfDate.setHours(0, 0, 0, 0);
  const days = Math.round(
    (startOfToday.getTime() - startOfDate.getTime()) / 86_400_000,
  );

  if (days <= 0) return 'Hoje';
  if (days === 1) return 'Ontem';
  if (days < 7) return 'Últimos 7 dias';
  if (days < 30) return 'Últimos 30 dias';
  return 'Mais antigas';
}

export function formatNumber(value: number): string {
  return NUMBER.format(value);
}

export function formatMilliseconds(value: number | null | undefined): string {
  if (value === null || value === undefined) {
    return '—';
  }
  return value < 1000 ? `${Math.round(value)} ms` : `${(value / 1000).toFixed(2)} s`;
}

export function formatBytes(value: number): string {
  if (value < 1024) return `${value} B`;
  if (value < 1024 * 1024) return `${(value / 1024).toFixed(1)} KB`;
  return `${(value / (1024 * 1024)).toFixed(2)} MB`;
}

/** Duracao de gravacao, no formato mm:ss usado pelo botao de audio. */
export function formatDuration(seconds: number): string {
  const safe = Math.max(0, Math.floor(seconds));
  const minutes = Math.floor(safe / 60);
  const rest = safe % 60;
  return `${String(minutes).padStart(2, '0')}:${String(rest).padStart(2, '0')}`;
}

/** Percentual de confianca do classificador, que chega no intervalo 0–1. */
export function formatConfidence(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

function toDate(value: string | Date | null | undefined): Date | null {
  if (!value) return null;
  const date = value instanceof Date ? value : new Date(value);
  return Number.isNaN(date.getTime()) ? null : date;
}
