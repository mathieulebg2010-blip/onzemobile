[app]
source.dir = .
title = OnzeMobile
package.name = onzemobile
package.domain = org.onzemusique
source.include_exts = py,png,jpg,kv,atlas,ico,mp3
version = 4.5
requirements = python3,kivy,pygame
orientation = portrait
fullscreen = 0
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 33
android.min_api = 21
android.sdk = 33
android.accept_sdk_license = True
android.ndk = 25b
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
