// Acquisition only; recorder final-chunk handling is a separate responsibility.
export type AudioResult =
  | { kind: 'ok'; stream: MediaStream }
  | { kind: 'busy' | 'cancelled' | 'unavailable' | 'denied' }
  | { kind: 'error'; cause: unknown };

export function audioAcquisition() {
  let generation = 0;
  let pending = false;
  let active: MediaStream | undefined;
  const stop = (s: MediaStream) => s.getTracks().forEach(t => t.stop());
  return {
    async start(): Promise<AudioResult> {
      if (pending || active) return { kind: 'busy' };
      const devices = typeof navigator !== 'undefined' ? navigator.mediaDevices : undefined;
      if (!devices || typeof devices.getUserMedia !== 'function') {
        return { kind: 'unavailable' };
      }
      pending = true;
      const request = generation;
      try {
        const stream = await devices.getUserMedia({ audio: true });
        if (request !== generation) {
          stop(stream);
          return { kind: 'cancelled' };
        }
        active = stream;
        return { kind: 'ok', stream };
      } catch (cause) {
        if (request !== generation) return { kind: 'cancelled' };
        const name = cause instanceof Error ? cause.name : '';
        if (name === 'NotAllowedError' || name === 'PermissionDeniedError' || name === 'SecurityError') {
          return { kind: 'denied' };
        }
        if (name === 'NotFoundError' || name === 'DevicesNotFoundError' || name === 'NotSupportedError') {
          return { kind: 'unavailable' };
        }
        return { kind: 'error', cause };
      } finally {
        pending = false;
      }
    },
    cancel() {
      generation++;
      if (active) stop(active);
      active = undefined;
      // Keep pending true until the outstanding permission request settles.
    },
  };
}
