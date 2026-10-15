// Official Actual SDK. Only read operations are exposed; credentials arrive via stdin.
import * as api from '@actual-app/api';
let input = '';
for await (const chunk of process.stdin) {
  input += chunk;
  if (input.length > 100000) process.exit(2);
}
const config = JSON.parse(input);
const originalConsole = {};
for (const method of ['log', 'info', 'debug', 'warn', 'error']) {
  originalConsole[method] = console[method];
  console[method] = () => {}; // SDK output must not corrupt JSON or expose credentials.
}
try {
  await api.init({ dataDir: config.dataDir, serverURL: config.url, password: config.password });
  await api.downloadBudget(config.budget_id, { password: config.encryption_password });
  const accounts = await api.getAccounts();
  if (!accounts.some(a => a.id === config.account)) throw new Error('unknown_account');
  const transactions = await api.getTransactions(config.account, config.start, config.end);
  const result = JSON.stringify({ status: 'ok', source: 'actual', account: config.account,
    start: config.start, end: config.end, amount_unit: 'integer_minor_units', transactions });
  if (Buffer.byteLength(result) > 1900000) throw new Error('result_too_large');
  await api.shutdown();
  process.stdout.write(result);
} catch {
  try { await api.shutdown(); } catch { /* No credential-bearing SDK errors emitted. */ }
  process.exitCode = 1;
} finally {
  Object.assign(console, originalConsole);
}
