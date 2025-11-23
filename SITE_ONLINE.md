# 🎉 PARABÉNS! SEU SISTEMA DE RESERVAS ESTÁ ONLINE! 🎉

## URLs do Seu Sistema

✅ **Site de Reservas (para clientes):**
https://marcos-lima-booking.vercel.app

✅ **Painel Administrativo:**
https://marcos-lima-booking.vercel.app/admin.html
- Login: `admin`
- Senha: `admin123`

✅ **Backend API:**
https://marcos-lima-booking.onrender.com

---

## 🔗 INTEGRAR NO ALBOOM

### Opção 1: iFrame Completo (Recomendado)

Use este código HTML no widget de código customizado do Alboom:

```html
<div style="width: 100%; max-width: 1200px; margin: 0 auto; padding: 20px;">
    <iframe 
        src="https://marcos-lima-booking.vercel.app" 
        width="100%" 
        height="1000px" 
        frameborder="0"
        style="border: none; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
    </iframe>
</div>
```

**Como adicionar no Alboom:**
1. Acesse o editor do seu site Alboom
2. Crie uma nova página chamada "Reservas" ou "Agendar Estúdio"
3. Adicione um bloco **"HTML/Código Personalizado"**
4. Cole o código acima
5. Salve e publique!

---

### Opção 2: Botão de Redirecionamento (Mais Simples)

Se o Alboom não permitir iframe, use um botão:

```html
<div style="text-align: center; padding: 40px 20px;">
    <a href="https://marcos-lima-booking.vercel.app" 
       target="_blank"
       style="display: inline-block; 
              background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
              color: white; 
              padding: 18px 40px; 
              text-decoration: none; 
              border-radius: 30px;
              font-size: 18px;
              font-weight: 600;
              box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
              transition: all 0.3s ease;">
        📅 Reservar Estúdio
    </a>
</div>
```

---

## 📱 TESTAR O SISTEMA

### 1. Teste a Página de Reservas
- Acesse: https://marcos-lima-booking.vercel.app
- Selecione uma sala
- Escolha data e horário
- Faça uma reserva teste

### 2. Teste o Painel Admin
- Acesse: https://marcos-lima-booking.vercel.app/admin.html
- Login: `admin` / `admin123`
- Veja a reserva que você fez
- Teste aprovar/rejeitar
- Adicione novas salas
- Configure horários de funcionamento

---

## ⚙️ CONFIGURAÇÕES IMPORTANTES

### Alterar Senha do Admin

**IMPORTANTE:** Troque a senha padrão por segurança!

1. Abra o arquivo `admin-script.js` no seu computador
2. Na linha 2-5, você vai ver:
   ```javascript
   const ADMIN_CREDENTIALS = {
       username: 'admin',
       password: 'admin123'
   };
   ```
3. Mude para:
   ```javascript
   const ADMIN_CREDENTIALS = {
       username: 'admin',
       password: 'SUASENHAFORTE123'
   };
   ```
4. Salve o arquivo
5. Faça commit e push:
   ```powershell
   git add admin-script.js
   git commit -m "Update admin password"
   git push
   ```
6. Aguarde 2 minutos - o Vercel vai atualizar automaticamente!

---

## 📋 PRÓXIMOS PASSOS

- [ ] **Testar todo o fluxo de reserva**
- [ ] **Adicionar suas salas reais no admin**
- [ ] **Configurar horários de funcionamento**
- [ ] **Trocar a senha do admin**
- [ ] **Integrar no Alboom**
- [ ] **Compartilhar o link com clientes**
- [ ] **(Opcional)** Configurar domínio personalizado

---

## ⚠️ LIMITAÇÕES DO PLANO GRATUITO

### Backend (Render.com - Free)
- ⚠️ **"Dorme" após 15min sem uso** - primeira requisição leva ~30 segundos
- ⚠️ **750 horas/mês** - suficiente para uso moderado
- ⚠️ **Banco SQLite pode perder dados** em redeployments

### Frontend (Vercel - Free)
- ✅ **Totalmente funcional**
- ✅ **Bandwidth ilimitado**
- ✅ **100% confiável**

### Quando Atualizar para Pago?

Considere plano pago (~$7/mês) quando:
- Tiver mais de 50 reservas/mês
- Backend "dormindo" incomodar clientes
- Precisar de banco PostgreSQL confiável
- Quiser uploads de imagens garantidos

---

## 🔄 COMO FAZER ATUALIZAÇÕES

### Atualizar Código

1. Edite os arquivos no seu computador
2. Faça commit:
   ```powershell
   git add .
   git commit -m "Descrição da mudança"
   git push
   ```
3. Render e Vercel atualizam automaticamente!

### Ver Logs de Erro

- **Backend:** https://dashboard.render.com → seu serviço → "Logs"
- **Frontend:** https://vercel.com/dashboard → seu projeto → "Logs"

---

## 📞 SUPORTE

### URLs Importantes
- **Render Dashboard:** https://dashboard.render.com
- **Vercel Dashboard:** https://vercel.com/dashboard
- **GitHub Repo:** https://github.com/matheus9607-lgtm/booking-system

### Dúvidas Comuns

**Q: O site está lento na primeira vez**
A: Normal! Backend gratuito "dorme". Aguarde 30s na primeira requisição.

**Q: Como adiciono mais salas?**
A: Acesse o admin, vá em "Salas" → "+ Nova Sala"

**Q: Como bloqueio horários?**
A: Admin → "Disponibilidade" → selecione sala e bloqueie

**Q: Perdi reservas após atualização**
A: Use banco PostgreSQL (recomendado para produção)

---

## 🎊 PRONTO!

Seu sistema de reservas está **100% funcional** e **online**!

**Próxima etapa:** Integre no Alboom e comece a receber reservas!

Qualquer dúvida, estou aqui! 🚀
