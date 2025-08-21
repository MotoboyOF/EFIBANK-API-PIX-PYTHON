Projeto feito para testar sua API da EFIBANK, para recebimento automatico de PIX
acesse o site da efi bank pelo computador, vá em aplicações e gere uma nova aplicação com as autorizaões necessarias e pegue o certificado

0. Jogue seu certificado na pasta do conversor e executa o .bat, 
gere o certificado e não separe a secret key

1. crie um arquivo um .env com as seguintes configurações (produção ou homologação)

EFI_CLIENT_ID=seu client id

EFI_CLIENT_SECRET=seu client secret

EFI_SANDBOX=false (colocar true se for homologação)

EFI_CERTIFICATE_PATH=seu certificado (necessario ser no formato .pem)

EFI_PIX_KEY=sua chave pix do efibank

FLASK_SECRET_KEY=senhafortealeatoriatmj

2. Colocar o certificado na raiz do projeto 

3. pip install -r requirements.txt

4. python webhooktest.py