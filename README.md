# 💜 PGK Wallet

### 🔐 Self-Hosted Telegram Cryptocurrency Wallet

PGK Wallet یک سیستم کیف پول رمزارزی مبتنی بر **Telegram Bot** است که با هدف ایجاد یک تجربه ساده، سریع و قابل توسعه برای مدیریت کیف پول، پرداخت، دریافت وجه و مدیریت تراکنش‌ها طراحی شده است.

این پروژه به‌صورت **Self-Hosted** طراحی شده؛ یعنی هر شخص می‌تواند سورس پروژه را دریافت کرده، تنظیمات خودش را انجام دهد و نسخه مستقل خودش از PGK Wallet را اجرا کند.

---

## 🌐 Languages

🇮🇷 فارسی • 🇬🇧 English • 🇷🇺 Русский • 🇨🇳 中文

---

# ✨ ویژگی‌ها

### 👤 User Wallet

هر کاربر می‌تواند از طریق ربات برای خود یک کیف پول ایجاد و مدیریت کند.

امکانات اصلی:

* 💼 ایجاد و مدیریت Wallet
* 💰 مشاهده موجودی
* 📥 دریافت رمزارز
* 📤 ارسال رمزارز
* 🔗 دریافت آدرس کیف پول
* 🧾 ایجاد درخواست پرداخت
* 📊 مشاهده تراکنش‌ها
* 🔔 دریافت اعلان تراکنش
* 🔐 مدیریت امن اطلاعات حساس

---

# 💳 Payment System

PGK Wallet فقط یک نمایش‌دهنده موجودی نیست؛ ساختار پروژه برای ایجاد جریان پرداخت داخل Telegram طراحی شده است.

### جریان پرداخت

```text
👤 Customer
     │
     ▼
🤖 PGK Wallet Bot
     │
     ▼
💳 Create Payment
     │
     ▼
🔗 Payment Request
     │
     ▼
💰 Blockchain Transaction
     │
     ▼
✅ Payment Verification
     │
     ▼
🔔 Notification
```

کاربر می‌تواند یک درخواست پرداخت ایجاد کند و اطلاعات موردنیاز پرداخت را دریافت کند.

---

# 💰 Wallet

بخش Wallet هسته اصلی سیستم است.

```text
┌─────────────────────────────┐
│        💜 PGK WALLET        │
├─────────────────────────────┤
│                             │
│  💰 Balance                 │
│                             │
│  📥 Receive                 │
│  📤 Send                    │
│  🔗 Wallet Address          │
│  📊 Transactions            │
│                             │
└─────────────────────────────┘
```

### Receive

کاربر می‌تواند آدرس دریافت کیف پول خود را مشاهده و برای شخص دیگری ارسال کند.

### Send

کاربر می‌تواند در صورت پشتیبانی شبکه و تنظیمات پروژه، تراکنش ارسال ایجاد کند.

### Transactions

تاریخچه تراکنش‌ها برای بررسی فعالیت‌های کیف پول در دسترس است.

---

# 🧾 Invoice & Payment

سیستم Invoice برای ایجاد درخواست‌های پرداخت طراحی شده است.

نمونه جریان:

```text
Create Invoice
      ↓
Select Amount
      ↓
Select Currency / Network
      ↓
Generate Payment Request
      ↓
Customer Pays
      ↓
Verify Transaction
      ↓
Payment Confirmed ✅
```

این ساختار می‌تواند برای موارد مختلفی مانند:

* فروش محصولات
* خدمات آنلاین
* پرداخت داخل Telegram
* دریافت هزینه
* Donation
* پرداخت‌های شخصی

استفاده شود.

---

# 👑 Admin Dashboard

PGK Wallet دارای بخش مدیریت برای صاحب ربات است.

مدیریت می‌تواند شامل مواردی مانند:

* 👥 کاربران
* 💰 کیف پول‌ها
* 💳 پرداخت‌ها
* 🧾 Invoiceها
* 📊 آمار
* 🔔 اعلان‌ها
* ⚙️ تنظیمات
* 🛠 مدیریت سیستم

باشد.

ساختار کلی:

```text
👑 ADMIN PANEL

├── 👥 Users
├── 💼 Wallets
├── 💳 Payments
├── 🧾 Invoices
├── 📊 Statistics
├── 🔔 Notifications
└── ⚙️ Settings
```

---

# 🔔 Notifications

سیستم اعلان برای اطلاع‌رسانی رویدادهای مهم طراحی شده است.

