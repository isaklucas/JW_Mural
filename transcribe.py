import subprocess
import os

# Caminho do arquivo enviado
audio_path = "C:/Users/Isaque/Downloads/0928.MP3"

try:
    # Diretório de saída (mesmo do áudio)
    output_dir = os.path.dirname(audio_path)
    
    # Rodar whisper via CLI (modelo base, idioma inglês)
    result = subprocess.run(
        [
            "whisper",
            audio_path,
            "--model", "base",
            "--language", "en",
            "--output_format", "txt",
            "--output_dir", output_dir
        ],
        capture_output=True,
        text=True
    )

    # Caminho do arquivo de transcrição gerado
    transcript_path = os.path.join(
        output_dir,
        os.path.splitext(os.path.basename(audio_path))[0] + ".txt"
    )

    # Log do caminho do arquivo TXT
    print(f"Arquivo de transcrição gerado em: {transcript_path}")

    # Abrir o arquivo TXT no final
    if os.path.exists(transcript_path):
        with open(transcript_path, "r", encoding="utf-8") as f:
            transcription = f.read().strip()
        print("Conteúdo da transcrição:\n")
        print(transcription)
    else:
        print("Falha ao gerar transcrição.")
        print("STDERR:", result.stderr)
except Exception as e:
    print(f"Erro: {e}")
    print("Certifique-se de que o comando 'whisper' está instalado e disponível no PATH.")
