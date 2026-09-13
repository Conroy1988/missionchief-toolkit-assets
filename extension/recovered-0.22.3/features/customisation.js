(() => {const seed=window.__MCMS_EXTENSION_SEED__||window.__MCMS_EXTENSION_PILOT__?.documentIdentity;if(!seed||(seed.documentToken&&(location.origin!==seed.origin||document.documentElement.getAttribute('data-mcms-extension-document')!==seed.documentToken)))return;
(()=>{'use strict';window.__MCMS_EXTENSION_FEATURES__ ||= Object.create(null);window.__MCMS_EXTENSION_FEATURES__["customisation"] ||= {"settingsTransferKey":__mcmsModuleContext=>(async function settingsTransferKey(passphrase, salt, iterations = __mcmsModuleContext.SETTINGS_TRANSFER.iterations) {
        const cryptoApi = (0,__mcmsModuleContext.settingsTransferCrypto)();
        const keyMaterial = await cryptoApi.subtle.importKey(
            'raw', new __mcmsModuleContext.TextEncoder().encode((0,__mcmsModuleContext.String)(passphrase || '')), { name: 'PBKDF2' }, false, ['deriveKey']
        );
        return cryptoApi.subtle.deriveKey(
            { name: 'PBKDF2', salt, iterations, hash: 'SHA-256' },
            keyMaterial,
            { name: 'AES-GCM', length: 256 },
            false,
            ['encrypt', 'decrypt']
        );
    }),
"encryptToolkitSettings":__mcmsModuleContext=>(async function encryptToolkitSettings(passphrase, exportedAt = new __mcmsModuleContext.Date()) {
        if ((0,__mcmsModuleContext.String)(passphrase || '').length < 12) throw new __mcmsModuleContext.Error('Use a passphrase of at least 12 characters.');
        const cryptoApi = (0,__mcmsModuleContext.settingsTransferCrypto)();
        const salt = cryptoApi.getRandomValues(new __mcmsModuleContext.Uint8Array(__mcmsModuleContext.SETTINGS_TRANSFER.saltBytes));
        const iv = cryptoApi.getRandomValues(new __mcmsModuleContext.Uint8Array(__mcmsModuleContext.SETTINGS_TRANSFER.ivBytes));
        const key = await (0,__mcmsModuleContext.settingsTransferKey)(passphrase, salt);
        const plaintext = new __mcmsModuleContext.TextEncoder().encode(__mcmsModuleContext.JSON.stringify((0,__mcmsModuleContext.buildToolkitSettingsBackup)(exportedAt, { includeSecrets: true })));
        const ciphertext = await cryptoApi.subtle.encrypt(
            { name: 'AES-GCM', iv, additionalData: (0,__mcmsModuleContext.settingsTransferAdditionalData)(), tagLength: 128 },
            key,
            plaintext
        );
        return {
        format: __mcmsModuleContext.SETTINGS_TRANSFER.format,
        schema: __mcmsModuleContext.SETTINGS_TRANSFER.schema,
        version: __mcmsModuleContext.SCRIPT.version,
        createdAt: exportedAt.toISOString(),
        crypto: {
            cipher: 'AES-GCM',
            kdf: 'PBKDF2-SHA-256',
            hash: 'SHA-256',
            iterations: __mcmsModuleContext.SETTINGS_TRANSFER.iterations,
            salt: (0,__mcmsModuleContext.settingsTransferBytesToBase64)(salt),
            iv: (0,__mcmsModuleContext.settingsTransferBytesToBase64)(iv)
        },
        ciphertext: (0,__mcmsModuleContext.settingsTransferBytesToBase64)(ciphertext)
        };
    }),
"decryptToolkitSettings":__mcmsModuleContext=>(async function decryptToolkitSettings(envelope, passphrase) {
        const validated = (0,__mcmsModuleContext.validateSettingsTransferEnvelope)(envelope);
        try {
        const key = await (0,__mcmsModuleContext.settingsTransferKey)(passphrase, validated.salt, validated.iterations);
        const plaintext = await (0,__mcmsModuleContext.settingsTransferCrypto)().subtle.decrypt(
            { name: 'AES-GCM', iv: validated.iv, additionalData: (0,__mcmsModuleContext.settingsTransferAdditionalData)(), tagLength: 128 },
            key,
            validated.ciphertext
        );
        const parsed = __mcmsModuleContext.JSON.parse(new __mcmsModuleContext.TextDecoder().decode(plaintext));
        if (!(0,__mcmsModuleContext.extractImportedToolkitState)(parsed)) throw new __mcmsModuleContext.Error('The decrypted file does not contain Toolkit settings.');
        return parsed;
        } catch (err) {
        if (err?.message?.includes('does not contain')) throw err;
        throw new __mcmsModuleContext.Error('The passphrase is wrong or the encrypted file has been altered.');
        }
    }),
"createEncryptedSettingsExport":__mcmsModuleContext=>(async function createEncryptedSettingsExport() {
        const overlay = (0,__mcmsModuleContext.commandExperienceElement)(__mcmsModuleContext.SCRIPT.commandExperienceModalId);
        const passphrase = overlay?.querySelector('[data-transfer-passphrase]')?.value || '';
        const confirmation = overlay?.querySelector('[data-transfer-passphrase-confirm]')?.value || '';
        const status = overlay?.querySelector('[data-transfer-status]');
        if (passphrase !== confirmation) { if (status) status.textContent = 'Passphrases do not match.'; return; }
        try {
        if (status) status.textContent = 'Encrypting private Toolkit settings…';
        const exportedAt = new __mcmsModuleContext.Date();
        const envelope = await (0,__mcmsModuleContext.encryptToolkitSettings)(passphrase, exportedAt);
        const BlobConstructor = __mcmsModuleContext.pageWindow.Blob || __mcmsModuleContext.globalThis.Blob;
        (0,__mcmsModuleContext.downloadToolkitSettingsBlob)(
            new BlobConstructor([__mcmsModuleContext.JSON.stringify(envelope, null, 2)], { type: 'application/json' }),
            (0,__mcmsModuleContext.settingsBackupFilename)(exportedAt, 'encrypted')
        );
        (0,__mcmsModuleContext.closeCommandExperienceModal)();
        (0,__mcmsModuleContext.showToast)('Encrypted Toolkit transfer created');
        } catch (err) {
        if (status) status.textContent = err?.message || 'Encrypted export failed.';
        }
    }),
"unlockEncryptedSettingsImport":__mcmsModuleContext=>(async function unlockEncryptedSettingsImport() {
        const pending = __mcmsModuleContext.settingsTransferPending;
        const overlay = (0,__mcmsModuleContext.commandExperienceElement)(__mcmsModuleContext.SCRIPT.commandExperienceModalId);
        const passphrase = overlay?.querySelector('[data-transfer-passphrase]')?.value || '';
        const status = overlay?.querySelector('[data-transfer-status]');
        if (pending?.type !== 'encrypted') return;
        try {
        if (status) status.textContent = 'Authenticating encrypted transfer…';
        const parsed = await (0,__mcmsModuleContext.decryptToolkitSettings)(pending.envelope, passphrase);
        (0,__mcmsModuleContext.renderSettingsTransferPreview)((0,__mcmsModuleContext.settingsTransferPreview)(parsed));
        } catch (err) {
        if (status) status.textContent = err?.message || 'The encrypted transfer could not be unlocked.';
        }
    }),
"playPayoutMediaSound":__mcmsModuleContext=>(async function playPayoutMediaSound(template) {
        if (!__mcmsModuleContext.state.payoutFlash.soundEnabled || __mcmsModuleContext.state.payoutFlash.soundVolume <= 0) return false;
        const audio = (0,__mcmsModuleContext.getPayoutMediaAudio)(template);
        if (!audio) return false;
        try {
            const generation = ++__mcmsModuleContext.payoutMediaGeneration;
            audio.pause();
            audio.currentTime = 0;
            audio.muted = false;
            audio.preload = 'auto';
            audio.volume = (0,__mcmsModuleContext.clamp)(__mcmsModuleContext.state.payoutFlash.soundVolume, 0, 1, 0.35);
            await audio.play();
            if (generation !== __mcmsModuleContext.payoutMediaGeneration) {
                audio.pause();
                return false;
            }
            return true;
        } catch (err) {
            __mcmsModuleContext.console.warn(`[${__mcmsModuleContext.SCRIPT.name}] Hosted payout audio was blocked or unavailable; using synthesized fallback.`, err);
            return false;
        }
    })};})();

})();
