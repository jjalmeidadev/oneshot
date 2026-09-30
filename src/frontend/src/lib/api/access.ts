import { API_BASE_URL, parseError } from './client';

export type ProfileKey = 'pmo' | 'lider_subportfolio' | 'gerente_projeto' | 'consulta';

export type AccessProfile = {
  display_name: string;
  email: string;
  role_name: string;
  profile_key: ProfileKey;
  scope_label: string;
  can_read: boolean;
  can_write: boolean;
  can_export: boolean;
};

export async function getCurrentAccessProfile(
  accessToken: string,
  signal?: AbortSignal,
): Promise<AccessProfile> {
  const response = await fetch(`${API_BASE_URL}/access/me`, {
    method: 'GET',
    headers: { Authorization: `Bearer ${accessToken}` },
    signal,
  });
  if (!response.ok) throw await parseError(response);
  return (await response.json()) as AccessProfile;
}
