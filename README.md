# SONiC Switch Telemetry Project 📈

ระบบ Monitor และ Telemetry สำหรับ Network Switch ที่เปลี่ยนมาใช้ระบบปฏิบัติการ **SONiC** โดยใช้สุดยอดเครื่องมืออย่าง **Prometheus** และ **Grafana** เพื่อเก็บรวบรวมข้อมูลและแสดงผลเป็นกราฟที่ดูง่ายและสวยงามประหยัดเวลา

ไฮไลท์หลักของโปรเจคนี้คือ **Custom Temperature Exporter** ที่เขียนขึ้นด้วย Python ซึ่งจะทำการรีโมท (SSH) เข้าไปยังอุปกรณ์ SONiC Switch เพื่อตรวจสอบอุณหภูมิแบบเรียลไทม์ และส่งข้อมูลไปยังหน้าปัดของ Prometheus 

## 🏗️ โครงสร้างของระบบ (Architecture)
1. **Prometheus**: ทำหน้าที่เข้าถึงเป้าหมายและดึงข้อมูลมาเก็บไว้ในฐานข้อมูล Time-series
2. **Grafana**: รับหน้าที่ดึงข้อมูลที่อยู่ใน Prometheus มาวาดเป็นกราฟบน Dashboard
3. **Temp Exporter (Python)**: พระเอกของเรา! สคริปต์ดึงค่าอุณหภูมิจาก SONiC Switch ผ่าน SSH 
4. **gNMI (ถ้ามี)**: รองรับการดึงข้อมูลสถิติหรือ Traffic จาก Interface แบบมาตรฐานด้วย gNMI Protocol (แก้ไขที่ `gnmic-config.yml`)

---

## 🚀 วิธีการดาวน์โหลดและเตรียมรันโปรเจค 

### 1. สิ่งที่ต้องมีเบื้องต้น (Prerequisites)
ก่อนเริ่มใช้งานเครื่องของคุณจะต้องมี 2 ส่วนนี้:
- **[Docker](https://docs.docker.com/get-docker/) และ [Docker Compose](https://docs.docker.com/compose/install/)** เครื่องมือที่ช่วยเสกโปรแกรมขึ้นมาในพริบตา
- **Git** สำหรับดึงซอร์สโค้ด

### 2. ดาวน์โหลดโปรเจค (Clone Repository)
ให้น้องๆ เปิด Terminal หรือ Command Prompt ในเครื่องของตัวเอง และพิมพ์สั่งตามนี้เพื่อดึงโค้ด:

```bash
git clone https://github.com/RachanP/Telemetry_Project.git
cd Telemetry_Project
```

### 3. ตั้งค่าระบบ (Configuration)
โปรเจคนี้จัดเก็บรหัสผ่านและข้อมูลเชื่อมต่อไว้ที่ไฟล์เดียวคือ **`.env`** 
เปิดไฟล์ `.env` ด้วยโปรแกรมเช่น Notepad หรือ VSCode เพื่อตั้งค่า IP ของสวิตช์:

```ini
# การตั้งค่า Switch แบบคร่าวๆ (แก้ไขตามสวิตช์ของคุณ)
SWITCH_IP=192.168.1.11      
SWITCH_USER=admin           
SWITCH_PASS=YourPaSsWoRd    
```

### 4. รันระบบทั้งหมดด้วยคำสั่งเดียว (Run the Stack)
แค่สั่งคำสั่งนี้ โปรเจคของเราจะพ่นลมหายใจขึ้นมาทำงานอยู่เบื้องหลัง:

```bash
docker compose up -d
```
*(ถ้าอยากเช็คผลว่าระบบพังไหมหรือทำอะไรอยู่บ้าง ลองใช้คำสั่ง `docker compose logs -f temp-exporter` ได้เลยครับ)*

---

## 💻 วิธีการเข้าชมผลลัพธ์ผ่านหน้าเว็บ (Access)

หลังรันคำสั่งเสร็จแล้ว คุณสามารถเข้าผ่าน Web Browser ไปยัง Address เหล่านี้ได้ทันที:

- 📊 **Grafana Dashboard**: [http://localhost:3000](http://localhost:3000)
    - Username: `admin`
    - Password: รหัสที่คุณเซ็ตไว้ตั้งต้นที่ไฟล์ `.env` (ที่ตัวแปร `GRAFANA_ADMIN_PASSWORD`)
    - *เริ่มต้นสร้างกราฟและพ่วงเข้ากับ `http://prometheus:9090` ได้เลย*
- 🗄️ **Prometheus Server**: [http://localhost:9090](http://localhost:9090)
    - สามารถเข้าไปทดสอบ Query ข้อมูลดิบโดยค้นหาตัวแปรเช่น `sonic_temperature_celsius`
- 🌡️ **Temp Exporter**: [http://localhost:9805/metrics](http://localhost:9805/metrics)
    - ลองกดเข้าไปดูว่าอุณหภูมิที่ดึงมาปรากฏขึ้นไหม

---

## 📁 โครงสร้างไฟล์ (File Structure)
* `docker-compose.yml`: ไฟล์กำหนด Service ต่างๆ ให้ทำงานร่วมกันบน Docker
* `prometheus.yml`: ไฟล์ Config กำหนดเป้าหมายเป้าประสงค์ที่จะให้ Prometheus ดึงข้อมูล
* `gnmic-config.yml`: ไฟล์ตั้งค่าสำหรับระบบ gNMI client 
* `sonic_temp_exporter.py`: สคริปต์หลักที่เป็นหัวใจสำหรับดึงอุณหภูมิจาก Switch
* `Dockerfile`: เครื่องจักรแพ็กระบบให้สคริปต์ Python กลายเป็น Docker
* `.env`: คอนฟิกตัวแปรระบบ (ในโปรเจคนี้ไม่ต้องห่วง เพราะผมใส่มาให้โหลดเข้าเครื่องใช้ได้เลย)

🎉 **ขอให้สนุกกับการทำ Telemetry Project นะครับทุกคน!** 🎉
