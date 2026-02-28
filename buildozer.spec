[app]
title = 水果新鮮度診斷測試
package.name = fruitfreshnesstest
package.domain = org.yourorg.fruitfreshnesstest
source.dir = .
source.main = test.py
source.include_exts = py,png,jpg,kv,ttf
version = 0.1
requirements = python3,kivy
orientation = portrait
osx.python_version = 3
osx.kivy_version = 2.2.1
fullscreen = 0
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.permissions = CAMERA, INTERNET
android.archs = arm64-v8a
android.gradle_dependencies = androidx.appcompat:appcompat:1.6.1
p4a.ignore = pyjnius

[buildozer]
log_level = 2
warn_on_root = 1
archs = arm64-v8a