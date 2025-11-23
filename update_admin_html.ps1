$filePath = "c:\Users\mathe\OneDrive\Área de Trabalho\Marcos Lima Fotografia Booking\admin.html"
$content = Get-Content $filePath -Raw

# Find the line with room-image input and replace it with file upload + URL input
$oldPattern = '                <div class="form-group">\r\n                    <label for="room-image">URL da Imagem</label>\r\n                    <input type="url" id="room-image" placeholder="https://...">\r\n                </div>'

$newPattern = @'
                <div class="form-group">
                    <label for="room-image">Imagem da Sala</label>
                    <input type="file" id="room-image-file" accept="image/*" style="margin-bottom: 10px;">
                    <small style="display: block; margin-bottom: 8px; color: #666;">Ou cole a URL de uma imagem:</small>
                    <input type="url" id="room-image" placeholder="https://..." style="display: block; width: 100%;">
                </div>
'@

$newContent = $content -replace [regex]::Escape($oldPattern), $newPattern

# Update script version
$newContent = $newContent -replace 'admin-script\.js\?v=7', 'admin-script.js?v=9'

Set-Content -Path $filePath -Value $newContent -NoNewline

Write-Host "Arquivo atualizado com sucesso!"
Write-Host "- Adicionado campo de upload de arquivo"
Write-Host "- Mantido campo de URL como alternativa"
Write-Host "- Atualizada versao do script para v9"
