[app]
title = Bry Download Pro
package.name = brydownload
package.domain = org.bry
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

# MUDANÇA IMPORTANTE: Removi ffpyplayer e openssl. 
# Travamos o Kivy na versão 2.3.0 para estabilidade.
requirements = python3,kivy==2.3.0,kivymd,yt-dlp,certifi

orientation = portrait
fullscreen = 0
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,ACCESS_NETWORK_STATE

# Configurações do Android
android.api = 33
android.minapi = 21
android.archs = arm64-v8a

# Configurações de Compilação (Evita erros de patch)
p4a.branch = master
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
