type UnauthorizedListener = () => void;

const listeners = new Set<UnauthorizedListener>();

export function subscribeToUnauthorized(listener: UnauthorizedListener) {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
}

export function notifyUnauthorized() {
  listeners.forEach((listener) => listener());
}
