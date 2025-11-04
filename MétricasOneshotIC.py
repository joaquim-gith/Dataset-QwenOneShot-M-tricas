import os
import glob
import json
import re
from pprint import pprint
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import statistics

def word2syllables(word): #Divisão por sílabas
    pattern = r'[^aeiouáéíóúâêîôûãõü]+[aeiouáéíóúâêîôûãõü]+|[aeiouáéíóúâêîôûãõü]+' 
    return re.findall(pattern, word, re.IGNORECASE)

def minha_tokenizacao(texto):
    # Tokeniza palavras com >=3 letras, incluindo acentos
    tokens = re.findall(r'\b[a-záàâãéèêíïóôõöúçñ]{3,}\b', texto.lower(), re.UNICODE)
    return tokens

def diversidade_lexical(tokens): #Calculo diversidade lexical
    return len(set(tokens)) / len(tokens) if tokens else 0

def complexidade_lexical(tokens): #Calculo complexidade lexical
    if not tokens:
        return 0
    total_silabas = sum(len(word2syllables(token)) for token in tokens)
    return total_silabas / len(tokens)

def natural_key(string_): #Ordena os arquivos de forma certa
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', string_)]

def processar_arquivos_json_da_pasta(caminho_da_pasta): #Leitura dos arquivos do dataset
    arquivos_json = glob.glob(os.path.join(caminho_da_pasta, '*.json'))
    arquivos_json.sort(key=natural_key)
    print(f"Total de arquivos JSON encontrados e lidos: {len(arquivos_json)}")

    div_lex_original_total = []
    comp_lex_original_total = []
    div_lex_gerado_total = []
    comp_lex_gerado_total = []

    palavras_nao_identificadas_original = set()
    palavras_nao_identificadas_gerado = set()

    total_palavras_original = 0
    total_palavras_identificadas_original = 0
    total_palavras_gerado = 0
    total_palavras_identificadas_gerado = 0

    resultados_individuais = []

    for arquivo in arquivos_json:
        with open(arquivo, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not isinstance(data, list):
                data = [data]

            for item in data:
                texto_original = item.get("comandoTematicoOriginal", "")
                texto_gerado_dict = item.get("comando_tematico", {})
                texto_gerado = " ".join(texto_gerado_dict.values()) if texto_gerado_dict else ""

                tokens_original = minha_tokenizacao(texto_original)
                tokens_gerado = minha_tokenizacao(texto_gerado)

                # Palavras totais sem filtro para log de não identificadas
                todas_palavras_original = re.findall(r'\b\w+\b', texto_original.lower())
                todas_palavras_gerado = re.findall(r'\b\w+\b', texto_gerado.lower())

                # As palavras não identificadas são aquelas com menos que 3 caracteres
                nao_identificadas_original = [p for p in todas_palavras_original if len(p) < 3]
                nao_identificadas_gerado = [p for p in todas_palavras_gerado if len(p) < 3]

                palavras_nao_identificadas_original.update(nao_identificadas_original)
                palavras_nao_identificadas_gerado.update(nao_identificadas_gerado)

                total_palavras_original += len(todas_palavras_original)
                total_palavras_identificadas_original += len(tokens_original)
                total_palavras_gerado += len(todas_palavras_gerado)
                total_palavras_identificadas_gerado += len(tokens_gerado)

                div_lex_original = diversidade_lexical(tokens_original)
                comp_lex_original = complexidade_lexical(tokens_original)
                div_lex_gerado = diversidade_lexical(tokens_gerado)
                comp_lex_gerado = complexidade_lexical(tokens_gerado)

                div_lex_original_total.append(div_lex_original)
                comp_lex_original_total.append(comp_lex_original)
                div_lex_gerado_total.append(div_lex_gerado)
                comp_lex_gerado_total.append(comp_lex_gerado)

                resultados_individuais.append({
                    "arquivo": os.path.basename(arquivo),
                    "diversidade_lexical_original": f"{div_lex_original:.3f}",
                    "complexidade_lexical_original": f"{comp_lex_original:.3f}",
                    "diversidade_lexical_sintetico": f"{div_lex_gerado:.3f}",
                    "complexidade_lexical_sintetico": f"{comp_lex_gerado:.3f}"
                })

    percentual_id_original = (total_palavras_identificadas_original / total_palavras_original * 100) if total_palavras_original > 0 else 0
    percentual_id_gerado = (total_palavras_identificadas_gerado / total_palavras_gerado * 100) if total_palavras_gerado > 0 else 0

    print(f"\nPercentual de palavras identificadas - Original: {percentual_id_original:.2f}%")
    print(f"Percentual de palavras identificadas - Sintético: {percentual_id_gerado:.2f}%")

    with open("palavras_nao_identificadas_original.txt", "w", encoding="utf-8") as f_out:
        for p in sorted(palavras_nao_identificadas_original):
            f_out.write(p + "\n")

    with open("palavras_nao_identificadas_gerado.txt", "w", encoding="utf-8") as f_out:
        for p in sorted(palavras_nao_identificadas_gerado):
            f_out.write(p + "\n")

    resultado_geral = { #Resultados Gerais
        "diversidade_lexical_original_média": f"{sum(div_lex_original_total)/len(div_lex_original_total):.2f}",
        "diversidade_lexical_original_desvio": f"{statistics.stdev(div_lex_original_total):.2f}" if len(div_lex_original_total)>1 else "0.00",
        "complexidade_lexical_original_média": f"{sum(comp_lex_original_total)/len(comp_lex_original_total):.2f}",
        "complexidade_lexical_original_desvio": f"{statistics.stdev(comp_lex_original_total):.2f}" if len(comp_lex_original_total)>1 else "0.00",
        "diversidade_lexical_sintetico_média": f"{sum(div_lex_gerado_total)/len(div_lex_gerado_total):.2f}",
        "diversidade_lexical_sintetico_desvio": f"{statistics.stdev(div_lex_gerado_total):.2f}" if len(div_lex_gerado_total)>1 else "0.00",
        "complexidade_lexical_sintetico_média": f"{sum(comp_lex_gerado_total)/len(comp_lex_gerado_total):.2f}",
        "complexidade_lexical_sintetico_desvio": f"{statistics.stdev(comp_lex_gerado_total):.2f}" if len(comp_lex_gerado_total)>1 else "0.00",
    }

    print("\n Resultado Individual:")
    pprint(resultados_individuais)
    print("\n Resultado Geral:")
    pprint(resultado_geral)
	#Explicação
    print("A métrica de complexidade lexical foi calculada com base na razão sílabas/ palavras, sendo assim, a complexidade lexical é a média de sílabas por palavra no texto. Foi usado sílabas em vez de tokens pois o código da professora era capaz de separar as palavras em sílabas, e assim aproveitei para essa métrica.")
#Box plot
    fig, axs = plt.subplots(1, 2, figsize=(14, 6))

    axs[0].boxplot(
        [comp_lex_original_total, comp_lex_gerado_total],
        labels=['Original', 'Sintético'],
        showmeans=True,
        meanprops=dict(marker='^', markerfacecolor='green', markeredgecolor='green', markersize=10)
    )
    axs[0].set_title('Box-plot da Complexidade Lexical')
    axs[0].set_ylabel('Média de Sílabas por Palavra')

    axs[1].boxplot(
        [div_lex_original_total, div_lex_gerado_total],
        labels=['Original', 'Sintético'],
        showmeans=True,
        meanprops=dict(marker='^', markerfacecolor='green', markeredgecolor='green', markersize=10)
    )
    axs[1].set_title('Box-plot da Diversidade Lexical')
    axs[1].set_ylabel('Diversidade Lexical')

    mean_marker = mlines.Line2D([], [], color='green', marker='^', linestyle='None', markersize=10, label='Média (triângulo verde)')
    median_line = mlines.Line2D([], [], color='orange', linewidth=2, label='Mediana (linha laranja)')
    iqr_box = mlines.Line2D([], [], color='black', marker='s', linestyle='None', markersize=10, label='Intervalo interquartil (caixa)')

    for ax in axs:
        ax.legend(handles=[mean_marker, median_line, iqr_box], loc='upper right')

    plt.suptitle('Análise do Dataset QwenOneshot')
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()

    return resultados_individuais, resultado_geral

if __name__ == "__main__":
    caminho_da_pasta = "."
    processar_arquivos_json_da_pasta(caminho_da_pasta)
