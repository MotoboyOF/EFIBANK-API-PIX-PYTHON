# Guia Rápido: Webhooks e Validação de Pagamentos PIX na Efí

Este guia mostra como registrar sua URL de webhook na Efí e validar pagamentos PIX em tempo real.  
São usados dois scripts principais: **`configurar_webhook.py`** e **`webhooktest.py`**.

## Execute:

```bash
    cd .\magika\
```

## 1. Configurando o Webhook (Honney Jar)

Para que a Efí possa notificar seu sistema sobre novos pagamentos, você primeiro precisa registrar o "endereço" do seu sistema na plataforma deles.

* **Arquivo Responsável:** `configurar_webhook.py`

### Objetivo
Este script é uma ferramenta de uso único. Sua função é registrar permanentemente a URL do seu sistema na plataforma da Efí, associando-a à sua chave PIX principal.

### Por que é Obrigatório?
Conforme a documentação oficial, a Efí exige esta configuração como um pré-requisito de segurança. Sem um webhook configurado para a sua chave PIX principal (a pagadora), a API não permitirá que sua aplicação **envie** PIX, bloqueando a funcionalidade de repasse automático.

### Como Usar
1.  **Edite o script:** Abra o arquivo `configurar_webhook.py` e altere as duas variáveis no topo com a sua chave PIX principal e a URL pública da sua aplicação.
2.  **Execute:** Rode o script **uma única vez** no seu terminal:
    ```bash
    python configurar_webhook.py
    ```
3.  **Confirme:** O terminal deve exibir uma mensagem de `--- SUCESSO! ---`. Uma vez executado com sucesso, esta configuração estará salva na sua conta Efí e você não precisará rodá-lo novamente, a menos que sua URL mude.

## 2. Validando o Recebimento de Pagamentos (O Servidor)

Depois que o webhook está configurado, sua aplicação precisa estar pronta para "ouvir" e processar as notificações de pagamento.

* **Arquivo Responsável:** `webhooktest.py`

### Objetivo
Receber as notificações automáticas (webhooks) que a Efí envia toda vez que um PIX destinado à sua chave principal é pago com sucesso. A chegada dessa notificação é a "validação do recebimento".

### Como Funciona
1.  O arquivo `webhooktest.py` cria um servidor web que fica online esperando por requisições.
2.  Dentro dele, a rota **`/webhook/pix`** é o endpoint específico que "escuta" as notificações da Efí.
3.  Quando um cliente paga um QR Code, a Efí envia os dados completos da transação (valor, txid, endToEndId, etc.) para a URL que você configurou no Passo 1.
4.  O código dentro da função `@app.route('/webhook/pix')` é executado. No exemplo, ele apenas exibe os dados no log (`logger.info(f"Dados do webhook: {data}")`). Este é o ponto de partida para qualquer automação. É aqui que você adicionaria a lógica para salvar no banco de dados, liberar um produto ou iniciar o repasse (split).

---

## Guia de Execução Rápido

Para testar o fluxo completo:

1.  **Preparação:**
    * Converta seu certificado `.p12` para `.pem` e coloque-o na raiz do projeto.
    * Crie o arquivo `.env` com suas credenciais de **Produção**.

2.  **Instalação de Dependências:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configuração (Passo Único):**
    * Edite e execute o `configurar_webhook.py` para registrar sua URL de webhook na Efí.

4.  **Execução do Servidor:**
    * Deixe o servidor principal rodando (seja no Railway ou localmente com Ngrok):
        ```bash
        python webhooktest.py
        ```
    * Gere um QR Code pela interface, pague-o e observe os logs do terminal. A notificação (webhook) deverá chegar e ser registrada, validando o recebimento.

    ![Logo Eopix](https://i.postimg.cc/q7nYcmLc/eopix-com-br.png)