# Guia Passo a Passo - Deploy do Sistema de Reservas

## ✅ ETAPA 1: PREPARAR GIT E GITHUB (15 min)

### Passo 1.1: Instalar Git (se não tiver)
1. Baixe em: https://git-scm.com/downloads
2. Instale com as opções padrão
3. Reinicie o computador se necessário

### Passo 1.2: Criar Repositório no GitHub
1. Acesse: https://github.com
2. Faça login (ou crie uma conta gratuita)
3. Clique no botão verde **"New"** (ou "+" → New repository)
4. Nome do repositório: `booking-system` (ou outro nome)
5. Deixe como **Público**
6. **NÃO** marque "Add README"
7. Clique em **"Create repository"**

### Passo 1.3: Subir Código para o GitHub
Abra o PowerShell na pasta do projeto e execute:

```powershell
cd "c:\Users\mathe\OneDrive\Área de Trabalho\Marcos Lima Fotografia Booking"

# Inicializar Git
git init

# Adicionar todos os arquivos
git add .

# Fazer primeiro commit
git commit -m "Initial commit - Booking system"

# Conectar com GitHub (substitua SEU-USUARIO pelo seu nome de usuário)
git remote add origin https://github.com/SEU-USUARIO/booking-system.git

# Enviar código
git branch -M main
git push -u origin main
```

**⚠️ IMPORTANTE:** Quando pedir usuário/senha do GitHub:
- Usuário: seu email do GitHub
- Senha: use um **Personal Access Token** (não a senha normal)
  - Criar token: https://github.com/settings/tokens
  - Marque: `repo` (acesso completo)

---

## ✅ ETAPA 2: DEPLOY DO BACKEND (20 min)

### Passo 2.1: Criar Conta no Render.com
1. Acesse: https://render.com
2. Clique em **"Get Started for Free"**
3. Faça login com sua conta do GitHub
4. Autorize o Render a acessar seus repositórios

### Passo 2.2: Criar Web Service
1. No painel do Render, clique em **"New +"** → **"Web Service"**
2. Selecione o repositório `booking-system`
3. Clique em **"Connect"**

### Passo 2.3: Configurar o Service
Preencha os campos:

- **Name**: `booking-backend` (ou outro nome)
- **Region**: `Oregon (US West)` (mais próximo)
- **Branch**: `main`
- **Root Directory**: (deixe vazio)
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python server/app.py`

### Passo 2.4: Configurar Plano
- Selecione: **Free** (R$ 0/mês)
- **⚠️ Atenção:** O serviço "dorme" após 15min sem uso

### Passo 2.5: Adicionar Variáveis de Ambiente (Opcional)
Clique em **"Advanced"** → **"Add Environment Variable"**:
- `FLASK_ENV` = `production`

### Passo 2.5.1: Configurar Banco de Dados (CRÍTICO PARA NÃO PERDER DADOS)
Para que seus dados não sumam quando o servidor reiniciar, você precisa conectar ao PostgreSQL:

1. No painel do Render, clique em **"New +"** → **"PostgreSQL"**.
2. Nome: `booking-db` (ou outro).
3. Plano: **Free**.
4. Clique em **"Create Database"**.
5. Copie a **"Internal Database URL"** (começa com `postgresql://...`).
6. Volte para o seu **Web Service** (o backend que você criou no passo 2.2).
7. Vá em **"Environment"** → **"Add Environment Variable"**.
8. Chave: `DATABASE_URL`
9. Valor: (Cole a URL que você copiou do banco).
10. Salve as alterações. O Render vai reiniciar o serviço automaticamente.

### Passo 2.6: Deploy!
1. Clique em **"Create Web Service"**
2. Aguarde 5-10 minutos enquanto faz o deploy
3. Quando aparecer **"Live"** em verde, está pronto!

### Passo 2.7: Copiar URL do Backend
Você vai ver algo como:
```
https://booking-backend-XXXX.onrender.com
```

**⭐ GUARDE ESSA URL! Vamos usar na próxima etapa.**

---

## ✅ ETAPA 3: PREPARAR FRONTEND (10 min)

