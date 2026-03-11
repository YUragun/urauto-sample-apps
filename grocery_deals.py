"""
Australian Grocery Deals - Full Windows Edition
Uses Selenium with Chrome
"""

import streamlit as st
import pandas as pd
import sqlite3
import re
import os
from datetime import datetime
from typing import List, Dict, Set
import time

# Selenium with ERROR DISPLAY
SELENIUM_AVAILABLE = False
SELENIUM_ERROR = None
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.action_chains import ActionChains
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except Exception as e:  # Catch ALL errors, not just ImportError
    SELENIUM_ERROR = str(e)
    import traceback
    SELENIUM_ERROR_TRACEBACK = traceback.format_exc()

# ===================== CONFIG =====================
st.set_page_config(page_title="Deals", layout="wide", initial_sidebar_state="collapsed")

# Add custom CSS


# ===================== SESSION STATE =====================
if 'grocery_load_more_count' not in st.session_state:
    st.session_state['grocery_load_more_count'] = 0
if 'grocery_page_num' not in st.session_state:
    st.session_state['grocery_page_num'] = 1
if 'show_images' not in st.session_state:
    st.session_state['show_images'] = True
if 'reset_filters' not in st.session_state:
    st.session_state['reset_filters'] = False
if 'confirm_delete' not in st.session_state:
    st.session_state['confirm_delete'] = False

# ===================== DATABASE =====================
def get_db_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_dir = os.path.join(current_dir, 'database')
    os.makedirs(db_dir, exist_ok=True)
    return os.path.join(db_dir, 'app.db')

