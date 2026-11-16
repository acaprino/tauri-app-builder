// Acquisition only; recorder final-chunk handling is a separate responsibility.
export function audioAcquisition() {
  let generation = 0;
  let pending = false;
  let active: MediaStream | undefined;
  const stop = (s: MediaStream) => s.getTracks().forEach(t => t.stop());
  return {
    async start(): Promise<MediaStream | undefined> {
      if (pending || active) return undefined;
      pending = true;
      const request = generation;
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        if (request !== generation) { stop(stream); return undefined; }
        active = stream;
        return stream;
      } finally { pending = false; }
    },
    cancel() {
      generation++;
      if (active) stop(active);
      active = undefined;
      // Keep pending true until the outstanding permission request settles.
    },
  };
}
