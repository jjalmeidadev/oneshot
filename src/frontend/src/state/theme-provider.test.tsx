import { act, render, renderHook, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { ThemeProvider, useThemeContext } from './theme-provider';
import { ThemeToggle } from '@/components/layout/theme-toggle';
import { TooltipProvider } from '@/components/ui/tooltip';

describe('ThemeProvider e ThemeToggle', () => {
  beforeEach(() => {
    localStorage.clear();
    document.documentElement.classList.remove('dark');
  });

  it('aplica tema salvo na raiz sem depender da montagem da barra lateral', () => {
    localStorage.setItem('metro-agent-theme', 'dark');
    render(
      <ThemeProvider>
        <p>Chat móvel</p>
      </ThemeProvider>,
    );
    expect(document.documentElement).toHaveClass('dark');
    expect(screen.getByText('Chat móvel')).toBeVisible();
  });

  it('alterna pelo teclado, atualiza nome acessível e persiste escolha', async () => {
    render(
      <ThemeProvider>
        <TooltipProvider>
          <ThemeToggle />
        </TooltipProvider>
      </ThemeProvider>,
    );
    await userEvent.tab();
    await userEvent.keyboard('{Enter}');
    expect(document.documentElement).toHaveClass('dark');
    expect(localStorage.getItem('metro-agent-theme')).toBe('dark');
    expect(screen.getByRole('button', { name: 'Usar tema claro' })).toHaveFocus();
    await userEvent.keyboard('{Enter}');
    expect(document.documentElement).not.toHaveClass('dark');
    expect(localStorage.getItem('metro-agent-theme')).toBe('light');
  });

  it('segue mudanças do sistema até existir preferência explícita e remove listener', () => {
    const add = vi.fn();
    const remove = vi.fn();
    vi.spyOn(window, 'matchMedia').mockReturnValue({
      matches: true,
      addEventListener: add,
      removeEventListener: remove,
    } as unknown as MediaQueryList);
    const { result, unmount } = renderHook(useThemeContext, { wrapper: ThemeProvider });
    expect(result.current.theme).toBe('dark');
    const change = add.mock.calls[0][1] as (event: { matches: boolean }) => void;
    act(() => change({ matches: false }));
    expect(result.current.theme).toBe('light');
    act(() => result.current.setTheme('dark'));
    act(() => change({ matches: false }));
    expect(result.current.theme).toBe('dark');
    unmount();
    expect(remove).toHaveBeenCalledWith('change', change);
  });

  it('mantém alternância em memória quando armazenamento está indisponível', () => {
    vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
      throw new Error('Storage bloqueado');
    });
    vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
      throw new Error('Storage bloqueado');
    });
    const { result } = renderHook(useThemeContext, { wrapper: ThemeProvider });
    act(() => result.current.setTheme('dark'));
    expect(result.current.theme).toBe('dark');
    expect(document.documentElement).toHaveClass('dark');
  });

  it('informa uso do contexto fora do provider', () => {
    expect(() => renderHook(useThemeContext)).toThrow(
      'useThemeContext precisa estar dentro de <ThemeProvider>.',
    );
  });
});
