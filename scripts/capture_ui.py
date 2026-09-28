import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1600, 'height': 950},
            device_scale_factor=2  # High-DPI 3200x1900 output
        )
        page = await context.new_page()
        
        print("Navigating to http://localhost:5173/...")
        await page.goto("http://localhost:5173/", wait_until="networkidle")
        await asyncio.sleep(2)
        
        # Click "+ New Chat" to start a fresh clean session
        new_chat_btn = page.locator("button:has-text('New Chat')")
        if await new_chat_btn.count() > 0:
            await new_chat_btn.first.click()
            await asyncio.sleep(1)

        textarea = page.locator("input[placeholder*='request'], textarea")
        send_btn = page.locator("button:has-text('Send')")
        
        print("Step 1: Submitting initial task request...")
        await textarea.fill("Create a formal leave letter for 5 days due to personal reasons")
        await send_btn.click()
        
        # Wait for Requirement Analyzer clarification question to appear
        print("Waiting for Requirement Analyzer response...")
        for _ in range(25):
            await asyncio.sleep(1)
            content = await page.inner_text("body")
            if "Requirement Analyzer" in content and ("addressed to" in content or "details" in content or "clarification" in content or "specify" in content):
                print("Clarification question received!")
                break
                
        await asyncio.sleep(2)
        
        print("Step 2: Submitting clarification details...")
        await textarea.fill("Address it to The Manager, from Karthick Balaji")
        await send_btn.click()
        
        print("Waiting for Plan, Document Agent execution, and Validation Agent pass...")
        for _ in range(45):
            await asyncio.sleep(1)
            content = await page.inner_text("body")
            if "Task completed successfully" in content or "output_1.docx" in content or "leave_letter.docx" in content or "Download DOCX" in content or "Document created successfully" in content:
                print("Execution and validation completed!")
                break
                
        await asyncio.sleep(3)
        
        os.makedirs("docs/figures", exist_ok=True)
        
        # Capture Figure 4: Functional Prototype UI (Full Workspace)
        fig4_path = os.path.abspath("docs/figures/figure_04_functional_prototype.png")
        await page.screenshot(path=fig4_path, full_page=False)
        print(f"Successfully captured Figure 4 (Full Interface): {fig4_path}")
        
        # Capture Figure 5: End-to-End Pipeline Trace (Focused execution trace & generated document artifact)
        fig5_path = os.path.abspath("docs/figures/figure_05_end_to_end_trace.png")
        # Clip the conversation log and the live agent trace panel (excluding sidebar)
        await page.screenshot(path=fig5_path, clip={'x': 260, 'y': 48, 'width': 1340, 'height': 902})
        print(f"Successfully captured Figure 5 (Focused Trace & Artifact): {fig5_path}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())

