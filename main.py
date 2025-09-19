# main.py — acesso + exportar excel no SGC (com download salvo + tela maximizada)
import os
from playwright.sync_api import sync_playwright, TimeoutError

URL   = "https://sgc.sabesp.com.br"
USER  = "Lcgaraujo"
PASS  = "352268@Sabesp2025+"

DOWNLOAD_DIR = "downloads"
OUTPUT_FILE  = os.path.join(DOWNLOAD_DIR, "contratos.xlsx")

def run():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        # Cria contexto com tela "maximizada"
        # None => usa resolução da tela do host
        context = browser.new_context(
            http_credentials={"username": USER, "password": PASS},
            ignore_https_errors=True,
            accept_downloads=True,
            viewport=None  # <= aqui é o truque
        )

        page = context.new_page()
        page.bring_to_front()

        # aceitar automaticamente alert() se aparecer
        page.on("dialog", lambda d: d.accept())

        try:
            print("➡️ Acessando site...")
            page.goto(URL, wait_until="load", timeout=60000)

            # aguarda a lista de ativos e clica
            print("➡️ Clicando em Lista de Ativos...")
            page.wait_for_selector(
                "body > div > app-resumos > div > div.col-sm-12.col-md-10 > div:nth-child(1) > app-contratos > div.cards-container > app-pie-resumo:nth-child(2) > div > div > a",
                timeout=60000
            )
            page.click("body > div > app-resumos > div > div.col-sm-12.col-md-10 > div:nth-child(1) > app-contratos > div.cards-container > app-pie-resumo:nth-child(2) > div > div > a")

            # abre menu exportar
            print("➡️ Abrindo menu de exportação...")
            page.wait_for_selector("#dropdownExportar", timeout=60000)
            page.click("#dropdownExportar")

            # espera pelo download ao clicar no botão
            print("➡️ Exportando para Excel...")
            with page.expect_download() as download_info:
                page.click("body > div > app-lista-contratos > div > div > div:nth-child(2) > dx-data-grid > div > div.dx-datagrid-header-panel > div > div > div.dx-toolbar-after > div:nth-child(3) > div > div.dropdown-menu-config.dropdown-menu.dropdown-menu-right.dropdown-menu-excel.show > div > a")

            download = download_info.value
            download.save_as(OUTPUT_FILE)

            print(f"✅ Exportação concluída! Arquivo salvo em: {OUTPUT_FILE}")

        except TimeoutError:
            print("⛔ Timeout ao esperar algum seletor.")
            page.screenshot(path="erro.png", full_page=True)
        finally:
            context.close()
            browser.close()

if __name__ == "__main__":
    run()
