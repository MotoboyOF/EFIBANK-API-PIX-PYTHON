# webhooktest.py
import os
import logging
import uuid
import traceback
import qrcode
import base64
from io import BytesIO
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv
from efipay import EfiPay


# Corrigir o caminho da pasta de templates
template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

app = Flask(__name__, template_folder=template_path)

# Carregar variáveis de ambiente
load_dotenv()

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("webhooktest.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-123')

# Configurações da EFI
credentials = {
    'client_id': os.getenv('EFI_CLIENT_ID'),
    'client_secret': os.getenv('EFI_CLIENT_SECRET'),
    'sandbox': os.getenv('EFI_SANDBOX', 'True').lower() == 'true',
    'certificate': os.getenv('EFI_CERTIFICATE_PATH', 'caminho/para/seu/certificado.pem')
}

logger.info(f"Configurando EFI com sandbox: {credentials['sandbox']}")
logger.info(f"Client ID: {credentials['client_id'][:5]}... (oculto por segurança)")
logger.info(f"Certificado: {credentials['certificate']}")

# Inicializar cliente EFI
try:
    efi = EfiPay(credentials)
    logger.info("Conexão com EFI configurada com sucesso")
except Exception as e:
    logger.error(f"Erro ao configurar conexão com EFI: {str(e)}")
    logger.error(traceback.format_exc())
    efi = None

# Produto para teste
PRODUTO_TESTE = {
    'nome': 'Produto Teste',
    'descricao': 'Descrição do produto de teste para pagamento via PIX',
    'valor': 1.00  # Valor em reais
}

@app.route('/')
def index():
    logger.info("Página inicial acessada")
    return render_template('index.html', produto=PRODUTO_TESTE)

@app.route('/gerar-qrcode', methods=['POST'])
def gerar_qrcode():
    try:
        logger.info("Solicitação para gerar QR Code recebida")
        
        if efi is None:
            logger.error("Tentativa de gerar QR Code sem conexão EFI configurada")
            return jsonify({
                'success': False,
                'error': 'Conexão com EFI não configurada'
            }), 500
            
        # Gerar txid único com UUID
        txid = str(uuid.uuid4()).replace('-', '')
        logger.info(f"TXID gerado: {txid}")
        
        # Parâmetros para a cobrança
        params = {
            'txid': txid
        }
        
        # Corpo da requisição
        pix_key = os.getenv('EFI_PIX_KEY')
        logger.info(f"Usando chave PIX: {pix_key}")
        
        body = {
            'calendario': {
                'expiracao': 3600  # 1 hora de expiração
            },
            'valor': {
                'original': f"{PRODUTO_TESTE['valor']:.2f}"
            },
            'chave': pix_key,
            'solicitacaoPagador': f'Pagamento - {PRODUTO_TESTE["nome"]}'
        }
        
        logger.info(f"Criando cobrança com params: {params} e body: {body}")
        
        # Criar cobrança imediata
        cobranca = efi.pix_create_immediate_charge(params=params, body=body)
        logger.info(f"Resposta da criação de cobrança: {cobranca}")
        
        # Obter o txid retornado pela EFI
        txid_efi = cobranca['txid']
        logger.info(f"TXID retornado pela EFI: {txid_efi}")

        # Obter ID da localização
        loc_id = cobranca['loc']['id']
        logger.info(f"Location ID obtido: {loc_id}")
        
        # Gerar string do QR Code
        qr_params = {
            'id': loc_id
        }
        logger.info(f"Gerando QR Code com params: {qr_params}")
        
        qrcode_data = efi.pix_generate_qrcode(params=qr_params)
        logger.info(f"Resposta do QR Code: {qrcode_data}")
        
        # Gerar imagem localmente a partir da string retornada
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=6,
            border=2,
        )
        qr.add_data(qrcode_data['qrcode'])
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        # Salvar txid na sessão
        session['txid'] = txid_efi
        session['valor'] = PRODUTO_TESTE['valor']
        logger.info(f"TXID salvo na sessão: {txid_efi}")
        
        return jsonify({
            'success': True,
            'qrcode': qrcode_data['qrcode'],
            'imagemQrcode': img_str,  # sempre nossa imagem gerada
            'txid': txid_efi,
            'valor': PRODUTO_TESTE['valor']
        })
        
    except Exception as e:
        logger.error(f"Erro ao gerar QR Code: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/verificar-pagamento', methods=['GET'])
def verificar_pagamento():
    try:
        txid = session.get('txid')
        logger.info(f"Verificando pagamento para TXID: {txid}")
        
        if not txid:
            logger.warning("Tentativa de verificar pagamento sem TXID na sessão")
            return jsonify({
                'success': False,
                'error': 'Nenhuma transação encontrada'
            }), 400
            
        # Consultar status da cobrança
        params = {
            'txid': txid
        }
        
        logger.info(f"Consultando cobrança com params: {params}")
        cobranca = efi.pix_detail_charge(params=params)
        logger.info(f"Resposta da consulta de cobrança: {cobranca}")
        
        # Verificar se foi paga
        status = cobranca.get('status', 'ATIVA')
        pago = status.upper() == 'CONCLUIDA'
        
        logger.info(f"Status da cobrança: {status}, Pago: {pago}")
        
        return jsonify({
            'success': True,
            'pago': pago,
            'status': status,
            'txid': txid
        })
        
    except Exception as e:
        logger.error(f"Erro ao verificar pagamento: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/webhook/pix', methods=['POST'])
def webhook_pix():
    try:
        logger.info("Webhook PIX recebido")
        
        # Verificar se é uma requisição válida da EFI
        # (implementar validação do HMAC se estiver usando skip-mTLS)
        
        data = request.get_json()
        logger.info(f"Dados do webhook: {data}")
        
        # Processar notificação de PIX
        if 'pix' in data:
            for pix in data['pix']:
                txid = pix.get('txid')
                valor = float(pix.get('valor', '0'))
                
                logger.info(f"Pagamento confirmado - TXID: {txid}, Valor: {valor}")
                
                # Aqui você processaria a confirmação do pagamento
                # e liberaria o produto para o cliente
        
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        logger.error(f"Erro no webhook: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'status': 'error'}), 500
    
@app.route('/cancelar-pix', methods=['POST'])
def cancelar_pix():
    try:
        txid = session.get('txid')
        if txid:
            logger.info(f"Cancelando PIX com TXID: {txid}")
            
            params = { 'txid': txid }
            body = { 'status': 'REMOVIDA_PELO_USUARIO_RECEBEDOR' }
            
            efi.pix_update_charge(params=params, body=body)
            logger.info(f"Cobrança {txid} cancelada")
            
            session.pop('txid', None)
        
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Erro ao cancelar PIX: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/teste-api')
def teste_api():
    try:
        logger.info("Testando conexão com API EFI")
        
        # Teste simples de conexão
        params = {
            'inicio': datetime.now().strftime('%Y-%m-%d'),
            'fim': datetime.now().strftime('%Y-%m-%d')
        }
        
        logger.info(f"Testando API com params: {params}")
        response = efi.pix_list_charges(params=params)
        logger.info(f"Resposta do teste de API: {response}")
        
        return jsonify({'success': True, 'response': response})
    except Exception as e:
        logger.error(f"Erro ao testar API: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    logger.info("Iniciando servidor Flask")
    app.run(debug=True, host='0.0.0.0', port=5000)