/* Set selected local files on an existing Browser Bridge file input.
 *
 * The generic `opencli browser upload` command expects Chrome to raise a
 * file-chooser event. Xiaohongshu keeps its image input hidden behind a
 * custom button, so that event is not emitted on every Creator build. The
 * Browser Bridge itself exposes a CDP route, but some installed extension
 * builds block DOM.setFileInputFiles. This helper uses OpenCLI's documented
 * legacy DataTransfer fallback inside the already-open Creator editor. It
 * keeps that operation in the draft-only delivery adapter rather than
 * introducing a second publisher.
 */
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const [bridgeModule, session, selector, filesBase64] = process.argv.slice(2);
if (!bridgeModule || !session || !selector || !filesBase64) {
  throw new Error('usage: opencli_native_file_input.mjs <bridge-module> <session> <selector> <files-json-base64>');
}

const files = JSON.parse(Buffer.from(filesBase64, 'base64').toString('utf8'));
if (!Array.isArray(files) || files.length === 0 || !files.every(file => typeof file === 'string' && file)) {
  throw new Error('files must be a non-empty JSON string array');
}

const { BrowserBridge } = await import(pathToFileURL(bridgeModule).href);
const bridge = new BrowserBridge();
const page = await bridge.connect({ session, surface: 'browser', windowMode: 'foreground' });
const images = files.map(file => ({
  name: path.basename(file),
  mimeType: ({
    '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png',
    '.webp': 'image/webp', '.pdf': 'application/pdf',
  })[path.extname(file).toLowerCase()] || 'application/octet-stream',
  base64: fs.readFileSync(file).toString('base64'),
}));
const result = await page.evaluate(`
  (() => {
    const images = ${JSON.stringify(images)};
    const input = document.querySelector(${JSON.stringify(selector)});
    if (!input) return { ok: false, error: 'image file input not found' };
    const dt = new DataTransfer();
    for (const image of images) {
      const binary = atob(image.base64);
      const bytes = new Uint8Array(binary.length);
      for (let index = 0; index < binary.length; index += 1) bytes[index] = binary.charCodeAt(index);
      dt.items.add(new File([bytes], image.name, { type: image.mimeType }));
    }
    Object.defineProperty(input, 'files', { value: dt.files, configurable: true });
    input.dispatchEvent(new Event('input', { bubbles: true }));
    input.dispatchEvent(new Event('change', { bubbles: true }));
    return { ok: true, count: dt.files.length };
  })()
`);
if (!result?.ok || result.count !== files.length) {
  throw new Error(result?.error || `Creator accepted ${result?.count ?? 0} of ${files.length} images`);
}
console.log(JSON.stringify({ uploaded: files.length }));
