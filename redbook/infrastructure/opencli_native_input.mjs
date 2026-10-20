/* Invoke OpenCLI Browser Bridge's CDP Input.insertText primitive.
 *
 * The public generic `browser type` command deliberately replaces the whole
 * contenteditable. Xiaohongshu's topic picker instead needs text appended at
 * the existing caret, so the delivery adapter invokes this narrow helper after
 * it has focused and positioned that caret with Browser Bridge.
 */
import { pathToFileURL } from 'node:url';

const [bridgeModule, session, focusScript, textBase64] = process.argv.slice(2);
if (!bridgeModule || !session || !focusScript || textBase64 === undefined) {
  throw new Error('usage: opencli_native_input.mjs <bridge-module> <session> <focus-script> <utf8-text-base64>');
}
const text = Buffer.from(textBase64, 'base64').toString('utf8');

const { BrowserBridge } = await import(pathToFileURL(bridgeModule).href);
const bridge = new BrowserBridge();
const page = await bridge.connect({ session, surface: 'browser', windowMode: 'foreground' });
await page.evaluate(focusScript);
await page.insertText(text);
console.log(JSON.stringify({ inserted: true }));
