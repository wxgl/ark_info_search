import os
import asyncio
import subprocess
from playwright.async_api import async_playwright


def set_china_mirror():
    """
    设置 Playwright 的国内镜像源
    （适配中国大陆环境，默认使用 npmmirror）
    """
    os.environ["PLAYWRIGHT_DOWNLOAD_HOST"] = "https://registry.npmmirror.com/-/binary/playwright"
    print("🌏 已设置 Playwright 国内镜像源 (npmmirror.com)")


async def ensure_chromium_installed():
    """
    确保 Chromium 已安装。
    若未安装则自动使用国内镜像下载。
    """
    set_china_mirror()

    try:
        subprocess.run(
            ["playwright", "install", "chromium-headless-shell"],
            check=True,
            capture_output=True
        )
        print("✅ Chromium 环境已安装或更新完成。")
    except subprocess.CalledProcessError as e:
        print("⚠️ Chromium 安装失败，可能是网络问题。")
        print(e.stderr.decode(errors="ignore"))
        print("请检查国内镜像连接或手动运行：playwright install chromium-headless-shell")


async def render_to_image(
    source: str,
    output_path: str = "output.png",
):
    """
    渲染网页或HTML为图片
    :param source: URL / HTML内容 / 本地文件路径
    :param output_path: 输出文件路径
    """
    await ensure_chromium_installed()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        # 加载内容
        print(f"🌐 正在加载：{source}")
        await page.goto(source, wait_until="domcontentloaded")
        element = await page.wait_for_selector("#mw-content-text", timeout=10000)
        print("已找到元素")

        await page.evaluate("""
            const imgs = document.querySelectorAll('img[loading="lazy"]');
            imgs.forEach(img => img.setAttribute('loading', 'eager'));
        """)

        await element.screenshot(path=output_path)
        print(f"✅ 截图完成：{output_path}")
        await browser.close()


if __name__ == "__main__":
    async def main():
        # 示例 1：直接截图网页
        await render_to_image("https://prts.wiki/w/娜仁图亚", "娜仁图亚.png")

        # 示例 2：截图 HTML 内容
        # html = "<h1>你好，PRTS！</h1><p>测试国内镜像环境渲染</p>"
        # await render_to_image(html, "example_html.png", input_type="html")

    asyncio.run(main())