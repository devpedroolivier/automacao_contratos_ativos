# main.py — login simples no SGC Sabesp (1 arquivo)
from playwright.sync_api import sync_playwright, TimeoutError

URL   = "https://sgc.sabesp.com.br"
USER  = "Lcgaraujo"
PASS  = "352268@Sabesp2025+"

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # mude p/ True se quiser
        # 1) Tenta autenticação via popup do navegador (HTTP Basic/Negotiate)
        context = browser.new_context(
            http_credentials={"username": USER, "password": PASS},
            ignore_https_errors=True
        )
        page = context.new_page()

        # Se aparecer alert() JS, aceitar automaticamente
        page.on("dialog", lambda d: d.accept())

        try:
            page.goto(URL, wait_until="domcontentloaded")
            # 2) Fallback rápido: se houver formulário na página, tenta preencher
            try:
                # Se existir campo de senha, tentamos preencher usuário e senha
                pwd_field = page.locator("input[type='password']").first
                if pwd_field.count():
                    # tenta achar o campo de usuário por heurística comum
                    user_field = page.locator(
                        "input[type='text'], input[type='email'], "
                        "input[name*='user' i], input[name*='login' i], "
                        "input[id*='user' i], input[id*='login' i]"
                    ).first
                    if user_field.count():
                        user_field.fill(USER)
                        pwd_field.fill(PASS)
                        submit = page.locator(
                            "button[type='submit'], input[type='submit'], "
                            "button:has-text('Entrar'), button:has-text('Acessar')"
                        ).first
                        if submit.count():
                            submit.click()
            except Exception:
                # Sem drama: se não for formulário, seguimos com o que já deu certo
                pass

            page.wait_for_timeout(2000)  # só pra visualizar
            page.screenshot(path="home.png", full_page=True)
            print("OK: Acesso realizado. Screenshot salvo em home.png")

        except TimeoutError:
            page.screenshot(path="erro_timeout.png", full_page=True)
            print("Timeout. Screenshot salvo em erro_timeout.png")
        finally:
            context.close()
            browser.close()

if __name__ == "__main__":
    run()
