from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class KabumCategoryAdapter:
    def __init__(self):
        self.url = "https://www.kabum.com.br/hardware/placa-de-video-vga"
        self.driver_path = "geckodriver.exe" 
        
        firefox_options = Options()
        # remova o comentário abaixo para rodar o navegador em modo headless
        # firefox_options.add_argument("--headless") 

        try:
            self.service = Service(executable_path=self.driver_path)
            self.driver = webdriver.Firefox(service=self.service, options=firefox_options)
        except Exception as e:
            print(f"Falha Crítica ao iniciar o Navegador: {e}")
            raise

    def collect(self):
        print(f"--- Iniciando coleta na Categoria VGA: {self.url} ---")
        try:
            self.driver.get(self.url)

            # Espera o container principal carregar, 20 segundos de limite
            wait = WebDriverWait(self.driver, 20)
            
            target_class = r".flex.flex-col.relative.gap-4.p-8.pt-2.rounded-\[16px\].group.min-w-\[165px\].max-w-\[230px\].h-\[366px\].bg-white"
            
            print("Aguardando renderização dos cards...")
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, target_class)))

            # Captura todos os produtos
            products = self.driver.find_elements(By.CSS_SELECTOR, target_class)
            total = len(products)
            print(f"Total de GPUs detectadas: {total}")

            # Vamos percorrer todos os 60 itens encontrados
            for index, product in enumerate(products, 1):
                try:
                    # Capturamos o texto completo do card via JavaScript
                    raw_text = self.driver.execute_script("return arguments[0].innerText;", product)
                    
                    # Limpamos e dividimos o texto por linhas
                    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]

                    if not lines:
                        continue

                    # Lógica de extração:
                    # 1. O nome ainda apresenta problema de captura, mas geralmente é a primeira linha do card
                    name = lines[0]
                    
                    # 2. O preço é qualquer linha que contenha o símbolo de moeda "R$"
                    price = "Preço não identificado"
                    for line in lines:
                        if "R$" in line:
                            price = line
                            break
                    
                    # 3. O link do produto
                    try:
                        link = product.find_element(By.TAG_NAME, "a").get_attribute("href")
                    except:
                        link = "Link não disponível"

                    # Print formatado no terminal
                    print(f"{index:02d}. {name[:55]}... | {price} | URL: {link[:40]}...")

                except Exception as inner_e:
                    # Se um card falhar, avisamos mas continuamos para o próximo
                    print(f"Erro no item {index}: {inner_e}")
                    continue

        except Exception as e:
            print(f"Erro crítico na estrutura da página: {e}")
        
        finally:
            self.driver.quit()
            print("\n--- Navegador fechado. Coleta finalizada. ---")

if __name__ == "__main__":
    bot = KabumCategoryAdapter()
    bot.collect()