برای مثال:

```text
💰 New Payment

Amount: 25 USDT
Status: Confirmed ✅

Transaction:
0x............
```

یا:

```text
📥 Incoming Transaction

Amount: 0.05 BTC
Status: Confirmed ✅
```

---

# 🗄 Database

PGK Wallet برای نگهداری اطلاعات موردنیاز سیستم از Database استفاده می‌کند.

اطلاعاتی مانند:

* User information
* Wallet information
* Transactions
* Payments
* Invoices
* Bot settings

می‌توانند در Database مدیریت شوند.

---

# 🔐 Security

امنیت یکی از بخش‌های مهم پروژه است.

پروژه برای استفاده شخصی و Self-Hosted طراحی شده و مسئولیت محافظت از اطلاعات حساس بر عهده صاحب Instance است.

### ⚠️ هرگز این اطلاعات را در GitHub قرار ندهید:

```text
BOT_TOKEN
PRIVATE_KEY
SEED_PHRASE
MNEMONIC
API_KEY
DATABASE_PASSWORD
ADMIN_SECRET
```

اطلاعات حساس باید در Environment Variables یا Secret Management نگهداری شوند.

نمونه:

```env
BOT_TOKEN=YOUR_BOT_TOKEN
DATABASE_URL=YOUR_DATABASE_URL
ADMIN_ID=YOUR_TELEGRAM_ID
```

---

# 🏠 Self-Hosted

یکی از اهداف اصلی PGK Wallet این است که هر شخص بتواند Instance مستقل خودش را داشته باشد.

```text
                PGK Wallet
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
     Server A     Server B     Server C
        │            │            │
     Bot A        Bot B        Bot C
        │            │            │
    Database A   Database B   Database C
```

هر Instance می‌تواند تنظیمات، Bot Token و Database مستقل خودش را داشته باشد.

---

# 🛠 Technology

پروژه بر پایه تکنولوژی‌های زیر توسعه داده شده است:

* 🐍 Python
* 🤖 Telegram Bot API
* 🗄 Database
* 🔐 Security Services
* 💳 Payment Services
* 🧾 Invoice System
* ⚙️ Modular Architecture

---

# 📁 Project Structure

ساختار کلی پروژه:

```text
PGK-Wallet/
│
├── main.py
├── config.py
├── requirements.txt
├── backup.py
│
└── app/
    │
    ├── bot/
    │   ├── handlers/
    │   ├── keyboards/
    │   ├── states/
    │   └── jobs.py
    │
    ├── database/
    │   ├── database.py
    │   ├── models.py
    │   └── repositories/
    │
    └── services/
        ├── wallet_service.py
        ├── payment_service.py
        ├── invoice_service.py
        ├── security_service.py
        └── notification_service.py
```

---

# 🚀 Installation

### 1. Clone

```bash
git clone https://github.com/YOUR_USERNAME/PGK-Wallet.git
cd PGK-Wallet
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

فایل `.env` را بر اساس `.env.example` ایجاد کنید.

```env
BOT_TOKEN=YOUR_BOT_TOKEN
ADMIN_ID=YOUR_TELEGRAM_ID
DATABASE_URL=YOUR_DATABASE_URL
```

### 4. Run

```bash
python main.py
```

---

# ⚙️ Configuration

قبل از اجرای ربات، تنظیمات موردنیاز را در Environment Variables وارد کنید.

هر Instance باید از Credentialهای خودش استفاده کند.

---

# 🧪 Development

برای توسعه پروژه:

```bash
git clone https://github.com/YOUR_USERNAME/PGK-Wallet.git
cd PGK-Wallet