def init_db():
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='grocery_deals'")
    table_exists = c.fetchone()
    
    if table_exists:
        c.execute("PRAGMA table_info(grocery_deals)")
        columns = [col[1] for col in c.fetchall()]
        
        if 'image_url' not in columns:
            try:
                c.execute("ALTER TABLE grocery_deals ADD COLUMN image_url TEXT")
                conn.commit()
            except:
                pass
    else:
        c.execute("""
            CREATE TABLE IF NOT EXISTS grocery_deals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL UNIQUE,
                image_url TEXT,
                coles_price REAL,
                coles_was_price REAL,
                coles_special TEXT,
                woolworths_price REAL,
                woolworths_was_price REAL,
                woolworths_special TEXT,
                source TEXT DEFAULT 'Grocerize',
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    
    conn.close()

def get_existing_product_names() -> Set[str]:
    try:
        conn = sqlite3.connect(get_db_path())
        c = conn.cursor()
        c.execute("SELECT product_name FROM grocery_deals")
        names = set(row[0] for row in c.fetchall())
        conn.close()
        return names
    except:
        return set()

def save_deals(deals: List[Dict], mode='add_new'):
    if not deals:
        return {'saved': 0, 'updated': 0}
    
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    
    saved = 0
    updated = 0
    
    if mode == 'replace':
        c.execute("DELETE FROM grocery_deals")
    
    for deal in deals:
        c.execute("SELECT id FROM grocery_deals WHERE product_name = ?", (deal['product_name'],))
        exists = c.fetchone()
        
        if exists:
            if mode == 'replace':
                c.execute("""
                    UPDATE grocery_deals 
                    SET image_url=?, coles_price=?, coles_was_price=?, coles_special=?,
                        woolworths_price=?, woolworths_was_price=?, woolworths_special=?,
                        source=?, scraped_at=?
                    WHERE product_name=?
                """, (deal.get('image_url'), deal.get('coles_price'), deal.get('coles_was_price'), 
                      deal.get('coles_special'), deal.get('woolworths_price'), 
                      deal.get('woolworths_was_price'), deal.get('woolworths_special'), 
                      'Grocerize', datetime.now(), deal['product_name']))
                updated += 1
        else:
            c.execute("""
                INSERT INTO grocery_deals 
                (product_name, image_url, coles_price, coles_was_price, coles_special,
                 woolworths_price, woolworths_was_price, woolworths_special, source, scraped_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (deal['product_name'], deal.get('image_url'), deal.get('coles_price'), 
                  deal.get('coles_was_price'), deal.get('coles_special'), 
                  deal.get('woolworths_price'), deal.get('woolworths_was_price'), 
                  deal.get('woolworths_special'), 'Grocerize', datetime.now()))
            saved += 1
    
    conn.commit()
    conn.close()
    return {'saved': saved, 'updated': updated}

def load_deals() -> pd.DataFrame:
    try:
        conn = sqlite3.connect(get_db_path())
        df = pd.read_sql("SELECT * FROM grocery_deals ORDER BY id DESC", conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

def delete_all():
    try:
        conn = sqlite3.connect(get_db_path())
        c = conn.cursor()
        c.execute("DELETE FROM grocery_deals")
        conn.commit()
        conn.close()
        return True
    except:
        return False

# ===================== SCRAPER =====================
class GrocerizeScraper:
    def __init__(self):
        self.driver = None
    
    def setup_driver(self):
        """Setup Chrome browser"""
        st.info(f"🔍 Chrome Available: {SELENIUM_AVAILABLE}")
        
        if not SELENIUM_AVAILABLE:
            st.error("❌ Selenium not installed")
            return False
        
        try:
            st.info("🔵 Starting Chrome...")
            
            chrome_options = ChromeOptions()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Set Chrome binary location
            chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
            if os.path.exists(chrome_path):
                chrome_options.binary_location = chrome_path
                st.info(f"✅ Chrome found: {chrome_path}")
            else:
                st.error(f"❌ Chrome not found at: {chrome_path}")
                return False
            
            chrome_service = ChromeService(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
            st.success("✅ Chrome browser ready!")
            return True
            
        except Exception as e:
            st.error(f"❌ Chrome setup failed: {e}")
            import traceback
            st.code(traceback.format_exc())
            return False
    
    def close_any_modals(self):
        """Close any visible modals"""
        try:
            actions = ActionChains(self.driver)
            actions.send_keys(Keys.ESCAPE).perform()
            time.sleep(0.5)
            
            close_buttons = self.driver.find_elements(By.XPATH, 
                "//button[.//svg[contains(@viewBox, '0 0 20 20')]]")
            
            for btn in close_buttons:
                try:
                    if btn.is_displayed():
                        btn.click()
                        st.info("✅ Closed modal")
                        time.sleep(1)
                        return True
                except:
                    continue
            
            return False
        except:
            return False
    
    def sort_by_biggest_savings(self):
        """Sort by biggest savings"""
        try:
            st.info("🔽 Setting sort to 'Biggest Savings'...")
            
            sort_btn = self.driver.find_element(By.ID, "item-sort-dropdown")
            sort_btn.click()
            time.sleep(1)
            
            options = self.driver.find_elements(By.XPATH, "//div[contains(text(), 'Biggest Savings')]")
            for opt in options:
                if opt.is_displayed():
                    opt.click()
                    st.success("✅ Selected 'Biggest Savings'")
                    time.sleep(1)
                    
                    actions = ActionChains(self.driver)
                    actions.send_keys(Keys.ESCAPE).perform()
                    time.sleep(1)
                    return True
            
            return False
        except Exception as e:
            st.warning(f"⚠️ Could not set sort: {e}")
            return False
    
    def get_product_count(self):
        """Get product count using JS"""
        try:
            return self.driver.execute_script("""
                return document.querySelectorAll('div.card img#item-image').length;
            """)
        except:
            return 0
    
    def press_end_key(self):
        """Press END key to scroll to absolute bottom"""
        try:
            actions = ActionChains(self.driver)
            actions.send_keys(Keys.END).perform()
            return True
        except:
            return False
    
    def scroll_with_end_key(self, rounds: int = 10):
        """Press END key multiple times with waits"""
        st.info(f"⌨️ Pressing END key {rounds} times to load content...")
        
        initial_count = self.get_product_count()
        st.info(f"📦 Starting with {initial_count} products")
        
        last_count = initial_count
        
        for i in range(rounds):
            st.info(f"🔄 Round {i + 1}/{rounds}: Pressing END key")
            
            before_count = self.get_product_count()
            self.press_end_key()
            
            st.info("⏳ Waiting 4 seconds for lazy loading...")
            time.sleep(4)
            
            self.close_any_modals()
            
            after_count = self.get_product_count()
            new_items = after_count - before_count
            
            if new_items > 0:
                st.success(f"✅ +{new_items} products loaded! (Total: {after_count})")
                last_count = after_count
            else:
                st.info(f"➡️ No new products this round (still at {after_count})")
                
                if i > 2 and after_count == last_count:
                    st.warning("⚠️ No new content after multiple END presses")
            
            if i < rounds - 1:
                time.sleep(1)
        
        final_count = self.get_product_count()
        total_loaded = final_count - initial_count
        st.success(f"✅ END key scrolling complete! Loaded {total_loaded} new products (Total: {final_count})")
        
        return final_count
    
    def scrape(self, end_key_rounds: int = 0, existing_products: Set[str] = None) -> List[Dict]:
        """Scrape using END key approach"""
        if existing_products is None:
            existing_products = set()
        
        deals = []
        
        try:
            self.driver.get("https://www.grocerize.com.au/browse")
            time.sleep(8)
            
            self.close_any_modals()
            self.sort_by_biggest_savings()
            
            st.info("⏳ Initial page load...")
            time.sleep(3)
            
            if end_key_rounds > 0:
                self.scroll_with_end_key(rounds=end_key_rounds * 5)
            else:
                st.info("⌨️ Pressing END key for initial scroll...")
                self.press_end_key()
                time.sleep(4)
                self.close_any_modals()
            
            st.info("⏳ Final wait for rendering...")
            time.sleep(3)
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            cards = []
            for div in soup.find_all('div', class_='card'):
                if div.find('img', id='item-image'):
                    cards.append(div)
            
            st.info(f"📦 Parsing {len(cards)} product cards...")
            
            new_products = 0
            skipped_existing = 0
            
            for card in cards:
                try:
                    image_url = None
                    img = card.find('img', id='item-image')
                    if img and img.get('src'):
                        image_url = img.get('src')
                    
                    name = None
                    name_div = card.find('div', class_=re.compile(r'u-truncate'))
                    if name_div:
                        name = name_div.get_text(strip=True)
                    if not name and img:
                        name = img.get('alt', '')
                    
                    if not name or len(name) < 3:
                        continue
                    
                    if name.strip() in existing_products:
                        skipped_existing += 1
                        continue
                    
                    deal = {
                        'product_name': name.strip(),
                        'image_url': image_url,
                        'coles_price': None,
                        'coles_was_price': None,
                        'coles_special': None,
                        'woolworths_price': None,
                        'woolworths_was_price': None,
                        'woolworths_special': None
                    }
                    
                    has_discount = False
                    
                    # Coles
                    coles_div = card.find('div', class_=re.compile(r'u-color-coles'))
                    if coles_div and coles_div.parent:
                        container = coles_div.parent
                        
                        for pdiv in container.find_all('div', class_=re.compile(r'u-main-font--medium.*u-bold')):
                            txt = pdiv.get_text(strip=True)
                            if txt.startswith('$') and '/' not in txt:
                                m = re.search(r'\$(\d+\.?\d{0,2})', txt)
                                if m:
                                    deal['coles_price'] = float(m.group(1))
                                    break
                        
                        badge = container.find('div', class_=re.compile(r'u-background--yellow'))
                        if badge:
                            special = badge.get_text(strip=True)
                            if special:
                                deal['coles_special'] = special
                                has_discount = True
                                
                                if special.startswith('-$') and deal['coles_price']:
                                    save_match = re.search(r'\$(\d+\.?\d{0,2})', special)
                                    if save_match:
                                        save = float(save_match.group(1))
                                        deal['coles_was_price'] = round(deal['coles_price'] + save, 2)
                    
                    # Woolworths
                    wool_div = card.find('div', class_=re.compile(r'u-color-woolworths'))
                    if wool_div and wool_div.parent:
                        container = wool_div.parent
                        
                        for pdiv in container.find_all('div', class_=re.compile(r'u-main-font--medium.*u-bold')):
                            txt = pdiv.get_text(strip=True)
                            if txt.startswith('$') and '/' not in txt:
                                m = re.search(r'\$(\d+\.?\d{0,2})', txt)
                                if m:
                                    deal['woolworths_price'] = float(m.group(1))
                                    break
                        
                        badge = container.find('div', class_=re.compile(r'u-background--yellow'))
                        if badge:
                            special = badge.get_text(strip=True)
                            if special:
                                deal['woolworths_special'] = special
                                has_discount = True
                                
                                if special.startswith('-$') and deal['woolworths_price']:
                                    save_match = re.search(r'\$(\d+\.?\d{0,2})', special)
                                    if save_match:
                                        save = float(save_match.group(1))
                                        deal['woolworths_was_price'] = round(deal['woolworths_price'] + save, 2)
                    
                    if has_discount and (deal['coles_price'] or deal['woolworths_price']):
                        deals.append(deal)
                        new_products += 1
                
                except:
                    continue
            
            st.success(f"✅ Found {new_products} NEW products (skipped {skipped_existing} existing)")
            return deals
            
        except Exception as e:
            st.error(f"Scrape error: {e}")
            import traceback
            st.code(traceback.format_exc())
            return []
    
    def cleanup(self):
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass

# ===================== UI =====================
def render_product_card(row):
    if st.session_state.get('show_images', False) and pd.notna(row.get('image_url')):
        img_col, content_col = st.columns([1, 4])
        
        with img_col:
            st.image(row['image_url'], width=150)
        
        with content_col:
            render_card_content(row)
    else:
        render_card_content(row)

def render_card_content(row):
    st.markdown(f"### 🛍️ {row['product_name']}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔴 Coles")
        if pd.notna(row['coles_price']) and row['coles_price'] > 0:
            # Always show the structure
            was_price = row['coles_was_price'] if pd.notna(row['coles_was_price']) and row['coles_was_price'] > 0 else None
            save = was_price - row['coles_price'] if was_price and was_price > 0 else None
            discount = round((save / was_price) * 100) if was_price and was_price > 0 else None
            special = row['coles_special'] if pd.notna(row['coles_special']) and row['coles_special'] else None
            
            col_a, col_b = st.columns(2)
            with col_a:
                if was_price:
                    st.markdown(f"**Was:** ~~${was_price:.2f}~~")
                else:
                    st.markdown(f"**Was:** :grey[_N/A_]")
                st.markdown(f"**Now:** ${row['coles_price']:.2f}")
            with col_b:
                if save:
                    st.markdown(f":green[**Save ${save:.2f}**]")
                else:
                    st.markdown(f":grey[Save: _N/A_]")
                if discount:
                    st.markdown(f":blue[**{discount}% off**]")
                else:
                    st.markdown(f":grey[_N/A_]")
            
            # Always show special box
            if special:
                st.markdown(f":orange[🎁 **{special}**]")
            else:
                st.markdown(f":grey[🎁 _N/A_]")
        else:
            st.caption("_Not available_")
    
    with col2:
        st.markdown("#### 🟢 Woolworths")
        if pd.notna(row['woolworths_price']) and row['woolworths_price'] > 0:
            # Always show the structure
            was_price = row['woolworths_was_price'] if pd.notna(row['woolworths_was_price']) and row['woolworths_was_price'] > 0 else None
            save = was_price - row['woolworths_price'] if was_price and was_price > 0 else None
            discount = round((save / was_price) * 100) if was_price and was_price > 0 else None
            special = row['woolworths_special'] if pd.notna(row['woolworths_special']) and row['woolworths_special'] else None
            
            col_a, col_b = st.columns(2)
            with col_a:
                if was_price:
                    st.markdown(f"**Was:** ~~${was_price:.2f}~~")
                else:
                    st.markdown(f"**Was:** :grey[_N/A_]")
                st.markdown(f"**Now:** ${row['woolworths_price']:.2f}")
            with col_b:
                if save:
                    st.markdown(f":green[**Save ${save:.2f}**]")
                else:
                    st.markdown(f":grey[Save: _N/A_]")
                if discount:
                    st.markdown(f":blue[**{discount}% off**]")
                else:
                    st.markdown(f":grey[_N/A_]")
            
            # Always show special box
            if special:
                st.markdown(f":orange[🎁 **{special}**]")
            else:
                st.markdown(f":grey[🎁 _N/A_]")
        else:
            st.caption("_Not available_")

# ===================== MAIN =====================
def main():
    init_db()
    
    st.title("🛒 Australian Grocery Deals")
    st.caption("Powered by Selenium • Discounts & specials only")
    
    # DEBUG: Show import status
    if not SELENIUM_AVAILABLE:
        st.error(f"❌ Selenium Import Failed!")
        if SELENIUM_ERROR:
            st.error(f"Error: {SELENIUM_ERROR}")
            with st.expander("🔍 Full Error Traceback"):
                st.code(SELENIUM_ERROR_TRACEBACK)
    else:
        st.success("✅ Selenium imported successfully!")
    
    st.divider()
    
    # Controls
    st.subheader("🎮 Controls")
    btn_col1, btn_col2, btn_col3, btn_col4, btn_col5 = st.columns(5)
    
    with btn_col1:
        if st.button("🔄 Refresh Deals", use_container_width=True):
            with st.spinner("Refreshing..."):
                st.session_state['grocery_load_more_count'] = 0
                st.session_state['grocery_page_num'] = 1
                scraper = GrocerizeScraper()
                if scraper.setup_driver():
                    deals = scraper.scrape(0)
                    scraper.cleanup()
                    if deals:
                        save_deals(deals, mode='replace')
                        st.success(f"✅ {len(deals)} deals")
                        time.sleep(1)
                        st.rerun()
    
    with btn_col2:
        if st.button("➕ Load More", type="primary", use_container_width=True):
            st.session_state['grocery_load_more_count'] += 1
            
            existing = get_existing_product_names()
            st.info(f"📊 Tracking {len(existing)} existing")
            
            with st.spinner(f"Loading round {st.session_state['grocery_load_more_count']}..."):
                scraper = GrocerizeScraper()
                if scraper.setup_driver():
                    deals = scraper.scrape(
                        end_key_rounds=st.session_state['grocery_load_more_count'],
                        existing_products=existing
                    )
                    scraper.cleanup()
                    
                    if deals:
                        result = save_deals(deals, mode='add_new')
                        if result['saved'] > 0:
                            st.success(f"✅ Added {result['saved']} NEW products!")
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.warning("⚠️ No new products")
                    else:
                        st.warning("⚠️ No new products found")
    
    with btn_col3:
        if st.button("🖼️ Images: " + ("ON" if st.session_state.get('show_images') else "OFF"), use_container_width=True):
            st.session_state['show_images'] = not st.session_state.get('show_images', False)
            st.rerun()
    
    with btn_col4:
        if st.button("🔄 Reset Filters", use_container_width=True):
            st.session_state['reset_filters'] = True
            st.session_state['grocery_page_num'] = 1
            st.rerun()
    
    df = load_deals()
    
    with btn_col5:
        if st.button("🗑️ Delete All Data", use_container_width=True):
            st.session_state['confirm_delete'] = True
    
    if st.session_state.get('confirm_delete', False):
        st.warning("⚠️ This will delete all data. Are you sure?")
        conf_col1, conf_col2, conf_col3 = st.columns([1, 1, 4])
        with conf_col1:
            if st.button("✅ Yes, Delete", type="primary"):
                delete_all()
                st.session_state['grocery_load_more_count'] = 0
                st.session_state['grocery_page_num'] = 1
                st.session_state['confirm_delete'] = False
                st.success("✅ All data deleted")
                st.rerun()
        with conf_col2:
            if st.button("❌ Cancel"):
                st.session_state['confirm_delete'] = False
                st.rerun()
    
    st.divider()
    
    if df.empty:
        st.info("👆 Click 'Refresh Deals' to start scraping")
        return
    
    if st.session_state.get('reset_filters', False):
        st.session_state['reset_filters'] = False
        st.rerun()
    
    # Filters
    st.subheader("🔍 Filters")
    
    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
    
    with filter_col1:
        discount_opt = st.selectbox("💰 Discount", ["All", "20%+", "50%+"], index=0)
    
    with filter_col2:
        special_opt = st.selectbox("🎁 Specials", ["All", "Multi-buy", "Price Drops"], index=0)
    
    with filter_col3:
        max_p = df[['coles_price', 'woolworths_price']].max().max()
        if pd.isna(max_p):
            max_p = 100
        price_max = st.slider("💵 Max $", 0.0, float(max_p), float(max_p), 1.0)
    
    with filter_col4:
        search = st.text_input("🔎 Search", placeholder="Product name...")
    
    st.divider()
    
    # Apply filters
    filtered = df.copy()
    
    if discount_opt == "20%+":
        def has_20(r):
            res = False
            if pd.notna(r['coles_was_price']) and r['coles_was_price'] > 0:
                if ((r['coles_was_price'] - r['coles_price']) / r['coles_was_price']) * 100 >= 20:
                    res = True
            if pd.notna(r['woolworths_was_price']) and r['woolworths_was_price'] > 0:
                if ((r['woolworths_was_price'] - r['woolworths_price']) / r['woolworths_was_price']) * 100 >= 20:
                    res = True
            return res
        filtered = filtered[filtered.apply(has_20, axis=1)]
    elif discount_opt == "50%+":
        def has_50(r):
            res = False
            if pd.notna(r['coles_was_price']) and r['coles_was_price'] > 0:
                if ((r['coles_was_price'] - r['coles_price']) / r['coles_was_price']) * 100 >= 50:
                    res = True
            if pd.notna(r['woolworths_was_price']) and r['woolworths_was_price'] > 0:
                if ((r['woolworths_was_price'] - r['woolworths_price']) / r['woolworths_was_price']) * 100 >= 50:
                    res = True
            return res
        filtered = filtered[filtered.apply(has_50, axis=1)]
    
    if special_opt == "Multi-buy":
        def has_multi(r):
            res = False
            if pd.notna(r['coles_special']) and 'for' in str(r['coles_special']).lower():
                res = True
            if pd.notna(r['woolworths_special']) and 'for' in str(r['woolworths_special']).lower():
                res = True
            return res
        filtered = filtered[filtered.apply(has_multi, axis=1)]
    elif special_opt == "Price Drops":
        def has_drop(r):
            res = False
            if pd.notna(r['coles_special']) and str(r['coles_special']).startswith('-$'):
                res = True
            if pd.notna(r['woolworths_special']) and str(r['woolworths_special']).startswith('-$'):
                res = True
            return res
        filtered = filtered[filtered.apply(has_drop, axis=1)]
    
    def within_price(r):
        res = False
        if pd.notna(r['coles_price']) and r['coles_price'] <= price_max:
            res = True
        if pd.notna(r['woolworths_price']) and r['woolworths_price'] <= price_max:
            res = True
        return res
    filtered = filtered[filtered.apply(within_price, axis=1)]
    
    if search:
        filtered = filtered[filtered['product_name'].str.contains(search, case=False, na=False)]
    
    # Statistics
    st.subheader("📊 Statistics")
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    
    with metric_col1:
        st.metric("📦 Filtered Products", len(filtered))
        
    with metric_col2:
        st.metric("📦 Total Products", len(df))
    
    with metric_col3:
        st.metric("🔄 Load Rounds", st.session_state.get('grocery_load_more_count', 0))
    
    st.divider()
    
    # Pagination
    if not filtered.empty:
        items_per_page = 25
        total_pages = max(1, (len(filtered) - 1) // items_per_page + 1)
        
        current_page = st.session_state.get('grocery_page_num', 1)
        if not isinstance(current_page, int) or current_page < 1 or current_page > total_pages:
            current_page = 1
            st.session_state['grocery_page_num'] = 1
    
        
        # Display paginated products
        start_idx = (current_page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        page_data = filtered.iloc[start_idx:end_idx]
        
        for idx, row in page_data.iterrows():
            with st.container():
                render_product_card(row)
                st.divider()
        
        # Pagination controls at bottom
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if current_page > 1:
                if st.button("⬅️ Previous Page", use_container_width=True):
                    st.session_state['grocery_page_num'] = current_page - 1
                    st.rerun()
        
        with col2:
            st.markdown(f"<div style='text-align: center; padding: 10px;'><b>Page {current_page} of {total_pages}</b></div>", unsafe_allow_html=True)
        
        with col3:
            if current_page < total_pages:
                if st.button("Next Page ➡️", use_container_width=True):
                    st.session_state['grocery_page_num'] = current_page + 1
                    st.rerun()
    else:
        st.warning("⚠️ No products match your filters")

if __name__ == "__main__":
    main()
