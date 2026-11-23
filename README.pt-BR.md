# Resolve Autopilot

Automatize o **DaVinci Resolve Studio** com Python e [Claude Code](https://claude.com/claude-code):
monte a timeline a partir de uma pasta de takes, aplique um visual consistente, pré-misture o áudio
(voz tratada, música que abaixa quando há fala, efeitos sonoros nos cortes) e renderize.

Deixe rodando e revise o resultado de manhã. A mídia original nunca é alterada nem apagada.

🇺🇸 [Read in English](README.md)

## O que tem

- **Conexão** com o Resolve no Windows, macOS e Linux, com mensagem clara quando ele não responde.
- **Montagem da timeline** a partir de takes numerados (`01.mp4`, `02.mp4`...).
- **Visual**: zoom alternado e cor (CDL) numa timeline *duplicada*, com marcador em cada corte.
- **Pré-mix de áudio com ffmpeg** (a API não controla volume): voz reconstruída dos originais e limpa,
  música com ducking, efeitos alinhados ao corte, tudo no volume-alvo (LUFS).
- **Render** pela fila do Resolve, aplicando as configurações uma a uma.
- **Inspetor somente leitura** que mostra as timelines em JSON para o assistente de IA.
- **Skill do Claude Code** em `skills/resolve-autopilot`.

## Requisitos

- DaVinci Resolve **Studio** aberto com um projeto.
- Resolve: *Preferences > System > General > External scripting using: Local*.
- Python 3.9+ e [ffmpeg](https://ffmpeg.org/) (ou `pip install imageio-ffmpeg`).

## Instalar e usar

```bash
pip install "resolve-autopilot[ffmpeg] @ git+https://github.com/costagonzaga/resolve-autopilot"
resolve-autopilot check
resolve-autopilot build ./takes "Meu reel"
resolve-autopilot look "Meu reel" "Meu reel v2"
resolve-autopilot mix "Meu reel v2" musica.wav ./audio --sfx whoosh1.wav whoosh2.wav
resolve-autopilot add-audio "Meu reel v2" ./audio
resolve-autopilot render "Meu reel v2" ./saida reel --size 1080 1920
```

## Motion: Resolve + Remotion

O Resolve edita, o [Remotion](https://www.remotion.dev) desenha os gráficos animados e o
`resolve-autopilot` faz a ponte: renderiza um clipe **ProRes 4444 transparente** no tamanho e
no frame rate da sua timeline e o coloca numa trilha nova acima da V1 de uma timeline *duplicada*.
Seus takes nunca são tocados.

```bash
cd motion && npm install && cd ..        # uma vez; precisa de Node.js 20+
resolve-autopilot motion "Meu reel v2" "Meu reel v3" \
    --lead "o segredo é" --word "CONSISTÊNCIA" --at 3.5 --duration 2.5
```

O template (`motion/src/TitleHighlight.tsx`) tem uma linha branca pequena e uma palavra grande
amarela em Poppins que entra com mola e some com fade. Copie-o para criar os seus.

## Situação

Versão inicial (v0.1), testada no Windows com Resolve Studio 21. Os caminhos de macOS e Linux seguem
a documentação da Blackmagic, mas **não foram testados**: relatos e correções são bem-vindos.
Veja o [CONTRIBUTING.md](CONTRIBUTING.md).

## Licença

MIT. DaVinci Resolve é marca da Blackmagic Design; este projeto não tem ligação com ela.
