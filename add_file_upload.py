# -*- coding: utf-8 -*-
import os

file_path = r"c:\Users\mathe\OneDrive\Área de Trabalho\Marcos Lima Fotografia Booking\admin.html"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the room-image input section
old_section = '''                <div class="form-group">
                    <label for="room-image">URL da Imagem</label>
                    <input type="url" id="room-image" placeholder="https://...">
                </div>'''

new_section = '''                <div class="form-group">
                    <label for="room-image">Imagem da Sala</label>
                    <input type="file" id="room-image-file"accept="image/*" style="margin-bottom: 10px;">
                    <small style="display: block; margin-bottom: 8px; color: #666;">Ou cole a URL de uma imagem:</small>
                    <input type="url" id="room-image" placeholder="https://..." style="display: block; width: 100%;">
                </div>'''

content = content.replace(old_section, new_section)

# Update script version
content = content.replace('admin-script.js?v=7', 'admin-script.js?v=9')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Sucesso! Arquivo atualizado:")
print("- Campo de upload de arquivo adicionado")
print("- Campo de URL mantido como alternativa")
print("- Versao do script atualizada para v9")
