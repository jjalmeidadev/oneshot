import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { expect, it, vi } from 'vitest';

import { ProfileSummary } from './user-card';

const profile = {
  display_name: '[DEMO] Gerente de Projeto',
  email: 'mvp.gerente-projeto@oneshot.example.com',
  role_name: 'equipe_projeto',
  profile_key: 'gerente_projeto' as const,
  scope_label: 'Projeto PRJ-0442',
  can_read: true,
  can_write: true,
  can_export: true,
};

it('ProfileSummary mostra perfil, escopo e permissões sem expor o token', async () => {
  const logout = vi.fn();
  render(<ProfileSummary profile={profile} onLogout={logout} />);

  expect(screen.getByText('[DEMO] Gerente de Projeto')).toBeVisible();
  expect(screen.getByText('Gerente de projeto · Projeto PRJ-0442')).toBeVisible();
  expect(screen.getByText('Pode consultar, alterar e exportar')).toBeVisible();
  await userEvent.click(screen.getByRole('button', { name: 'Sair' }));
  expect(logout).toHaveBeenCalledOnce();
});

it('ProfileSummary descreve perfil só de consulta', () => {
  render(
    <ProfileSummary
      profile={{ ...profile, can_write: false, can_export: false }}
      onLogout={vi.fn()}
    />,
  );
  expect(screen.getByText('Pode consultar')).toBeVisible();
});
