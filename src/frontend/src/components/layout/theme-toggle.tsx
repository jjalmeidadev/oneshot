import { Moon, Sun } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { useThemeContext } from '@/state/theme-provider';

export function ThemeToggle() {
  const { theme, toggleTheme } = useThemeContext();
  const label = theme === 'dark' ? 'Usar tema claro' : 'Usar tema escuro';

  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <Button variant="ghost" size="icon-sm" onClick={toggleTheme} aria-label={label}>
          {theme === 'dark' ? <Sun size={15} /> : <Moon size={15} />}
        </Button>
      </TooltipTrigger>
      <TooltipContent side="top">{label}</TooltipContent>
    </Tooltip>
  );
}
