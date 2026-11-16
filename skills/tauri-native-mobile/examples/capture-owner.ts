// Adapter contract: settles only once the native activity has settled.
// A UI timeout must NOT settle this promise or release native ownership.
export type Capture = { kind: 'ok'; uri: string } |
  { kind: 'cancelled' | 'unavailable' | 'error' };
let owner: symbol | undefined;
export async function captureOnce(
  nativeCapture: () => Promise<Capture>,
): Promise<Capture | { kind: 'busy' }> {
  if (owner) return { kind: 'busy' };
  const request = Symbol();
  owner = request;
  try { return await nativeCapture(); }
  finally { if (owner === request) owner = undefined; }
}
// Native code must enforce exclusivity and match callback request IDs too.
