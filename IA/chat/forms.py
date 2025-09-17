# Seu_App/forms.py

from django import forms
from .models import Conversa, PersonalidadeIA
from django.core.exceptions import ValidationError

# Define o limite de arquivos e o tamanho máximo, se aplicável
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB

class MensagemUsuarioForm(forms.Form):
    """
    Formulário para validar as entradas do usuário no chat, incluindo texto,
    ID da conversa, personalidade e anexos (arquivos e áudio).
    """
    mensagem = forms.CharField(
        required=False,
        # CORREÇÃO: Usar um widget de input de texto normal
        widget=forms.TextInput(attrs={'placeholder': 'Digite sua mensagem...'}),
        strip=True
    )
    conversa_id = forms.CharField(required=False)
    personalidade = forms.CharField(required=True)
    arquivos = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput
    )
    audio_file = forms.FileField(required=False)

    def clean_conversa_id(self):
        conversa_id = self.cleaned_data.get('conversa_id')
        if conversa_id:
            try:
                uuid.UUID(conversa_id)
            except ValueError:
                raise ValidationError("O ID da conversa não é um UUID válido.")
        return conversa_id

    def clean_arquivos(self):
        files = self.files.getlist('arquivos')
        for file in files:
            if file.size > MAX_UPLOAD_SIZE:
                raise ValidationError(
                    f"O arquivo '{file.name}' é muito grande (máximo: {MAX_UPLOAD_SIZE // 1024 // 1024} MB)."
                )
        return files

    def clean_audio_file(self):
        audio_file = self.cleaned_data.get('audio_file')
        if audio_file and audio_file.size > MAX_UPLOAD_SIZE:
            raise ValidationError(
                f"O arquivo de áudio é muito grande (máximo: {MAX_UPLOAD_SIZE // 1024 // 1024} MB)."
            )
        return audio_file
    
    def clean(self):
        cleaned_data = super().clean()
        mensagem = cleaned_data.get('mensagem')
        arquivos = self.files.getlist('arquivos')
        audio_file = self.files.get('audio_file')

        if not mensagem and not arquivos and not audio_file:
            raise ValidationError(
                "Você deve fornecer pelo menos uma mensagem, um arquivo ou um áudio."
            )
        
        return cleaned_data