# Introduction
This project aims to develop an intelligent email management assistant system to improve the efficiency of email handling in both organizational and personal use. As the volume of email communication continues to increase, users are required to spend considerable time filtering, categorizing, and understanding large amounts of email content. In addition, unwanted emails and spam messages may contain deceptive or harmful content that poses security risks to users. Therefore, this project applies Large Language Model (LLM) technology to process language-based content and support systematic email management.

## Prerequisites
- Python 3.11
- Miniconda or Anaconda (not required but recommended for environment management)
- Git

## Steps
1. Clone the repository

   Open the terminal and navigate to the directory where you want to clone the repository, then run:
   ```
   git clone https://github.com/ai-email-client/backend.git
   ```
2. Install the required packages

   You can use Miniconda or Anaconda to create a virtual environment:
   ```
   conda env create -f env.yml
   ```
   or if you want to install the required packages directly:
   ```
   pip install -r requirements.txt
   ```

3. Set up the environment variables

   All configuration is stored in the `.env` file following the `.env.example` template:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your credentials Important variables include:
   - `GOOGLE_CLIENT_ID`: Your Google client ID
   - `GOOGLE_CLIENT_SECRET`: Your Google client secret
   - `GOOGLE_REDIRECT_URI`: Your Google redirect URI
   - `SUPABASE_URL`: Your Supabase URL
   - `SUPABASE_KEY`: Your Supabase key
   - `DIFY_URL`: Your Dify URL
   - `DIFY_SUMMARY`: Your Dify summary app ID
   - `DIFY_WRITER`: Your Dify writer app ID
   - `SECRET_KEY`: Your secret key for JWT token
   - `ALGORITHM`: Your algorithm for JWT token
4. Run the application
   ```bash
   python main.py
   ```
   or use docker
   ```bash
   docker compose up -d
   ```
___
# บทนำ

โปรเจกต์นี้มีเป้าหมายเพื่อพัฒนาระบบผู้ช่วยจัดการอีเมลอัจฉริยะ เพื่อเพิ่มประสิทธิภาพในการจัดการอีเมลทั้งในระดับองค์กรและส่วนบุคคล เนื่องจากปริมาณการสื่อสารผ่านอีเมลเพิ่มขึ้นอย่างต่อเนื่อง ผู้ใช้จึงต้องใช้เวลามากในการกรอง จัดหมวดหมู่ และทำความเข้าใจเนื้อหาอีเมลจำนวนมาก นอกจากนี้ อีเมลที่ไม่ต้องการและสแปมอาจมีเนื้อหาที่หลอกลวงหรือเป็นอันตราย ซึ่งก่อให้เกิดความเสี่ยงด้านความปลอดภัยแก่ผู้ใช้ ดังนั้น โปรเจกต์นี้จึงนำ Large Language Model (LLM) มาประยุกต์ใช้ในการประมวลผลเนื้อหาที่เป็นภาษา และรองรับการจัดการอีเมลอย่างเป็นระบบ

## ข้อกำหนดเบื้องต้น

- Python 3.11
- Miniconda หรือ Anaconda (ไม่จำเป็น แต่แนะนำสำหรับการจัดการสภาพแวดล้อม)
- Git

## ขั้นตอน

1. **โคลน Repository**

   เปิด Terminal แล้วไปยังไดเรกทอรีที่ต้องการโคลน Repository จากนั้นรันคำสั่ง:
   ```
   git clone https://github.com/yourusername/ai-email-client.git
   ```

2. **ติดตั้งแพ็คเกจที่จำเป็น**

   สามารถใช้ Miniconda หรือ Anaconda เพื่อสร้าง Virtual Environment:
   ```
   conda env create -f env.yml
   ```
   หรือหากต้องการติดตั้งแพ็คเกจโดยตรง:
   ```
   pip install -r requirements.txt
   ```

3. **ตั้งค่า Environment Variables**

   การกำหนดค่าทั้งหมดจะถูกเก็บไว้ในไฟล์ `.env` ตามเทมเพลต `.env.example`:
   ```bash
   cp .env.example .env
   ```
   แก้ไขไฟล์ `.env` โดยใส่ข้อมูลรับรองของคุณ ตัวแปรที่สำคัญ ได้แก่:
   - `GOOGLE_CLIENT_ID`: Google Client ID ของคุณ
   - `GOOGLE_CLIENT_SECRET`: Google Client Secret ของคุณ
   - `GOOGLE_REDIRECT_URI`: Google Redirect URI ของคุณ
   - `SUPABASE_URL`: Supabase URL ของคุณ
   - `SUPABASE_KEY`: Supabase Key ของคุณ
   - `DIFY_URL`: Dify URL ของคุณ
   - `DIFY_SUMMARY`: ID ของ Dify Summary App ของคุณ
   - `DIFY_WRITER`: ID ของ Dify Writer App ของคุณ
   - `SECRET_KEY`: Secret Key สำหรับ JWT Token ของคุณ
   - `ALGORITHM`: อัลกอริทึมสำหรับ JWT Token ของคุณ

4. **รันแอปพลิเคชัน**
   ```bash
   python main.py
   ```
   หรือใช้ Docker:
   ```bash
   docker compose up -d
   ```