python -m venv venv
```

فعال‌سازی محیط مجازی در Windows:

```powershell
venv\Scripts\activate
```

سپس:

```bash
pip install -r requirements.txt
```

---

# 📌 Roadmap

برنامه توسعه پروژه می‌تواند شامل موارد زیر باشد:

* [ ] Multi-Currency Wallet
* [ ] Multi-Network Support
* [ ] Advanced Payment System
* [ ] QR Code Payments
* [ ] Payment Links
* [ ] Advanced Admin Dashboard
* [ ] Enhanced Security
* [ ] Automatic Blockchain Monitoring
* [ ] Detailed Analytics
* [ ] Docker Deployment
* [ ] Web Dashboard
* [ ] API
* [ ] More Languages

---

# 🤝 Contributing

اگر می‌خواهید در توسعه پروژه مشارکت کنید:

```bash
git fork
git clone
git checkout -b feature/your-feature
```

تغییرات خود را انجام دهید و سپس Pull Request ارسال کنید.

---

# ⚠️ Disclaimer

PGK Wallet یک پروژه نرم‌افزاری Self-Hosted است.

قبل از استفاده با دارایی واقعی، کد، تنظیمات امنیتی، وابستگی‌ها، مدیریت کلیدها و نحوه اتصال به شبکه‌های بلاکچین را به‌طور کامل بررسی و آزمایش کنید.

**هیچ‌گاه Seed Phrase یا Private Key را در GitHub، Telegram، فایل‌های عمومی یا Repository عمومی قرار ندهید.**

---

# 📄 License

This project is distributed under the license specified in this repository.

---

# 🇮🇷 فارسی

## PGK Wallet چیست؟

PGK Wallet یک ربات کیف پول رمزارزی برای Telegram است که برای مدیریت کیف پول، دریافت و ارسال دارایی، پرداخت، Invoice و مدیریت تراکنش‌ها طراحی شده است.

معماری پروژه به شکل **Self-Hosted** است؛ بنابراین کاربران می‌توانند سورس پروژه را دریافت کرده و Instance مستقل خودشان را راه‌اندازی کنند.

### امکانات

* 💼 ساخت و مدیریت کیف پول
* 💰 مشاهده موجودی
* 📥 دریافت
* 📤 ارسال
* 🔗 آدرس کیف پول
* 💳 پرداخت
* 🧾 Invoice
* 📊 تراکنش‌ها
* 🔔 اعلان‌ها
* 👑 پنل مدیریت
* 🗄 Database
* 🔐 قابلیت‌های امنیتی
* 🌐 قابلیت توسعه برای چند زبان و چند شبکه

---

# 🇬🇧 English

## What is PGK Wallet?

PGK Wallet is a Telegram-based cryptocurrency wallet bot designed for wallet management, receiving and sending assets, payments, invoices, and transaction management.

The project follows a **Self-Hosted** architecture, allowing users to deploy and operate their own independent instance.

### Features

* 💼 Wallet creation and management
* 💰 Balance tracking
* 📥 Receive
* 📤 Send
* 🔗 Wallet addresses
* 💳 Payments
* 🧾 Invoices
* 📊 Transaction history
* 🔔 Notifications
* 👑 Admin dashboard
* 🗄 Database
* 🔐 Security-focused architecture
* 🌐 Extensible multilingual architecture

---

# 🇷🇺 Русский

## Что такое PGK Wallet?

PGK Wallet — это Telegram-бот криптовалютного кошелька, предназначенный для управления кошельками, получения и отправки активов, создания платежей, счетов и отслеживания транзакций.

Проект использует архитектуру **Self-Hosted**, поэтому каждый пользователь может самостоятельно развернуть собственный экземпляр системы.

### Возможности

* 💼 Создание и управление кошельком
* 💰 Просмотр баланса
* 📥 Получение средств
* 📤 Отправка средств
* 🔗 Адрес кошелька
* 💳 Платежи
* 🧾 Счета / Invoice
* 📊 История транзакций
* 🔔 Уведомления
* 👑 Панель администратора
* 🗄 База данных
* 🔐 Безопасная архитектура
* 🌐 Поддержка расширения на несколько языков и сетей

---

# 🇨🇳 中文

## 什么是 PGK Wallet？

PGK Wallet 是一个基于 Telegram 的加密货币钱包机器人，用于管理钱包、接收和发送资产、创建支付请求、Invoice 以及管理交易记录。

项目采用 **Self-Hosted（自主部署）** 架构，用户可以下载源代码并独立部署属于自己的实例。

### 功能

* 💼 创建和管理钱包
* 💰 查看余额
* 📥 接收资产
* 📤 发送资产
* 🔗 钱包地址
* 💳 支付系统
* 🧾 Invoice
* 📊 交易记录
* 🔔 通知系统
* 👑 管理员面板
* 🗄 数据库
* 🔐 安全架构
* 🌐 可扩展的多语言及多网络支持

---

# 💜 PGK Wallet

**Private • Self-Hosted • Telegram-Based • Extensible**

Built for developers who want to run their own Telegram-based cryptocurrency wallet infrastructure.

⭐ Star the project if you find it useful.

🐛 Found a bug? Open an Issue.

💡 Have an idea? Start a Discussion or Pull Request.
