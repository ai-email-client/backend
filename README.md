## ⚙️ การติดตั้งและการใช้งานส่วน Backend (Backend Setup)

**ข้อกำหนดเบื้องต้น (Prerequisites):**
- [Miniconda](https://docs.conda.io/en/latest/miniconda.html) หรือ Anaconda สำหรับจัดการ Environment
- Python 3.11

**ขั้นตอนการติดตั้ง:**

**โคลนโปรเจกต์และเข้าไปที่โฟลเดอร์ของ Backend**
   ```bash
   git clone <repository-url>
   cd ai-email-client/backend
   ```

**สร้างและเปิดใช้งาน Conda Environment**
   ```bash
   conda env create -f env.yml
   conda activate ace
   ```

**หรือใช้คำสั่ง Pip ในการลง Package ต่างๆแทน Conda**
   ```bash
   pip install -r requirements.txt
   ```

**ตั้งค่า Environment Variables**
   ```bash
   copy .env.sample .env
   ```
จากนั้นเข้าไปกำหนดค่าตัวแปรในไฟล์ .env ให้สอดคล้องกับระบบของคุณ เช่น:
```yml
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
DIFY_URL=your_dify_url
DIFY_API_KEY=your_dify_api_key
```
**รันเซิร์ฟเวอร์ (Run the API Server)**
   ```bash
   python main.py
   ```
หรือใช้คำสั่ง Docker ในการรันเซิร์ฟเวอร์
   ```bash
   docker-compose up --build
   ```