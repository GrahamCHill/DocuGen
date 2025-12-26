from .base import Fetcher, FetchResult


class PlaywrightFetcher(Fetcher):
    async def fetch(self, url: str) -> FetchResult:
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            raise Exception("Playwright is not installed. Please run 'pip install playwright'.")
            
        try:
            async with async_playwright() as pw:
                try:
                    browser = await pw.chromium.launch()
                except Exception as e:
                    if "playwright install" in str(e).lower():
                        raise Exception("Playwright browsers not installed. Please run 'playwright install chromium'.")
                    raise e
                    
                page = await browser.new_page()
                await page.goto(url, wait_until="networkidle")
                
                # Wait a bit more for any JS to finish rendering content
                await page.wait_for_timeout(5000)
                
                # Scroll from top to bottom to trigger lazy-loading content
                await page.evaluate("""
                    async () => {
                        await new Promise((resolve) => {
                            let totalHeight = 0;
                            let distance = 100;
                            let timer = setInterval(() => {
                                let scrollHeight = document.body.scrollHeight;
                                window.scrollBy(0, distance);
                                totalHeight += distance;

                                if(totalHeight >= scrollHeight){
                                    clearInterval(timer);
                                    resolve();
                                }
                            }, 100);
                        });
                        window.scrollTo(0, 0);
                    }
                """)

                # Wait for stability: check if the content size remains constant
                last_html_len = 0
                stable_count = 0
                max_stability_checks = 10
                for _ in range(max_stability_checks):
                    html = await page.content()
                    current_len = len(html)
                    if current_len > 0 and current_len == last_html_len:
                        stable_count += 1
                    else:
                        stable_count = 0
                        last_html_len = current_len
                    
                    if stable_count >= 3:
                        break
                    await page.wait_for_timeout(1000)

                html = await page.content()
                await browser.close()
                return FetchResult(url, html)
        except Exception as e:
            raise Exception(f"Playwright error: {e}")
