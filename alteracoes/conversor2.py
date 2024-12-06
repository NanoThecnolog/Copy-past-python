import os
import subprocess
import matplotlib.pyplot as plt
import psutil
import time
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors

def monitor_resources(process, interval=1):
    """
    Monitora o uso da CPU em intervalos especificados enquanto um processo está em execução.

    Args:
        process: Processo a ser monitorado.
        interval: Intervalo em segundos

    Returns:
        list: Uma lista contendo os valores de uso de CPU durante a execução do processo.
    """
    cpu_usage = []

    try:
        while process.poll() is None:
            cpu_percent = psutil.cpu_percent(interval=interval)
            cpu_usage.append(cpu_percent)
    except KeyboardInterrupt:
        pass  # Permite interrupção manual

    return cpu_usage

def convert_video(input_file, output_file, codec):
    """
    Converte um vídeo para um codec especificado usando FFmpeg.

    Args:
        input_file (str): Caminho do arquivo de vídeo de entrada.
        output_file (str): Caminho do arquivo de vídeo convertido.
        codec (str): Codec de vídeo para conversão.

    Returns:
        list: Dados de uso de CPU durante a conversão.
    """
    # Comando FFmpeg para conversão de vídeo
    cmd = [
        'ffmpeg', '-i', input_file, '-c:v', codec, '-crf', '23', output_file
    ]
    # Inicia o processo de conversão
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)

    # Monitora o uso de CPU enquanto o processo está ativo
    cpu_usage = monitor_resources(process)
    process.wait()  # Aguarda a conclusão do processo

    # Verifica se o arquivo de saída foi criado com sucesso
    if not os.path.exists(output_file):
        raise FileNotFoundError(f"Erro: Arquivo de saída '{output_file}' não foi criado.")
    
    print(f"Conversão para {codec} concluída com sucesso.")
    return cpu_usage

def calculate_metrics(input_file, output_file):
    """
    Calcula métricas de qualidade (PSNR, SSIM), taxa de bits e tamanho do arquivo.

    Args:
        input_file (str): Caminho do arquivo de vídeo original.
        output_file (str): Caminho do arquivo de vídeo convertido.

    Returns:
        tuple: Métricas calculadas (PSNR, SSIM, taxa de bits, tamanho do arquivo em MB).
    """
    if not os.path.exists(output_file):
        raise FileNotFoundError(f"Arquivo de saída '{output_file}' não encontrado.")

    # Comando para calcular PSNR e SSIM usando FFmpeg
    cmd = [
        'ffmpeg', '-i', output_file, '-i', input_file, '-lavfi', 
        '[0:v][1:v]psnr=stats_file=psnr.log;[0:v][1:v]ssim=stats_file=ssim.log', 
        '-f', 'null', '-'
    ]
    # Executa o comando FFmpeg
    process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    
    # Extrai as métricas PSNR e SSIM dos logs gerados
    psnr_lines = [line for line in process.stderr.split('\n') if 'average:' in line]
    ssim_lines = [line for line in process.stderr.split('\n') if 'All:' in line]

    if not psnr_lines or not ssim_lines:
        raise ValueError("Falha ao extrair PSNR ou SSIM. Verifique a saída do FFmpeg.")

    # Extrai os valores específicos de PSNR e SSIM
    psnr_value = float(psnr_lines[0].split('average:')[1].strip().split()[0])
    ssim_value = float(ssim_lines[0].split('All:')[1].split('(')[0].strip().split()[0])
    
    # Calcula o tamanho do arquivo convertido em megabytes
    file_size = os.path.getsize(output_file) / 1024 / 1024  
    
    # Comando para calcular a taxa de bits do vídeo convertido
    bitrate_cmd = [
        'ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 
        'stream=bit_rate', '-of', 'default=noprint_wrappers=1:nokey=1', output_file
    ]
    bitrate = float(subprocess.check_output(bitrate_cmd).decode('utf-8').strip())
    
    return psnr_value, ssim_value, bitrate, file_size

def plot_results(results, output_folder):
    """
    Gera gráficos das métricas calculadas e salva em um arquivo PNG.

    Args:
        results (list): Lista de resultados com métricas dos vídeos convertidos.
        output_folder (str): Caminho da pasta onde os gráficos serão salvos.
    """
    # Extrai dados dos resultados para plotagem
    codecs = [r[0] for r in results]
    psnr_values = [r[1] for r in results]
    ssim_values = [r[2] for r in results]
    bitrate_values = [r[3] for r in results]
    file_size_values = [r[4] for r in results]

    # Cria uma figura com 4 gráficos verticais
    fig, axs = plt.subplots(4, 1, figsize=(10, 24))

    # Gráfico PSNR
    axs[0].bar(codecs, psnr_values, color='blue')
    axs[0].set_title('Comparação de PSNR')

    # Gráfico SSIM
    axs[1].bar(codecs, ssim_values, color='green')
    axs[1].set_title('Comparação de SSIM')

    # Gráfico Taxa de Bits
    axs[2].bar(codecs, bitrate_values, color='orange')
    axs[2].set_title('Comparação de Taxa de Bits')

    # Gráfico Tamanho do Arquivo
    axs[3].bar(codecs, file_size_values, color='red')
    axs[3].set_title('Comparação de Tamanho de Arquivo')

    # Ajusta a disposição e salva a imagem
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'resultados_graficos.png'))
    plt.close()


