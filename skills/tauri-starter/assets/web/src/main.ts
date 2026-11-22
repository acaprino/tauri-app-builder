import { invoke } from '@tauri-apps/api/core';

const byId = (id: string) => document.getElementById(id) as HTMLElement;
const show = (label: string, value: unknown) => {
  byId('out').textContent = `${label}: ${typeof value === 'string' ? value : JSON.stringify(value)}`;
};

invoke<string>('platform_name').then(
  (name) => { byId('platform').textContent = `Running on ${name}`; },
  (error) => show('platform_name failed', String(error)),
);

// Granted by the capability files: the opener plugin.
byId('open').addEventListener('click', () => {
  invoke('plugin:opener|open_url', { url: 'https://tauri.app' }).then(
    () => show('opener', 'allowed'),
    (error) => show('opener denied', String(error)),
  );
});

// Not granted anywhere: the call must be refused by the ACL, which shows the capability files work.
byId('denied').addEventListener('click', () => {
  invoke('plugin:window-state|save_window_state', { flags: 63 }).then(
    () => show('window-state', 'allowed'),
    (error) => show('window-state denied', String(error)),
  );
});
