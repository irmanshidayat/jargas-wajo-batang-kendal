# Instruksi Manual: Copy SSH Public Key ke Server

Karena SSH masih meminta password, ikuti langkah berikut untuk copy public key secara manual:

## Langkah 1: Baca Public Key

Di Windows PowerShell, jalankan:
```powershell
Get-Content "$env:USERPROFILE\.ssh\github_actions.pub"
```

Output akan seperti ini:
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIC1EpYbTekG20g8y8Vo6wjLyy3AgCAEKdVYfoXKL3zb4 github-actions
```

## Langkah 2: Copy Public Key

Copy seluruh baris public key di atas (dari `ssh-ed25519` sampai `github-actions`)

## Langkah 3: SSH ke Server

```bash
ssh root@72.61.142.109
```

(Masukkan password saat diminta)

## Langkah 4: Tambahkan Public Key ke Server

Setelah login ke server, jalankan perintah berikut (ganti `YOUR_PUBLIC_KEY` dengan public key yang sudah di-copy):

```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIC1EpYbTekG20g8y8Vo6wjLyy3AgCAEKdVYfoXKL3zb4 github-actions" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

## Langkah 5: Verifikasi

Keluar dari server (`exit`), lalu test SSH tanpa password:

```powershell
ssh -i "$env:USERPROFILE\.ssh\github_actions" root@72.61.142.109 "echo 'SSH OK'"
```

Jika berhasil, akan menampilkan "SSH OK" tanpa minta password.

## Langkah 6: Verifikasi Setup Lengkap

Jalankan script verifikasi:
```powershell
.\scripts\active\verify-server-setup-dev.ps1
```

Sekarang seharusnya semua check berhasil, termasuk SSH connection.

