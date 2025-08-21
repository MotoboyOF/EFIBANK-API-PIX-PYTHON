Projeto feito para testar sua API da EFIBANK, para recebimento automatico de PIX

1. Adicione um .env com as seguintes configurações (produção ou homologação)

EFI_CLIENT_ID=seu client id
EFI_CLIENT_SECRET=seu client secret
EFI_SANDBOX=false (colocar true se for produção)
EFI_CERTIFICATE_PATH=seu certificado (necessario ser no formato .pem e não ter senhas de acesso)
EFI_PIX_KEY=sua chave pix do efibank
FLASK_SECRET_KEY=senhafortealeatoriatmj

2. Colocar o certificado na raiz do projeto (converta de .p12 para .pem sem separar a senha dele)

3. pip install -r requirements.txt

4. python webhooktest.py