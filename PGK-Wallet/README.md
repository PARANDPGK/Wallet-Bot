# PGK Wallet — ربات تلگرامی درگاه پرداخت رمزارزی

یک ربات تلگرامی برای صدور فاکتور و پذیرش پرداخت‌های رمزارزی (BTC, ETH, DAI, TRX, TON) با
**تأیید مستقل و واقعی روی بلاک‌چین**، به‌علاوه گردش‌کار پرداخت ریالی با بررسی دستی ادمین.

## ⚠️ هیچ پرداختی صرفاً بر اساس اسکرین‌شات یا ادعای کاربر تأیید نمی‌شود
هسته امنیتی سیستم در `app/services/payment_service.py` قرار دارد: هر فاکتور فقط زمانی
`PAID` می‌شود که تراکنش آن به‌صورت مستقل از طریق API بلاک‌چین (Blockstream، Etherscan،
Tronscan، TonCenter) پیدا و با آدرس/مبلغ/تعداد تأییدیه فاکتور مطابقت داده شده باشد.

---

## نصب و راه‌اندازی

### ۱. نصب وابستگی‌ها
```bash
python3 -m venv venv
source venv/bin/activate   # ویندوز: venv\Scripts\activate
pip install -r requirements.txt
```

### ۲. ساخت فایل `.env`
```bash
cp .env.example .env
```
سپس مقادیر زیر را در `.env` تکمیل کنید:

| متغیر | توضیح |
|---|---|
| `BOT_TOKEN` | توکن ربات از [@BotFather](https://t.me/BotFather) |
| `BOT_USERNAME` | یوزرنیم ربات (بدون @) — برای ساخت لینک پرداخت لازم است |
| `ADMIN_TELEGRAM_ID` | شناسه عددی تلگرام شما (از [@userinfobot](https://t.me/userinfobot) بگیرید) |
| `ADMIN_PASSWORD_HASH` | هش رمز عبور ادمین (دستور زیر) |
| `ENCRYPTION_KEY` | کلید تصادفی (دستور زیر) |
| `ETHERSCAN_API_KEY` | کلید رایگان از https://etherscan.io/apis (برای شبکه اتریوم و DAI) |
| `TON_API_KEY` | اختیاری، از https://toncenter.com برای افزایش نرخ درخواست |

**ساخت هش رمز عبور ادمین:**
```bash
python -c "from argon2 import PasswordHasher; print(PasswordHasher().hash('رمز-قوی-من'))"
```

**ساخت کلید رمزنگاری:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### ۳. اجرای ربات
```bash
python main.py
```
دیتابیس SQLite و پوشه‌های `data/`, `logs/`, `receipts/` به‌صورت خودکار ساخته می‌شوند.

### ۴. ورود به پنل ادمین
در تلگرام به ربات دستور `/admin` را بفرستید و رمز عبوری که هش آن را در `.env` گذاشتید وارد کنید.
ورود‌های ناموفق متوالی باعث قفل موقت (Rate Limiting) می‌شود.

### ۵. افزودن اولین کیف‌پول
از منوی ادمین گزینه «👛 کیف‌پول‌ها» یا دستور `/addwallet` را بزنید و آدرس عمومی کیف‌پول خود
(هیچ‌وقت کلید خصوصی) را برای هر ارز/شبکه ثبت کنید.

---

## ساختار پروژه
```
PGK-Wallet/
├── main.py                  # نقطه ورود
├── backup.py                 # بکاپ‌گیری از دیتابیس و فیش‌ها
├── config.py                  # تنظیمات (از .env خوانده می‌شود)
├── app/
│   ├── bot/
│   │   ├── handlers/           # هندلرهای مشتری و ادمین
│   │   ├── keyboards/          # کیبوردهای Reply/Inline
│   │   ├── states/             # استیت‌های Conversation
│   │   └── jobs.py             # پایش خودکار پرداخت‌ها (Polling)
│   ├── database/
│   │   ├── models.py           # مدل‌های SQLAlchemy
│   │   ├── database.py         # اتصال و session
│   │   └── repositories/       # لایه دسترسی به داده
│   ├── blockchain/             # پرووایدرهای BTC/ETH/TRON/TON
│   ├── services/                # منطق تجاری (احراز هویت، فاکتور، پرداخت، ...)
│   ├── localization/            # رشته‌های فارسی/انگلیسی
│   └── utils/                    # امنیت، فرمت، QR، لاگ
└── tests/                        # تست‌های pytest
```

## اجرای تست‌ها
```bash
pytest
```
> تست‌ها از یک دیتابیس SQLite درون‌حافظه‌ای استفاده می‌کنند و به شبکه نیاز ندارند.

## نکات امنیتی
- رمز عبور ادمین هرگز به‌صورت متن ساده ذخیره نمی‌شود (Argon2id).
- توکن‌های فاکتور و نشست با `secrets.token_urlsafe` (رمزنگاری‌ایمن) تولید می‌شوند.
- هر تراکنش بلاک‌چین فقط یک‌بار می‌تواند برای تأیید یک فاکتور استفاده شود (جلوگیری از استفاده مجدد).
- فایل‌های آپلودی (فیش واریزی) از نظر پسوند، نوع MIME و حجم بررسی می‌شوند و نام‌گذاری امن دارند.
- تمام رویدادهای امنیتی (ورود موفق/ناموفق، خروج) در جدول `audit_logs` ثبت می‌شوند.
- **هیچ کلید خصوصی کیف‌پولی در این پروژه ذخیره یا پردازش نمی‌شود** — فقط آدرس عمومی.

## محدودیت‌های شناخته‌شده (Known Limitations)
- این پروژه در محیطی بدون دسترسی به اینترنت ساخته شده، بنابراین وابستگی‌ها نصب و اجرای
  زنده (End-to-End) آزمایش نشده‌اند. پیش از استفاده در محیط Production حتماً:
  - `pip install -r requirements.txt` را اجرا و نسخه‌های واقعی موجود را بررسی کنید.
  - ربات را در محیط تست (Testnet/Sandbox) امتحان کنید.
- شبکه TON در API رایگان TonCenter امکان جست‌وجوی مستقیم تراکنش با هش را ندارد؛ به‌جای آن
  از فهرست تراکنش‌های آدرس استفاده می‌شود (`get_transactions_for_address`).
- برای توکن‌های ERC20 فعلاً فقط DAI پیاده‌سازی شده؛ افزودن توکن جدید یعنی افزودن یک
  ورودی به `ERC20_CONTRACTS` در `app/blockchain/ethereum.py`.

---

## English Summary

PGK Wallet is a Telegram bot for issuing invoices and accepting crypto payments
(BTC, ETH, DAI, TRX, TON) with **independent on-chain verification** — no payment
is ever marked PAID based on a screenshot or user claim alone — plus a fiat (IRR)
payment workflow with manual admin review.

1. `pip install -r requirements.txt`
2. `cp .env.example .env` and fill in `BOT_TOKEN`, `ADMIN_TELEGRAM_ID`,
   `ADMIN_PASSWORD_HASH` (generate with the Argon2 command above), and
   `ENCRYPTION_KEY`.
3. `python main.py`
4. Send `/admin` to the bot and log in with your password.
5. Add a wallet via `/addwallet` (public address only — never a private key).

Run tests with `pytest` (uses an in-memory SQLite DB, no network required).

**This project was built in a sandbox with no internet access**, so dependencies
could not be installed or run end-to-end here. Please `pip install` and test
against a testnet before production use.
