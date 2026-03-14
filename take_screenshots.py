from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    # 截取首页
    page = browser.new_page()
    page.set_viewport_size({"width": 1920, "height": 1080})
    print("Loading Home page...")
    page.goto('http://localhost:5174', wait_until='networkidle')
    page.wait_for_timeout(3000)
    page.screenshot(path='E:/EventPredictor/final_home.png', full_page=False)
    print("Saved: E:/EventPredictor/final_home.png")

    # 点击查看详情进入分析页面
    print("Navigating to analysis page...")
    try:
        # 尝试点击View Full Analysis按钮
        view_btn = page.locator('text=View Full Analysis')
        if view_btn.count() > 0:
            view_btn.first.click()
            page.wait_for_timeout(3000)
            page.screenshot(path='E:/EventPredictor/final_analysis.png', full_page=False)
            print("Saved: E:/EventPredictor/final_analysis.png")
        else:
            print("View Full Analysis button not found, navigating directly...")
            page.goto('http://localhost:5174/analysis', wait_until='networkidle')
            page.wait_for_timeout(3000)
            page.screenshot(path='E:/EventPredictor/final_analysis.png', full_page=False)
            print("Saved: E:/EventPredictor/final_analysis.png")
    except Exception as e:
        print(f"Error navigating: {e}")
        # 直接导航到分析页面
        page.goto('http://localhost:5174/analysis', wait_until='networkidle')
        page.wait_for_timeout(3000)
        page.screenshot(path='E:/EventPredictor/final_analysis.png', full_page=False)
        print("Saved: E:/EventPredictor/final_analysis.png")

    browser.close()
    print("Done!")
