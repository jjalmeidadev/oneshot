import { createContext, useContext, type ReactNode } from 'react';

import { useTheme, type Theme } from '@/hooks/use-theme';

/**
 * Tema da aplicacao.
 *
 * O provedor fica na raiz de proposito. Antes o hook era chamado dentro do
 * botao de alternancia, que vive na barra lateral — e em telas estreitas a
 * barra so monta quando o menu abre, entao a classe `dark` nunca chegava ao
 * documento e a interface abria sempre clara no celular.
 */
type ThemeContextValue = {
  theme: Theme;
  toggleTheme: () => void;
  setTheme: (theme: Theme) => void;
};

const ThemeContext = createContext<ThemeContextValue | null>(null);

export function ThemeProvider({ children }: { children: ReactNode }) {
  const value = useTheme();
  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useThemeContext(): ThemeContextValue {
  const value = useContext(ThemeContext);
  if (!value) {
    throw new Error('useThemeContext precisa estar dentro de <ThemeProvider>.');
  }
  return value;
}
