# Quick Start Guide - FILE-MANAGEMENT-SYSTEM-OS

## 🚀 การรันโปรแกรม (3 ขั้นตอน)

### Step 1: เปิด Command Prompt
กด `Win + R` แล้วพิมพ์ `cmd` กด Enter

### Step 2: เข้าโฟลเดอร์โปรเจ็ค
```bash
cd "C:\Users\pariy\OneDrive\เดสก์ท็อป\Xcottz\ProjectOS\GUI-OS"
```

### Step 3: รันโปรแกรม
```bash
run_integrated.bat
```

หรือ double-click ที่ไฟล์ `run_integrated.bat`

## ✅ สิ่งที่โปรแกรมจะทำอัตโนมัติ

1. ✓ เช็ค dependencies ทั้งหมด
2. ✓ ถ้าขาด จะถามให้ติดตั้ง (กด Y)
3. ✓ ติดตั้ง package ที่ขาดอัตโนมัติ
4. ✓ เปิดโปรแกรม

## 🔌 วิธีเชื่อมต่อ Raspberry Pi

### ใช้ SSH Key (แนะนำ)

1. คลิก **"🔌 เชื่อมต่อ"** ที่ sidebar ซ้ายมือ

2. กรอกข้อมูล:
   ```
   ชื่อการเชื่อมต่อ:  Raspberry Pi
   โปรโตคอล:         SFTP
   ชื่อโฮสต์:        100.100.144.94
   พอร์ต:            2222
   ชื่อผู้ใช้:        shinrugn
   ไฟล์คีย์:         C:\Users\pariy\.ssh\id_rsa
   ```

3. ✅ เช็ค **"บันทึกการเชื่อมต่อ"**

4. คลิก **"เชื่อมต่อ"**

5. รอ Progress Dialog แสดงสถานะ:
   ```
   ✓ Searching for host...
   ✓ Connecting to host...
   ✓ Authenticating...
   ✓ Using username "shinrugn"
   ✓ Authenticating with public key...
   ✓ Connection successful!
   ```

6. จะเห็น Toast notification **"✓ Connected successfully"**

### ครั้งถัดไป (โหลด Config)

1. คลิก **"🔌 เชื่อมต่อ"**
2. เลือกจาก dropdown **"การเชื่อมต่อที่บันทึกไว้"**
3. เลือก **"Raspberry Pi"**
4. ข้อมูลจะถูกกรอกอัตโนมัติ
5. คลิก **"เชื่อมต่อ"**

## 📂 การใช้งาน Dual-Panel

### Panel ซ้าย (💻 Local)
- แสดงไฟล์ในเครื่องของคุณ
- เริ่มที่ Home directory
- สามารถ navigate ได้ตามปกติ

### Panel ขวา (🌐 Remote)
- แสดงไฟล์บน Raspberry Pi
- เริ่มที่ home directory ของ user
- navigate ได้เหมือน Local

### ปุ่มตรงกลาง
- **→ อัปโหลด:** เลือกไฟล์ทาง Local แล้วกดปุ่มนี้
- **← ดาวน์โหลด:** เลือกไฟล์ทาง Remote แล้วกดปุ่มนี้

## 💻 การใช้ Terminal

1. คลิกที่ Tab **"💻 Terminal"**
2. พิมพ์คำสั่ง Linux เช่น:
   ```bash
   ls -la
   pwd
   df -h
   cat /etc/os-release
   ```
3. กด Enter หรือคลิก **"ส่งคำสั่ง"**

## 📝 ดู Logs

Logs อยู่ที่: `src/logs/`

เปิดไฟล์ล่าสุด:
```bash
src/logs/app_YYYYMMDD_HHMMSS.log
```

## 🎨 เปลี่ยนภาษา

1. ไปที่ Sidebar (ซ้ายมือ)
2. เลื่อนลงล่างสุด
3. หา dropdown **"ภาษา:"**
4. เลือก **"ไทย 🇹🇭"** หรือ **"English 🇬🇧"**

## 🎨 เปลี่ยนธีม

ที่ Sidebar > **"รูปแบบ:"**
- สว่าง (Light)
- มืด (Dark) ← Default
- ระบบ (System)

## 🐛 แก้ปัญหา

### ❌ "Module not found"
```bash
# รันอีกครั้ง จะติดตั้งอัตโนมัติ
run_integrated.bat
```

### ❌ "Connection timeout"
ตรวจสอบ:
- [ ] Raspberry Pi เปิดอยู่หรือไม่
- [ ] เชื่อมต่อ Network เดียวกันหรือไม่
- [ ] Port 2222 ถูกต้องหรือไม่

### ❌ "Authentication failed"
ตรวจสอบ:
- [ ] SSH Key path ถูกต้องหรือไม่
- [ ] Username ถูกต้องหรือไม่
- [ ] Key มี passphrase หรือไม่

## 📋 Keyboard Shortcuts

- `Ctrl + C` - Copy (ใน Terminal)
- `Ctrl + V` - Paste (ใน Terminal)
- `Enter` - Execute command (ใน Terminal)
- `Enter` - Navigate to path (ใน Path Entry)
- `Double Click` - Open folder (ใน File Browser)
- `Right Click` - Context menu (ใน File Browser)

## 🎯 Tips

1. **บันทึก Config**: เช็ค "บันทึกการเชื่อมต่อ" ครั้งแรก
2. **Quick Transfer**: เลือกไฟล์แล้วกดปุ่มกลาง
3. **View Logs**: เช็ค `src/logs/` เมื่อมี error
4. **Auto Cleanup**: Logs เก่าจะถูกลบอัตโนมัติทุก 7 วัน
5. **Toast Notification**: จะแสดงผลการทำงานเป็น popup ที่หายไปเอง

## 📞 ติดต่อ / Report Bug

- **Student ID:** 67050651
- **Email:** 67050651@kmit.ac.th

## 📄 Documents

- [README.md](README.md) - เอกสารฉบับเต็ม
- [requirements.txt](requirements.txt) - รายการ dependencies

---

**เริ่มต้น:** Double-click `run_integrated.bat`

**Logs:** `src/logs/`

**Config:** `~/.gui_os/config.json`
