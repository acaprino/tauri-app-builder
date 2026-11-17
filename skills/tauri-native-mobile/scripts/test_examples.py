"""Runtime behavior regressions for the bundled TypeScript examples."""
from pathlib import Path
import shutil
import subprocess
import unittest

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / 'examples'
NODE = shutil.which('node')


@unittest.skipUnless(NODE, 'Node.js runtime not installed')
class ExampleContractTests(unittest.TestCase):
    def run_node_ts(self, script_body):
        result = subprocess.run(
            [NODE, '--experimental-strip-types', '--input-type=module', '-e', script_body],
            cwd=str(EXAMPLES_DIR),
            capture_output=True,
            text=True,
            encoding='utf-8',
        )
        return result

    def test_capture_owner_enforces_exclusivity_and_releases_after_settle(self):
        code = """
        import assert from 'node:assert/strict';
        import { captureOnce } from './capture-owner.ts';

        let release;
        const gate = new Promise(r => { release = r; });
        const first = captureOnce(async () => { await gate; return { kind: 'ok', uri: 'file:///a.jpg' }; });
        const second = await captureOnce(async () => ({ kind: 'ok', uri: 'file:///b.jpg' }));
        assert.deepEqual(second, { kind: 'busy' });
        release();
        assert.deepEqual(await first, { kind: 'ok', uri: 'file:///a.jpg' });
        const third = await captureOnce(async () => ({ kind: 'cancelled' }));
        assert.deepEqual(third, { kind: 'cancelled' });
        """
        res = self.run_node_ts(code)
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)

    def test_audio_acquisition_distinguishes_busy_cancelled_denied_unavailable_and_ok(self):
        code = """
        import assert from 'node:assert/strict';
        import { audioAcquisition } from './audio-acquisition.ts';

        // 1. Missing mediaDevices -> unavailable
        Object.defineProperty(globalThis, 'navigator', { value: {}, configurable: true });
        const unavailableAcq = audioAcquisition();
        assert.deepEqual(await unavailableAcq.start(), { kind: 'unavailable' });

        // 2. Concurrent request -> busy, and cancel while pending -> cancelled + stops tracks
        let stopped = 0;
        let resolvePrompt;
        const fakeStream = { getTracks: () => [{ stop() { stopped++; } }] };
        Object.defineProperty(globalThis, 'navigator', {
          value: { mediaDevices: { getUserMedia: () => new Promise(r => { resolvePrompt = r; }) } },
          configurable: true,
        });
        const cancelAcq = audioAcquisition();
        const pendingStart = cancelAcq.start();
        assert.deepEqual(await cancelAcq.start(), { kind: 'busy' });
        cancelAcq.cancel();
        resolvePrompt(fakeStream);
        assert.deepEqual(await pendingStart, { kind: 'cancelled' });
        assert.equal(stopped, 1);

        // 3. Permission denied -> denied (does not collapse to undefined or throw raw error)
        Object.defineProperty(globalThis, 'navigator', {
          value: {
            mediaDevices: {
              getUserMedia: async () => {
                const err = new Error('User denied');
                err.name = 'NotAllowedError';
                throw err;
              },
            },
          },
          configurable: true,
        });
        const deniedRes = await audioAcquisition().start();
        assert.equal(deniedRes.kind, 'denied');

        // 4. Successful acquisition -> ok + active stream stopped on cancel
        let activeStopped = 0;
        const liveStream = { getTracks: () => [{ stop() { activeStopped++; } }] };
        Object.defineProperty(globalThis, 'navigator', {
          value: { mediaDevices: { getUserMedia: async () => liveStream } },
          configurable: true,
        });
        const okAcq = audioAcquisition();
        const okRes = await okAcq.start();
        assert.equal(okRes.kind, 'ok');
        assert.equal(okRes.stream, liveStream);
        assert.deepEqual(await okAcq.start(), { kind: 'busy' });
        okAcq.cancel();
        assert.equal(activeStopped, 1);
        """
        res = self.run_node_ts(code)
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)


if __name__ == '__main__':
    unittest.main()
