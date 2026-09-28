# BuildSuite Core — Mobile App Guide (Android & iOS)

BuildSuite Core can be built as an installable mobile application for Android and iOS using **Capacitor**, or installed as a **PWA** directly from a web browser.

---

## 1. Architecture Overview

```mermaid
flowchart TD
    subgraph Mobile Device (Android / iOS)
        A[Native Capacitor Shell] --> B[Embedded WebView]
        B --> C[Vue 3 SPA - dist-mobile]
        C --> D[Mobile Seam / Storage Layer]
    end

    subgraph Authentication & API Seam
        D -->|Preferences| E[Server URL + API Token Key:Secret]
        C -->|Global Fetch & XHR Interceptor| F[resolveApiUrl]
        F -->|Prepend Server Origin + Auth Header| G[Remote Frappe Server]
    end
```

- **Dual-target Vite configuration:**
  - `yarn build`: Compiles for Frappe web hosting into `../buildsuite_core/public/frontend` with `base: /assets/buildsuite_core/frontend/`. Served at `/core`.
  - `yarn build:mobile` (`vite build --mode mobile`): Compiles into `frontend/dist-mobile` with `base: "./"` and hash routing (`createWebHashHistory`).
- **Routing:**
  - On web: Standard pushState history mounted under `/core`.
  - On mobile: Hash history (`createWebHashHistory()`) to ensure safe routing from local assets (`https://localhost/#/...`).

---

## 2. Server Connection & Authentication Model

### Two Types of Auth
The mobile login view provides a dedicated toggle supporting two distinct usage profiles:

1. **Supervisors (Field Operations):**
   - Tailored for Site Supervisors, Site Engineers, Foremen, and Project Managers.
   - Profile presets automatically configure field permissions.
   - Landing view prioritizes daily labour muster / attendance, task progress entries, and site petty cash / expenses.
2. **Administrator:**
   - Full system management and administrative configuration.

### Cross-Origin Token Auth
Mobile WebViews run on `https://localhost` (Android) or `capacitor://localhost` (iOS). To prevent cross-origin cookie loss and third-party cookie blocking:
1. **Server URL Configuration:**
   - First-run screen prompts for the Frappe/ERPNext server address (e.g. `https://erp.example.com`).
   - Validates reachability via `GET {url}/api/method/ping`.
   - Persisted using `@capacitor/preferences`.
2. **Token Issuance:**
   - User signs in with username and password against `POST {url}/api/method/login`.
   - Once authenticated in the session, the app immediately invokes the whitelisted backend endpoint:
     `POST {url}/api/method/buildsuite_core.api.mobile_auth.get_or_create_api_keys`
   - Returns and stores `api_key` and `api_secret` in secure storage.
3. **Unified Request Interception:**
   - All `fetch` and `XMLHttpRequest` (frappe-ui resources, DocType requests, FileUploadHandler) calls pass through a unified interceptor.
   - Transparently prepends the configured server URL.
   - Injects the `Authorization: token {api_key}:{api_secret}` and `X-Frappe-Site-Name` headers.
   - Automatically handles 401s by navigating back to the in-app login screen.

---

## 3. Server Configuration (`site_config.json`)

To permit cross-origin API calls from the mobile app, add the following to your Frappe site's `site_config.json` (under `sites/<site-name>/site_config.json`):

```json
{
  "allow_cors": "*",
  "allow_cors_credentials": true
}
```

Or for tighter security, specify the Capacitor webview origins:

```json
{
  "allow_cors": "https://localhost, capacitor://localhost",
  "allow_cors_credentials": true
}
```

After modifying `site_config.json`, restart Frappe/bench workers:
```bash
bench restart
```

---

## 4. Mobile UX & Native Hardware Plugins

- **Responsive DeskShell:** Collapses the desktop sidebar into an accessible slide-in drawer plus a fixed **Bottom Navigation Bar** for quick one-tap field access to:
  - 🏠 **Home**
  - 👷 **Muster / Attendance**
  - ⏱️ **Progress Entries**
  - 💰 **Expenses & Petty Cash**
  - 📋 **Menu (Drawer)**
- **Touch-optimized Targets:** Minimum 44px touch targets on buttons, form controls, and table rows.
- **Safe-area insets:** Full support for `env(safe-area-inset-top)` and `env(safe-area-inset-bottom)` around notches and gesture bars.
- **Hardware Back Button:** Android back button is intercepted using `@capacitor/app` to navigate backwards through Vue router history rather than exiting the app.
- **Camera Plugin:** `@capacitor/camera` allows field workers to capture receipt photos and site progress images directly from the device camera or gallery.
- **Network & Offline Banner:** Monitors connectivity using `@capacitor/network`. Shows a non-intrusive offline banner and prevents premature ERPNext document submissions when disconnected.

---

## 5. Building & Testing

### Android Development

```bash
cd frontend

# 1. Build mobile web assets and sync to native project
yarn mobile:build

# 2. Compile Debug APK
cd android
./gradlew assembleDebug

# Output APK path:
# frontend/android/app/build/outputs/apk/debug/app-debug.apk
```

#### Sideload to Phone via ADB
With your Android phone connected over USB (USB debugging enabled):
```bash
adb install -r frontend/android/app/build/outputs/apk/debug/app-debug.apk
adb shell am start -n io.buildsuite.core/.MainActivity
```

#### Producing a Signed Release Android App Bundle (AAB)
1. Generate an upload keystore (if you do not already have one):
   ```bash
   keytool -genkey -v -keystore buildsuite-release-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias buildsuite
   ```
2. In `frontend/android/app/build.gradle`, configure signing:
   ```groovy
   signingConfigs {
       release {
           storeFile file("buildsuite-release-key.jks")
           storePassword System.getenv("KEYSTORE_PASSWORD")
           keyAlias "buildsuite"
           keyPassword System.getenv("KEY_PASSWORD")
       }
   }
   buildTypes {
       release {
           signingConfig signingConfigs.release
           minifyEnabled false
           proguardFiles getDefaultProguardFile('proguard-android.txt'), 'proguard-rules.pro'
       }
   }
   ```
3. Build the release bundle for Google Play:
   ```bash
   ./gradlew bundleRelease
   ```
   Output: `frontend/android/app/build/outputs/bundle/release/app-release.aab`.

---

### iOS Development
Building for iOS requires macOS with Xcode 15+:

1. Sync the project:
   ```bash
   yarn mobile:build
   ```
2. Open the native Xcode project:
   ```bash
   yarn mobile:ios
   # or: open frontend/ios/App/App.xcworkspace
   ```
3. In Xcode:
   - Select the `App` target.
   - In **Signing & Capabilities**, select your Apple Developer Team.
   - Build to a connected iPhone or simulator, or select **Product → Archive** to produce an `.ipa` for TestFlight / App Store.

---

## 6. PWA Support (Web Browser Fallback)

BuildSuite Core also ships with a Web App Manifest and Service Worker (`vite-plugin-pwa`) for browsers:
- Any user opening `/core` on a mobile browser (Chrome, Safari) can tap **"Add to Home Screen"** to install it without app store installation.
- The service worker handles application caching while strictly bypassing `/api/*` so live ERPNext transactions are never served stale.

---

## 7. Local Testing With Phone

To test your mobile app against a local dev environment over USB without deploying to a public server:
1. Connect phone with USB debugging enabled.
2. Run port reversal:
   ```bash
   adb reverse tcp:8000 tcp:8000
   ```
3. On the phone's "Server Address" screen, enter:
   ```
   http://localhost:8000
   ```
   Requests will route over the USB cable directly to your PC.
