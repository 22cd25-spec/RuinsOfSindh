[app]

# (str) Title of your application
title = Ruins of Sindh

# (str) Package name
package.name = ruinsofsindh

# (str) Package domain (needed for android/ios packaging)
package.domain = org.yourname

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,ttf,wav,json

# (str) Application versioning
version = 1.0.0

# (list) Application requirements
requirements = python3, pygame, pillow

# (list) Supported orientations
orientation = landscape

#
# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# (list) Permissions
android.permissions = VIBRATE

# (int) Target Android API (Play Store 2026 requires 34+)
android.api = 34

# (int) Minimum API support
android.minapi = 21

# (int) Android SDK version to use
android.sdk = 34

# (str) Android NDK version to use
android.ndk = 25b

# (bool) If True, then automatically accept SDK license
android.accept_sdk_license = True

# (str) Bootstrap to use for android builds (MUST BE SDL2 for Pygame)
p4a.bootstrap = sdl2

# (list) The Android archs to build for
android.archs = arm64-v8a, armeabi-v7a

# (bool) enables Android auto backup feature
android.allow_backup = True

# (str) The format used to package the app for release mode
android.release_artifact = aab

# (str) The format used to package the app for debug mode
android.debug_artifact = apk

# --- KEYSTORE SIGNING (CRITICAL FOR PLAY STORE) ---
# Ensure the my-release-key.keystore file is in the same folder as main.py
android.keystore = my-release-key.keystore
android.keystore_password = password123
android.keyalias = my-key-alias
android.keyalias_password = password123


[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 1