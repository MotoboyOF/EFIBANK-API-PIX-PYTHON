import os
import sys
from dotenv import load_dotenv
from efipay import EfiPay
import logging


CHAVE_PIX_PRINCIPAL = "CHAVE-PIX" 
WEBHOOK_URL = "https://www.site.com.br/webhook/pix"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

print("--- Iniciando configuração de Webhook na Efí Pay ---")

try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    certificate_filename = os.getenv('EFI_CERTIFICATE_PATH', 'efi-full.pem')
    certificate_path = os.path.join(BASE_DIR, certificate_filename)

    if not os.path.exists(certificate_path):
        raise FileNotFoundError(f"Arquivo de certificado não encontrado em: {certificate_path}")
    
    credentials = {
        'client_id': os.getenv('EFI_CLIENT_ID'),
        'client_secret': os.getenv('EFI_CLIENT_SECRET'),
        'sandbox': os.getenv('EFI_SANDBOX', 'false').lower() == 'true',
        'certificate': certificate_path
    }

    if not all([credentials['client_id'], credentials['client_secret']]):
        raise ValueError("Client ID ou Client Secret não encontrados no arquivo .env")

    print(f"Usando certificado: {credentials['certificate']}")
    print(f"Modo Sandbox: {credentials['sandbox']}")

    efi = EfiPay(credentials)

except Exception as e:
    logging.error(f"ERRO CRÍTICO na configuração inicial: {e}")
    sys.exit(1)

params = {
    'chave': CHAVE_PIX_PRINCIPAL
}
body = {
    'webhookUrl': WEBHOOK_URL
}

print(f"\nTentando configurar o webhook para a chave: {CHAVE_PIX_PRINCIPAL}")
print(f"Com a URL: {WEBHOOK_URL}\n")

try:

    headers = {
        'x-skip-mtls-checking': 'true'
    }
    
    response = efi.pix_config_webhook(params=params, body=body, headers=headers)
    
    print("--- SUCESSO! ---")
    print("O Webhook foi configurado com sucesso na sua conta Efí.")
    print("Resposta da API (esperado ser vazio ou status 204):", response)
    print("\nAgora você pode realizar um novo teste de pagamento.")

except Exception as e:
    print("--- FALHA! ---")
    logging.error(f"Ocorreu um erro ao tentar configurar o webhook: {e}")