<div align="center">

# 💜 PGK Wallet

### 🔐 Self-Hosted Telegram Cryptocurrency Wallet

**A modular cryptocurrency wallet system built for Telegram**

<br>

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge\&logo=python\&logoColor=white)](https://www.python.org/)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?style=for-the-badge\&logo=telegram\&logoColor=white)](https://telegram.org/)
[![Self Hosted](https://img.shields.io/badge/Self--Hosted-Yes-2EA44F?style=for-the-badge)](https://github.com/)
[![License](https://img.shields.io/badge/License-See%20Repository-6E40C9?style=for-the-badge)](LICENSE)

<br>

**Private • Self-Hosted • Modular • Extensible**

<br>

### 🌐 Select Your Language

🇮🇷 **[فارسی](#-فارسی)**   •  
🇬🇧 **[English](#-english)**   •  
🇷🇺 **[Русский](#-русский)**   •  
🇨🇳 **[中文](#-中文)**

</div>

---

# 🇮🇷 فارسی

## 💜 PGK Wallet چیست؟

**PGK Wallet** یک سیستم کیف پول رمزارزی مبتنی بر **Telegram Bot** است که با هدف ایجاد یک زیرساخت ساده، ماژولار، قابل توسعه و **Self-Hosted** برای مدیریت کیف پول و پرداخت‌های رمزارزی ساخته شده است.

هدف پروژه این است که هر توسعه‌دهنده بتواند سورس کد را دریافت کند، تنظیمات خودش را وارد کند و **نسخه مستقل PGK Wallet خودش** را روی سرور یا سیستم شخصی اجرا کند.

> ⚠️ PGK Wallet یک پروژه نرم‌افزاری Self-Hosted است و استفاده از آن با دارایی واقعی نیازمند بررسی کامل کد، شبکه، کلیدهای خصوصی و تنظیمات امنیتی است.

---

## ✨ امکانات اصلی

### 👤 سیستم کاربران

PGK Wallet برای مدیریت کاربران Telegram طراحی شده است.

* 👤 مدیریت حساب کاربری
* 🆔 اتصال حساب به Telegram ID
* 💼 مدیریت Wallet
* 💰 مشاهده موجودی
* 📊 مشاهده فعالیت‌ها
* 🔔 دریافت اعلان‌ها

---

## 💼 Wallet

بخش **Wallet** هسته اصلی پروژه است.

ساختار کلی:

```text
                 💼 WALLET
                    │
       ┌────────────┼────────────┐
       ▼            ▼            ▼
    💰 Balance    📥 Receive    📤 Send
       │            │            │
       └────────────┼────────────┘
                    ▼
              📊 Transactions
```

### 💰 Balance

کاربر می‌تواند موجودی کیف پول خود را مشاهده کند.

### 📥 Receive

برای دریافت دارایی، کاربر می‌تواند اطلاعات موردنیاز کیف پول خود را دریافت کند.

### 📤 Send

سیستم می‌تواند فرآیند ارسال دارایی را مدیریت کند؛ اجرای واقعی تراکنش به شبکه، ارز و تنظیمات مربوط به Instance بستگی دارد.

### 📊 Transactions

تراکنش‌های مرتبط با کیف پول قابل مدیریت و پیگیری هستند.

---

## 💳 Payment System

سیستم پرداخت برای ایجاد یک جریان پرداخت ساختاریافته طراحی شده است.

```text
👤 Customer
      │
      ▼
🤖 Telegram Bot
      │
      ▼
🧾 Create Invoice
      │
      ▼
💳 Payment Request
      │
      ▼
💰 Blockchain Transaction
      │
      ▼
🔎 Verification
      │
      ▼
✅ Payment Confirmed
      │
      ▼
🔔 Notification
```

این معماری می‌تواند برای مواردی مانند:

* فروش محصولات
* خدمات آنلاین
* دریافت هزینه
* Donation
* پرداخت‌های داخل Telegram
* سیستم‌های تجاری

توسعه داده شود.

---

## 🧾 Invoice

Invoice برای ایجاد یک درخواست پرداخت مشخص استفاده می‌شود.

نمونه ساختار:

```text
┌─────────────────────────────┐
│        🧾 INVOICE           │
├─────────────────────────────┤
│ Amount:      25 USDT        │
│ Status:      Pending        │
│ Network:     Selected       │
│ Payment:     Required       │
└─────────────────────────────┘
```

پس از پرداخت، سیستم می‌تواند وضعیت Invoice را بررسی و به‌روزرسانی کند.

---

## 👑 Admin Panel

PGK Wallet دارای ساختار مدیریتی برای کنترل Instance است.

```text
👑 ADMIN PANEL

├── 👥 Users
├── 💼 Wallets
├── 💳 Payments
├── 🧾 Invoices
├── 📊 Statistics
├── 🔔 Notifications
├── 🗄 Database
└── ⚙️ Settings
```

پنل مدیریت می‌تواند برای مشاهده و مدیریت اطلاعات اصلی سیستم استفاده شود.

---

## 🔔 Notification System

سیستم اعلان برای اطلاع‌رسانی رویدادهای مهم طراحی شده است.

برای مثال:

```text
💰 Payment Received

Amount: 25 USDT
Status: Confirmed ✅

Transaction:
xxxxxxxxxxxxxxxx
```

---

## 🗄 Database

اطلاعات موردنیاز سیستم در Database مدیریت می‌شوند.

از جمله:

* 👤 Users
* 💼 Wallets
* 💳 Payments
* 🧾 Invoices
* 📊 Transactions
* ⚙️ Settings

---

## 🔐 Security

امنیت برای یک Wallet بسیار مهم است.

اطلاعات حساس نباید در Repository عمومی قرار بگیرند.

### ❌ هرگز این موارد را روی GitHub قرار ندهید:

```text
BOT_TOKEN
PRIVATE_KEY
SEED_PHRASE
MNEMONIC
API_KEY
DATABASE_PASSWORD
ADMIN_SECRET
```

اطلاعات حساس باید از طریق Environment Variables یا روش امن مشابه مدیریت شوند.

نمونه:

```env
BOT_TOKEN=YOUR_BOT_TOKEN
ADMIN_ID=YOUR_TELEGRAM_ID
DATABASE_URL=YOUR_DATABASE_URL
```

---

## 🏠 Self-Hosted Architecture

یکی از ویژگی‌های اصلی PGK Wallet امکان اجرای مستقل آن است.

```text
                    PGK WALLET
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
       Server A      Server B      Server C
          │             │             │
        Bot A         Bot B         Bot C
          │             │             │
       Database A   Database B   Database C
```

هر شخص می‌تواند Instance خودش را داشته باشد.

---

## 🧩 Architecture

معماری کلی پروژه به‌صورت ماژولار طراحی شده است:

```text
                    ┌──────────────┐
                    │   Telegram   │
                    │     Bot      │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   Handlers   │
                    └──────┬───────┘
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
       ┌──────────┐  ┌──────────┐  ┌──────────┐
       │  Wallet  │  │ Payment  │  │ Invoice  │
       │ Service  │  │ Service  │  │ Service  │
       └────┬─────┘  └────┬─────┘  └────┬─────┘
            │             │             │
            └─────────────┼─────────────┘
                          ▼
                   ┌──────────────┐
                   │   Database   │
                   └──────────────┘
```

---

## 📁 ساختار پروژه

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

## 🛠 تکنولوژی‌ها

* 🐍 Python
* 🤖 Telegram Bot API
* 🗄 Database
* 💼 Wallet Services
* 💳 Payment Services
* 🧾 Invoice Services
* 🔐 Security Services
* 🔔 Notification Services

---

## 🚀 نصب

### 1. دریافت پروژه

```bash
git clone https://github.com/YOUR_USERNAME/PGK-Wallet.git
cd PGK-Wallet
```

### 2. نصب وابستگی‌ها

```bash
pip install -r requirements.txt
```

### 3. تنظیم Environment

فایل `.env` را بر اساس `.env.example` ایجاد و تنظیم کنید.

```env
BOT_TOKEN=YOUR_BOT_TOKEN
ADMIN_ID=YOUR_TELEGRAM_ID
DATABASE_URL=YOUR_DATABASE_URL
```

### 4. اجرای پروژه

```bash
python main.py
```

---

## 🗺 Roadmap

* [ ] Multi-Currency Wallet
* [ ] Multi-Network Support
* [ ] QR Payments
* [ ] Payment Links
* [ ] Advanced Invoice System
* [ ] Advanced Admin Panel
* [ ] Blockchain Monitoring
* [ ] Advanced Analytics
* [ ] Docker Deployment
* [ ] Web Dashboard
* [ ] Public API
* [ ] More Languages

---

## 🤝 مشارکت

Pull Request و پیشنهادهای فنی برای توسعه پروژه قابل بررسی هستند.

```bash
git fork
git clone
git checkout -b feature/your-feature
```

پس از اعمال تغییرات، Pull Request ایجاد کنید.

---

## ⚠️ هشدار امنیتی

قبل از استفاده از PGK Wallet با دارایی واقعی، تمام بخش‌های مربوط به:

* Private Key
* Seed
* Transaction Signing
* Blockchain RPC
* Network Configuration
* Database Security
* Access Control

را به‌صورت کامل بررسی و در محیط آزمایشی تست کنید.

**هیچ Seed Phrase یا Private Key را در GitHub یا Telegram ارسال نکنید.**

---

[⬆ بازگشت به انتخاب زبان](#-select-your-language)

---

# 🇬🇧 English

## 💜 What is PGK Wallet?

**PGK Wallet** is a Telegram-based cryptocurrency wallet system designed to provide a simple, modular, extensible, and **Self-Hosted** infrastructure for wallet management and cryptocurrency payments.

The project allows developers to obtain the source code, configure their own environment, and deploy an independent PGK Wallet instance on their own server or computer.

> ⚠️ PGK Wallet is a self-hosted software project. Before using real assets, thoroughly review and test the wallet implementation, blockchain integration, private-key handling, and security configuration.

---

## ✨ Core Features

### 👤 User System

* 👤 User management
* 🆔 Telegram ID integration
* 💼 Wallet management
* 💰 Balance tracking
* 📊 Activity tracking
* 🔔 Notifications

---

## 💼 Wallet

The **Wallet** is the core component of PGK Wallet.

```text
                 💼 WALLET
                    │
       ┌────────────┼────────────┐
       ▼            ▼            ▼
    💰 Balance    📥 Receive    📤 Send
       │            │            │
       └────────────┼────────────┘
                    ▼
              📊 Transactions
```

### 💰 Balance

Users can view their wallet balance.

### 📥 Receive

Users can access the information required to receive assets into their wallet.

### 📤 Send

The system can manage the asset-sending workflow. Actual transaction execution depends on the configured blockchain, asset, and network.

### 📊 Transactions

Wallet-related transactions can be tracked and managed.

---

## 💳 Payment System

The payment system is designed around a structured payment flow.

```text
👤 Customer
      │
      ▼
🤖 Telegram Bot
      │
      ▼
🧾 Create Invoice
      │
      ▼
💳 Payment Request
      │
      ▼
💰 Blockchain Transaction
      │
      ▼
🔎 Verification
      │
      ▼
✅ Payment Confirmed
      │
      ▼
🔔 Notification
```

Potential use cases include:

* Online products
* Digital services
* Donations
* Telegram-based payments
* Business payment systems

---

## 🧾 Invoice System

Invoices provide a structured way to request a specific payment.

```text
┌─────────────────────────────┐
│        🧾 INVOICE           │
├─────────────────────────────┤
│ Amount:      25 USDT        │
│ Status:      Pending        │
│ Network:     Selected       │
│ Payment:     Required       │
└─────────────────────────────┘
```

After payment, the system can verify and update the invoice status.

---

## 👑 Admin Panel

The project includes an administrative architecture for managing an instance.

```text
👑 ADMIN PANEL

├── 👥 Users
├── 💼 Wallets
├── 💳 Payments
├── 🧾 Invoices
├── 📊 Statistics
├── 🔔 Notifications
├── 🗄 Database
└── ⚙️ Settings
```

---

## 🔔 Notifications

Important wallet and payment events can be communicated through Telegram notifications.

Example:

```text
💰 Payment Received

Amount: 25 USDT
Status: Confirmed ✅

Transaction:
xxxxxxxxxxxxxxxx
```

---

## 🗄 Database

The database can manage core application data including:

* Users
* Wallets
* Payments
* Invoices
* Transactions
* Settings

---

## 🔐 Security

Security is a critical part of any cryptocurrency wallet system.

Never commit sensitive credentials to a public repository.

### ❌ Never publish:

```text
BOT_TOKEN
PRIVATE_KEY
SEED_PHRASE
MNEMONIC
API_KEY
DATABASE_PASSWORD
ADMIN_SECRET
```

Use environment variables or an appropriate secret-management solution.

```env
BOT_TOKEN=YOUR_BOT_TOKEN
ADMIN_ID=YOUR_TELEGRAM_ID
DATABASE_URL=YOUR_DATABASE_URL
```

---

## 🏠 Self-Hosted

PGK Wallet is designed so users can operate independent instances.

```text
                    PGK WALLET
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
       Server A      Server B      Server C
          │             │             │
        Bot A         Bot B         Bot C
          │             │             │
       Database A   Database B   Database C
```

---

## 🧩 Architecture

```text
                    ┌──────────────┐
                    │   Telegram   │
                    │     Bot      │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   Handlers   │
                    └──────┬───────┘
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
       ┌──────────┐  ┌──────────┐  ┌──────────┐
       │  Wallet  │  │ Payment  │  │ Invoice  │
       │ Service  │  │ Service  │  │ Service  │
       └────┬─────┘  └────┬─────┘  └────┬─────┘
            │             │             │
            └─────────────┼─────────────┘
                          ▼
                   ┌──────────────┐
                   │   Database   │
                   └──────────────┘
```

---

## 🚀 Installation

```bash
git clone https://github.com/YOUR_USERNAME/PGK-Wallet.git
cd PGK-Wallet
pip install -r requirements.txt
```

Configure your environment:

```env
BOT_TOKEN=YOUR_BOT_TOKEN
ADMIN_ID=YOUR_TELEGRAM_ID
DATABASE_URL=YOUR_DATABASE_URL
```

Run:

```bash
python main.py
```

---

## 🗺 Roadmap

* [ ] Multi-Currency Wallet
* [ ] Multi-Network Support
* [ ] QR Payments
* [ ] Payment Links
* [ ] Advanced Invoice System
* [ ] Advanced Admin Panel
* [ ] Blockchain Monitoring
* [ ] Analytics
* [ ] Docker Deployment
* [ ] Web Dashboard
* [ ] Public API
* [ ] More Languages

---

[⬆ Back to language selection](#-select-your-language)

---

# 🇷🇺 Русский

## 💜 Что такое PGK Wallet?

**PGK Wallet** — это криптовалютный кошелёк в формате Telegram-бота, созданный как простая, модульная, расширяемая и **Self-Hosted** система для управления кошельками и криптовалютными платежами.

Разработчик может получить исходный код, настроить собственную конфигурацию и запустить независимый экземпляр PGK Wallet на своём сервере или компьютере.

> ⚠️ Перед использованием реальных активов необходимо тщательно проверить код кошелька, работу с блокчейном, приватными ключами и настройки безопасности.

---

## ✨ Основные возможности

### 👤 Пользователи

* 👤 Управление пользователями
* 🆔 Telegram ID
* 💼 Управление кошельком
* 💰 Баланс
* 📊 История активности
* 🔔 Уведомления

---

## 💼 Кошелёк

**Wallet** является основной частью системы.

```text
                 💼 WALLET
                    │
       ┌────────────┼────────────┐
       ▼            ▼            ▼
    💰 Баланс    📥 Получить   📤 Отправить
       │            │            │
       └────────────┼────────────┘
                    ▼
              📊 Транзакции
```

Кошелёк предназначен для управления балансом, получения и отправки активов и отслеживания операций.

---

## 💳 Платежная система

```text
👤 Клиент
    │
    ▼
🤖 Telegram Bot
    │
    ▼
🧾 Invoice
    │
    ▼
💳 Запрос платежа
    │
    ▼
💰 Blockchain
    │
    ▼
🔎 Проверка
    │
    ▼
✅ Подтверждение
    │
    ▼
🔔 Уведомление
```

Система может использоваться для онлайн-сервисов, товаров, пожертвований и других платежных сценариев.

---

## 🧾 Invoice

Invoice позволяет создавать структурированные запросы на оплату.

```text
┌─────────────────────────────┐
│        🧾 INVOICE           │
├─────────────────────────────┤
│ Amount:      25 USDT        │
│ Status:      Pending        │
│ Network:     Selected       │
└─────────────────────────────┘
```

---

## 👑 Панель администратора

```text
👑 ADMIN PANEL

├── 👥 Users
├── 💼 Wallets
├── 💳 Payments
├── 🧾 Invoices
├── 📊 Statistics
├── 🔔 Notifications
├── 🗄 Database
└── ⚙️ Settings
```

---

## 🔐 Безопасность

Никогда не публикуйте:

```text
BOT_TOKEN
PRIVATE_KEY
SEED_PHRASE
MNEMONIC
API_KEY
DATABASE_PASSWORD
ADMIN_SECRET
```

Используйте переменные окружения или систему управления секретами.

---

## 🏠 Self-Hosted

Каждый пользователь может развернуть собственный экземпляр:

```text
PGK Wallet
    │
    ├── Server A → Bot A → Database A
    │
    ├── Server B → Bot B → Database B
    │
    └── Server C → Bot C → Database C
```

---

## 🚀 Установка

```bash
git clone https://github.com/YOUR_USERNAME/PGK-Wallet.git
cd PGK-Wallet
pip install -r requirements.txt
python main.py
```

---

## 🗺 План развития

* [ ] Несколько валют
* [ ] Несколько сетей
* [ ] QR-платежи
* [ ] Payment Links
* [ ] Расширенная система Invoice
* [ ] Расширенная админ-панель
* [ ] Мониторинг блокчейна
* [ ] Аналитика
* [ ] Docker
* [ ] Web Dashboard
* [ ] Public API
* [ ] Дополнительные языки

---

[⬆ Вернуться к выбору языка](#-select-your-language)

---

# 🇨🇳 中文

## 💜 什么是 PGK Wallet？

**PGK Wallet** 是一个基于 **Telegram Bot** 的加密货币钱包系统，旨在提供一个简单、模块化、可扩展并支持 **Self-Hosted（自主部署）** 的钱包和加密货币支付基础设施。

开发者可以获取源代码，配置自己的环境，并在自己的服务器或计算机上运行独立的 PGK Wallet 实例。

> ⚠️ 在使用真实资产之前，请完整检查并测试钱包代码、区块链连接、私钥管理以及安全配置。

---

## ✨ 主要功能

### 👤 用户系统

* 👤 用户管理
* 🆔 Telegram ID
* 💼 钱包管理
* 💰 余额查看
* 📊 活动记录
* 🔔 通知

---

## 💼 Wallet 钱包

**Wallet** 是 PGK Wallet 的核心部分。

```text
                 💼 WALLET
                    │
       ┌────────────┼────────────┐
       ▼            ▼            ▼
    💰 余额       📥 接收       📤 发送
       │            │            │
       └────────────┼────────────┘
                    ▼
              📊 交易记录
```

钱包用于管理余额、接收和发送资产以及跟踪相关交易。

---

## 💳 支付系统

```text
👤 客户
   │
   ▼
🤖 Telegram Bot
   │
   ▼
🧾 创建 Invoice
   │
   ▼
💳 支付请求
   │
   ▼
💰 区块链交易
   │
   ▼
🔎 交易验证
   │
   ▼
✅ 支付确认
   │
   ▼
🔔 通知
```

该系统可以用于在线服务、数字产品、Donation 以及其他支付场景。

---

## 🧾 Invoice

Invoice 用于创建结构化的支付请求。

```text
┌─────────────────────────────┐
│        🧾 INVOICE           │
├─────────────────────────────┤
│ Amount:      25 USDT        │
│ Status:      Pending        │
│ Network:     Selected       │
└─────────────────────────────┘
```

---

## 👑 管理员面板

```text
👑 ADMIN PANEL

├── 👥 Users
├── 💼 Wallets
├── 💳 Payments
├── 🧾 Invoices
├── 📊 Statistics
├── 🔔 Notifications
├── 🗄 Database
└── ⚙️ Settings
```

---

## 🔐 安全

请勿将以下敏感信息提交到公开 GitHub 仓库：

```text
BOT_TOKEN
PRIVATE_KEY
SEED_PHRASE
MNEMONIC
API_KEY
DATABASE_PASSWORD
ADMIN_SECRET
```

建议使用 Environment Variables 或专业的 Secret Management 系统管理敏感信息。

---

## 🏠 Self-Hosted 自主部署

每个用户都可以运行自己的 PGK Wallet 实例：

```text
PGK Wallet
    │
    ├── Server A → Bot A → Database A
    │
    ├── Server B → Bot B → Database B
    │
    └── Server C → Bot C → Database C
```

---

## 🚀 安装

```bash
git clone https://github.com/YOUR_USERNAME/PGK-Wallet.git
cd PGK-Wallet
pip install -r requirements.txt
python main.py
```

配置环境变量：

```env
BOT_TOKEN=YOUR_BOT_TOKEN
ADMIN_ID=YOUR_TELEGRAM_ID
DATABASE_URL=YOUR_DATABASE_URL
```

然后运行：

```bash
python main.py
```

---

## 🗺 开发路线图

* [ ] 多币种钱包
* [ ] 多网络支持
* [ ] QR 支付
* [ ] Payment Links
* [ ] 高级 Invoice 系统
* [ ] 高级管理员面板
* [ ] 区块链监控
* [ ] 数据分析
* [ ] Docker 部署
* [ ] Web Dashboard
* [ ] Public API
* [ ] 更多语言

---

[⬆ 返回语言选择](#-select-your-language)

---

<div align="center">

# 💜 PGK Wallet

### Private • Self-Hosted • Telegram-Based

**Built for developers who want to run their own wallet infrastructure.**

⭐ If you find PGK Wallet useful, consider giving the repository a Star.

</div>
