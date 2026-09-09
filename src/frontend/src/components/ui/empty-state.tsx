import type { LucideIcon } from 'lucide-react';
import type { ReactNode } from 'react';

import { cn } from '@/lib/utils';

export function EmptyState({
  icon: Icon,
  title,
  description,
  action,
  className,
  compact = false,
}: {
  icon: LucideIcon;
  title: string;
  description?: ReactNode;
  action?: ReactNode;
  className?: string;
  compact?: boolean;
}) {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center text-center',
        compact ? 'gap-2 px-4 py-8' : 'gap-3 px-6 py-12',
        className,
      )}
    >
      <span
        className={cn(
          'flex items-center justify-center rounded-full bg-muted text-fg-subtle',
          compact ? 'h-9 w-9' : 'h-12 w-12',
        )}
      >
        <Icon size={compact ? 16 : 20} />
      </span>
      <p className={cn('font-medium text-fg', compact ? 'text-xs' : 'text-sm')}>
        {title}
      </p>
      {description && (
        <p className="max-w-sm text-xs leading-5 text-fg-muted">{description}</p>
      )}
      {action}
    </div>
  );
}
