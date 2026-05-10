from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import re
from datetime import datetime
import os

class KabumCategoryAdapter:
    def __init__(self):
        self.url = "https://www.kabum.com.br/hardware/placa-de-video-vga"
        self.driver_path = "geckodriver.exe" 
        
        firefox_options = Options()
        firefox_options.add_argument("--headless") 

        try:
            self.service = Service(executable_path=self.driver_path)
            self.driver = webdriver.Firefox(service=self.service, options=firefox_options)
        except Exception as e:
            print(f"Falha Crítica ao iniciar o Navegador: {e}")
            raise

    def clean_price(self, price_str):
        """Converte 'R$ 1.172,15' em float 1172.15"""
        try:
            clean_val = price_str.replace('R$', '').replace('.', '').replace(',', '.').strip()
            return float(clean_val)
        except:
            return 0.0

    def extract_brand(self, name):
        """Extrai a marca baseada em palavras-chave comuns no nome do produto"""
        brands = ["ASUS", "MSI", "GIGABYTE", "GALAX", "ZOTAC", "PALIT", "PNY", 
                  "POWERCOLOR", "SAPPHIRE", "XFX", "ASROCK", "PCYES"]
        for brand in brands:
            if brand in name.upper():
                return brand
        return "OUTRA"

    def collect(self):
        print(f"--- Iniciando coleta na Categoria VGA: {self.url} ---")
        captured_data = []
        capture_time = datetime.now()

        try:
            self.driver.get(self.url)
            wait = WebDriverWait(self.driver, 20)
            
            target_class = r".flex.flex-col.relative.gap-4.p-8.pt-2.rounded-\[16px\].group.min-w-\[165px\].max-w-\[230px\].h-\[366px\].bg-white"
            
            print("Aguardando renderização dos cards...")
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, target_class)))

            products = self.driver.find_elements(By.CSS_SELECTOR, target_class)
            print(f"Total de GPUs detectadas: {len(products)}")

            for index, product in enumerate(products, 1):
                try:
                    # 1 e 5. EXTRAÇÃO DO ID E GERAÇÃO DA URL
                    # O href costuma ser: /produto/475647/nome-do-produto
                    href = product.get_attribute("href")
                    product_id = "0"
                    if href:
                        id_match = re.search(r"/produto/(\d+)/", href)
                        product_id = id_match.group(1) if id_match else "0"
                    
                    product_url = f"https://www.kabum.com.br/produto/{product_id}"

                    # 2. CAPTURA DO NOME
                    try:
                        name = product.find_element(By.CSS_SELECTOR, "span.line-clamp-2").text.strip()
                    except:
                        name = "Nome não localizado"

                    # 3. CAPTURA DO PREÇO E CONVERSÃO
                    price_raw = "0"
                    try:
                        price_spans = product.find_elements(By.CSS_SELECTOR, "span.text-gray-800.font-semibold")
                        if price_spans:
                            price_raw = "".join([s.text.strip() for s in price_spans if "R$" in s.text or "," in s.text])
                    except:
                        raw_text = self.driver.execute_script("return arguments[0].innerText;", product)
                        for line in raw_text.split('\n'):
                            if "R$" in line and "," in line:
                                price_raw = line.strip()
                                break
                    
                    price_numeric = self.clean_price(price_raw)

                    # 4. STORE NAME
                    store_name = "Kabum"

                    # 6. EXTRAÇÃO DA MARCA (BRAND)
                    brand = self.extract_brand(name)

                    # 7. VERIFICAÇÃO DE DISPONIBILIDADE
                    # Se o preço for 0 ou o texto contiver 'Esgotado', is_available é False
                    is_available = True if price_numeric > 0 else False

                    # 8. MOMENTO DA CAPTURA
                    captured_at = capture_time.strftime("%Y-%m-%d %H:%M:%S")

                    # Adicionando ao dicionário de dados
                    captured_data.append({
                        "id": product_id,
                        "product_name": name,
                        "price_numeric": price_numeric,
                        "store_name": store_name,
                        "product_url": product_url,
                        "brand": brand,
                        "is_available": is_available,
                        "captured_at": captured_at
                    })

                except Exception as e:
                    continue

            # 1. Garante que a pasta data exista
            output_dir = "data"
            os.makedirs(output_dir, exist_ok=True)

            # 2. Define o nome do arquivo e o caminho completo
            filename = f"kabum_{capture_time.strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = os.path.join(output_dir, filename)

            keys = ["id", "product_name", "price_numeric", "store_name", "product_url", "brand", "is_available", "captured_at"]
            
            # 3. Abre o arquivo usando o caminho completo
            with open(filepath, 'w', newline='', encoding='utf-8') as output_file:
                dict_writer = csv.DictWriter(output_file, fieldnames=keys)
                dict_writer.writeheader()
                dict_writer.writerows(captured_data)
            
            print(f"✅ Sucesso! Arquivo gerado em: {filepath} ({len(captured_data)} registros).")

        except Exception as e:
            print(f"Erro crítico: {e}")
        
        finally:
            self.driver.quit()

if __name__ == "__main__":
    bot = KabumCategoryAdapter()
    bot.collect()