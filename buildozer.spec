[app]
title = 水果新鮮度診斷
package.name = fruitfreshness
package.domain = org.yourorg.fruitfreshness
source.dir = .
source.include_exts = py,png,jpg,kv,env
version = 0.1
requirements = python3,kivy,Pillow,google-genai,python-dotenv
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

# 🔥 關鍵：指定自訂的 p4a 目錄，Buildozer 將不會重新克隆
android.p4a_dir = /home/runner/work/p4a

[buildozer]
log_level = 2
warn_on_root = 1
archs = arm64-v8a