# Move from Tampermonkey to the extension

**The MissionChief Map Command Toolkit userscript is no longer supported.** The supported edition is the **[Chrome Web Store extension](https://chromewebstore.google.com/detail/lmnojpchebgcochdfnfjmnficicnaaoc)**.

## Switch safely

1. Finish or pause any active Toolkit task. Export any settings you need using the old Toolkit's existing export controls.
2. Install the extension from the Store. This is a separate browser installation, not a Tampermonkey update.
3. In Tampermonkey's dashboard, switch off **MissionChief Map Command Toolkit**. Keep Tampermonkey if you use it for other scripts.
4. Open the extension popup, enable Toolkit and apply/reload. Fully reload all open MissionChief UK tabs.
5. Check your settings before starting an operation. Retain your old export until you are happy with the extension.

Ordinary settings may be copied where supported. Complete migration is not guaranteed, particularly across browsers or between unpacked and Store copies. Discord destinations may need to be entered again. Do not clear MissionChief site storage while you have saved plans you need to recover.

## Why the old script still runs

An already installed script can continue to execute after support ends. Updating the README cannot change that copy. The final migration update adds a visible notice and a direct Store link while retaining the old controls long enough to export settings. It does not delete data or install an extension automatically.

Tampermonkey must receive that update through the metadata and download URLs already recorded in the installed script. Users with automatic updates disabled must check for updates manually. The [delivery notes](../legacy/README.md) distinguish a prepared package from a verified live deployment.

## Browser support

The Store edition targets MissionChief UK in compatible browsers. Do not assume support for other national game editions from the legacy script's wider URL matches. Ordinary iOS Safari cannot install a Chrome extension; Orion ZIP testing is a separate route with browser-specific limitations.

[Get the extension](https://chromewebstore.google.com/detail/lmnojpchebgcochdfnfjmnficicnaaoc) · [Setup and troubleshooting](EXTENSION_GUIDE.md)
