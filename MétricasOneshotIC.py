import os
import glob
import json
import re
from pprint import pprint

def word2syllables(word):
    pattern = r'[^aeiouáéíóúâêîôûãõü]+[aeiouáéíóúâêîôûãõü]+|[aeiouáéíóúâêîôûãõü]+'
    return re.findall(pattern, word, re.IGNORECASE)

def minha_tokenizacao(texto):
    return re.findall(r'\b[\wáéíóúâêîôûãõçü]+\b', texto, re.UNICODE)

def diversidade_lexical(tokens):
    return len(set(tokens)) / len(tokens) if tokens else 0

def complexidade_lexical(tokens):
    if not tokens:
        return 0
    total_silabas = sum(len(word2syllables(token.lower())) for token in tokens)
    return total_silabas / len(tokens)

def processar_texto(texto):
    tokens = minha_tokenizacao(texto)
    div_lex = diversidade_lexical(tokens)
    comp_lex = complexidade_lexical(tokens)
    return tokens, div_lex, comp_lex

def natural_key(string_):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', string_)]

def calcular_media(valores):
    return sum(valores) / len(valores) if valores else 0

def calcular_desvio_padrao(valores):
    n = len(valores)
    if n <= 1:
        return 0
    media = calcular_media(valores)
    variancia = sum((x - media) ** 2 for x in valores) / (n - 1)
    return variancia ** 0.5

def processar_arquivos_json_da_pasta(caminho_da_pasta):
    arquivos_json = glob.glob(os.path.join(caminho_da_pasta, '*.json'))
    arquivos_json.sort(key=natural_key)
    print(f"Total de arquivos JSON encontrados e lidos: {len(arquivos_json)}")

    div_lex_original_total = []
    comp_lex_original_total = []
    div_lex_gerado_total = []
    comp_lex_gerado_total = []

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

                _, div_lex_original, comp_lex_original = processar_texto(texto_original)
                _, div_lex_gerado, comp_lex_gerado = processar_texto(texto_gerado)

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

    resultado_geral = {
        "diversidade_lexical_original_média": f"{calcular_media(div_lex_original_total):.2f}",
        "diversidade_lexical_original_desvio": f"{calcular_desvio_padrao(div_lex_original_total):.2f}",
        "complexidade_lexical_original_média": f"{calcular_media(comp_lex_original_total):.2f}",
        "complexidade_lexical_original_desvio": f"{calcular_desvio_padrao(comp_lex_original_total):.2f}",
        "diversidade_lexical_sintetico_média": f"{calcular_media(div_lex_gerado_total):.2f}",
        "diversidade_lexical_sintetico_desvio": f"{calcular_desvio_padrao(div_lex_gerado_total):.2f}",
        "complexidade_lexical_sintetico_média": f"{calcular_media(comp_lex_gerado_total):.2f}",
        "complexidade_lexical_sintetico_desvio": f"{calcular_desvio_padrao(comp_lex_gerado_total):.2f}",
    }

    print("\n Resultado Individual:")
    pprint(resultados_individuais)
    print("\n Resultado Geral:")
    pprint(resultado_geral)
    print("A métrica de complexidade lexical foi calculada com base na razão sílabas/ palavras, sendo assim, a complexidade lexical é a média de silabas por palavra no texto. Foi se usado sílabas em vez de tokens pois o código da professora era capaz de separar as palavras em sílabas, e dessa forma, eu aproveitei esse código para calcular essa métrica substituindo os tokens pelas sílabas")

    return resultados_individuais, resultado_geral
    

if __name__ == "__main__":
    caminho_da_pasta = "."  # pasta atual onde estão script e JSONs
    processar_arquivos_json_da_pasta(caminho_da_pasta)
