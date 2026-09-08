# Guia Prático de Deploy na Hetzner

A sua aplicação ALFRED está 100% pronta para Produção. Esta pasta (`ALFRED-Deploy`) contém tudo o que o seu servidor precisa.

## Passo a Passo

1. **Envie esta pasta para a VPS**
   Você pode usar um programa como o **FileZilla**, **WinSCP** ou o terminal.
   Copie a pasta `ALFRED-Deploy` inteira para a raiz do seu usuário (ex: `/root/ALFRED-Deploy`).

2. **Acesse sua VPS via SSH**
   Abra seu terminal e digite:
   `ssh root@IP_DA_SUA_VPS`

3. **Inicie o Servidor**
   Lá dentro do terminal da VPS, entre na pasta e ligue os contêineres:
   ```bash
   cd ALFRED-Deploy
   docker compose up -d --build
   ```

## E o Domínio e o SSL?
Como você já apontou `alfred.gestaocomercial360.com.br` para o **Cloudflare**, basta ir no painel do Cloudflare:
1. Vá em **SSL/TLS**.
2. Defina o modo de encriptação como **Flexible** (Flexível).
Dessa forma, o Cloudflare garantirá o "Cadeadinho Verde" (HTTPS) para o usuário final e redirecionará a requisição normal (Porta 80) para a nossa VPS, que será recebida pelo Nginx e roteada para o seu Córtex!

## Como ver os logs se algo der errado?
Lá na VPS, basta digitar:
`docker logs -f alfred_backend`
ou
`docker logs -f alfred_nginx`
