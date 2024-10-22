import os
import subprocess
import matplotlib.pyplot as plt

def convert_video(input_file, output_file, codec):
    """Converte o vídeo para o codec especificado."""
    cmd = [
        'ffmpeg', '-i', input_file, '-c:v', codec, '-crf', '23', output_file
    ]
    process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    
    # Verificar se a conversão foi bem-sucedida
    if not os.path.exists(output_file):
        raise FileNotFoundError(f"Erro: Arquivo de saída '{output_file}' não foi criado.")
    
    print(f"Conversão para {codec} concluída com sucesso.")
    

def calculate_metrics(input_file, output_file):
    #Calcula PSNR, SSIM, taxa de bits e tamanho do arquivo.
    
    # Verifica se o arquivo de saída existe
    if not os.path.exists(output_file):
        raise FileNotFoundError(f"Arquivo de saída '{output_file}' não encontrado. Verifique se a conversão foi bem-sucedida.")

    # Comando para calcular o PSNR e SSIM usando FFmpeg
    cmd = [
        'ffmpeg', '-i', output_file, '-i', input_file, '-lavfi', 
        '[0:v][1:v]psnr=stats_file=psnr.log;[0:v][1:v]ssim=stats_file=ssim.log', 
        '-f', 'null', '-'
    ]

    # Executa o comando e captura a saída
    process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    
    # Exibe a saída completa para depuração
    print("FFmpeg output:", process.stderr)

    # Busca o valor de PSNR na saída
    psnr_lines = [line for line in process.stderr.split('\n') if 'average:' in line]
    if not psnr_lines:
        raise ValueError("Não foi possível encontrar a linha PSNR na saída do FFmpeg.")
    
    psnr_value_str = psnr_lines[0].split('average:')[1].strip().split()[0]
    print("PSNR value string:", psnr_value_str)  # print de depuração
    psnr_value = float(psnr_value_str)

    # Busca o valor de SSIM na saída
    ssim_lines = [line for line in process.stderr.split('\n') if 'All:' in line]
    if not ssim_lines:
        raise ValueError("Não foi possível encontrar a linha SSIM na saída do FFmpeg.")
    
    ssim_value_str = ssim_lines[0].split('All:')[1].split('(')[0].strip().split()[0]
    print("SSIM value string:", ssim_value_str)  # print pra depurar
    ssim_value = float(ssim_value_str)

    # Pega o tamanho do arquivo gerado
    file_size = os.path.getsize(output_file) / 1024 / 1024  # em MB
    
    # Bitrate do arquivo convertido
    cmd_bitrate = [
        'ffprobe', '-v', 'error', '-select_streams', 'v:0', 
        '-show_entries', 'stream=bit_rate', 
        '-of', 'default=noprint_wrappers=1:nokey=1', 
        output_file
    ]
    bitrate = subprocess.check_output(cmd_bitrate).decode('utf-8').strip()
    print("Bitrate value string:", bitrate)  # print pra depurar
    bitrate_value = float(bitrate)

    return psnr_value, ssim_value, bitrate_value, file_size

def plot_results(results):
    """Gera gráficos de PSNR, SSIM, taxa de bits e tamanho de arquivo."""
    codecs = [r[0] for r in results]
    psnr_values = [r[1] for r in results]
    ssim_values = [r[2] for r in results]
    bitrate_values = [r[3] for r in results]
    file_size_values = [r[4] for r in results]
    
    # cria uma unica imagem png com os graficos
    fig, axs = plt.subplots(4, 1, figsize=(10, 24))

    # Gráfico PSNR
    axs[0].bar(codecs, psnr_values, color='blue')
    axs[0].set_title('Comparação de PSNR')
    axs[0].set_xlabel('Codec')
    axs[0].set_ylabel('PSNR')

    # Gráfico SSIM
    axs[1].bar(codecs, ssim_values, color='green')
    axs[1].set_title('Comparação de SSIM')
    axs[1].set_xlabel('Codec')
    axs[1].set_ylabel('SSIM')

    # Gráfico Taxa de Bits
    axs[2].bar(codecs, bitrate_values, color='orange')
    axs[2].set_title('Comparação de Taxa de Bits')
    axs[2].set_xlabel('Codec')
    axs[2].set_ylabel('Taxa de Bits (bps)')

    # Gráfico Tamanho do Arquivo
    axs[3].bar(codecs, file_size_values, color='red')
    axs[3].set_title('Comparação de Tamanho de Arquivo')
    axs[3].set_xlabel('Codec')
    axs[3].set_ylabel('Tamanho do Arquivo (MB)')

    # Ajustar layout para evitar sobreposição
    plt.tight_layout()

    # Salva a figura em um arquivo PNG
    plt.savefig('resultados_graficos.png')
    plt.close()

    """# Gráfico PSNR
    plt.figure(figsize=(10, 6))
    plt.bar(codecs, psnr_values, color='blue')
    plt.title('Comparação de PSNR')
    plt.xlabel('Codec')
    plt.ylabel('PSNR')
    plt.show()

    # Gráfico SSIM
    plt.figure(figsize=(10, 6))
    plt.bar(codecs, ssim_values, color='green')
    plt.title('Comparação de SSIM')
    plt.xlabel('Codec')
    plt.ylabel('SSIM')
    plt.show()

    # Gráfico Taxa de Bits
    plt.figure(figsize=(10, 6))
    plt.bar(codecs, bitrate_values, color='orange')
    plt.title('Comparação de Taxa de Bits')
    plt.xlabel('Codec')
    plt.ylabel('Taxa de Bits (bps)')
    plt.show()

    # Gráfico Tamanho do Arquivo
    plt.figure(figsize=(10, 6))
    plt.bar(codecs, file_size_values, color='red')
    plt.title('Comparação de Tamanho de Arquivo')
    plt.xlabel('Codec')
    plt.ylabel('Tamanho do Arquivo (MB)')
    plt.show()"""

def main():
    input_file = "video.mp4"  # Substitua pelo caminho do seu vídeo
    codecs = ['libx264', 'libx265', 'vp9']  # Codecs para comparar
    results = []

    for codec in codecs:
        output_file = f"output_{codec}.mp4"
        print(f"Convertendo {input_file} para {codec}...")

        # Executa a conversão
        try:
            convert_video(input_file, output_file, codec)
        except FileNotFoundError as e:
            print(e)
            continue  # Pula para o próximo codec se a conversão falhar

        # Calcula PSNR e SSIM
        try:
            psnr, ssim, bitrate, file_size = calculate_metrics(input_file, output_file)
            results.append((codec, psnr, ssim, bitrate, file_size))
        except ValueError as e:
            print(f"Erro ao calcular métricas para {output_file}: {e}")
    
    # Gerar gráficos com os resultados
    if results:
        plot_results(results)

if __name__ == "__main__":
    main()