### Passo 3.1: Atualizar URLs no Código
Você precisa editar 2 arquivos e colocar a URL do seu backend:

**Arquivo 1: `script.js`**
Procure por:
```javascript
const API_URL = `http://${window.location.hostname}:5000/api`;
```

Substitua por:
```javascript
const API_URL = 'https://SEU-BACKEND.onrender.com/api';
```

**Arquivo 2: `admin-script.js`**
Procure por:
```javascript
const API_URL = `http://${window.location.hostname}:5000/api`;
```

Substitua por:
```javascript
const API_URL = 'https://SEU-BACKEND.onrender.com/api';
```

### Passo 3.2: Fazer Commit das Mudanças
```powershell
git add .
git commit -m "Update API URLs for production"
git push
```

---

## ✅ ETAPA 4: DEPLOY DO FRONTEND (15 min)

### Opção A: Vercel (Recomendado)

#### Passo 4.1: Criar Conta
1. Acesse: https://vercel.com
2. Clique em **"Sign Up"**
3. Faça login com GitHub

#### Passo 4.2: Importar Projeto
1. Clique em **"Add New..."** → **"Project"**
2. Selecione o repositório `booking-system`
3. Clique em **"Import"**

#### Passo 4.3: Configurar
- **Framework Preset**: `Other`
- **Root Directory**: `./` (raiz)
- **Build Command**: (deixe vazio)
- **Output Directory**: `./` (raiz)

#### Passo 4.4: Deploy
1. Clique em **"Deploy"**
2. Aguarde 2-3 minutos
3. Quando aparecer confete 🎉, está pronto!

#### Passo 4.5: Copiar URL
Você vai ver algo como:
```
https://booking-system-XXXX.vercel.app
```

**⭐ ESSA É A URL DO SEU SITE DE RESERVAS!**

---

## ✅ ETAPA 5: TESTAR TUDO (5 min)

### Teste 1: Acessar o Site
1. Abra: `https://SEU-SITE.vercel.app`
2. Deve aparecer a página de reservas
3. Tente selecionar uma sala e horário

### Teste 2: Acessar Admin
1. Abra: `https://SEU-SITE.vercel.app/admin.html`
2. Login: `admin` / `admin123`
3. Verifique se carrega as salas

---

## ✅ ETAPA 6: INTEGRAR NO ALBOOM (10 min)

### Passo 6.1: Criar Código do iFrame
Use este código (substitua a URL):

```html
<div style="width: 100%; max-width: 1200px; margin: 0 auto;">
    <iframe 
        src="https://SEU-SITE.vercel.app" 
        width="100%" 
        height="900px" 
        frameborder="0"
        style="border: none; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
    </iframe>
</div>
```

### Passo 6.2: Adicionar no Alboom
1. Acesse o editor do seu site Alboom
2. Crie uma nova página chamada **"Reservas"** ou **"Agendar"**
3. Adicione um bloco **"HTML"** ou **"Código Personalizado"**
4. Cole o código do iframe acima
5. Ajuste a altura se necessário (mude `900px`)
6. Salve e publique!

---

## 🎉 PRONTO!

Seu sistema de reservas está online e integrado ao Alboom!

**URLs importantes:**
- Site de reservas: `https://SEU-SITE.vercel.app`
- Painel admin: `https://SEU-SITE.vercel.app/admin.html`
- Backend API: `https://SEU-BACKEND.onrender.com`

---

## ⚠️ LIMITAÇÕES DO PLANO GRATUITO

1. **Backend "dorme"**: Após 15min sem uso, primeira requisição demora ~30s
2. **Banco SQLite**: Pode perder dados em redeployments
3. **Uploads**: Podem ser perdidos em atualizações

**Solução:** Migrar para plano pago (~$7/mês) quando tiver clientes reais.

---

## 📞 PRÓXIMOS PASSOS

- [ ] Testar fazer uma reserva completa
- [ ] Configurar domínio personalizado (opcional)
- [ ] Adicionar mais salas no admin
- [ ] Treinar equipe para usar o painel admin

---

**Dúvidas?** Me chame a qualquer momento!
