import { requestJson } from './client';
import type {
  AlertNotification,
  AlertSubscriptionResponse,
  NotificationListResponse,
} from './schemas';

export function getNotifications(token: string): Promise<NotificationListResponse> {
  return requestJson('/notifications', {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export function markNotificationRead(
  id: string,
  token: string,
): Promise<AlertNotification> {
  return requestJson(`/notifications/${id}/read`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
  });
}

export function getAlertSubscriptions(
  token: string,
): Promise<AlertSubscriptionResponse[]> {
  return requestJson('/alert-subscriptions', {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export function changeAlertSubscription(input: {
  id: string;
  action: 'pause' | 'resume' | 'cancel';
  revision: number;
  token: string;
}): Promise<AlertSubscriptionResponse> {
  return requestJson(`/alert-subscriptions/${input.id}/${input.action}`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${input.token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      revision: input.revision,
      client_action_id: crypto.randomUUID(),
    }),
  });
}
