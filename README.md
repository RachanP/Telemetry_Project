# SONiC Switch Telemetry Project

โปรเจคนี้คือระบบ Monitor และ Telemetry สำหรับ Switch ที่รันระบบปฏิบัติการ **SONiC** โดยใช้ Stack ยอดนิยมคือ **Prometheus** และ **Grafana** เพื่อเก็บข้อมูลและแสดงผลเป็นกราฟ 

ความสามารถพิเศษของโปรเจคนี้คือมีสคริปต์ **Custom Temperature Exporter** ที่เขียนด้วย Python ซึ่งจะทำหน้าที่รีโมท (SSH) เข้าไปที่ SONiC Switch เพื่อดึงค่าอุณหภูมิของอุปกรณ์ (ผ่านคำสั่ง `show platform temperature`) แล้วนำมาแปลงให้อยู่ในรูปแบบที่ Prometheus สามารถอ่านได้

## 🏗️ โครงสร้างของระบบ (Architecture)
1. **Prometheus**: ทำหน้าที่ดึงข้อมูล (Scrape) จาก Exporter ต่างๆ ตามเวลาที่กำหนด
2. **Grafana**: เป็นหน้า Dashboard สวยงามสำหรับดึงข้อมูลจาก Prometheus มาแสดงผล
3. **Temp Exporter (Python)**: โปรแกรมที่เราเขียนขึ้นมาดึงค่าอุณหภูมิจาก SONiC Switch โดยเฉพาะ
4. **gNMI (ถ้ามี)**: รองรับการดึงข้อมูลพื้นฐานหรือ Traffic จาก interface ของ Switch ผ่านระบบ gNMI ได้ด้วย (สามารถตั้งค่าใน `gnmic-config.yml`)

---

## 🚀 วิธีการติดตั้งและใช้งาน (Installation & Quick Start)

### 1. สิ่งที่ต้องมีเบื้องต้น (Prerequisites)
- [Docker](https://docs.docker.com/get-docker/) และ [Docker Compose](https://docs.docker.com/compose/install/) ติดตั้งในเครื่อง
- Git

### 2. ดาวน์โหลดโปรเจค (Clone Repository)
เปิด Terminal หรือ Command Prompt ในเครื่องของคุณ และรันคำสั่งเพื่อดาวน์โหลดซอร์สโค้ด:

```bash
git clone <นำ-URL-จาก-GitHub-ของคุณมาใส่ตรงนี้>
cd telemetry_project
```

### 3. ตั้งค่าระบบ (Configuration)
โปรเจคนี้ออกแบบมาให้ตั้งค่าทุกอย่างแบบรวมศูนย์ผ่านไฟล์ **`.env`** 
เปิดไฟล์ `.env` ด้วย Text Editor คู่ใจของคุณเพื่อแก้ไขค่าต่างๆ ให้ตรงกับระบบจริง:

```ini
# ตัวอย่างการตั้งค่า Switch
SWITCH_IP=192.168.1.11      # IP ของ SONiC Switch
SWITCH_USER=admin           # Username ของ SONiC Switch
SWITCH_PASS=YourPaSsWoRd    # Password ของ SONiC Switch
```
*(ถ้าใน repository ไม่มีการ Ignore ไฟล์ `.env` คุณสามารถแก้ไขและเซฟทับได้เลย)*

### 4. รันระบบ (Run the Stack)
ให้มั่นใจว่าคุณอยู่ในโฟลเดอร์ของโปรเจค จากนั้นสั่งรันด้วย Docker Compose:

```bash
docker compose up -d
```
> **หมายเหตุ:** `up -d` หมายถึงรันแบบ Detached mode (รันเป็น Background)

หากต้องการดู Log ตอนทำงานว่าตัว Exporter ดึงอุณหภูมิได้ไหม ให้รันคำสั่ง:
```bash
docker compose logs -f temp-exporter
```

---

## 📊 การเข้าถึงหน้าเว็บ (Accessing Services)

เมื่อระบบรันขึ้นมาแล้ว คุณสามารถเข้าผ่าน Web Browser ได้ตามช่องทางนี้:

- **Grafana**: http://localhost:3000
    - Username เริ่มต้น: `admin`
    - Password เริ่มต้น: ดึงมาจากค่า `GRAFANA_ADMIN_PASSWORD` ในไฟล์ `.env` (ค่าเดิมคือ `admin`)
    - *คุณสามารถสร้าง Dashboard และเชื่อมต่อ Data Source ไปยัง `http://prometheus:9090` ได้ที่นี่!*
- **Prometheus**: http://localhost:9090
    - คุณสามารถเข้าไปพิมพ์หา Metric เช่น `sonic_temperature_celsius` ดูข้อมูลดิบๆ ได้เลย
- **Temp Exporter**: http://localhost:9805/metrics
    - เปิดดูเพื่อตรวจสอบว่าตัว Python Exporter ผลิตข้อมูลออกมาได้ถูกต้องหรือไม่

---

## 🛠️ โครงสร้างไฟล์ (File Structure)
* `docker-compose.yml`: ไฟล์กำหนด Service ต่างๆ ให้ทำงานร่วมกันบน Docker
* `prometheus.yml`: ไฟล์ Config กำหนดเป้าหมาย (Targets) ที่จะให้ Prometheus ไปดึงข้อมูล
* `gnmic-config.yml`: ไฟล์ตั้งค่าสำหรับ gNMI client (ถ้ามีการใช้งานร่วมกับ SONiC)
* `sonic_temp_exporter.py`: สคริปต์หลักที่เป็นหัวใจสำคัญในการดึงอุณหภูมิจาก Switch
* `Dockerfile`: ไฟล์สำหรับแพ็กสคริปต์ Python ลงเป็น Docker Container
* `.env`: ถังเก็บตัวแปรระบบ (Environment Variables) เช่น รหัสผ่าน หรือ IP
* `.env.example`: ตัวอย่างไฟล์ตั้งค่า (เพื่อความปลอดภัย ไม่ใส่รหัสผ่านจริงไว้ในนี้)

**Enjoy the Telemetry! 📈**