def generate_pdf_report(output_folder, results, resource_data):
    """
    Gera um relatório PDF contendo as métricas calculadas e dados de uso de recursos.

    Args:
        output_folder (str): Caminho da pasta onde o relatório PDF será salvo.
        results (list): Lista de resultados das métricas calculadas para cada codec.
        resource_data (list): Dados de uso de CPU coletados durante a conversão.

    Returns:
        None: O relatório é salvo como um arquivo PDF no diretório especificado.
    """
    pdf_file = os.path.join(output_folder, 'relatorio.pdf')
    c = canvas.Canvas(pdf_file, pagesize=letter)  # Cria o arquivo PDF
    
    # Título do PDF
    c.setFont("Helvetica-Bold", 16)
    c.drawString(1 * inch, 10.5 * inch, "Relatório de Comparação de Vídeos")
    c.setLineWidth(1)
    c.line(1 * inch, 10.3 * inch, 7.5 * inch, 10.3 * inch)
    
    y = 9.8 * inch  # Posição inicial para o conteúdo do relatório
    
    for idx, (codec, psnr, ssim, bitrate, size) in enumerate(results):
        # Dados das métricas para cada codec
        c.setFont("Helvetica-Bold", 14)
        c.drawString(1 * inch, y, f"Codec: {codec}")
        
        c.setFont("Helvetica", 12)
        c.drawString(1.2 * inch, y - 20, f"PSNR: {psnr:.2f} dB")
        c.drawString(1.2 * inch, y - 40, f"SSIM: {ssim:.4f}")
        c.drawString(1.2 * inch, y - 60, f"Bitrate: {bitrate / 1000:.2f} kbps")  # Conversão para kbps
        c.drawString(1.2 * inch, y - 80, f"Tamanho: {size:.2f} MB")
        
        # Calcula o uso médio da CPU durante a conversão
        cpu_avg = sum(resource_data[idx]['cpu']) / len(resource_data[idx]['cpu'])
        c.drawString(1.2 * inch, y - 100, f"Uso médio da CPU: {cpu_avg:.2f}%")
        
        # Desenha um separador entre as seções de cada codec
        y -= 160  # Move a posição para a próxima seção
        c.line(1 * inch, y + 20, 7.5 * inch, y + 20)
        
        # Cria uma nova página se o espaço acabar
        if y < 1.5 * inch:
            c.showPage()
            y = 9.8 * inch

    c.save()  # Salva o relatório PDF

def main():
    """
    Função principal que controla o fluxo de processamento de vídeos e geração de relatórios.

    - Converte vídeos para diferentes codecs.
    - Calcula métricas de qualidade e uso de recursos.
    - Gera gráficos comparativos e um relatório em PDF.

    Returns:
        None: Os resultados são salvos em arquivos gráficos e PDFs.
    """
    input_videos = ["video1.mp4", "video2.mp4", "video3.mp4"]  # Lista de vídeos de entrada
    codecs = ['libx264', 'libx265', 'vp9']  # Codecs de vídeo a serem testados



    for input_file in input_videos:
        print("Arquivo de entrada:", os.path.abspath(input_file))
        
        # Cria uma pasta específica para os resultados de cada vídeo
        video_name = os.path.splitext(os.path.basename(input_file))[0]
        output_folder = os.path.join("resultados", video_name)
        os.makedirs(output_folder, exist_ok=True)

        results = []  # Armazena métricas calculadas para cada codec
        resource_data = []  # Armazena dados de uso de CPU

        for codec in codecs:
            output_file = os.path.join(output_folder, f"{video_name}_{codec}.mp4")
            print(f"Convertendo {input_file} para {codec}...")

            try:
                # Converte o vídeo e monitora o uso de CPU
                cpu_usage = convert_video(input_file, output_file, codec)
                # Calcula métricas de qualidade e desempenho
                psnr, ssim, bitrate, file_size = calculate_metrics(input_file, output_file)
                
                # Armazena os resultados e os dados de uso de recursos
                results.append((codec, psnr, ssim, bitrate, file_size))
                resource_data.append({'cpu': cpu_usage})
            
            except Exception as e:
                print(f"Erro no processamento do codec {codec}: {e}")

        # Gera gráficos das métricas calculadas
        plot_results(results, output_folder)
        # Gera um relatório em PDF com os resultados e o uso de recursos
        generate_pdf_report(output_folder, results, resource_data)

if __name__ == "__main__":
    main()