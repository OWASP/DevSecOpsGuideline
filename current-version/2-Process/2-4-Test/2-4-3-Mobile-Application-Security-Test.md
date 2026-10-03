# Mobile Application Security Testing

Mobile applications introduce a distinct threat surface: the app runs on a device the user (and potential attacker) fully controls, stores data locally, communicates over untrusted networks, and can be decompiled and inspected. Mobile Application Security Testing adapts static, dynamic, and interactive techniques to the realities of iOS and Android.

## The OWASP MAS standard

The [OWASP Mobile Application Security (MAS)](https://mas.owasp.org/) project is the definitive reference:

- **MASVS (Verification Standard)** — the security requirements a mobile app should meet, organized into controls: Storage, Cryptography, Authentication, Network, Platform, Code Quality, and Resilience.
- **MASTG (Testing Guide)** — concrete techniques and test cases for verifying those requirements on both iOS and Android, with platform-specific tools and scripts.
- **MAS Checklist** — maps MASVS controls to MASTG test cases for structured assessments; use it as your test plan template.

### MASVS level selection

MASVS defines three security levels. Choose based on your app's risk profile:

| Level | Target apps | Key requirements |
|---|---|---|
| L1 | All apps — baseline for consumer apps with low sensitivity | No sensitive data in logs/cleartext; TLS enforced; basic input validation |
| L2 | Apps handling sensitive or personal data (healthcare, financial, enterprise) | Secure storage (Keystore/Keychain), certificate pinning, strong auth, anti-tampering basics |
| R (Resilience) | High-value apps: banking, digital wallets, DRM, security-sensitive | Obfuscation, jailbreak/root detection, anti-debugging, certificate pinning bypass resistance |

A mobile banking app should target L2 + R. A general consumer utility app targets L1. An enterprise MDM app likely targets L2.

## The mobile-specific threat surface

Mobile introduces threat vectors that do not exist in web apps:

### Data storage
- Sensitive data in unprotected `SharedPreferences` (Android) or `NSUserDefaults` (iOS) — readable by any app with filesystem access on a rooted device
- Cleartext credentials in SQLite databases, log files, or OS-level screenshot captures
- Auto-backup to cloud (Android) and iCloud (iOS) may exfiltrate data unintentionally

### Transport and certificate security
- **Certificate pinning bypass** — on rooted/jailbroken devices, an attacker can install a custom CA (e.g., Burp Suite CA) to MitM all TLS traffic. Apps handling sensitive data should implement certificate pinning and detect bypass attempts.
- Missing or misconfigured Network Security Config (Android) or App Transport Security (iOS) allows cleartext HTTP

### Authentication and biometrics
- Biometric authentication (Face ID, fingerprint) can be bypassed at the OS level on compromised devices. The app must use hardware-backed biometric APIs (Android BiometricPrompt with `BIOMETRIC_STRONG`, iOS LocalAuthentication with `.deviceOwnerAuthenticationWithBiometrics`) and must not fall back to PIN trivially.
- JWT or session tokens stored in SharedPreferences or NSUserDefaults instead of Android Keystore / iOS Keychain are readable on rooted devices

### Deep links and inter-app communication
- Unvalidated deep links accept attacker-controlled URLs that invoke privileged in-app actions
- Android Intents with exported Activities/Services/Broadcast Receivers that lack permission checks allow any app to trigger internal functionality
- iOS Universal Links require proper apple-app-site-association configuration; improper setup allows link hijacking

### Reverse engineering
- Debug builds with `android:debuggable="true"` allow arbitrary code injection via `adb`
- Hardcoded API keys, encryption keys, or credentials in `strings.xml`, `BuildConfig`, or `Info.plist`
- Unobfuscated business logic exposes algorithms, backend endpoints, and internal decision trees to competitors or attackers

### Jailbreak and root detection
- On jailbroken (iOS) or rooted (Android) devices, security controls enforced by the OS (sandboxing, Keychain isolation, certificate pinning) may be bypassed. L2/R apps should detect and respond to compromised device states.

## What to test (organized by MASVS category)

- **Storage** — check all data written after sensitive operations (login, payment, health data entry) using device filesystem inspection
- **Cryptography** — review algorithms used; look for hardcoded keys, ECB mode, deprecated hash functions
- **Authentication** — test session expiry, re-authentication for sensitive actions, biometric bypass on rooted devices
- **Network** — proxy all traffic; look for HTTP, self-signed cert acceptance, missing pinning
- **Platform** — check exported components, deep link handling, clipboard exposure, screenshot protection
- **Code Quality** — static analysis for dangerous APIs, debug flags, hardcoded secrets
- **Resilience** (L2+R) — test jailbreak/root detection bypass, debugger attachment, dynamic instrumentation hooks

## Static analysis with MobSF (walkthrough)

MobSF provides automated static and dynamic analysis via a web UI and REST API. For CI integration:

```bash
# 1. Start MobSF (Docker)
docker run -it --rm -p 8000:8000 opensecurity/mobile-security-framework-mobsf:latest

# 2. Upload and scan an APK
HASH=$(curl -s -X POST "http://localhost:8000/api/v1/upload" \
  -H "Authorization: $MOBSF_API_KEY" \
  -F "file=@./app-release.apk" | jq -r '.hash')

# 3. Trigger scan
curl -s -X POST "http://localhost:8000/api/v1/scan" \
  -H "Authorization: $MOBSF_API_KEY" \
  -d "hash=$HASH"

# 4. Get JSON report
curl -s -X POST "http://localhost:8000/api/v1/report_json" \
  -H "Authorization: $MOBSF_API_KEY" \
  -d "hash=$HASH" | jq '.average_cvss, .security_score'

# 5. Gate: fail build if security score below threshold
SCORE=$(curl -s -X POST "http://localhost:8000/api/v1/report_json" \
  -H "Authorization: $MOBSF_API_KEY" \
  -d "hash=$HASH" | jq '.security_score')
[ "$SCORE" -lt 60 ] && echo "FAIL: MobSF score $SCORE below threshold" && exit 1
```

Run this step in CI on every release build and on the nightly build for the main branch.

## Dynamic analysis with Frida

[Frida](https://frida.re/) is a dynamic instrumentation toolkit that lets you inject JavaScript into a running app process to hook methods, bypass controls (for testing), and observe behavior static analysis cannot see.

Common testing use cases:

```javascript
// Hook SSL pinning methods to observe bypassed traffic during testing
// (Android — OkHttp certificate pinner)
Java.perform(function () {
  var CertificatePinner = Java.use('okhttp3.CertificatePinner');
  CertificatePinner.check.overload('java.lang.String', 'java.util.List').implementation = function (hostname, peerCertificates) {
    console.log('[Frida] SSL pinning bypassed for: ' + hostname);
    return; // skip the check
  };
});

// Hook biometric authentication result (for testing fallback behavior)
Java.perform(function () {
  var BiometricPrompt = Java.use('androidx.biometric.BiometricPrompt$AuthenticationCallback');
  BiometricPrompt.onAuthenticationSucceeded.implementation = function (result) {
    console.log('[Frida] Biometric auth succeeded (hooked)');
    this.onAuthenticationSucceeded(result);
  };
});
```

Use Frida to validate that L2/R controls are effective: attempt a bypass and confirm detection. The [objection](https://github.com/sensepost/objection) framework wraps Frida into an interactive shell for common tasks without writing scripts.

**Important:** Frida-based pinning bypass is a testing technique for evaluating implementation correctness. Production builds must enforce pinning and detect Frida/instrumentation frameworks as part of Resilience controls.

## App Store and Play Store security review

Both Apple and Google perform automated and manual security review:

- **Google Play** — uses automated scanning for known malware patterns and policy violations. Severe security issues can trigger removal. Play App Signing gives Google control over the final signing key.
- **Apple App Store** — manual review checks for private API usage, inappropriate data access, and some security patterns. App Attest and DeviceCheck APIs provide server-side device integrity signals.

Neither store's review is a substitute for your own security assessment — store reviews focus on policy compliance, not application security depth. Run your security program independently.

## CI/CD integration

A typical mobile security pipeline step:

```yaml
# GitHub Actions — mobile security gate on release builds
- name: Mobile SAST (MobSF)
  run: |
    HASH=$(curl -s -X POST "$MOBSF_URL/api/v1/upload" \
      -H "Authorization: $MOBSF_API_KEY" \
      -F "file=@$APK_PATH" | jq -r '.hash')
    curl -s -X POST "$MOBSF_URL/api/v1/scan" \
      -H "Authorization: $MOBSF_API_KEY" -d "hash=$HASH"
    SCORE=$(curl -s -X POST "$MOBSF_URL/api/v1/report_json" \
      -H "Authorization: $MOBSF_API_KEY" -d "hash=$HASH" | jq '.security_score')
    [ "$SCORE" -lt 60 ] && exit 1 || echo "Score: $SCORE"
```

Gate on MobSF's security score and block on critical findings. Complement with periodic manual assessment for logic flaws, reverse-engineering resistance, and platform-specific misuse.

## Common pitfalls and anti-patterns

- **Testing only against an emulator** — some security controls (Secure Enclave, hardware-backed Keystore) behave differently on physical devices. Test on real hardware for L2/R assessments.
- **Bypassing SSL pinning without understanding the impact** — pinning bypass is necessary for testing but never acceptable in production. Verify pinning is actually enforced in release builds.
- **Treating mobile security as a one-time pentest** — mobile threat landscape changes with OS updates. Continuous CI scanning catches regressions introduced by dependency or SDK updates.
- **Ignoring the backend** — mobile-specific app security means little if the backend API accepts unauthenticated calls or has BOLA/IDOR flaws.
- **Not testing deep-link and intent handling** — these are a common entry point for mobile-specific attacks and are often missed by automated scanners.

## Maturity progression

**Starter** — Run MobSF static scan on every release APK/IPA. Review MASVS L1 checklist manually for critical apps. Create tickets for high findings.

**Intermediate** — Automate MobSF in CI pipeline with a score gate. Add dynamic testing with Burp Suite proxy during QA. Validate all MASVS L1 controls automatically; manually verify L2 controls for sensitive apps.

**Advanced** — Full MASVS L2 automated coverage with Frida scripts for runtime checks. Continuous API testing from proxied device tests. Integrate findings into central ASPM. Resilience (R) assessment for banking or DRM apps. Track MASVS coverage as a metric per release.

## Metrics and KPIs

- **MASVS controls passing per level (L1/L2/R)** — expressed as a percentage; track regression per release.
- **Critical/high findings per build** — gate signal; should reach zero before release.
- **Mean time to remediate mobile findings** — compare to web app MTTR.
- **MobSF security score trend** — track over time to catch gradual degradation from dependency updates.

---

## Tools[^1]

### Open-source

- [Frida](https://frida.re/) — Dynamic instrumentation toolkit for inspecting and manipulating apps at runtime; hooks methods, bypasses SSL pinning (for testing), dumps memory, and traces API calls. The foundation of most advanced mobile testing and L2/R validation.
- [MobSF (Mobile Security Framework)](https://github.com/MobSF/Mobile-Security-Framework-MobSF) — Automated static and dynamic analysis for Android and iOS; supports APK, IPA, and APPX; REST API enables CI integration. Best starting point for automated mobile scanning.
- [objection](https://github.com/sensepost/objection) — Runtime mobile exploration powered by Frida; provides an interactive shell for real-time security testing without needing to write Frida scripts manually. Fastest path to SSL pinning bypass and biometric testing.
- [apktool](https://github.com/iBotPeaches/Apktool) — Reverse-engineering tool for Android APKs; decompiles to smali, inspects resources and manifest, and repackages. Used for manifest analysis and detecting debug flags.
- [jadx](https://github.com/skylot/jadx) — Dex-to-Java decompiler; reads Android app logic from compiled bytecode. Cleaner output than apktool's smali for code review.

### Commercial

- [Appknox](https://www.appknox.com/) — Mobile application security testing platform with automated SAST/DAST, compliance mapping, and app store integration; good for teams wanting managed mobile security without building their own toolchain.
- [NowSecure](https://www.nowsecure.com/) — Mobile app security testing and continuous monitoring with automated dynamic analysis on real devices; widely used in financial services for L2 and R assessments.
- [Oversecured](https://oversecured.com/) — Android-focused static analysis with deep interprocedural analysis; finds vulnerabilities that simpler scanners miss, particularly in complex multi-component apps.

---

### Links

[^1]: Listed in alphabetical order.
