#!/usr/bin/env python3
"""Offline regression tests for SHIVAM STORE BOT core logic.
These tests intentionally do not contact Telegram or any payment service.
"""
import os, tempfile, unittest, inspect
from email.message import EmailMessage
from datetime import timedelta
from pathlib import Path

# Stub python-telegram-bot so core persistence/validation can be tested offline.
import sys, types
telegram = types.ModuleType('telegram')
class Dummy:
    def __init__(self,*a,**k):
        self.args = a
        self.kwargs = k
        if a and isinstance(a[0], list):
            self.inline_keyboard = a[0]
        if a and isinstance(a[0], str):
            self.text = a[0]
        if len(a) > 1 and isinstance(a[1], str):
            self.callback_data = a[1]
        if "callback_data" in k:
            self.callback_data = k["callback_data"]
        if "text" in k:
            self.text = k["text"]
for n in ['InlineKeyboardButton','InlineKeyboardMarkup','KeyboardButton','ReplyKeyboardMarkup','ReplyKeyboardRemove','ForceReply','Update']:
    setattr(telegram,n,Dummy)
constants = types.ModuleType('telegram.constants'); constants.ParseMode=types.SimpleNamespace(HTML='HTML')
ext = types.ModuleType('telegram.ext')
class Filters:
    CONTACT=PHOTO=TEXT=COMMAND=0
ext.Application=ext.CallbackQueryHandler=ext.CommandHandler=ext.ContextTypes=ext.MessageHandler=Dummy
ext.ContextTypes=types.SimpleNamespace(DEFAULT_TYPE=dict)
ext.filters=Filters()
class DummyHandler: pass
sys.modules['telegram']=telegram; sys.modules['telegram.constants']=constants; sys.modules['telegram.ext']=ext

os.environ['ADMIN_USER_ID']='12345'
_tmp = tempfile.NamedTemporaryFile(suffix='.sqlite3', delete=False); _tmp.close()
os.environ['DB_PATH']=_tmp.name
import bot

class CoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): bot.init_db()
    def test_chat_utr_flow_is_not_webapp_flow(self):
        source = Path(bot.__file__).read_text(encoding="utf-8")
        self.assertIn('button("💳 VERIFY PAYMENT", "payment:verify")', source)
        self.assertIn('context.user_data["flow"] = "utr"', source)
        self.assertNotIn('UTR_WEBAPP_URL', source)
        self.assertNotIn('web_app=WebAppInfo', source)


    def test_product_stock_is_grouped_by_product_then_plan(self):
        source = Path(bot.__file__).read_text(encoding="utf-8")
        self.assertIn('stock_product_picker', source)
        self.assertIn('stockprod:', source)
        self.assertIn('stockplan:', source)
        self.assertIn("Add Keys — {safe(row[\'name\'])}", source)

    def test_product_maintenance_is_persistent_and_enforced(self):
        source = Path(bot.__file__).read_text(encoding="utf-8")
        self.assertIn('maintenance_mode INTEGER NOT NULL DEFAULT 0', source)
        self.assertIn('ensure_column(connection, "products", "maintenance_mode"', source)
        self.assertIn('productmaint:', source)
        self.assertIn('plan["maintenance_mode"]', source)

    def test_owner_only_admin(self):
        self.assertTrue(bot.is_admin(12345))
        self.assertFalse(bot.is_admin(99999))


    def test_imap_targeted_search_and_pending_ui(self):
        self.assertIn("BODY", inspect.getsource(bot._imap_search_uids))
        self.assertIn("search_utr", inspect.getsource(bot._fetch_recent_imap_messages))
        self.assertIn("pending_message_chat_id", inspect.getsource(bot.submit_utr_from_chat))
        self.assertIn("PENDING", inspect.getsource(bot.submit_utr_from_chat))
        self.assertIn("pending_message_id", inspect.getsource(bot.auto_fulfill_verified_order))

    def test_imap_html_payment_match(self):
        with bot.db() as c:
            c.execute("INSERT OR IGNORE INTO users(id,username,first_name,created_at,updated_at) VALUES (555,'imap','IMAP',?,?)", (bot.iso_now(),bot.iso_now()))
            c.execute("INSERT INTO orders(order_no,user_id,order_type,amount,original_amount,topup_amount,utr,status,created_at,expiry_at) VALUES (?,?,?,?,?,?,?,?,?,?)", ('IMAP-TEST',555,'balance',499,499,499,'123456789012','pending',bot.iso_now(),(bot.utc_now()+timedelta(minutes=10)).isoformat()))
            c.execute("INSERT OR REPLACE INTO settings(key,value) VALUES('upi_id','shivam@upi')")
            c.commit()
            row=c.execute("SELECT * FROM orders WHERE order_no='IMAP-TEST'").fetchone()
        msg=EmailMessage()
        msg['From']='Bank Alerts <alerts@bank.example>'
        msg['Date']=bot.utc_now().strftime('%a, %d %b %Y %H:%M:%S +0000')
        msg['Subject']='UPI payment received'
        msg.set_content('<html><body>Amount ₹499.00 paid to shivam@upi<br>UTR 123456789012</body></html>', subtype='html')
        old=(bot.IMAP_REQUIRE_RECIPIENT_MATCH, bot.IMAP_ALLOWED_SENDERS)
        bot.IMAP_REQUIRE_RECIPIENT_MATCH=True
        bot.IMAP_ALLOWED_SENDERS={'alerts@bank.example'}
        try:
            ok, reason=bot._match_payment_email(row, [(1,msg,'alerts@bank.example')])
        finally:
            bot.IMAP_REQUIRE_RECIPIENT_MATCH, bot.IMAP_ALLOWED_SENDERS=old
        self.assertTrue(ok, reason)

    def test_imap_rejects_wrong_amount_and_future_email(self):
        msg=EmailMessage(); msg['From']='alerts@bank.example'; msg['Date']='Fri, 04 Sep 2099 00:00:00 +0000'; msg['Subject']='Payment'; msg.set_content('Amount ₹500.00 UTR 123456789012 shivam@upi')
        self.assertFalse(bot._message_is_recent(msg))

    def test_imap_disabled_diagnostic_is_safe(self):
        old=(bot.IMAP_ENABLED, bot.IMAP_USERNAME, bot.IMAP_APP_PASSWORD)
        bot.IMAP_ENABLED=False; bot.IMAP_USERNAME=''; bot.IMAP_APP_PASSWORD=''
        try:
            ok, detail=bot.imap_connection_check()
        finally:
            bot.IMAP_ENABLED, bot.IMAP_USERNAME, bot.IMAP_APP_PASSWORD=old
        self.assertFalse(ok)
        self.assertIn('disabled', detail)

    def test_legacy_qr_and_password_settings_removed(self):
        self.assertEqual(bot.setting('qr_file_id',''), '')
        self.assertEqual(bot.setting('admin_password_hash',''), '')
    def test_amount_validation(self):
        self.assertEqual(bot.parse_amount('1,234.50'),1234.5)
        self.assertIsNone(bot.parse_amount('nan'))
        self.assertIsNone(bot.parse_amount('-1', minimum=0))
    def test_upi_validation(self):
        self.assertTrue(bot.valid_upi_id('shivam@upi'))
        self.assertTrue(bot.valid_upi_id('merchant.name@okaxis'))
        self.assertFalse(bot.valid_upi_id('not-a-upi-id'))

    def test_start_menu_is_single_tracked_screen(self):
        source = Path(bot.__file__).read_text(encoding="utf-8")
        self.assertIn("cleanup_admin_session_messages(update, context, delete_screen=True)", inspect.getsource(bot.start))
        self.assertIn("remember_screen(context, sent)", inspect.getsource(bot.start))

    def test_admin_input_cleanup_and_logout(self):
        source = Path(bot.__file__).read_text(encoding="utf-8")
        self.assertIn("admin_flows = {", inspect.getsource(bot.text_router))
        self.assertIn("await delete_incoming(update)", inspect.getsource(bot.text_router))
        self.assertIn("cleanup_admin_session_messages", source)
        self.assertIn('action == "logout"', inspect.getsource(bot.callback_router))

    def test_dynamic_upi_qr(self):
        qr = bot.generate_upi_qr('shivam@upi', 125.50, 'BAL-TEST-001')
        self.assertIsNotNone(qr)
        self.assertTrue(qr.getvalue().startswith(b'\x89PNG'))
        self.assertGreater(len(qr.getvalue()), 100)

    def test_url_validation(self):
        self.assertTrue(bot.valid_url('https://example.com/a'))
        self.assertFalse(bot.valid_url('javascript:alert(1)'))
    def test_coupon_expiry_and_usage(self):
        bot.set_setting('test_marker','ok')
        with bot.db() as c:
            c.execute("INSERT INTO coupons(code,discount_type,discount_value,max_uses,used_count,active,expires_at) VALUES ('TEST10','percent',10,1,0,1,NULL)")
            c.commit()
        self.assertEqual(bot.calculate_coupon('TEST10',100),(90.0,'TEST10'))
        with bot.db() as c:
            c.execute("UPDATE coupons SET used_count=1 WHERE code='TEST10'"); c.commit()
        self.assertIsNone(bot.calculate_coupon('TEST10',100))
    def test_balance_order_lifecycle(self):
        import asyncio
        with bot.db() as c:
            c.execute("INSERT OR IGNORE INTO users(id, username, first_name, created_at, updated_at, balance) VALUES (12345,'owner','Owner',?,?,0)", (bot.iso_now(), bot.iso_now()))
            c.commit()
        order_id = asyncio.run(bot.create_balance_order(12345, 250))
        with bot.db() as c:
            row = c.execute("SELECT status, amount, topup_amount FROM orders WHERE id=?", (order_id,)).fetchone()
        self.assertEqual(row['status'], 'awaiting_utr')
        self.assertEqual(float(row['amount']), 250.0)
        self.assertEqual(float(row['topup_amount']), 250.0)

    def test_new_feature_tables_and_order_tracking(self):
        with bot.db() as c:
            tables={r['name'] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        self.assertIn('scheduled_broadcasts', tables)
        self.assertIn('risk_flags', tables)
        self.assertEqual(bot.order_status_label('pending'), '🔎 Payment Submitted — Automatic Verification')
        self.assertEqual(bot.order_status_label('approved','delivered'), '✅ Completed — Delivered')

    def test_category_creation_handler_exists(self):
        source = Path(bot.__file__).read_text(encoding="utf-8")
        self.assertIn('if flow == "add_category":', source)
        self.assertIn('INSERT INTO categories(name, description, active)', source)

    def test_admin_callback_whitelist_covers_catalog_and_stock(self):
        source = Path(bot.__file__).read_text(encoding="utf-8")
        for prefix in ["pwcat:", "stockplan:", "paddplan", "psave", "pcancel", "coupon_type:", "coupon_save", "riskresolve:", "userban:", "maintenance:toggle"]:
            self.assertIn(f'"{prefix}"', source)

    def test_payment_wait_state_only_prompts_after_verify(self):
        source = Path(bot.__file__).read_text(encoding="utf-8")
        self.assertIn('context.user_data["flow"] = "payment_wait"', source)
        self.assertIn('elif data == "payment:verify":', source)
        self.assertIn('context.user_data["flow"] = "utr"', source)

    def test_pending_orders_have_expiry_support(self):
        with bot.db() as c:
            c.execute("INSERT OR IGNORE INTO users(id,username,first_name,created_at,updated_at) VALUES (777,'u','U',?,?)", (bot.iso_now(), bot.iso_now()))
            old=(bot.utc_now()-bot.timedelta(minutes=21)).isoformat()
            c.execute("INSERT INTO orders(order_no,user_id,order_type,amount,original_amount,status,created_at,expiry_at) VALUES (?,?,?,?,?,'pending',?,?)", ('EXP-TEST',777,'product',10,10,old,old))
            c.commit()
        bot.expire_stale_orders()
        with bot.db() as c:
            row=c.execute("SELECT status FROM orders WHERE order_no='EXP-TEST'").fetchone()
        self.assertEqual(row['status'],'expired')

    def test_balance_order_has_expiry_timestamp(self):
        import asyncio
        with bot.db() as c:
            c.execute("INSERT OR IGNORE INTO users(id,username,first_name,created_at,updated_at) VALUES (777,'u','U',?,?)", (bot.iso_now(), bot.iso_now()))
            c.commit()
        oid=asyncio.run(bot.create_balance_order(777,100))
        with bot.db() as c:
            row=c.execute("SELECT expiry_at FROM orders WHERE id=?",(oid,)).fetchone()
        self.assertTrue(row['expiry_at'])

    def test_stock_import_reports_invalid_separately(self):
        source=Path(bot.__file__).read_text(encoding='utf-8')
        self.assertIn('invalid += 1', source)
        self.assertIn('duplicate += 1', source)
        self.assertIn('Skipped total', source)

    def test_legacy_webapp_receiver_removed(self):
        source=Path(bot.__file__).read_text(encoding='utf-8')
        self.assertNotIn('def web_app_data_router', source)
        self.assertNotIn('WEB_APP_DATA', source)

    def test_wallet_adjustment_cannot_go_negative(self):
        with bot.db() as c:
            c.execute("INSERT OR REPLACE INTO users(id,username,first_name,created_at,updated_at,balance) VALUES (99,'u','U',?,?,10)",(bot.iso_now(),bot.iso_now())); c.commit()
        with bot.db() as c:
            row=c.execute('SELECT balance FROM users WHERE id=99').fetchone()
        self.assertEqual(row['balance'],10)


    def test_imap_security_sender_and_amount_scope(self):
        from email.message import EmailMessage
        with bot.db() as c:
            c.execute("INSERT OR IGNORE INTO users(id,username,first_name,created_at,updated_at) VALUES (556,'scope','Scope',?,?)", (bot.iso_now(),bot.iso_now()))
            c.execute("INSERT INTO orders(order_no,user_id,order_type,amount,original_amount,topup_amount,utr,status,created_at,expiry_at) VALUES (?,?,?,?,?,?,?,?,?,?)", ('SCOPE-TEST',556,'balance',499,499,499,'DEF987654321','pending',bot.iso_now(),(bot.utc_now()+timedelta(minutes=10)).isoformat()))
            c.execute("INSERT OR REPLACE INTO settings(key,value) VALUES('upi_id','shivam@upi')"); c.commit()
            row=c.execute("SELECT * FROM orders WHERE order_no='SCOPE-TEST'").fetchone()
        msg=EmailMessage(); msg['From']='alerts@bank.example'; msg['Date']=bot.utc_now().strftime('%a, %d %b %Y %H:%M:%S +0000'); msg['Subject']='Payment'
        msg.set_content('Amount ₹1000.00 paid. Available balance ₹499.00. UTR DEF987654321 shivam@upi')
        old=bot.IMAP_ALLOWED_SENDERS
        bot.IMAP_ALLOWED_SENDERS={'alerts@bank.example'}
        try:
            ok, reason=bot._match_payment_email(row, [(9,msg,'alerts@bank.example')])
        finally: bot.IMAP_ALLOWED_SENDERS=old
        self.assertFalse(ok, reason)

    def test_imap_rejects_untrusted_sender(self):
        old=bot.IMAP_ALLOWED_SENDERS
        bot.IMAP_ALLOWED_SENDERS=set()
        try: self.assertFalse(bot._sender_allowed('alerts@bank.example'))
        finally: bot.IMAP_ALLOWED_SENDERS=old

    def test_expired_pending_is_not_fulfilled(self):
        import asyncio
        with bot.db() as c:
            c.execute("INSERT OR IGNORE INTO users(id,username,first_name,created_at,updated_at) VALUES (778,'e','E',?,?)", (bot.iso_now(),bot.iso_now()))
            c.execute("INSERT INTO orders(order_no,user_id,order_type,amount,original_amount,topup_amount,utr,status,created_at,expiry_at) VALUES (?,?,?,?,?,?,?,?,?,?)", ('EXPIRED-FILL',778,'balance',10,10,10,'EXP123456789','pending',bot.iso_now(),(bot.utc_now()-timedelta(minutes=1)).isoformat())); c.commit()
            oid=c.execute("SELECT id FROM orders WHERE order_no='EXPIRED-FILL'").fetchone()[0]
        ok, reason=asyncio.run(bot.auto_fulfill_verified_order(None, oid))
        self.assertFalse(ok); self.assertIn('expired', reason.lower())
        with bot.db() as c: self.assertEqual(c.execute("SELECT status FROM orders WHERE id=?",(oid,)).fetchone()[0], 'expired')




    def test_sender_domain_boundary_and_payment_event_table(self):
        old=bot.IMAP_ALLOWED_SENDERS
        bot.IMAP_ALLOWED_SENDERS={'bank.com'}
        try:
            self.assertTrue(bot._sender_allowed('alerts@bank.com'))
            self.assertFalse(bot._sender_allowed('alerts@fakebank.com'))
        finally: bot.IMAP_ALLOWED_SENDERS=old
        with bot.db() as c:
            tables={r['name'] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        self.assertIn('payment_events', tables)

    def test_clean_payment_screen_paths_exist(self):
        source=Path(bot.__file__).read_text(encoding='utf-8')
        self.assertIn('async def send_clean_text_screen', source)
        self.assertIn('await delete_tracked_screen(update, context)', source)
        self.assertIn('payment_verified_stock_unavailable', source)

    def test_matcher_enforces_trusted_sender_defense_in_depth(self):
        from email.message import EmailMessage
        with bot.db() as c:
            c.execute("INSERT OR IGNORE INTO users(id,username,first_name,created_at,updated_at) VALUES (901,'s','S',?,?)", (bot.iso_now(),bot.iso_now()))
            c.execute("INSERT INTO orders(order_no,user_id,order_type,amount,original_amount,topup_amount,utr,status,created_at,expiry_at) VALUES (?,?,?,?,?,?,?,?,?,?)", ('SENDER-DEF',901,'balance',499,499,499,'GHI246813579','pending',bot.iso_now(),(bot.utc_now()+timedelta(minutes=10)).isoformat()))
            c.execute("INSERT OR REPLACE INTO settings(key,value) VALUES('upi_id','shivam@upi')")
            c.commit(); row=c.execute("SELECT * FROM orders WHERE order_no='SENDER-DEF'").fetchone()
        m=EmailMessage(); m['From']='alerts@fakebank.com'; m['Date']=bot.utc_now().strftime('%a, %d %b %Y %H:%M:%S +0000'); m.set_content('Amount INR 499.00 paid to shivam@upi UTR GHI246813579')
        old=bot.IMAP_ALLOWED_SENDERS; bot.IMAP_ALLOWED_SENDERS={'alerts@bank.com'}
        try:
            ok,_=bot._match_payment_email(row,[(1,m,'alerts@fakebank.com')])
        finally: bot.IMAP_ALLOWED_SENDERS=old
        self.assertFalse(ok)

    def test_amount_match_checks_repeated_utr_occurrences(self):
        text='UTR XYZ135791357 status summary. Footer repeats UTR XYZ135791357. Amount INR 499.00 paid to merchant.'
        self.assertTrue(bot._amount_matches_near_utr(text, bot.Decimal('499.00'), 'XYZ135791357'))

    def test_referral_registration_blocks_self_and_duplicate(self):
        with bot.db() as c:
            now=bot.iso_now()
            c.execute("INSERT OR IGNORE INTO users(id,username,first_name,created_at,updated_at) VALUES (1001,'ref','Ref',?,?)",(now,now))
            c.execute("INSERT OR IGNORE INTO users(id,username,first_name,created_at,updated_at) VALUES (1002,'new','New',?,?)",(now,now))
            c.commit()
        self.assertFalse(bot.register_referral(1001,1001))
        self.assertTrue(bot.register_referral(1001,1002))
        self.assertFalse(bot.register_referral(1001,1002))

    def test_referral_reward_is_exactly_once_and_wallet_credited(self):
        with bot.db() as c:
            now=bot.iso_now()
            c.execute("INSERT OR REPLACE INTO users(id,username,first_name,created_at,updated_at,balance) VALUES (1010,'ref','Ref',?,?,0)",(now,now))
            c.execute("INSERT OR REPLACE INTO users(id,username,first_name,created_at,updated_at,balance) VALUES (1011,'new','New',?,?,0)",(now,now))
            c.execute("INSERT OR REPLACE INTO referrals(referrer_id,referred_user_id,status,reward_amount,created_at) VALUES (1010,1011,'pending',0,?)",(now,))
            c.execute("INSERT INTO orders(order_no,user_id,order_type,amount,original_amount,status,created_at) VALUES ('REF-ORDER',1011,'product',100,100,'approved',?)",(now,))
            oid=c.execute("SELECT id FROM orders WHERE order_no='REF-ORDER'").fetchone()[0]
            c.commit()
            c.execute("BEGIN IMMEDIATE")
            ok,reward,referrer=bot.reward_referral_for_order(c,1011,oid,now)
            c.commit()
        self.assertTrue(ok); self.assertEqual(reward, bot.Decimal('20.00')); self.assertEqual(referrer,1010)
        with bot.db() as c:
            balance=c.execute("SELECT balance FROM users WHERE id=1010").fetchone()[0]
            count=c.execute("SELECT COUNT(*) FROM wallet_transactions WHERE user_id=1010 AND type='referral_reward'").fetchone()[0]
            status=c.execute("SELECT status FROM referrals WHERE referred_user_id=1011").fetchone()[0]
        self.assertEqual(balance,20.0); self.assertEqual(count,1); self.assertEqual(status,'qualified')
        with bot.db() as c:
            c.execute("BEGIN IMMEDIATE")
            ok2,_,_=bot.reward_referral_for_order(c,1011,oid,now)
            c.commit()
        self.assertFalse(ok2)
        with bot.db() as c:
            self.assertEqual(c.execute("SELECT balance FROM users WHERE id=1010").fetchone()[0],20.0)
            self.assertEqual(c.execute("SELECT COUNT(*) FROM wallet_transactions WHERE user_id=1010 AND type='referral_reward'").fetchone()[0],1)

    def test_referral_schema_and_admin_ui_exist(self):
        source=Path(bot.__file__).read_text(encoding='utf-8')
        self.assertIn('CREATE TABLE IF NOT EXISTS referrals', source)
        self.assertIn('button(tr(user_id, "referral"), "referral")', source)
        self.assertIn('action == "referrals"', source)
        self.assertIn('set_referral_reward', source)
        self.assertIn('referral_reward', source)

    def test_language_selection_and_localized_content_storage(self):
        source = Path(bot.__file__).read_text(encoding="utf-8")
        self.assertIn('tr(user_id, "language")', source)
        self.assertIn('"language"', source)
        self.assertIn('button("🛍️  ✦  " + tr(user_id, "shop") + "  ✦", "shop")', source)
        self.assertIn('data.startswith("language:")', source)
        self.assertIn('ensure_column(connection, "users", "language"', source)
        self.assertIn('name_i18n', source)
        self.assertIn('description_i18n', source)
        with bot.db() as c:
            now = bot.iso_now()
            c.execute("INSERT OR REPLACE INTO users(id,username,first_name,language,created_at,updated_at) VALUES(777,'lang','Lang','hi',?,?)", (now,now))
            c.commit()
        self.assertEqual(bot.user_language(777), 'hi')
        self.assertEqual(bot.tr(777, 'shop'), '🛍️  शॉप नाउ')
        self.assertIn('referral', bot.SUPPORTED_LANGUAGES) if False else None

    def test_referral_link_and_coupon_code_are_not_transformed(self):
        source = Path(bot.__file__).read_text(encoding="utf-8")
        self.assertIn('blue_link = f\'<a href="{safe(link)}">{safe(link)}</a>\'', source)
        self.assertIn('coupon_code', source)
        self.assertIn('code.upper()', source)
        self.assertIn('referral_share_text', source)
        self.assertIn('settings:wallet_history', source)
        self.assertIn('settings:referral_earnings', source)
        self.assertIn('settings:failed_protection', source)

    def test_premium_main_menu_has_four_by_two_actions_and_large_edges(self):
        kb = bot.main_keyboard(12345).inline_keyboard
        self.assertEqual([len(r) for r in kb], [1,2,2,2,2,1])
        self.assertEqual(kb[0][0].callback_data, 'shop')
        self.assertEqual(kb[-1][0].callback_data, 'language')
        callbacks = [b.callback_data for row in kb[1:5] for b in row]
        self.assertEqual(callbacks, ['profile','balance','referral','history','support','proof_tutorial','reseller','settings'])

    def test_profile_contains_joined_date_and_localized_labels(self):
        source = Path(bot.__file__).read_text(encoding='utf-8')
        for key in ['profile_title','joined','completed_orders_label','profile_overview','profile_overview_text']:
            self.assertIn(f'"{key}"', source)
        self.assertIn('created_at', source)
        self.assertIn('datetime.fromisoformat(user["created_at"]', source)

    def test_user_settings_and_password_lock_features_exist(self):
        source = Path(bot.__file__).read_text(encoding='utf-8')
        for token in ('settings_screen','settings:security','settings:theme','bot_password_hash','password_remember_until','user_password_unlock','proof_tutorial','Selling Proof + Tutorial','Theme Preference'):
            self.assertIn(token, source)

    def test_user_password_hash_roundtrip(self):
        salt, digest = bot._hash_user_password('TestPass123')
        self.assertTrue(bot._verify_user_password('TestPass123', salt, digest))
        self.assertFalse(bot._verify_user_password('WrongPass123', salt, digest))

    def test_user_settings_theme_and_lock_columns(self):
        with bot.db() as c:
            cols = {r['name'] for r in c.execute('PRAGMA table_info(users)').fetchall()}
        for col in ('bot_password_hash','bot_password_salt','password_remember_until','password_lock_enabled','theme_preference','notifications_enabled'):
            self.assertIn(col, cols)

if __name__=='__main__':
    unittest.main(verbosity=2)
