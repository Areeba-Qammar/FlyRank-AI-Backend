const store = new Map<string, unknown>();

export function setResult(eventId: string, result: unknown) {
  store.set(eventId, result);
}

export function getResult(eventId: string) {
  return store.get(eventId);
}