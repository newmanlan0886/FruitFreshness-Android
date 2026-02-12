$buildozerSpec = @'
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
android.p4a_dir = /home/runner/work/p4a

[buildozer]
log_level = 2
warn_on_root = 1
archs = arm64-v8a
'@

# 寫入檔案（強制覆蓋）
$buildozerSpec | Out-File -FilePath buildozer.spec -Encoding UTF8 -Force

Write-Host "✅ buildozer.spec 已更新為終極簡潔版" -ForegroundColor Green